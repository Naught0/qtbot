import asyncpg


class PGDB:
    def __init__(self, pg_con):
        self.pg_con = pg_con

    async def fetch_user_info(self, member_id: int, column: str):
        query = f"""SELECT {column} FROM user_info WHERE member_id = {member_id};"""
        return await self.pg_con.fetchval(query)

    async def insert_user_info(self, member_id: int, column: str, col_value):
        execute = f"""INSERT INTO user_info (member_id, {column}) VALUES ($1, $2)
                      ON CONFLICT (member_id) DO UPDATE SET {column} = $2;"""
        await self.pg_con.execute(execute, member_id, col_value)

    async def remove_user_info(self, member_id: int, column: str):
        execute = f"""UPDATE user_info SET {column} = null WHERE member_id = {member_id};"""
        await self.pg_con.execute(execute)
