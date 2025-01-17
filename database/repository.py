from database.postgres import Database
from utils import config
from datetime import datetime

cfg = config.load()

db = Database(cfg)

async def read_parameter(user_id, field):
    res = await db.fetch(f'SELECT {field} FROM users WHERE user_id = $1', user_id)
    if res:
        return res[0][field]
    return None

async def update_parameter(user_id, field, value):
    query = f"UPDATE users SET {field} = $1 WHERE user_id = $2"
    await db.execute(query, value, user_id)

async def add_user(user_id, name, mob_number, age, gender, height, weight, timezone):
    query = """
    INSERT INTO users (user_id, name, mob_number, age, gender, height, weight, timezone)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    """
    await db.execute(query, user_id, name, mob_number, age, gender, height, weight, timezone)

async def get_user(user_id):
    query = """
    SELECT * FROM users WHERE user_id = $1
    """
    result = await db.fetch(query, user_id)
    return result

## убрать и воспользоваться гет юзер
async def if_exists(user_id):
    query = """
    SELECT EXISTS (
        SELECT 1 
        FROM users
        WHERE user_id = $1
    )
    """
    result = await db.fetch(query, user_id)
    return result[0]['exists']

async def get_weight(user_id):
    query = """
    SELECT weight
    FROM users
    WHERE user_id = $1
    """
    result = await db.fetch(query, user_id)
    return result[0]['weight']

async def add_water(user_id):
    current_day = datetime.now().date()
    res = await get_water(db, user_id, current_day)
    if res:
        new_water_amount = res + 250
        await db.execute(
            'UPDATE user_drinked_water SET water = $1 WHERE user_id = $2 AND day = $3',
            new_water_amount, user_id, current_day
        )
    else:
        await db.execute(
            'INSERT INTO user_drinked_water (user_id, day, water) VALUES ($1, $2, $3)',
            user_id, current_day, 250
        )

async def get_water(user_id, day):
    res = await db.fetch('SELECT water FROM user_drinked_water WHERE user_id = $1 AND day = $2', user_id, day)
    if res:
        return res[0]['water']
    return None

async def save_survey_data(user_id, data):
    query = """
    INSERT INTO daily_survey (user_id, survey_date, physical_activity, stress, mood, sleep_quality)
    VALUES ($1, $2, $3, $4, $5, $6)
    """
    await db.execute(query, user_id, data['survey_date'], data['physical_activity'], data['stress'], data['mood'], data['sleep_quality'])