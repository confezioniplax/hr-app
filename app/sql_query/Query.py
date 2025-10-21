class QuerySqlMYSQL:

    # ---------- MACHINES ----------
    @staticmethod
    def get_all_machines_sql(active_only: bool = True) -> str:
        where = "WHERE active=1" if active_only else ""
        return f"""
            SELECT id, code, name, machine_type_id, department_id, active
            FROM machines
            {where}
            ORDER BY id
        """

    @staticmethod
    def get_machine_by_id_sql() -> str:
        return """
            SELECT id, code, name, machine_type_id, department_id, active
            FROM machines
            WHERE id = %s
        """

    # ---------- OPERATORS ----------
    @staticmethod
    def list_operators_sql(active_only: bool = True, filter_by_department: bool = False) -> str:
        """
        Se filter_by_department=True usa la JOIN con operator_departments e un placeholder %s per department_id.
        """
        if filter_by_department:
            where_active = "o.active=1" if active_only else "1=1"
            return f"""
                SELECT DISTINCT
                    o.id,
                    o.first_name,
                    o.last_name,
                    o.badge_code,
                    o.email,
                    o.role,
                    o.active
                FROM operators o
                JOIN operator_departments od ON od.operator_id = o.id
                WHERE {where_active} AND od.department_id = %s
                ORDER BY o.last_name, o.first_name
            """
        else:
            where = "WHERE active=1" if active_only else ""
            return f"""
                SELECT
                    id,
                    first_name,
                    last_name,
                    badge_code,
                    email,
                    role,
                    active
                FROM operators
                {where}
                ORDER BY last_name, first_name
            """

    @staticmethod
    def get_operator_sql() -> str:
        return """
            SELECT 
                id, first_name, last_name, badge_code, email, role, active
            FROM operators
            WHERE id=%s
        """


    # ---------- CLIENTS ----------
    @staticmethod
    def get_client_by_name_sql() -> str:
        return "SELECT id, name FROM clients WHERE name=%s"

    @staticmethod
    def insert_client_sql() -> str:
        return "INSERT INTO clients (name) VALUES (%s)"

    # ---------- ARTICLES ----------
    @staticmethod
    def get_article_by_code_client_sql() -> str:
        # se code è NULL, matcha per client_id con code IS NULL
        return """
            SELECT id, code, description, client_id
            FROM articles
            WHERE
              ((code=%s AND %s IS NOT NULL) OR (code IS NULL AND %s IS NULL))
              AND (client_id=%s OR (%s IS NULL AND client_id IS NULL))
            LIMIT 1
        """

    @staticmethod
    def insert_article_sql() -> str:
        return "INSERT INTO articles (code, description, client_id) VALUES (%s,%s,%s)"

    # ---------- LOTS ----------
    @staticmethod
    def get_lot_by_code_sql() -> str:
        return "SELECT id, lot_code, client_id, article_id FROM lots WHERE lot_code=%s"

    @staticmethod
    def insert_lot_sql() -> str:
        return "INSERT INTO lots (lot_code, client_id, article_id) VALUES (%s,%s,%s)"

    # ---------- JOBS ----------
    @staticmethod
    def insert_job_sql() -> str:
        return """
            INSERT INTO jobs
              (job_date, machine_id, process_type, lot_id, start_time, end_time,
               meters_produced, scrap_meters, scrap_kg, setup_meters, notes, shift_label)
            VALUES
              (%(job_date)s, %(machine_id)s, %(process_type)s, %(lot_id)s, %(start_time)s, %(end_time)s,
               %(meters_produced)s, %(scrap_meters)s, %(scrap_kg)s, %(setup_meters)s, %(notes)s, %(shift_label)s)
        """

    @staticmethod
    def get_job_sql() -> str:
        return """
            SELECT j.*, m.code AS machine_code, m.name AS machine_name
            FROM jobs j
            JOIN machines m ON m.id = j.machine_id
            WHERE j.id = %s
        """

    @staticmethod
    def list_jobs_by_day_machine_sql() -> str:
        return """
            SELECT j.*, m.code AS machine_code, m.name AS machine_name
            FROM jobs j
            JOIN machines m ON m.id = j.machine_id
            WHERE j.job_date = %s AND j.machine_id = %s
            ORDER BY j.start_time
        """

    # ---------- JOB OPERATORS ----------
    @staticmethod
    def attach_operator_sql() -> str:
        return "INSERT IGNORE INTO job_operators (job_id, operator_id, role) VALUES (%s,%s,%s)"

    @staticmethod
    def list_job_operators_sql() -> str:
        return """
            SELECT jo.operator_id, o.first_name, o.last_name, jo.role
            FROM job_operators jo
            JOIN operators o ON o.id = jo.operator_id
            WHERE jo.job_id = %s
            ORDER BY o.last_name, o.first_name
        """

    # ---------- QUALITY CHECKS ----------
    @staticmethod
    def add_quality_check_sql() -> str:
        return """
            INSERT INTO job_quality_checks (job_id, check_type_id, result, value_text)
            VALUES (
              %s,
              (SELECT id FROM quality_check_types WHERE code=%s),
              %s, %s
            )
            ON DUPLICATE KEY UPDATE result=VALUES(result), value_text=VALUES(value_text)
        """

    @staticmethod
    def list_quality_checks_sql() -> str:
        return """
            SELECT qct.code, qct.description, jqc.result, jqc.value_text
            FROM job_quality_checks jqc
            JOIN quality_check_types qct ON qct.id = jqc.check_type_id
            WHERE jqc.job_id = %s
            ORDER BY qct.code
        """

    # ---------- MATERIALS ----------
    @staticmethod
    def add_material_sql() -> str:
        return """
            INSERT INTO job_materials
              (job_id, material_type, material_name, lot_number, quantity, unit, setpoint_value)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """

    @staticmethod
    def list_materials_sql() -> str:
        return """
            SELECT material_type, material_name, lot_number, quantity, unit, setpoint_value
            FROM job_materials
            WHERE job_id = %s
        """

    # ---------- CONSUMABLES ----------
    @staticmethod
    def add_consumable_sql() -> str:
        return """
            INSERT INTO job_consumables (job_id, consumable_type, quantity, unit, notes)
            VALUES (%s,%s,%s,%s,%s)
        """

    @staticmethod
    def list_consumables_sql() -> str:
        return """
            SELECT consumable_type, quantity, unit, notes
            FROM job_consumables
            WHERE job_id = %s
        """

    # ---------- EVENTS ----------
    @staticmethod
    def add_job_event_sql() -> str:
        return """
            INSERT INTO job_events (job_id, event_type, reason, minutes, quantity_m, quantity_kg)
            VALUES (%s,%s,%s,%s,%s,%s)
        """

    @staticmethod
    def list_job_events_sql() -> str:
        return """
            SELECT event_type, reason, minutes, quantity_m, quantity_kg
            FROM job_events
            WHERE job_id = %s
            ORDER BY id
        """

    # ---------- PROPERTIES ----------
    @staticmethod
    def set_job_property_sql() -> str:
        return """
            INSERT INTO job_properties (job_id, prop_key, prop_value)
            VALUES (%s,%s,%s)
        """

    @staticmethod
    def list_job_properties_sql() -> str:
        return "SELECT prop_key, prop_value FROM job_properties WHERE job_id = %s"

    # ---------- UTILS ----------
    @staticmethod
    def last_insert_id_sql() -> str:
        return "SELECT LAST_INSERT_ID() AS id"
