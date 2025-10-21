from app.db.db import DbManager, MySQLDb, QueryType
from app.sql_query.Query import QuerySqlMYSQL

class LotRepository:
    def __init__(self):
        self.db = DbManager(MySQLDb())

    def get_or_create(self, lot_code: str, client_id: int | None, article_id: int | None) -> int:
        sel = QuerySqlMYSQL.get_lot_by_code_sql()
        ins = QuerySqlMYSQL.insert_lot_sql()
        with self.db as db:
            row = db.execute_query(sel, (lot_code,), fetchall=False, query_type=QueryType.GET)
            if row:
                return int(row["id"])
            db.execute_query(ins, (lot_code, client_id, article_id), query_type=QueryType.INSERT)
            rid = db.execute_query(QuerySqlMYSQL.last_insert_id_sql(), fetchall=False, query_type=QueryType.GET)
            db.commit()
            return int(rid["id"])
