
# Venue-Access Project

The Venue-Access project is a comprehensive full-stack web application designed to efficiently manage employee entrances and exits using QR code technology. This application facilitates HR personnel and directors by providing robust tools for managing employee access and monitoring attendance.

## Table of Contents

- [Concept](#concept)
- [User Stories](#user-stories)
- [Requirements](#requirements)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Deployment](#deployment)
- [License](#license)

## Concept

The application is built using FastAPI with HTML templates rendered through Jinja and runs on a Uvicorn ASGI web server. All data is stored in a MySQL database.

## User Functionalities

### HR Personnel and CEO

1. Add new employee details to the system.
2. Update existing employee information.
3. View access logs.
4. Generate compliance and attendance reports.
5. Delete an employee from the system.
6. Log employee access by scanning QR codes.

### Employee

1. View personal access logs.

## Requirements

### Functional Requirements

- **Employee Management**:
  - Add, update, and delete employee details.
- **Access Logging**:
  - Log access using QR codes.
  - Manual access log entry.
- **Reporting and Analytics**:
  - View access logs.
  - Generate and export reports.

### Non-functional Requirements

- **Security**:
  - Cookie-based JWT for session management.
  - Data encryption in transit and at rest.
- **Usability**:
  - Responsive design.
  - Intuitive UI/UX.

## Architecture

The application is designed with a service-oriented architecture. It consists of the following components:

- **MySQL database**: Central data store.
- **Repositories and Services**: Handle business logic and data interaction.
- **Routers**: Manage API and view routing.
- **Front-end**: Jinja templates for HTML rendering.

## Installation

### Prerequisites

- Python
- MySQL
- Docker (optional, for containerized deployment)

### Steps

1. **Clone the repository**

2. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up the database**:
- the app work on a MySQL db, the generations of the tables are in [text](app/sql/sql_executions.sql)
4. **Run the application**:
- Press F5 to start the FastAPI application with Uvicorn in debug mode.


## Usage

### Accessing the System

- **Logging In**: Navigate to the login page and enter your credentials.
- **HR Functions**: Manage employees, view logs, and generate reports.
- **Employee Functions**: View personal access logs.

### API Endpoints

#### POST /api/insert_presence
Logs an employee's presence using their unique ID.
- **Parameters**:
  - `id` (required): Employee's unique identifier.

#### POST /api/add_or_update_person
Adds or updates an employee record.
- **Parameters**:
  - `rowId`, `first_name`, `last_name`, `email`, `role`, `hire_date`, `end_date`, `user_password`.

#### POST /api/delete_person
Deletes an employee record.
- **Parameters**:
  - `rowId` (required): Unique identifier for the employee record.

#### GET /api/extract_delays
Generates an Excel file with delay details.
- **Parameters**:
  - `monthYear` (required): Formatted as YYYY-MM-XX.

#### GET /api/create_excel_report
Generates an Excel report of work hours.
- **Parameters**:
  - `monthYear` (required): Formatted as YYYY-MM-XX.

## Testing

Run tests using `pytest`:

```sh
pytest
```

### Coverage

Check the coverage report to ensure all critical paths are tested.

## Deployment

### CI/CD Pipeline

The CI/CD pipeline uses GitHub Actions to build, test, and deploy the application:

1. **Build and Test**:
   - Defined in `.github/workflows/*.yaml`.
2. **Artifact Management**:
   - Docker images stored in a Harbor registry.
3. **Deployment**:
   - Kubernetes and ArgoCD for automated deployments.
4. **Monitoring and Security**:
   - Cloudflare for CDN and additional security layers.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
