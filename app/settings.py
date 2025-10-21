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

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    API_MYSQL_HOSTNAME: str = Field(...,validation_alias="API_MYSQL_HOSTNAME")
    API_MYSQL_PORT: str = Field(...,validation_alias="API_MYSQL_PORT")
    API_MYSQL_USERNAME: str = Field(...,validation_alias="API_MYSQL_USERNAME")
    API_MYSQL_PASSWORD: str = Field(...,validation_alias="API_MYSQL_PASSWORD")
    SECRET_KEY_JWT: str = Field(...,validation_alias="SECRET_KEY_JWT")
    ALGORITHM_JWT: str = Field(...,validation_alias="ALGORITHM_JWT")

    model_config = SettingsConfigDict(env_file=".env")
    
@lru_cache()
def get_settings():
    return Settings()