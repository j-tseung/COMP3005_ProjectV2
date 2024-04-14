-- CREATE SCHEMA public;
-- DROP SCHEMA public CASCADE;

-- Admin Password
CREATE TABLE admin (
    password VARCHAR(255) PRIMARY KEY
);

-- Member Accounts
CREATE TABLE member_accounts (
    email VARCHAR(255) UNIQUE PRIMARY KEY,
    name VARCHAR(255),
    password TEXT,
    gender TEXT,
    age INT
);

-- Exercise Routines
CREATE TABLE exercise_routines (
    email VARCHAR(255) PRIMARY KEY REFERENCES member_accounts(email),
    routine1 TEXT,
    routine2 TEXT,
    routine3 TEXT
);

-- Fitness Achievements
CREATE TABLE fitness_achievements (
    email VARCHAR(255) PRIMARY KEY REFERENCES member_accounts(email),
    first_fitness_goal_achieved BOOLEAN,
    never_skipped_leg_day BOOLEAN,
    can_do_pushup BOOLEAN,
    can_do_pullup BOOLEAN,
    can_touch_toes BOOLEAN,
    achieved_weight_loss_goal BOOLEAN,
    achieved_muscle_gain_goal BOOLEAN
);

-- Health Statistics
CREATE TABLE health_statistics (
    email VARCHAR(255) PRIMARY KEY REFERENCES member_accounts(email),
    fitness_level INT CHECK (fitness_level BETWEEN 1 AND 10),
    strength INT CHECK (strength BETWEEN 1 AND 10),
    flexibility INT CHECK (flexibility BETWEEN 1 AND 10),
    endurance INT CHECK (endurance BETWEEN 1 AND 10),
    stamina INT CHECK (stamina BETWEEN 0 AND 10),
    has_water BOOLEAN,
    has_protein BOOLEAN,
    is_injured BOOLEAN
);

-- Fitness Goals
CREATE TABLE fitness_goals (
    email VARCHAR(255) PRIMARY KEY REFERENCES member_accounts(email),
    goal1 TEXT,
    goal2 TEXT,
    goal3 TEXT
);

-- Member Health Metrics
CREATE TABLE member_health_metrics (
    email VARCHAR(255) PRIMARY KEY REFERENCES member_accounts(email),
    height DECIMAL,
    weight DECIMAL,
    body_fat_percentage DECIMAL,
    resting_heart_rate INT
);

-- Trainer Accounts
CREATE TABLE trainer_accounts (
    trainer_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    password TEXT,
    monday_available BOOLEAN,
    tuesday_available BOOLEAN,
    wednesday_available BOOLEAN,
    thursday_available BOOLEAN,
    friday_available BOOLEAN,
    saturday_available BOOLEAN,
    sunday_available BOOLEAN
);

-- Rooms
CREATE TABLE rooms (
    room_id SERIAL PRIMARY KEY,
    room_name VARCHAR(255) NOT NULL,
    room_availability BOOLEAN
);

-- Bookings
CREATE TABLE bookings (
    booking_id SERIAL PRIMARY KEY,
    trainer_id INT NOT NULL REFERENCES trainer_accounts(trainer_id),
    room_id INT NOT NULL REFERENCES rooms(room_id),
    duration INT,
    day_of_week VARCHAR(3) CHECK (day_of_week IN ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')),
    start_time TIME
);

-- Equipment
CREATE TABLE equipment (
    equipment_id SERIAL PRIMARY KEY,
    equipment_name VARCHAR(255) NOT NULL,
    room_id INT NOT NULL REFERENCES rooms(room_id),
    quality INT CHECK (quality BETWEEN 1 AND 10)
);


-- Class Schedule
CREATE TABLE class_schedule (
    class_id SERIAL PRIMARY KEY,
    class_name VARCHAR(255) NOT NULL,
    trainer_id INT NOT NULL REFERENCES trainer_accounts(trainer_id),
    room_id INT NOT NULL REFERENCES rooms(room_id),
    day_of_week VARCHAR(3) CHECK (day_of_week IN ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')),
    start_time TIME,
    duration INT
);

-- Create Payment Table
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    email VARCHAR(255) REFERENCES member_accounts(email),
    amount DECIMAL(10, 2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_type VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL
);