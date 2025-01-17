CREATE TABLE IF NOT EXISTS users (
    id serial PRIMARY KEY NOT NULL,
    user_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    mob_number TEXT NOT NULL,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    height INTEGER NOT NULL,
    weight INTEGER NOT NULL,
    timezone TEXT NOT NULL,
    water_reminders BOOL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS user_actions (
    id serial PRIMARY KEY NOT NULL,
    user_id BIGINT NOT NULL,
    username TEXT NOT NULL,
    action_type TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS user_drinked_water (
    user_id INTEGER NOT NULL,
    day DATE NOT NULL,
    PRIMARY KEY(user_id, day),
    water INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_survey (
    user_id BIGINT NOT NULL, 
    survey_date DATE NOT NULL,
    physical_activity INTEGER,
    stress INTEGER,
    mood INTEGER,
    sleep_quality INTEGER
);
