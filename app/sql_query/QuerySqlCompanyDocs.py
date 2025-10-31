class QuerySqlCompanyDocs:
    @staticmethod
    def table() -> str:
        return "company_documents"

    # LIST con filtri dinamici
    @staticmethod
    def list_docs_sql(q=None, year=None, frequency=None):
        conds = []
        params = []
        if q:
            conds.append("(title LIKE %s OR category LIKE %s)")
            like = f"%{q}%"
            params.extend([like, like])
        if year is not None:
            conds.append("year = %s")
            params.append(int(year))
        if frequency:
            conds.append("frequency = %s")
            params.append(frequency)

        where = ("WHERE " + " AND ".join(conds)) if conds else ""
        sql = f"""
            SELECT id, title, year, category, frequency, notes, file_path, created_at, updated_at
            FROM {QuerySqlCompanyDocs.table()}
            {where}
            ORDER BY year DESC, title ASC
        """
        return sql, params

    # GET
    @staticmethod
    def get_doc_sql() -> str:
        return f"""
            SELECT id, title, year, category, frequency, notes, file_path, created_at, updated_at
            FROM {QuerySqlCompanyDocs.table()}
            WHERE id = %s
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
            SET title = %s,
                year = %s,
                category = %s,
                frequency = %s,
                notes = %s,
                updated_at = NOW()
            WHERE id = %s
        """

    # UPDATE con file_path
    @staticmethod
    def update_doc_with_file_sql() -> str:
        return f"""
            UPDATE {QuerySqlCompanyDocs.table()}
            SET title = %s,
                year = %s,
                category = %s,
                frequency = %s,
                notes = %s,
                file_path = %s,
                updated_at = NOW()
            WHERE id = %s
        """

    @staticmethod
    def delete_doc_sql() -> str:
        return f"DELETE FROM {QuerySqlCompanyDocs.table()} WHERE id = %s"

    @staticmethod
    def last_insert_id_sql() -> str:
        return "SELECT LAST_INSERT_ID() AS id"
