import os
from dotenv import load_dotenv
import asyncpg

load_dotenv("env.env")

# Чтение и установка env
DB_CONFIG = {
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

# Pool settings
POOL_MIN_CONN = int(os.getenv("POOL_MIN_CONN", 1))
POOL_MAX_CONN = int(os.getenv("POOL_MAX_CONN", 10))

async def get_connection():
    """Устанавливает соединение с базой данных PostgreSQL и возвращает объект подключения."""
    conn = await asyncpg.connect(**DB_CONFIG)
    return conn

connection_pool = None



async def init_pool():
    connection_pool: asyncpg.Pool = await asyncpg.create_pool(
        **DB_CONFIG,
        min_size=1,
        max_size=10,
    )
    #print("Initializing connection pool...")
    return connection_pool


async def close_pool(connection_pool: asyncpg.Pool):
    await connection_pool.close()
    #print("Connection pool closed.")