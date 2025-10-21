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

from app.entities.Person import Person
from app.db.db import DbManager, MySQLDb, QueryType
from app.services.AuthenticationService import AuthenticationService
from app.sql_query.QueryUserAuth import SqlUserAuth

class PersonRepository:
    def __init__(self):
        self.db = DbManager(MySQLDb())

    def get_user_info_auth(self, username: str) -> Person:
        sql = SqlUserAuth.get_user_info_auth()
        params = {"email": username}
        with self.db as db:
            result = db.execute_query(sql, (username,), fetchall=True, query_type=QueryType.GET)
        if result:
            return Person(**result[0])
        return None

    def get_encrypted_password(self, password: str) -> dict:
        hashed_pw = AuthenticationService.hash_password(password=password)
        return hashed_pw
    
    def check_password(self, stored_password: str, password: str):
        return AuthenticationService.check_password(stored_hash=stored_password, provided_password=password)
