from app.db.db import DbManager, MySQLDb, QueryType
from app.sql_query.Query import QuerySqlMYSQL

class ArticleRepository:
    def __init__(self):
        self.db = DbManager(MySQLDb())

    def get_or_create(self, code: str | None, description: str | None, client_id: int | None) -> int:
        sel = QuerySqlMYSQL.get_article_by_code_client_sql()
        ins = QuerySqlMYSQL.insert_article_sql()
        params = (code, code, code, client_id, client_id)
        with self.db as db:
            row = db.execute_query(sel, params, fetchall=False, query_type=QueryType.GET)
            if row:
                return int(row["id"])
            db.execute_query(ins, (code, description, client_id), query_type=QueryType.INSERT)
            rid = db.execute_query(QuerySqlMYSQL.last_insert_id_sql(), fetchall=False, query_type=QueryType.GET)
            db.commit()
            return int(rid["id"])
