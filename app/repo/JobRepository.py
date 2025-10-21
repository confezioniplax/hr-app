from app.db.db import DbManager, MySQLDb, QueryType
from app.sql_query.Query import QuerySqlMYSQL

class JobRepository:
    def __init__(self):
        self.db = DbManager(MySQLDb())

    # --- Jobs ---
    def create_job(self, payload: dict) -> int:
        sql = QuerySqlMYSQL.insert_job_sql()
        with self.db as db:
            db.execute_query(sql, payload, query_type=QueryType.INSERT)
            rid = db.execute_query(QuerySqlMYSQL.last_insert_id_sql(), fetchall=False, query_type=QueryType.GET)
            db.commit()
            return int(rid["id"])

    def get_job(self, job_id: int):
        sql = QuerySqlMYSQL.get_job_sql()
        with self.db as db:
            return db.execute_query(sql, (job_id,), fetchall=False, query_type=QueryType.GET)

    def list_jobs_by_day_machine(self, job_date: str, machine_id: int):
        sql = QuerySqlMYSQL.list_jobs_by_day_machine_sql()
        with self.db as db:
            return db.execute_query(sql, (job_date, machine_id), query_type=QueryType.GET)

    # --- Operators on job ---
    def attach_operator(self, job_id: int, operator_id: int, role: str | None = None):
        sql = QuerySqlMYSQL.attach_operator_sql()
        with self.db as db:
            db.execute_query(sql, (job_id, operator_id, role), query_type=QueryType.INSERT)
            db.commit()

    def list_job_operators(self, job_id: int):
        sql = QuerySqlMYSQL.list_job_operators_sql()
        with self.db as db:
            return db.execute_query(sql, (job_id,), query_type=QueryType.GET)

    # --- Quality checks ---
    def add_quality_check(self, job_id: int, check_type_code: str, result: str, value_text: str | None = None):
        sql = QuerySqlMYSQL.add_quality_check_sql()
        with self.db as db:
            db.execute_query(sql, (job_id, check_type_code, result, value_text), query_type=QueryType.INSERT)
            db.commit()

    def list_quality_checks(self, job_id: int):
        sql = QuerySqlMYSQL.list_quality_checks_sql()
        with self.db as db:
            return db.execute_query(sql, (job_id,), query_type=QueryType.GET)

    # --- Materials (es. adesivo per accoppiamento) ---
    def add_material(self, job_id: int, material_type: str, material_name: str | None,
                     lot_number: str | None, quantity: float | None, unit: str | None,
                     setpoint_value: float | None):
        sql = QuerySqlMYSQL.add_material_sql()
        with self.db as db:
            db.execute_query(sql, (job_id, material_type, material_name, lot_number, quantity, unit, setpoint_value), query_type=QueryType.INSERT)
            db.commit()

    def list_materials(self, job_id: int):
        sql = QuerySqlMYSQL.list_materials_sql()
        with self.db as db:
            return db.execute_query(sql, (job_id,), query_type=QueryType.GET)

    # --- Consumables (es. lame) ---
    def add_consumable(self, job_id: int, consumable_type: str, quantity: float, unit: str, notes: str | None = None):
        sql = QuerySqlMYSQL.add_consumable_sql()
        with self.db as db:
            db.execute_query(sql, (job_id, consumable_type, quantity, unit, notes), query_type=QueryType.INSERT)
            db.commit()

    def list_consumables(self, job_id: int):
        sql = QuerySqlMYSQL.list_consumables_sql()
        with self.db as db:
            return db.execute_query(sql, (job_id,), query_type=QueryType.GET)

    # --- Events (fermi/scarti) ---
    def add_event(self, job_id: int, event_type: str, reason: str | None, minutes: int | None,
                  quantity_m: int | None, quantity_kg: float | None):
        sql = QuerySqlMYSQL.add_job_event_sql()
        with self.db as db:
            db.execute_query(sql, (job_id, event_type, reason, minutes, quantity_m, quantity_kg), query_type=QueryType.INSERT)
            db.commit()

    def list_events(self, job_id: int):
        sql = QuerySqlMYSQL.list_job_events_sql()
        with self.db as db:
            return db.execute_query(sql, (job_id,), query_type=QueryType.GET)

    # --- Properties (EAV) ---
    def set_property(self, job_id: int, prop_key: str, prop_value: str | None):
        sql = QuerySqlMYSQL.set_job_property_sql()
        with self.db as db:
            db.execute_query(sql, (job_id, prop_key, prop_value), query_type=QueryType.INSERT)
            db.commit()

    def list_properties(self, job_id: int):
        sql = QuerySqlMYSQL.list_job_properties_sql()
        with self.db as db:
            return db.execute_query(sql, (job_id,), query_type=QueryType.GET)
