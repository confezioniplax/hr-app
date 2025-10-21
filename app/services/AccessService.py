"""
 MIT License
 
 Copyright (c) 2024 Riccardo Leonelli
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
 
"""

from decimal import Decimal
from fastapi.encoders import jsonable_encoder
import pandas as pd
from app.dependencies import TokenData
from app.repo.AccessRepository import AccessRepository


class AccessService:
    def __init__(self):
        # Initialize with an AccessRepository instance
        self.repository = AccessRepository()

    def get_access_by_date(self, date: str):
        # Retrieve access records by specific date
        return self.repository.get_access_by_date(date)

    def get_access_by_employee(self, date: str, current_user: TokenData):
        # Retrieve access records by date for a specific employee
        return self.repository.get_access_by_employee(date, current_user)

    def get_registry(self):
        # Fetch the complete registry of employees
        return self.repository.get_registry()

    def person_exists(self, employee_id: int) -> bool:
        # Check if a person exists in the database by employee ID
        return self.repository.person_exists(employee_id)
    
    def add_person(self, employee_id: int, first_name: str, last_name: str, email: str, role: str, hire_date: str, end_date: str, user_password: str):
        # Add a new person to the registry
        self.repository.add_person(employee_id, first_name, last_name, email, role, hire_date, end_date, user_password)

    def update_person(self, employee_id: int, first_name: str, last_name: str, email: str, role: str, hire_date: str, end_date: str, user_password: str):
        # Update an existing person's details in the registry
        self.repository.update_person(employee_id, first_name, last_name, email, role, hire_date, end_date, user_password)

    def delete_person(self, employee_id: int):
        # Remove a person from the registry
        self.repository.delete_person(employee_id)

    def insert_access(self, employee_id: int):
        # Log access event for an employee
        self.repository.insert_access(employee_id)

    def insert_access_manual(self, employee_id: int, timestamp, creator):
        # Manually log access for an employee
        self.repository.insert_access_manual(employee_id, timestamp, creator)

    def extract_delays(self, date):
        # Extract delays data for a specific date and create an Excel report
        data = self.repository.extract_delays(date)
        if data:
            df = pd.DataFrame(data)
            
            # Convert Decimal types to float for compatibility
            df['delay_minutes'] = df['delay_minutes'].apply(lambda x: float(x) if isinstance(x, Decimal) else x)

            # Create Excel file path and save
            excel_path = f"delays_{date.strftime('%m%d%Y')}.xlsx"
            df.to_excel(excel_path, index=False)
            
            print(f"Excel file created at {excel_path}")
            return excel_path
        else:
            print("No data found for the given date.")
            return None 
    
    def create_excel_report(self, date):
        data = self.repository.get_report_data(date)
        df = pd.DataFrame(data)

        # Format and prepare data for Excel output
        df['access_time'] = pd.to_datetime(df['access_time'])
        df.sort_values(by=['employee_id', 'access_time'], inplace=True)

        # Sequence numbers for pairing in and out times
        df['seq'] = df.groupby(['employee_id', df['access_time'].dt.date]).cumcount() + 1

        # Separate in and out times
        in_times = df[df['seq'] % 2 != 0].copy()
        out_times = df[df['seq'] % 2 == 0].copy()

        # Rename columns for clarity
        in_times.rename(columns={'access_time': 'in_time'}, inplace=True)
        out_times.rename(columns={'access_time': 'out_time'}, inplace=True)

        # Sort times to ensure correct pairing
        in_times.sort_values(by='in_time', inplace=True)
        out_times.sort_values(by='out_time', inplace=True)

        # Merge in and out times to calculate durations
        merged_times = pd.merge_asof(
            in_times,
            out_times,
            left_on='in_time',
            right_on='out_time',
            by='employee_id',
            direction='forward',
            allow_exact_matches=True
        )

        # Calculate durations and aggregate monthly hours
        merged_times['duration'] = (merged_times['out_time'] - merged_times['in_time']).dt.total_seconds() / 3600

        # Aggregate hours and prepare final DataFrame
        monthly_hours = merged_times.groupby('employee_id')['duration'].sum().reset_index()
        monthly_hours['employee_id'] = monthly_hours['employee_id'].astype(int)
        monthly_hours['duration'] = monthly_hours['duration'].astype(float)

        # Prepare the final report with employee names
        reg = self.get_registry()
        name_map = {emp['employee_id']: (emp['first_name'], emp['last_name']) for emp in reg}

        # Create lists for first and last names
        first_names = []
        last_names = []

        for emp_id in monthly_hours['employee_id']:
            if emp_id in name_map:
                first_name, last_name = name_map[emp_id]
            else:
                first_name, last_name = None, None
            first_names.append(first_name)
            last_names.append(last_name)

        # Add the names to the DataFrame
        monthly_hours['first_name'] = first_names
        monthly_hours['last_name'] = last_names

        # Format the final DataFrame
        df = pd.DataFrame(monthly_hours)
        df.rename(columns={
            'employee_id': 'ID',
            'first_name': 'FIRST NAME',
            'last_name': 'LAST NAME',
            'duration': 'WORK HOURS'
        }, inplace=True)

        df = df[['ID', 'FIRST NAME', 'LAST NAME', 'WORK HOURS']]

        # Write to Excel file and return the file name
        file_name = 'month_report_' + date.strftime('%Y_%m') + '.xlsx'
        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Employee Hours')

        return file_name
