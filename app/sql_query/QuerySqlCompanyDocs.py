class QuerySqlCompanyDocs:
    @staticmethod
    def table() -> str:
        return "company_documents"

    # LIST con filtri dinamici (q, year, frequency, category_code)
    @staticmethod
    def list_docs_sql(q=None, year=None, frequency=None, category_code=None):
        """
        Ritorna (sql, params).

        - q: filtro su title OPPURE label della categoria
        - year: filtro esatto sull'anno
        - frequency: 'annuale', 'semestrale', ecc.
        - category_code: codice categoria (FK su company_doc_categories.code)
        """
        conds = []
        params = []

        if q:
            like = f"%{q}%"
            # cerco sia nel titolo sia nell'etichetta categoria
            conds.append("(cd.title LIKE %s OR cat.label LIKE %s)")
            params.extend([like, like])

        if year is not None:
            conds.append("cd.year = %s")
            params.append(int(year))

        if frequency:
            conds.append("cd.frequency = %s")
            params.append(frequency)

        if category_code:
            conds.append("cd.category = %s")
            params.append(category_code)

        where = ("WHERE " + " AND ".join(conds)) if conds else ""

        sql = f"""
            SELECT
                cd.id,
                cd.title,
                cd.year,
                cd.category,
                cat.label AS category_label,
                cd.deadline_rule_id,
                cd.reference_date,
                cd.next_due_date,
                cd.frequency,
                cd.notes,
                cd.file_path,
                dr.document_name AS rule_name,
                dr.expiry_years AS rule_expiry_years,
                dr.trigger_event AS rule_trigger_event,
                cd.created_at,
                cd.updated_at
            FROM {QuerySqlCompanyDocs.table()} cd
            LEFT JOIN company_doc_categories cat
                   ON cat.code = cd.category
            LEFT JOIN company_document_deadline_rules dr
                   ON dr.id = cd.deadline_rule_id
            {where}
            ORDER BY
                cd.year DESC,
                cat.sort_order ASC,
                cd.title ASC
        """
        return sql, params

    # GET (con join per avere anche la label della categoria)
    @staticmethod
    def get_doc_sql() -> str:
        return f"""
            SELECT
                cd.id,
                cd.title,
                cd.year,
                cd.category,
                cat.label AS category_label,
                cd.deadline_rule_id,
                cd.reference_date,
                cd.next_due_date,
                cd.frequency,
                cd.notes,
                cd.file_path,
                dr.document_name AS rule_name,
                dr.expiry_years AS rule_expiry_years,
                dr.trigger_event AS rule_trigger_event,
                cd.created_at,
                cd.updated_at
            FROM {QuerySqlCompanyDocs.table()} cd
            LEFT JOIN company_doc_categories cat
                   ON cat.code = cd.category
            LEFT JOIN company_document_deadline_rules dr
                   ON dr.id = cd.deadline_rule_id
            WHERE cd.id = %s
            LIMIT 1
        """

    # INSERT
    @staticmethod
    def insert_doc_sql() -> str:
        return f"""
            INSERT INTO {QuerySqlCompanyDocs.table()}
                (title, year, category, deadline_rule_id, reference_date, next_due_date, frequency, notes, file_path, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """

    # UPDATE senza cambiare file_path
    @staticmethod
    def update_doc_without_file_sql() -> str:
        return f"""
            UPDATE {QuerySqlCompanyDocs.table()}
            SET title           = %s,
                year            = %s,
                category        = %s,
                deadline_rule_id= %s,
                reference_date  = %s,
                next_due_date   = %s,
                frequency       = %s,
                notes           = %s,
                updated_at      = NOW()
            WHERE id = %s
        """

    # UPDATE con file_path
    @staticmethod
    def update_doc_with_file_sql() -> str:
        return f"""
            UPDATE {QuerySqlCompanyDocs.table()}
            SET title           = %s,
                year            = %s,
                category        = %s,
                deadline_rule_id= %s,
                reference_date  = %s,
                next_due_date   = %s,
                frequency       = %s,
                notes           = %s,
                file_path       = %s,
                updated_at      = NOW()
            WHERE id = %s
        """

    @staticmethod
    def delete_doc_sql() -> str:
        return f"DELETE FROM {QuerySqlCompanyDocs.table()} WHERE id = %s"

    @staticmethod
    def last_insert_id_sql() -> str:
        return "SELECT LAST_INSERT_ID() AS id"
