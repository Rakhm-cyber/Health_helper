import asyncpg
import config

class Database:
    def __init__(self, cfg):
        self.user = cfg.postgres_user
        self.password = cfg.postgres_password
        self.database = cfg.postgres_db
        self.host = cfg.postgres_host
        self.port = cfg.postgres_port
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            user=self.user,
            password=self.password,
            database=self.database,
            host=self.host,
            port=self.port
        )

    async def close(self):
        await self.pool.close()

    async def execute(self, query, *args):
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def fetch(self, query, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

cfg = config.load()

db = Database(cfg)

async def save_user_data(db, user_id, name, mob_number, age, gender, height, weight):
    query = """
    INSERT INTO users (user_id, name, mob_number, age, gender, height, weight)
    VALUES ($1, $2, $3, $4, $5, $6, $7)
    """
    await db.execute(query, user_id, name, mob_number, age, gender, height, weight)

async def if_exists(db, user_id):
    query = """
    SELECT EXISTS (
        SELECT 1 
        FROM users
        WHERE user_id = $1
    )
    """
    result = await db.fetch(query, user_id)
    return result[0]['exists']

async def get_weight(db, user_id):
    query = """
    SELECT weight
    FROM users
    WHERE user_id = $1
    """
    result = await db.fetch(query, user_id)
    return result[0]['weight']
