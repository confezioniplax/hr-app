from __future__ import annotations
from typing import Any, Dict, List, Optional

from app.db.db import DbManager, MySQLDb, QueryType
from app.sql_query.QuerySqlCompanyDocs import QuerySqlCompanyDocs


class CompanyDocsRepository:
    def __init__(self):
        self.db = DbManager(MySQLDb())

    # ==========================
    #  LIST DOCUMENTI
    # ==========================
    def list_docs(
        self,
        q: Optional[str],
        year: Optional[int],
        frequency: Optional[str],
        category_code: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Restituisce la lista dei documenti aziendali con eventuali filtri:
        - q: cerca su titolo o label categoria
        - year: anno
        - frequency: annuale, semestrale, ...
        - category_code: codice categoria (FK su company_doc_categories.code)
        """
        sql, params = QuerySqlCompanyDocs.list_docs_sql(
            q=q,
            year=year,
            frequency=frequency,
            category_code=category_code,
        )
        with self.db as db:
            return db.execute_query(sql, params, query_type=QueryType.GET)

    # ==========================
    #  GET SINGOLO DOCUMENTO
    # ==========================
    def get_doc(self, doc_id: int) -> Optional[Dict[str, Any]]:
        sql = QuerySqlCompanyDocs.get_doc_sql()
        with self.db as db:
            row = db.execute_query(sql, [int(doc_id)], fetchall=False, query_type=QueryType.GET)
            return row if row else None

    # ==========================
    #  UPSERT
    # ==========================
    def upsert_doc(
        self,
        *,
        id: Optional[int],
        title: str,
        year: int,
        category: str,
        deadline_rule_id: Optional[int],
        reference_date: Optional[str],
        next_due_date: Optional[str],
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
                params = [
                    title,
                    int(year),
                    category,
                    int(deadline_rule_id) if deadline_rule_id is not None else None,
                    reference_date,
                    next_due_date,
                    frequency,
                    notes,
                    int(id),
                ]
            else:
                sql = QuerySqlCompanyDocs.update_doc_with_file_sql()
                params = [
                    title,
                    int(year),
                    category,
                    int(deadline_rule_id) if deadline_rule_id is not None else None,
                    reference_date,
                    next_due_date,
                    frequency,
                    notes,
                    file_path,
                    int(id),
                ]
            with self.db as db:
                db.execute_query(sql, params, query_type=QueryType.UPDATE)
                return int(id)
        else:
            sql = QuerySqlCompanyDocs.insert_doc_sql()
            params = [
                title,
                int(year),
                category,
                int(deadline_rule_id) if deadline_rule_id is not None else None,
                reference_date,
                next_due_date,
                frequency,
                notes,
                file_path,
            ]
            with self.db as db:
                db.execute_query(sql, params, query_type=QueryType.INSERT)
                row = db.execute_query(
                    QuerySqlCompanyDocs.last_insert_id_sql(),
                    fetchall=False,
                    query_type=QueryType.GET,
                )
                return int(row["id"]) if row else 0

    def list_deadline_rules(self, *, category_code: Optional[str] = None, q: Optional[str] = None, active_only: bool = True, rule_id: Optional[int] = None) -> List[Dict[str, Any]]:
        sql = [
            "SELECT id, category_code, document_name, expiry_years, trigger_event, description, is_active",
            "FROM company_document_deadline_rules",
        ]
        conds = []
        params: List[Any] = []
        if active_only:
            conds.append("is_active = 1")
        if rule_id is not None:
            conds.append("id = %s")
            params.append(rule_id)
        if category_code:
            conds.append("category_code = %s")
            params.append(category_code)
        if q:
            conds.append("document_name LIKE %s")
            params.append(f"%{q}%")
        where = (" WHERE " + " AND ".join(conds)) if conds else ""
        order = " ORDER BY category_code ASC, document_name ASC"
        with self.db as db:
            return db.execute_query("\n".join(sql) + where + order, params if params else None, query_type=QueryType.GET)

    # ==========================
    #  DELETE
    # ==========================
    def delete_doc(self, doc_id: int) -> None:
        sql = QuerySqlCompanyDocs.delete_doc_sql()
        with self.db as db:
            db.execute_query(sql, [int(doc_id)], query_type=QueryType.DELETE)

    # ==========================
    #  CATEGORIE DOCUMENTI
    # ==========================
    def list_categories(self) -> List[Dict[str, Any]]:
        """
        Ritorna le categorie disponibili da company_doc_categories
        per popolare la combo in UI.
        """
        sql = """
            SELECT
                code,
                label,
                sort_order
            FROM company_doc_categories
            ORDER BY sort_order ASC, label ASC
        """
        with self.db as db:
            return db.execute_query(sql, query_type=QueryType.GET)
