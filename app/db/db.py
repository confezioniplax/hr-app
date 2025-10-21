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

from abc import ABC, abstractmethod
import traceback
import mysql.connector
from enum import Enum
from fastapi import HTTPException
from ..settings import get_settings

class QueryType(Enum):
    GET = 1
    INSERT = 2
    UPDATE = 3
    DELETE = 4

class DbConnection(Enum):
    DEFAULT = 1

class Db(ABC):

    @abstractmethod
    def get_connection(self):
        pass

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def execute_query(self, sql, param, fetchall, query_type: QueryType):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

class DbManager:
    def __init__(self, db_connection: Db):
        self.db = db_connection

    def __enter__(self):    
        self.db.open()    
        return self.db
        
    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.db.close()
        return True
    

class MySQLDb:    
    hostname: str = None
    port: str = None
    username: str = None
    password: str = None
    conn = None    
    cursor = None

    def __init__(self, connection: DbConnection = DbConnection.DEFAULT):        
        if connection == DbConnection.DEFAULT:
            self.hostname = get_settings().API_MYSQL_HOSTNAME
            self.port = get_settings().API_MYSQL_PORT
            self.username = get_settings().API_MYSQL_USERNAME
            self.password = get_settings().API_MYSQL_PASSWORD

    def get_connection(self):
        self.conn = mysql.connector.connect(user=self.username, password=self.password, host=self.hostname , port=self.port, database='plax')

    def open(self):
        self.get_connection()
        self.cursor = self.conn.cursor(dictionary=True)
    
    def execute_query(self, sql, param=(), fetchall: bool = True, query_type: QueryType = QueryType.GET):
        result = None
        try:
            if query_type == QueryType.GET:
                self.cursor.execute(sql, param)
                if fetchall:
                    result = self.cursor.fetchall()
                else:
                    result = self.cursor.fetchone()
            elif query_type in [QueryType.INSERT, QueryType.UPDATE, QueryType.DELETE]:
                self.cursor.execute(sql, param)
                self.conn.commit()
                res = self.cursor.rowcount
                return res
        except mysql.connector.Error as e:
            if query_type in [QueryType.INSERT, QueryType.UPDATE, QueryType.DELETE]:
                self.conn.rollback()
            raise HTTPException(status_code=500, detail="Exception: " + str(e))
        return result

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):   
        if self.cursor:    
            self.cursor.close()            
        if self.conn:
            self.conn.close()

