import asyncpg

class Database:
    def __init__(self, user, password, database, host, port=5432):
        self.user = user
        self.password = password
        self.database = database
        self.host = host
        self.port = port
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


db = Database(
    user="postgres",
    password="1",
    database="1",
    host="localhost"
)

async def save_user_data(db, user_id, name, mob_number, age, gender, height, weight):
    query = """
    INSERT INTO users (user_id, name, mob_number, age, gender, height, weight)
    VALUES ($1, $2, $3, $4, $5, $6, $7)
    ON CONFLICT (user_id) DO UPDATE
    SET name = EXCLUDED.name,
        mob_number = EXCLUDED.mob_number,
        age = EXCLUDED.age,
        gender = EXCLUDED.gender,
        height = EXCLUDED.height,
        weight = EXCLUDED.weight;
    """
    await db.execute(query, user_id, name, mob_number, age, gender, height, weight)
