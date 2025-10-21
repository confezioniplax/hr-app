from app.db.db import DbManager, MySQLDb, QueryType
from app.sql_query.Query import QuerySqlMYSQL

class MachineRepository:
    def __init__(self):
        self.db = DbManager(MySQLDb())

    def get_all(self, active_only: bool = True):
        sql = QuerySqlMYSQL.get_all_machines_sql(active_only)
        with self.db as db:
            return db.execute_query(sql, query_type=QueryType.GET)

    def get_by_id(self, machine_id: int):
        sql = QuerySqlMYSQL.get_machine_by_id_sql()
        with self.db as db:
            return db.execute_query(sql, (machine_id,), fetchall=False, query_type=QueryType.GET)
