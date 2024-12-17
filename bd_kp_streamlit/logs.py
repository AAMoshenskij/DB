import asyncpg
import asyncio

async def get_registration_logs(connection_pool):
    async with connection_pool.acquire() as conn:
        logs = await conn.fetch("SELECT * FROM RegistrationLogs ORDER BY changed_at DESC;")
        for log in logs:
            print(log)