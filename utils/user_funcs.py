#!bin/env python

import asyncpg

class PGDB:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    async def fetch_user_info(self, member_id: int, column: str):
        query = f'''SELECT {column} FROM user_info WHERE member_id = {member_id};'''
        return await self.db_conn.fetchval(query)

    async def insert_user_info(self, member_id: int, column: str, col_value):
        execute = (
            f"""INSERT INTO user_info (member_id, {column}) 
                    VALUES ({member_id}, {col_value})
                    ON CONFLICT (member_id)
                        DO UPDATE SET {column} = {col_value};""")
        await self.db_conn.execute(execute)
