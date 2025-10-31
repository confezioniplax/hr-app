from __future__ import annotations
from typing import Any, Dict, List, Optional

from app.db.db import DbManager, MySQLDb, QueryType
from app.sql_query.QuerySqlCompanyDocs import QuerySqlCompanyDocs


class CompanyDocsRepository:
    def __init__(self):
        self.db = DbManager(MySQLDb())

    # LIST
    def list_docs(self, q: Optional[str], year: Optional[int], frequency: Optional[str]) -> List[Dict[str, Any]]:
        sql, params = QuerySqlCompanyDocs.list_docs_sql(q=q, year=year, frequency=frequency)
        with self.db as db:
            return db.execute_query(sql, params, query_type=QueryType.GET)

    # GET
    def get_doc(self, doc_id: int) -> Optional[Dict[str, Any]]:
        sql = QuerySqlCompanyDocs.get_doc_sql()
        with self.db as db:
            row = db.execute_query(sql, [int(doc_id)], fetchall=False, query_type=QueryType.GET)
            return row if row else None

    # UPSERT
    def upsert_doc(
        self,
        *,
        id: Optional[int],
        title: str,
        year: int,
        category: str,
        frequency: str,
        notes: Optional[str],
        file_path: Optional[str],
    ) -> int:
        """
        Se file_path è None durante un UPDATE, non aggiorna la colonna file_path.
        """
        if id:
            if file_path is None:
                sql = QuerySqlCompanyDocs.update_doc_without_file_sql()
                params = [title, int(year), category, frequency, notes, int(id)]
            else:
                sql = QuerySqlCompanyDocs.update_doc_with_file_sql()
                params = [title, int(year), category, frequency, notes, file_path, int(id)]
            with self.db as db:
                db.execute_query(sql, params, query_type=QueryType.UPDATE)
                return int(id)
        else:
            sql = QuerySqlCompanyDocs.insert_doc_sql()
            params = [title, int(year), category, frequency, notes, file_path]
            with self.db as db:
                db.execute_query(sql, params, query_type=QueryType.INSERT)
                row = db.execute_query(QuerySqlCompanyDocs.last_insert_id_sql(), fetchall=False, query_type=QueryType.GET)
                return int(row["id"]) if row else 0

    # DELETE
    def delete_doc(self, doc_id: int) -> None:
        sql = QuerySqlCompanyDocs.delete_doc_sql()
        with self.db as db:
            db.execute_query(sql, [int(doc_id)], query_type=QueryType.DELETE)
