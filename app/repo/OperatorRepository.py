from typing import Any, Dict, List, Optional
from app.db.db import DbManager, MySQLDb, QueryType
from app.sql_query.Query import QuerySqlMYSQL

class OperatorRepository:
    def __init__(self):
        self.db = DbManager(MySQLDb())


    def list(self, department_id: Optional[int] = None, q: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Se department_id è valorizzato, filtra via JOIN su operator_departments.
        Il filtro 'q' è opzionale (nome/cognome).
        """
        with self.db as db:
            if department_id is not None:
                sql = QuerySqlMYSQL.list_operators_sql(active_only=True, filter_by_department=True)
                rows = db.execute_query(sql, (department_id,), query_type=QueryType.GET)
            else:
                sql = QuerySqlMYSQL.list_operators_sql(active_only=True, filter_by_department=False)
                rows = db.execute_query(sql, query_type=QueryType.GET)

        # normalizza a list[dict]
        data = [dict(r) for r in rows]

        if q:
            ql = q.strip().lower()
            data = [
                o for o in data
                if ql in str(o.get("first_name","")).lower()
                or ql in str(o.get("last_name","")).lower()
                or ql in (str(o.get("last_name",""))+" "+str(o.get("first_name",""))).lower()
                or ql in (str(o.get("first_name",""))+" "+str(o.get("last_name",""))).lower()
            ]
        return data

    def get(self, operator_id: int):
        sql = QuerySqlMYSQL.get_operator_sql()
        with self.db as db:
            return db.execute_query(sql, (operator_id,), fetchall=False, query_type=QueryType.GET)

    def create(self, first_name: str, last_name: str, badge_code: str | None = None) -> int:
        sql = QuerySqlMYSQL.insert_operator_sql()
        with self.db as db:
            db.execute_query(sql, (first_name, last_name, badge_code), query_type=QueryType.INSERT)
            row = db.execute_query(QuerySqlMYSQL.last_insert_id_sql(), fetchall=False, query_type=QueryType.GET)
            db.commit()
            return int(row["id"])

    def update(self, operator_id: int, first_name: str, last_name: str, badge_code: str | None, active: bool):
        sql = QuerySqlMYSQL.update_operator_sql()
        with self.db as db:
            db.execute_query(sql, (first_name, last_name, badge_code, active, operator_id), query_type=QueryType.UPDATE)
            db.commit()

    def get_by_email(self, email: str):
        sql = "SELECT * FROM operators WHERE email=%s"
        with self.db as db:
            return db.execute_query(sql, (email,), fetchall=False, query_type=QueryType.GET)

    def create_with_auth(self, first_name: str, last_name: str, email: str, password_hash: str, role: str = "HR"):
        sql = "INSERT INTO operators (first_name, last_name, email, user_password, role, active) VALUES (%s,%s,%s,%s,%s,1)"
        with self.db as db:
            db.execute_query(sql, (first_name, last_name, email, password_hash, role), query_type=QueryType.INSERT)
            db.commit()

    def update_password_and_role(self, operator_id: int, password_hash: str, role: str):
        sql = "UPDATE operators SET user_password=%s, role=%s WHERE id=%s"
        with self.db as db:
            db.execute_query(sql, (password_hash, role, operator_id), query_type=QueryType.UPDATE)
            db.commit()