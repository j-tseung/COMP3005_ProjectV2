
-- guest account
INSERT INTO member_accounts (email, name) VALUES ('guest', 'guest');

-- admin account
INSERT INTO member_accounts (email, password) VALUES ('admin', '$2b$12$kEILKLegjmsn.1MOnMlMk.JDLXTLOzlpoeRDmz2GmhNecmpW/Qnnm');
-- random accounts
INSERT INTO member_accounts (email, name, password, gender, age)
VALUES
    ('jane.doe@example.com', 'Jane Doe', 'password123', 'Female', 30),
    ('john.smith@example.com', 'John Smith', 'password456', 'Male', 35),
    ('alice.johnson@example.com', 'Alice Johnson', 'password789', 'Female', 28),
    ('dave.wilson@example.com', 'Dave Wilson', 'passwordABC', 'Male', 40),
    ('emily.white@example.com', 'Emily White', 'passwordDEF', 'Female', 32);



-- sample trainers_accounts (no password)
INSERT INTO trainer_accounts (trainer_id, name, password, monday_available, tuesday_available, wednesday_available, thursday_available, friday_available, saturday_available, sunday_available)
VALUES
    (1, 'John Doe', '', true, false, true, false, true, false, true),
    (2, 'Jane Smith', '', false, true, false, true, false, true, false),
    (3, 'Michael Johnson', '', true, false, true, false, true, false, true),
    (4, 'Emily Brown', '', false, true, false, true, false, true, false),
    (5, 'David Lee', '', true, true, true, true, true, true, true);


-- Sample Rooms
INSERT INTO rooms (room_id, room_name, room_availability) VALUES
(1, 'Yoga Room', true),
(2, 'Personal Training Room', true),
(3, 'Spin Room', true),
(4, 'Dance Room', true),
(5, 'Strength Training', true);

-- Sample Room Bookings
INSERT INTO bookings (booking_id, trainer_id, room_id, duration, day_of_week, start_time)
VALUES
(1, 1, 2, 60, 'Mon', '09:00:00'),
(2, 2, 4, 45, 'Tue', '14:30:00'),
(3, 3, 3, 120, 'Wed', '11:00:00'),
(4, 4, 1, 30, 'Thu', '16:00:00'),
(5, 5, 5, 90, 'Fri', '10:30:00');



-- sample equipment
INSERT INTO equipment (equipment_name, room_id, quality)
VALUES
('Treadmill', 1, 10),
('Yoga Mat', 1, 8),
('Yoga Blocks', 1, 3),
('Yoga Strap', 1, 7),
('Stepper Machine', 1, 8),

('Elliptical Trainer', 2, 1),
('Weight Bench', 2, 9),

('Spin Bike', 3, 8),
('Stationary Bike', 3, 7),
('Exercise Bike', 1, 7),

('Medicine Balls', 3, 7),
('Resistance Bands', 3, 8),

('Dance Pole', 4, 7),
('Dance Ribbons', 4, 1),
('Dance Barre', 4, 8),
('Jump Ropes', 4, 6),

('Barbell', 5, 9),
('Bench Press', 5, 8),
('Power Rack', 5, 10),
('Dumbbells', 5, 3);

INSERT INTO class_schedule (class_name, trainer_id, room_id, day_of_week, start_time, duration)
VALUES
    ('Yoga Class', 1, 1, 'Mon', '09:00:00', 60),
    ('Spin Class', 2, 3, 'Tue', '14:00:00', 45),
    ('Zumba Class', 3, 4, 'Wed', '18:30:00', 60),
    ('Pilates Class', 4, 1, 'Thu', '10:00:00', 60),
    ('HIIT Class', 5, 5, 'Fri', '16:00:00', 45);


-- Insert Sample Data into Payment Table
INSERT INTO payments (email, amount, payment_date, payment_type, status)
VALUES
    ('jane.doe@example.com', 50.00, '2024-04-01', 'Annual Membership', 'Refunded'),
    ('john.smith@example.com', 75.00, '2024-04-02', 'Personal Training', 'Pending'),
    ('alice.johnson@example.com', 20.00, '2024-04-03', 'Yoga Class', 'Completed'),
    ('dave.wilson@example.com', 100.00, '2024-04-04', 'Annual Membership', 'Refunded'),
    ('emily.white@example.com', 65.00, '2024-04-05', 'HIIT Class', 'Refunded');




