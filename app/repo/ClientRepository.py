from app.db.db import DbManager, MySQLDb, QueryType
from app.sql_query.Query import QuerySqlMYSQL

class ClientRepository:
    def __init__(self):
        self.db = DbManager(MySQLDb())

    def get_or_create(self, name: str) -> int:
        sel = QuerySqlMYSQL.get_client_by_name_sql()
        ins = QuerySqlMYSQL.insert_client_sql()
        with self.db as db:
            row = db.execute_query(sel, (name,), fetchall=False, query_type=QueryType.GET)
            if row:
                return int(row["id"])
            db.execute_query(ins, (name,), query_type=QueryType.INSERT)
            rid = db.execute_query(QuerySqlMYSQL.last_insert_id_sql(), fetchall=False, query_type=QueryType.GET)
            db.commit()
            return int(rid["id"])
