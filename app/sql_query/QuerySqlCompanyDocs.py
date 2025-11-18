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
                cd.frequency,
                cd.notes,
                cd.file_path,
                cd.created_at,
                cd.updated_at
            FROM {QuerySqlCompanyDocs.table()} cd
            LEFT JOIN company_doc_categories cat
                   ON cat.code = cd.category
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
                cd.frequency,
                cd.notes,
                cd.file_path,
                cd.created_at,
                cd.updated_at
            FROM {QuerySqlCompanyDocs.table()} cd
            LEFT JOIN company_doc_categories cat
                   ON cat.code = cd.category
            WHERE cd.id = %s
            LIMIT 1
        """

    # INSERT
    @staticmethod
    def insert_doc_sql() -> str:
        return f"""
            INSERT INTO {QuerySqlCompanyDocs.table()}
                (title, year, category, frequency, notes, file_path, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        """

    # UPDATE senza cambiare file_path
    @staticmethod
    def update_doc_without_file_sql() -> str:
        return f"""
            UPDATE {QuerySqlCompanyDocs.table()}
            SET title      = %s,
                year       = %s,
                category   = %s,
                frequency  = %s,
                notes      = %s,
                updated_at = NOW()
            WHERE id = %s
        """

    # UPDATE con file_path
    @staticmethod
    def update_doc_with_file_sql() -> str:
        return f"""
            UPDATE {QuerySqlCompanyDocs.table()}
            SET title      = %s,
                year       = %s,
                category   = %s,
                frequency  = %s,
                notes      = %s,
                file_path  = %s,
                updated_at = NOW()
            WHERE id = %s
        """

    @staticmethod
    def delete_doc_sql() -> str:
        return f"DELETE FROM {QuerySqlCompanyDocs.table()} WHERE id = %s"

    @staticmethod
    def last_insert_id_sql() -> str:
        return "SELECT LAST_INSERT_ID() AS id"
