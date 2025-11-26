"""
 MIT License
 (c) 2025 Riccardo Leonelli
"""

class QuerySqlHRMYSQL:
    # ---------- META ----------
    @staticmethod
    def list_departments_sql() -> str:
        return """
            SELECT id, name, module_code, active
            FROM departments
            WHERE active = 1
            ORDER BY name
        """

    @staticmethod
    def list_cert_types_sql() -> str:
        return """
            SELECT id, code, description, requires_expiry
            FROM operator_cert_types
            ORDER BY code
        """

    @staticmethod
    def list_operators_light_sql(active_filter: bool = True) -> str:
        where = "WHERE o.active = %s" if active_filter else ""
        return f"""
            SELECT o.id, o.first_name, o.last_name
            FROM operators o
            {where}
            ORDER BY o.last_name, o.first_name
        """

    # ---------- ANAGRAFICA ----------
    @staticmethod
    def list_operator_core_sql(filter_by_department: bool = False) -> str:
        """
        Restituisce i campi principali dell’anagrafica operatori.
        Ora include anche o.job_title.
        """
        join_dep_filter = (
            "INNER JOIN operator_departments odf ON odf.operator_id = o.id AND odf.department_id = %s"
            if filter_by_department else ""
        )
        return f"""
            SELECT
                o.id,
                CONCAT(o.last_name, ' ', o.first_name) AS operator_name,
                o.email,
                o.phone,
                o.fiscal_code,
                o.birth_date,
                o.citizenship,
                o.education_level,
                o.hire_date,
                o.contract_type,
                o.contract_expiry,
                o.`level`,
                o.ral,
                o.address,
                o.job_title,     -- 👈 nuovo campo
                o.active,
                dep.departments
            FROM operators o
            {join_dep_filter}
            LEFT JOIN (
                SELECT od.operator_id,
                    GROUP_CONCAT(DISTINCT d.name ORDER BY d.name SEPARATOR ', ') AS departments
                FROM operator_departments od
                JOIN departments d ON d.id = od.department_id
                GROUP BY od.operator_id
            ) dep ON dep.operator_id = o.id
            WHERE 1=1
            {{extra_conditions}}
            ORDER BY operator_name
        """

    @staticmethod
    def get_operator_sql() -> str:
        """Dettaglio operatore, aggiornato con job_title."""
        return """
            SELECT 
                o.id,
                o.first_name,
                o.last_name,
                o.fiscal_code,
                o.phone,
                o.birth_date,
                o.citizenship,
                o.education_level,
                o.hire_date,
                o.contract_type,
                o.contract_expiry,
                o.`level`,
                o.ral,
                o.email,
                o.birth_place,
                o.address,
                o.job_title,     -- 👈 nuovo campo
                o.active,
                (
                    SELECT GROUP_CONCAT(DISTINCT d.name ORDER BY d.name SEPARATOR '; ')
                    FROM operator_departments od
                    JOIN departments d ON d.id = od.department_id
                    WHERE od.operator_id = o.id
                ) AS departments
            FROM operators o
            WHERE o.id = %s
            LIMIT 1
        """

    @staticmethod
    def insert_operator_sql() -> str:
        """Creazione nuova anagrafica, ora include job_title."""
        return """
            INSERT INTO operators
                (first_name, last_name, fiscal_code, phone, email, address,
                 birth_date, citizenship, education_level,
                 hire_date, contract_type, contract_expiry, `level`, ral,
                 job_title,     -- 👈 aggiunto qui
                 active)
            VALUES (%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,
                    %s,%s,%s,%s,%s,
                    %s,           -- job_title
                    %s)
        """

    @staticmethod
    def update_operator_sql() -> str:
        """Update anagrafica, ora include job_title."""
        return """
            UPDATE operators
            SET first_name      = %s,
                last_name       = %s,
                fiscal_code     = %s,
                phone           = %s,
                birth_date      = %s,
                citizenship     = %s,
                education_level = %s,
                hire_date       = %s,
                contract_type   = %s,
                contract_expiry = %s,
                `level`         = %s,
                ral             = %s,
                email           = %s,
                address         = %s,
                job_title       = %s,   -- 👈 aggiunto
                active          = %s
            WHERE id = %s
        """

    # ---------- CERTIFICAZIONI ----------
    @staticmethod
    def list_cert_status_sql(filter_by_department: bool = False) -> str:
        join_dep_filter = (
            "INNER JOIN operator_departments odf ON odf.operator_id = o.id AND odf.department_id = %s"
            if filter_by_department else ""
        )
        return f"""
 SELECT
    o.id AS operator_id,
    CONCAT(o.last_name, ' ', o.first_name) AS operator_name,
    dep.departments,
    t.id   AS cert_type_id,
    t.code AS cert_code,
    COALESCE(oc.status, 'MANCA') AS raw_status,
    oc.issue_date,
    oc.expiry_date,
    oc.notes,
    oc.file_path,
    oc.id,
    CASE
        WHEN oc.id IS NULL THEN 'MANCA'
        WHEN oc.status = 'ND' THEN 'ND'
        WHEN (COALESCE(t.requires_expiry,0) = 1 OR oc.expiry_date IS NOT NULL)
             AND oc.expiry_date IS NULL THEN 'ND'
        WHEN oc.expiry_date IS NOT NULL AND DATE(oc.expiry_date) <  CURRENT_DATE() THEN 'SCADUTA'
        WHEN oc.expiry_date IS NOT NULL AND DATE(oc.expiry_date) <= CURRENT_DATE() + INTERVAL 30 DAY THEN 'IN_SCADENZA_30'
        WHEN oc.expiry_date IS NOT NULL AND DATE(oc.expiry_date) <= CURRENT_DATE() + INTERVAL 60 DAY THEN 'IN_SCADENZA_60'
        WHEN oc.expiry_date IS NOT NULL AND DATE(oc.expiry_date) <= CURRENT_DATE() + INTERVAL 90 DAY THEN 'IN_SCADENZA_90'
        ELSE 'OK'
    END AS status_calc
FROM operators o
{join_dep_filter}
CROSS JOIN operator_cert_types t
LEFT JOIN operator_certifications oc
       ON oc.operator_id = o.id
      AND oc.cert_type_id = t.id
LEFT JOIN (
    SELECT od.operator_id,
           GROUP_CONCAT(DISTINCT d.name ORDER BY d.name SEPARATOR ', ') AS departments
    FROM operator_departments od
    JOIN departments d ON d.id = od.department_id
    GROUP BY od.operator_id
) dep ON dep.operator_id = o.id
WHERE o.active = 1
  {{extra_conditions}}
ORDER BY
    FIELD(status_calc,
          'SCADUTA','IN_SCADENZA_30','IN_SCADENZA_60','IN_SCADENZA_90','MANCA','ND','OK'),
    oc.expiry_date IS NULL,
    oc.expiry_date ASC,
    operator_name ASC,
    cert_code ASC
        """

    @staticmethod
    def upsert_certification_sql() -> str:
        return """
INSERT INTO operator_certifications
  (operator_id, cert_type_id, status, issue_date, expiry_date, notes, file_path)
VALUES (%s,%s,%s,%s,%s,%s,%s)
ON DUPLICATE KEY UPDATE
  status = VALUES(status),
  issue_date = VALUES(issue_date),
  expiry_date = VALUES(expiry_date),
  notes = VALUES(notes),
  file_path = COALESCE(VALUES(file_path), file_path),
  id = LAST_INSERT_ID(id)
        """

    @staticmethod
    def get_certification_sql() -> str:
        return """
            SELECT id, operator_id, cert_type_id, file_path
            FROM operator_certifications
            WHERE id = %s
            LIMIT 1
        """

    @staticmethod
    def delete_certification_sql() -> str:
        return "DELETE FROM operator_certifications WHERE id = %s"

    @staticmethod
    def last_insert_id_sql() -> str:
        return "SELECT LAST_INSERT_ID() AS id"

    # ---------- KPI ----------
    @staticmethod
    def count_active_operators_sql(filter_by_department: bool = False) -> str:
        if filter_by_department:
            return """
                SELECT COUNT(DISTINCT o.id) AS n
                FROM operators o
                INNER JOIN operator_departments od ON od.operator_id = o.id
                WHERE o.active = 1 AND od.department_id = %s
            """
        else:
            return "SELECT COUNT(*) AS n FROM operators WHERE active = 1"

    @staticmethod
    def list_expiring_certs_sql(filter_by_department: bool = False) -> str:
        join_dep_filter = (
            "INNER JOIN operator_departments odf ON odf.operator_id = o.id AND odf.department_id = %s"
            if filter_by_department else ""
        )
        return f"""
            SELECT
                o.id AS operator_id,
                CONCAT(o.last_name, ' ', o.first_name) AS operator_name,
                dep.departments,
                t.id AS cert_type_id,
                t.code AS cert_code,
                oc.expiry_date,
                DATEDIFF(oc.expiry_date, CURRENT_DATE()) AS days_left
            FROM operators o
            {join_dep_filter}
            INNER JOIN operator_certifications oc ON oc.operator_id = o.id
            INNER JOIN operator_cert_types t ON t.id = oc.cert_type_id
            LEFT JOIN (
                SELECT od.operator_id,
                       GROUP_CONCAT(DISTINCT d.name ORDER BY d.name SEPARATOR ', ') AS departments
                FROM operator_departments od
                JOIN departments d ON d.id = od.department_id
                GROUP BY od.operator_id
            ) dep ON dep.operator_id = o.id
            WHERE o.active = 1
              AND oc.expiry_date IS NOT NULL
              AND DATE(oc.expiry_date) <= CURRENT_DATE() + INTERVAL %s DAY
            ORDER BY
              (CASE WHEN DATEDIFF(oc.expiry_date, CURRENT_DATE()) < 0 THEN 0 ELSE 1 END) ASC,
              DATEDIFF(oc.expiry_date, CURRENT_DATE()) ASC,
              operator_name ASC,
              cert_code ASC
        """

    @staticmethod
    def export_operator_certs_sql() -> str:
        """
        Export per Excel:
        - solo operatori attivi
        - solo certificazioni effettivamente caricate
        - non include MANCA
        - include job_title
        - elimina hire_date, contract_type, contract_expiry, level, ral
        """
        return """
            SELECT
                o.id AS operator_id,
                o.last_name,
                o.first_name,
                o.fiscal_code,
                o.job_title,
                dep.departments,
                t.code AS cert_code,
                t.description AS cert_description,
                oc.issue_date,
                oc.expiry_date,
                oc.notes
            FROM operators o
            LEFT JOIN (
                SELECT od.operator_id,
                    GROUP_CONCAT(DISTINCT d.name ORDER BY d.name SEPARATOR ', ') AS departments
                FROM operator_departments od
                JOIN departments d ON d.id = od.department_id
                GROUP BY od.operator_id
            ) dep ON dep.operator_id = o.id
            INNER JOIN operator_certifications oc
                ON oc.operator_id = o.id
            INNER JOIN operator_cert_types t
                ON t.id = oc.cert_type_id
            WHERE o.active = 1
            AND oc.status <> 'MANCA'
            ORDER BY
                o.last_name, o.first_name,
                t.code,
                oc.expiry_date IS NULL,
                oc.expiry_date ASC
        """
