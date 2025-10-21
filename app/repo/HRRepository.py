from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import date

from app.db.db import DbManager, MySQLDb, QueryType
from app.sql_query.QuerySqlHRMYSQL import QuerySqlHRMYSQL


class HRRepository:
    def __init__(self):
        self.db_manager = DbManager(MySQLDb())

    # ---------------- helper placeholder ----------------
    @staticmethod
    def _inject_extra(sql: str, extra: str) -> str:
        # nelle f-string del modulo SQL il placeholder è {extra_conditions}
        sql = sql.replace("{extra_conditions}", extra or "")
        # copriamo anche eventuali doppie graffe per sicurezza
        sql = sql.replace("{{extra_conditions}}", extra or "")
        return sql

    @staticmethod
    def _fmt(d: Optional[date]) -> Optional[str]:
        return d.strftime("%Y-%m-%d") if d else None

    # =====================================================
    # META
    # =====================================================
    def list_departments(self) -> List[Dict[str, Any]]:
        sql = QuerySqlHRMYSQL.list_departments_sql()
        with self.db_manager as db:
            return db.execute_query(sql, query_type=QueryType.GET)

    def list_cert_types(self) -> List[Dict[str, Any]]:
        sql = QuerySqlHRMYSQL.list_cert_types_sql()
        with self.db_manager as db:
            return db.execute_query(sql, query_type=QueryType.GET)

    # =====================================================
    # ANAGRAFICA — LISTE
    # =====================================================
    def list_operators_light(self, active: Optional[int] = 1) -> List[Dict[str, Any]]:
        sql = QuerySqlHRMYSQL.list_operators_light_sql(active_filter=(active is not None))
        params: List[Any] = []
        if active is not None:
            params.append(int(active))
        with self.db_manager as db:
            return db.execute_query(sql, params, query_type=QueryType.GET)

    def list_operator_core(
        self,
        q: Optional[str] = None,
        department_id: Optional[int] = None,
        active: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        sql = QuerySqlHRMYSQL.list_operator_core_sql(filter_by_department=(department_id is not None))
        params: List[Any] = []
        conds: List[str] = []

        if q:
            like = f"%{q}%"
            conds.append("(o.first_name LIKE %s OR o.last_name LIKE %s OR o.fiscal_code LIKE %s)")
            params.extend([like, like, like])

        if active is not None:
            conds.append("o.active = %s")
            params.append(int(active))

        if department_id is not None:
            # la JOIN odf ... department_id = %s richiede questo parametro per primo
            params.insert(0, int(department_id))

        extra = (" AND " + " AND ".join(conds)) if conds else ""
        sql = self._inject_extra(sql, extra)

        with self.db_manager as db:
            return db.execute_query(sql, params, query_type=QueryType.GET)

    # =====================================================
    # ANAGRAFICA — DETTAGLIO + CREATE + UPDATE
    # =====================================================
    def get_operator(self, op_id: int) -> Optional[Dict[str, Any]]:
        sql = QuerySqlHRMYSQL.get_operator_sql()
        with self.db_manager as db:
            row = db.execute_query(sql, [int(op_id)], fetchall=False, query_type=QueryType.GET)
            return row if row else None

    def create_operator(
        self,
        *,
        first_name: str,
        last_name: str,
        fiscal_code: Optional[str],
        phone: Optional[str],
        email: Optional[str],
        address: Optional[str],
        birth_date: Optional[date],
        hire_date: Optional[date],
        contract_type: Optional[str],
        contract_expiry: Optional[date],
        level: Optional[str],
        ral: Optional[float],
        departments: Optional[str],
        active: Optional[int],
    ) -> int:
        """
        Crea anagrafica + (opzionale) associazioni reparti da stringa "REP1; REP2".
        Ritorna il nuovo id.
        """
        with self.db_manager as db:
            sql_ins = QuerySqlHRMYSQL.insert_operator_sql()
            params = [
                first_name,
                last_name,
                (fiscal_code or None),
                (phone or None),
                (email or None),
                (address or None),
                self._fmt(birth_date),
                self._fmt(hire_date),
                (contract_type or None),
                self._fmt(contract_expiry),
                (level or None),
                (None if ral is None else float(ral)),
                (None if active is None else int(active)),
            ]
            db.execute_query(sql_ins, params, query_type=QueryType.INSERT)
            row = db.execute_query(QuerySqlHRMYSQL.last_insert_id_sql(), fetchall=False, query_type=QueryType.GET)
            new_id = int(row["id"]) if row else 0

            # opzionale: reparti passati come stringa "REP1; REP2"
            if new_id and departments:
                names = [n.strip() for n in departments.split(";") if n.strip()]
                if names:
                    placeholders = ", ".join(["%s"] * len(names))
                    sql_dep = f"""
                        INSERT INTO operator_departments (operator_id, department_id)
                        SELECT %s, d.id FROM departments d WHERE d.name IN ({placeholders})
                    """
                    db.execute_query(sql_dep, [new_id, *names], query_type=QueryType.INSERT)

            return new_id

    def update_operator(
        self,
        *,
        id: int,
        first_name: str,
        last_name: str,
        fiscal_code: Optional[str],
        phone: Optional[str],
        birth_date: Optional[date],
        hire_date: Optional[date],
        contract_type: Optional[str],
        contract_expiry: Optional[date],
        level: Optional[str],
        ral: Optional[float],
        email: Optional[str],
        address: Optional[str],
        departments: Optional[str],
        active: Optional[int],
    ) -> None:
        with self.db_manager as db:
            # UPDATE operators (campi nuovi inclusi)
            sql_upd = QuerySqlHRMYSQL.update_operator_sql()
            params_upd = [
                first_name,
                last_name,
                (fiscal_code or None),
                (phone or None),
                self._fmt(birth_date),
                self._fmt(hire_date),
                (contract_type or None),
                self._fmt(contract_expiry),
                (level or None),
                (None if ral is None else float(ral)),
                (email or None),
                (address or None),
                (None if active is None else int(active)),
                int(id),
            ]
            db.execute_query(sql_upd, params_upd, query_type=QueryType.UPDATE)

            # riallineo reparti se stringa valorizzata
            if departments is not None:
                names = [n.strip() for n in departments.split(";") if n.strip()]
                db.execute_query(
                    "DELETE FROM operator_departments WHERE operator_id = %s",
                    [int(id)],
                    query_type=QueryType.DELETE,
                )
                if names:
                    placeholders = ", ".join(["%s"] * len(names))
                    sql_ins = f"""
                        INSERT INTO operator_departments (operator_id, department_id)
                        SELECT %s, d.id
                        FROM departments d
                        WHERE d.name IN ({placeholders})
                    """
                    db.execute_query(sql_ins, [int(id), *names], query_type=QueryType.INSERT)

    # =====================================================
    # CERTIFICAZIONI — LISTA STATO + UPSERT + DELETE
    # =====================================================
    def list_cert_status(
        self,
        department_id: Optional[int] = None,
        cert_type_id: Optional[int] = None,
        status_calc: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        sql = QuerySqlHRMYSQL.list_cert_status_sql(filter_by_department=(department_id is not None))
        params: List[Any] = []
        conds: List[str] = []

        if department_id is not None:
            params.append(int(department_id))  # per la JOIN

        if cert_type_id is not None:
            conds.append("t.id = %s")
            params.append(int(cert_type_id))

        if operator_id is not None:
            conds.append("o.id = %s")
            params.append(int(operator_id))

        extra = (" AND " + " AND ".join(conds)) if conds else ""
        sql = self._inject_extra(sql, extra)

        with self.db_manager as db:
            rows = db.execute_query(sql, params, query_type=QueryType.GET)

        if status_calc:
            rows = [r for r in rows if (r.get("status_calc") == status_calc)]
        return rows

    def upsert_certification(
        self,
        *,
        id: Optional[int],
        operator_id: int,
        cert_type_id: int,
        status: str,
        issue_date: Optional[date],
        expiry_date: Optional[date],
        notes: Optional[str],
    ) -> int:
        # ON DUPLICATE KEY su (operator_id, cert_type_id)
        sql = QuerySqlHRMYSQL.upsert_certification_sql()
        params = (
            operator_id,
            cert_type_id,
            status,
            self._fmt(issue_date),
            self._fmt(expiry_date),
            notes,
        )
        with self.db_manager as db:
            db.execute_query(sql, params, query_type=QueryType.INSERT)
            row = db.execute_query(QuerySqlHRMYSQL.last_insert_id_sql(), fetchall=False, query_type=QueryType.GET)
            return int(row["id"]) if row else 0

    def delete_certification(self, cert_id: int) -> None:
        sql = QuerySqlHRMYSQL.delete_certification_sql()
        with self.db_manager as db:
            db.execute_query(sql, [int(cert_id)], query_type=QueryType.DELETE)

    # =====================================================
    # KPI / UTILITY
    # =====================================================
    def count_active_operators(self, department_id: Optional[int] = None) -> int:
        sql = QuerySqlHRMYSQL.count_active_operators_sql(filter_by_department=(department_id is not None))
        params: List[Any] = []
        if department_id is not None:
            params.append(int(department_id))
        with self.db_manager as db:
            row = db.execute_query(sql, params, fetchall=False, query_type=QueryType.GET)
            return int(row["n"]) if row else 0
