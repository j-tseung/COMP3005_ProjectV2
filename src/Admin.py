"""
The Admin class encapsulates all administrative functionalities within the Pain to Progress 
Health and Fitness Club's management system. It offers static methods to manage various 
aspects of the fitness club such as room bookings, equipment maintenance, class schedules, 
payment processing, and the management of trainers and members.

Key Functionalities:
- add_admin_password(): Adds a hashed password for the admin into the database.
- log_in(): Authenticates an admin using a password to provide access to the administrative dashboard.
- run_dashboard(): Provides an interactive dashboard for managing the entire fitness club operations including rooms, equipment, classes, payments, trainers, and members.
- manage_room_bookings(), monitor_equipment_maintenance(), manage_class_schedule(), process_payments(), manage_trainers(), and manage_members(): Each function allows the admin to perform specific management tasks, updating the database as necessary and providing a user-friendly interface for each administrative function.
- admin_exit(): Safely exits the admin session and closes the application.
"""

import psycopg2
import getpass
import bcrypt
import time
import datetime
import sys

from ClearScreen import clear_screen
from DatabaseManager import DBManager

class Admin:
    @staticmethod
    def add_admin_password():
        password = getpass.getpass("Please enter the admin password: ")
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Use DBManager for database connection
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(
                        "INSERT INTO admin (password) VALUES (%s)",
                        (hashed_password.decode('utf-8'),)
                    )
                    conn.commit()
                    print("Admin password added successfully.")
                except psycopg2.Error as e:
                    conn.rollback()
                    print(f"An error occurred: {e}")
    @staticmethod
    def admin_exit():
        print("Thanks for all your hard work, administrator!")
        sys.exit(0)
        
    @staticmethod
    def log_in():
        clear_screen()
        print("====================================================")
        print("Admin Log In")
        password = getpass.getpass("Enter admin password: ")

        # Use the context manager from DBManager to handle the database connection
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    # Execute the query to retrieve the admin password
                    cursor.execute("SELECT password FROM member_accounts WHERE email = 'admin'")
                    record = cursor.fetchone()

                    # Check if an admin record exists
                    if record is None:
                        print("No admin records found. Please contact system administrator.")
                        return False

                    # Check the entered password against the hashed password in the database
                    stored_password = record['password'].encode('utf-8')
                    if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                        print("Login successful! Accessing Admin Dashboard...")
                        time.sleep(1) # sleep for so above prompt appears
                        Admin.run_dashboard()
                        return True
                    else:
                        print("Incorrect Admin password. Redirecting to Main Menu...")
                        time.sleep(1)
                        return False
                except psycopg2.Error as e:
                    print(f"An error occurred during login: {e}")
                    return False
        
    @staticmethod
    def run_dashboard():
        
        options = {
            "1": Admin.manage_room_bookings,
            "2": Admin.monitor_equipment_maintenance,
            "3": Admin.manage_class_schedule,
            "4": Admin.process_payments,
            "5": Admin.manage_trainers,
            "6": Admin.manage_members,
            "7": lambda: print("Returning to main menu..."),
            "8": Admin.admin_exit
        }

        while True:
            clear_screen()
            print("=========================================================")
            print("Admin Dashboard")
            print("1. Manage Room Bookings")
            print("2. Monitor Equipment Maintenance")
            print("3. Manage Class Schedule")
            print("4. Process Payments")
            print("5. Manage Trainers")
            print("6: Manage Members")
            print("7. Go back to Main Menu")
            print("8. Exit")
            
            choice = input("Enter choice: ")
            action = options.get(choice)

            if action:
                result = action()
                if result:  # Print any messages returned by actions
                    print(result)
                if choice == "7":
                    break  # Break out of the loop if returning to main menu or logging out
            else:
                print("Invalid choice. Please choose again.")

    @staticmethod
    def manage_room_bookings():
        
        while True:  # Wrap the content in a while loop to return to the menu after each action
            with DBManager.connection() as conn:
                with conn.cursor() as cursor:
                    try:
                        # Retrieve bookings for all rooms
                        cursor.execute("""
                            SELECT b.booking_id, b.room_id, r.room_name, b.duration, b.day_of_week, b.start_time 
                            FROM bookings b
                            JOIN rooms r ON b.room_id = r.room_id
                            ORDER BY b.booking_id
                        """)
                        bookings = cursor.fetchall()
                        clear_screen()
                        print("=========================================================")
                        print("Current Room Bookings:")
                        print("| {:^12} | {:<25} | {:^5} | {:^10} | {:^10} |".format(
                            "Booking ID", "Room Name", "Day", "Start Time", "Duration"
                        ))

                        for booking in bookings:
                            print("| {:^12} | {:<25} | {:^5} | {:^10} | {:^10} |".format(
                                booking['booking_id'],
                                booking['room_name'],
                                booking['day_of_week'],
                                booking['start_time'].strftime('%H:%M:%S'),
                                str(booking['duration']),
                            ))

                        print("--------------------------------------------------------")
                        print("1. Edit Booking")
                        print("2. Add Booking")
                        print("3. Delete Booking")
                        print("4. Go Back to Admin Dashboard")
                        print("5. Exit")
                        choice = input("Choose an action: ")

                        if choice == "1":
                            booking_id = input("Enter Booking ID to update: ")
                            Admin.edit_booking(booking_id)
                        elif choice == "2":
                            Admin.add_room_booking()
                        elif choice == "3":
                            booking_id = input("Enter Booking ID to delete: ")
                            Admin.delete_booking(booking_id)
                        elif choice == "4":
                            break  # Break the loop to go back to the previous menu
                        elif choice == "5":
                            Admin.admin_exit
                        else:
                            print("Invalid choice. Please choose again.")

                    except psycopg2.Error as e:
                        print("An error occurred while managing room bookings:", e)


    @staticmethod
    def add_room_booking():
        clear_screen()
        print("=========================================================")
        print("Add New Room Booking:")

        # Display available rooms and trainers
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT room_id, room_name FROM rooms")
                rooms = cursor.fetchall()
                print("Available Rooms:")
                for room in rooms:
                    print(f"{room['room_id']}: {room['room_name']}")

                cursor.execute("SELECT trainer_id, name FROM trainer_accounts")
                trainers = cursor.fetchall()
                print("\nAvailable Trainers:")
                for trainer in trainers:
                    print(f"{trainer['trainer_id']}: {trainer['name']}")

        valid_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        # Validate booking_id
        booking_id = Admin.get_unique_booking_id()

        if booking_id == 'q':
            print("Returning to manage room bookings menu...")
            return

        room_id = Admin.get_valid_room_id(rooms, "Enter Room ID: ")
        trainer_id = Admin.get_valid_trainer_id(trainers, "Enter Trainer ID: ")
        duration = Admin.get_valid_integer("Enter Duration (in minutes): ")
        day_of_week = Admin.get_valid_day_of_week(valid_days, "Enter Day of the Week (e.g., Mon): ")
        start_time = Admin.get_valid_time("Enter Start Time (HH:MM): ")

        # Insert the new booking into the database
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("""
                        INSERT INTO bookings (booking_id, room_id, trainer_id, duration, day_of_week, start_time)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (booking_id, room_id, trainer_id, duration, day_of_week, start_time))
                    conn.commit()
                    print("Booking successfully added.")
                except psycopg2.Error as e:
                    conn.rollback()
                    print("Failed to add booking. Error:", e)

    @staticmethod
    def get_unique_booking_id():
        while True:
            booking_id = input("Enter Booking ID (or type 'q' to go back): ")
            if booking_id.lower() == 'q':
                return 'q'
            try:
                booking_id = int(booking_id)
                with DBManager.connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT booking_id FROM bookings WHERE booking_id = %s", (booking_id,))
                        if cursor.fetchone():
                            print("This Booking ID already exists. Please try a different ID.")
                        else:
                            return booking_id
            except ValueError:
                print("Invalid Booking ID. Please enter a numerical ID.")

    @staticmethod
    def get_valid_room_id(rooms, prompt):
        while True:
            room_id = input(prompt)
            if room_id.isdigit() and any(room['room_id'] == int(room_id) for room in rooms):
                return int(room_id)
            print("Invalid Room ID. Please enter a valid numeric ID from the available rooms list.")

    @staticmethod
    def get_valid_trainer_id(trainers, prompt):
        while True:
            trainer_id = input(prompt)
            if trainer_id.isdigit() and any(trainer['trainer_id'] == int(trainer_id) for trainer in trainers):
                return int(trainer_id)
            print("Invalid Trainer ID. Please enter a valid numeric ID from the available trainers list.")

    @staticmethod
    def get_valid_integer(prompt):
        while True:
            value = input(prompt)
            if value.isdigit():
                return int(value)
            print("Invalid input. Please enter a valid integer.")

    @staticmethod
    def get_valid_day_of_week(valid_days, prompt):
        while True:
            day = input(prompt).capitalize()
            if day in valid_days:
                return day
            print(f"Invalid day. Please enter one of the following: {', '.join(valid_days)}")

    @staticmethod
    def get_valid_time(prompt):
        while True:
            time_str = input(prompt)
            try:
                return datetime.datetime.strptime(time_str, '%H:%M').time()
            except ValueError:
                print("Invalid time format. Please use HH:MM format.")

    @staticmethod
    def edit_booking(booking_id):
        clear_screen()
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    # Retrieve the selected booking
                    cursor.execute("""
                        SELECT b.booking_id, r.room_name, b.day_of_week, b.start_time, b.duration, b.room_id
                        FROM bookings b
                        JOIN rooms r ON b.room_id = r.room_id
                        WHERE b.booking_id = %s
                    """, (booking_id,))
                    booking = cursor.fetchone()

                    if not booking:
                        print("Booking ID not found.")
                        return  # Exit if no booking is found

                    # Display current booking details
                    print("=========================================================")
                    print("Edit Booking Details:")
                    print(f"Current Room Name: {booking['room_name']}")
                    print(f"Current Day of Week: {booking['day_of_week']}")
                    print(f"Current Start Time: {booking['start_time']}")
                    print(f"Current Duration: {booking['duration']}")

                    # Get room choices
                    cursor.execute("SELECT room_id, room_name FROM rooms")
                    rooms = cursor.fetchall()
                    print("Available Rooms:")
                    for room in rooms:
                        print(f"{room['room_id']}: {room['room_name']}")

                    # Get updates from user
                    print("--------------------------------------------------------")
                    new_room_id = input("Choose new room ID, or press enter to keep current: ") or booking['room_id']
                    new_day = input("New Day of Week (e.g., Mon, Tue), press enter to keep current: ") or booking['day_of_week']
                    new_time = input("New Start Time (HH:MM:SS), press enter to keep current: ") or booking['start_time'].strftime('%H:%M:%S')
                    new_duration = input("New Duration (e.g., 1:25:00), press enter to keep current: ") or str(booking['duration'])

                    # Update booking
                    cursor.execute("""
                        UPDATE bookings
                        SET room_id = %s, day_of_week = %s, start_time = %s, duration = %s
                        WHERE booking_id = %s
                    """, (new_room_id, new_day, new_time, new_duration, booking_id))

                    conn.commit()
                    print("Booking updated successfully.")
                
                except psycopg2.Error as e:
                    conn.rollback()
                    print(f"An error occurred while managing room bookings: {e}")
    
    @staticmethod
    def delete_booking(booking_id):
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("DELETE FROM bookings WHERE booking_id = %s", (booking_id,))
                    conn.commit()
                    print(f"Booking {booking_id} has been deleted.")

                except psycopg2.Error as e:
                    conn.rollback()
                    print(f"An error occurred while deleting the booking: {e}")
                    
    @staticmethod
    def monitor_equipment_maintenance():
        clear_screen()
        print("=========================================================")
        print("Equipment Maintenance Monitoring:")
        print("| {:<20} | {:<25} | {:^8} |".format(
            "Equipment Name", "Room Name", "Quality"
        ))

        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("""
                        SELECT e.equipment_name, r.room_name, e.quality
                        FROM equipment e
                        JOIN rooms r ON e.room_id = r.room_id
                        ORDER BY e.quality DESC
                    """)
                    equipments = cursor.fetchall()

                    for equipment in equipments:
                        print("| {:<20} | {:<25} | {:^8} |".format(
                            equipment['equipment_name'],
                            equipment['room_name'],
                            equipment['quality'],
                        ))

                    # List equipment needing immediate attention
                    Admin.highlight_problematic_equipment(equipments)
                    
                except psycopg2.Error as e:
                    print("An error occurred while monitoring equipment maintenance:", e)

    @staticmethod
    def highlight_problematic_equipment(equipments):
        
        print("\nChecking for equipment needing immediate attention...")
        problematic = [equip for equip in equipments if equip['quality'] < 4 ]
        if problematic:
            print("| {:<20} | {:<25} | {:^8} |".format(
                "Equipment Name", "Room Name", "Quality",
            ))
            for equip in problematic:
                print("| {:<20} | {:<25} | {:^8} |".format(
                    equip['equipment_name'],
                    equip['room_name'],
                    equip['quality'],
                    
                ))
            print("\n1. Send Equipment for Maintenance")
            print("2. Go Back to Menu")
            choice = input("Enter your choice: ")
            if choice == "1":
                Admin.fix_equipment()
        else:
            print("\nAll equipment is in good condition.")
            input("Press Enter to go back to the menu...")

    @staticmethod
    def fix_equipment():
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("""
                        UPDATE equipment
                        SET quality = 10
                        WHERE quality < 4
                    """)
                    updated_rows = cursor.rowcount
                    conn.commit()
                    print(f"All necessary equipment has been fixed. Total items updated: {updated_rows}.")
                except psycopg2.Error as e:
                    conn.rollback()
                    print("An error occurred while fixing the equipment: ", e)

        # Show the updated maintenance monitoring again
        Admin.monitor_equipment_maintenance()

    @staticmethod
    def manage_class_schedule():
        # Rest of the code for adding, editing, deleting classes
        while True:
            clear_screen()
            print("=========================================================")
            print("Class Schedule Management")

            # Display current classes
            with DBManager.connection() as conn:
                with conn.cursor() as cursor:
                    try:
                        cursor.execute("""
                            SELECT class_id, class_name, trainer_id, room_id, day_of_week, start_time, duration
                            FROM class_schedule
                            ORDER BY class_id
                        """)
                        classes = cursor.fetchall()
                        if classes:
                            print("Current Classes:")
                            print("| {:^10} | {:<15} | {:^15} | {:^7} | {:^15} | {:^10} | {:^10} |".format(
                                "Class ID", "Class Name", "Trainer ID", "Room ID", "Day of Week", "Start Time", "Duration"))
                            for class_ in classes:
                                print("| {:^10} | {:<15} | {:^15} | {:^7} | {:^15} | {:^10} | {:^10} |".format(
                                    class_['class_id'],
                                    class_['class_name'],
                                    class_['trainer_id'],
                                    class_['room_id'],
                                    class_['day_of_week'],
                                    class_['start_time'].strftime('%H:%M'),
                                    class_['duration']))
                            print("--------------------------------------------------------")
                        else:
                            print("No classes found.")
                    except psycopg2.Error as e:
                        print("An error occurred while fetching class schedule:", e)
        
            print("1. Add New Class")
            print("2. Edit Existing Class")
            print("3. Delete Class")
            print("4. Go Back")
            
            choice = input("Enter choice: ")
            
            if choice == "1":
                Admin.add_class()
            elif choice == "2":
                Admin.edit_class()
            elif choice == "3":
                Admin.delete_class()
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please choose again.")

    @staticmethod
    def add_class():
        clear_screen()
        print("=========================================================")
        print("Add New Class Schedule:")

        # Display available trainers and rooms
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT room_id, room_name FROM rooms")
                rooms = cursor.fetchall()
                print("Available Rooms:")
                for room in rooms:
                    print(f"{room['room_id']}: {room['room_name']}")

                cursor.execute("SELECT trainer_id, name FROM trainer_accounts")
                trainers = cursor.fetchall()
                print("\nAvailable Trainers:")
                for trainer in trainers:
                    print(f"{trainer['trainer_id']}: {trainer['name']}")

        class_name = input("Enter Class Name: ")
        trainer_id = Admin.get_valid_trainer_id(trainers, "Enter Trainer ID: ")
        room_id = Admin.get_valid_room_id(rooms, "Enter Room ID: ")
        day_of_week = Admin.get_valid_day_of_week(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "Enter Day of the Week (e.g., Mon): ")
        start_time = Admin.get_valid_time("Enter Start Time (HH:MM): ")
        duration = Admin.get_valid_integer("Enter Duration (in minutes): ")

        # Insert the new class into the database
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("""
                        INSERT INTO class_schedule (class_name, trainer_id, room_id, day_of_week, start_time, duration)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (class_name, trainer_id, room_id, day_of_week, start_time, duration))
                    conn.commit()
                    print("Class added successfully. Redirecting...")
                    time.sleep(1)
                except psycopg2.Error as e:
                    conn.rollback()
                    print("Failed to add class. Error:", e)

                    
    @staticmethod
    def edit_class():
        print("=========================================================")
        class_id = input("Enter Class ID to update: ")
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("""
                        SELECT class_name, trainer_id, room_id, day_of_week, start_time, duration
                        FROM class_schedule
                        WHERE class_id = %s
                    """, (class_id,))
                    class_info = cursor.fetchone()

                    if not class_info:
                        print("No class found with that ID. Redirecting...")
                        time.sleep(1)
                        return

                    # Display existing information and ask for new data
                    new_class_name = input(f"New Class Name [{class_info['class_name']}]: ") or class_info['class_name']

                    new_trainer_id = input(f"New Trainer ID [{class_info['trainer_id']}]: ") or class_info['trainer_id']
                    new_trainer_id = int(new_trainer_id) if new_trainer_id.isdigit() else class_info['trainer_id']

                    new_room_id = input(f"New Room ID [{class_info['room_id']}]: ") or class_info['room_id']
                    new_room_id = int(new_room_id) if new_room_id.isdigit() else class_info['room_id']

                    valid_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                    new_day = input(f"New Day of Week [{class_info['day_of_week']}]: ").capitalize() or class_info['day_of_week']
                    new_day = new_day if new_day in valid_days else class_info['day_of_week']

                    new_start_time = input(f"New Start Time (HH:MM) [{class_info['start_time']}]: ") or class_info['start_time']
                    try:
                        new_start_time = datetime.datetime.strptime(new_start_time, '%H:%M').time()
                    except ValueError:
                        pass

                    new_duration = input(f"New Duration (HH:MM) [{class_info['duration']}]: ") or class_info['duration']
                    if ':' in new_duration:
                        try:
                            new_duration = datetime.datetime.strptime(new_duration, '%H:%M').time()
                        except ValueError:
                            pass

                    cursor.execute("""
                        UPDATE class_schedule
                        SET class_name = %s, trainer_id = %s, room_id = %s, day_of_week = %s,
                            start_time = %s, duration = %s 
                        WHERE class_id = %s
                    """, (new_class_name, new_trainer_id, new_room_id, new_day, new_start_time, new_duration, class_id))
                    conn.commit()
                    print("Class updated successfully. Redirecting...")
                    time.sleep(1)
                except psycopg2.Error as e:
                    conn.rollback()
                    print("An error occurred while updating the class:", e)
                    time.sleep(1)


    @staticmethod
    def delete_class():
        print("=========================================================")
        class_id = input("Enter Class ID to delete: ")
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("DELETE FROM class_schedule WHERE class_id = %s", (class_id,))
                    conn.commit()
                    print(f"Class {class_id} has been deleted.")
                except psycopg2.Error as e:
                    conn.rollback()
                    print("An error occurred while deleting the class:", e)

    @staticmethod
    def process_payments():
        clear_screen()
        print("=========================================================")
        print("Payment Processing")
        # Show all payments immediately upon entering the menu
        Admin.view_all_payments()
        while True:
            print("1. Mark Payment as Completed")
            print("2. Process a Refund")
            print("3. Go Back")

            choice = input("Enter choice: ")

            if choice == "1":
                Admin.mark_payment_completed()
            elif choice == "2":
                Admin.process_refund()
            elif choice == "3":
                break
            else:
                print("Invalid choice. Please choose again.")

    @staticmethod
    def view_all_payments():
        clear_screen()
        # This function now only prints the payments without the surrounding menu text
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("""
                        SELECT payment_id, email, amount, payment_date, payment_type, status
                        FROM payments
                        ORDER BY payment_id
                    """)
                    payments = cursor.fetchall()
                    print("Current Payments:")
                    print("| {:^10} | {:<30} | {:^8} | {:^10} | {:<20} | {:^10} |".format(
                        "ID", "Email", "Amount", "Date", "Type", "Status"
                    ))
                    for payment in payments:
                        print("| {:^10} | {:<30} | ${:<7.2f} | {:^10} | {:<20} | {:^10} |".format(
                            payment['payment_id'],
                            payment['email'],
                            payment['amount'],
                            payment['payment_date'].strftime('%Y-%m-%d'),
                            payment['payment_type'],
                            payment['status']
                        ))
                    print("--------------------------------------------------------")
                except psycopg2.Error as e:
                    print("An error occurred during payment viewing:", e)

    @staticmethod
    def mark_payment_completed():
        payment_id = input("Enter Payment ID to mark as completed: ")
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("""
                        UPDATE payments
                        SET status = 'Completed'
                        WHERE payment_id = %s
                    """, (payment_id,))
                    conn.commit()
                    print(f"Payment {payment_id} marked as completed.")
                except psycopg2.Error as e:
                    conn.rollback()
                    print(f"An error occurred while marking the payment as completed: {e}")
        # Call view_all_payments to refresh the list
        Admin.view_all_payments()

    @staticmethod
    def process_refund():
        payment_id = input("Enter Payment ID to process a refund: ")
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("""
                        UPDATE payments
                        SET status = 'Refunded'
                        WHERE payment_id = %s
                    """, (payment_id,))
                    conn.commit()
                    print(f"Refund processed for Payment {payment_id}.")
                except psycopg2.Error as e:
                    conn.rollback()
                    print(f"An error occurred during the refund process: {e}")
        # Call view_all_payments to refresh the list
        Admin.view_all_payments()
        
               
    @staticmethod
    def view_all_trainers():

        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("""
                        SELECT trainer_id, name, monday_available, tuesday_available, wednesday_available,
                               thursday_available, friday_available
                        FROM trainer_accounts
                        ORDER BY trainer_id
                    """)
                    trainers = cursor.fetchall()
                    if trainers:
                        print("| {:^10} | {:<20} | {:<5} | {:<5} | {:<5} | {:<5} | {:<5} |".format(
                            "ID", "Name", "Mon", "Tue", "Wed", "Thu", "Fri"))
                        for trainer in trainers:
                            print("| {:^10} | {:<20} | {:<5} | {:<5} | {:<5} | {:<5} | {:<5} |".format(
                                trainer['trainer_id'],
                                trainer['name'],
                                "Yes" if trainer['monday_available'] else "No",
                                "Yes" if trainer['tuesday_available'] else "No",
                                "Yes" if trainer['wednesday_available'] else "No",
                                "Yes" if trainer['thursday_available'] else "No",
                                "Yes" if trainer['friday_available'] else "No"
                            ))
                    else:
                        print("No trainers found.")
                except psycopg2.Error as e:
                    print("An error occurred while retrieving trainers:", e)

    @staticmethod
    def manage_trainers():
        while True:
            clear_screen()
            print("====================================================")
            print("Trainer Management")  
            Admin.view_all_trainers()
              
            
            print("\n1. Add New Trainer")
            print("2. Delete Trainer")
            print("3. Go Back")

            choice = input("Enter your choice: ")

            if choice == "1":
                Admin.create_trainer_account()
            elif choice == "2":
                Admin.delete_trainer()
            elif choice == "3":
                break  # Exit the loop to go back to the previous menu
            else:
                print("Invalid choice. Please try again.")

    @staticmethod
    def create_trainer_account():
        clear_screen()
        print("====================================================")
        print("Creating Trainer Account - Please face system to new trainer.")

        # Prompt user for account details
        name = input("Enter trainer full name: ")
        password = getpass.getpass("Create your password: ")

        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Use DBManager's context manager to handle the database connection
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    # Insert new trainer into the trainers table
                    cursor.execute(
                        "INSERT INTO trainer_accounts (name, password) VALUES (%s, %s) RETURNING trainer_id",
                        (name, hashed_password.decode('utf-8'))
                    )

                    # Commit changes and retrieve the unique trainer_id
                    trainer_id = cursor.fetchone()['trainer_id']
                    conn.commit()

                    print(f"Trainer account created successfully! Your unique Trainer ID is {trainer_id}.")
                    print("Face system back to Administrator.")
                    time.sleep(1) # sleep for so above prompt appears


                except psycopg2.Error as e:
                    conn.rollback()  # Ensure all changes are rolled back in case of an error
                    if 'unique constraint' in str(e).lower():
                        print("A trainer with this name already exists, please try a different name.")
                    else:
                        print(f"An error occurred while trying to create your trainer account: {e}")


    @staticmethod
    def delete_trainer():
        trainer_id = input("Enter Trainer ID to delete: ")
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("DELETE FROM trainer_accounts WHERE trainer_id = %s", (trainer_id,))
                    conn.commit()
                    print(f"Trainer {trainer_id} has been successfully deleted.")
                except psycopg2.Error as e:
                    conn.rollback()
                    print("Failed to delete trainer. Error:", e)
                    
                    
    def manage_members():
        clear_screen()
        print("====================================================")
        print("Member Management")

        while True:
            with DBManager.connection() as conn:
                with conn.cursor() as cursor:
                    try:
                        cursor.execute("SELECT email, name FROM member_accounts ORDER BY name")
                        members = cursor.fetchall()
                        clear_screen()
                        print("List of All Members:")
                        print("| {:^5} | {:<30} | {:<15} |".format("No.", "Email", "Name"))
                        member_dict = {}
                        index = 1  # Start the index at 1
                        for member in members:
                            email = member['email']  
                            name = member['name'] if member['name'] is not None else "Unknown"
                            
                            # Skip guest accounts
                            if email.lower() == 'guest' or email.lower() == 'admin':
                                continue
                            
                            print("| {:^5} | {:<30} | {:<15} |".format(index, email, name))
                            member_dict[index] = email
                            index += 1  # Increment index after every displayed member
                        print("----------------------------------------------------")
                    except psycopg2.Error as e:
                        print("Failed to retrieve members. Error:", e)
            
            print("Enter the number of the member to delete, or press Enter to go back:")
            choice = input()

            if choice.isdigit() and int(choice) in member_dict:
                Admin.delete_member(member_dict[int(choice)])
            elif choice == "":
                break  # Exit the loop to go back
            else:
                print("Invalid choice. Please try again.")


    @staticmethod
    def delete_member(email):
        if email.lower() == 'guest':
            print("Cannot delete guest account.")
            return

        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    # Start by deleting from dependent tables
                    cursor.execute("DELETE FROM fitness_goals WHERE email = %s", (email,))
                    cursor.execute("DELETE FROM exercise_routines WHERE email = %s", (email,))
                    cursor.execute("DELETE FROM member_health_metrics WHERE email = %s", (email,))
                    cursor.execute("DELETE FROM payments WHERE email = %s", (email,))
                    cursor.execute("DELETE FROM fitness_achievements WHERE email = %s", (email,))
                    cursor.execute("DELETE FROM health_statistics WHERE email = %s", (email,))
                    cursor.execute("DELETE FROM member_accounts WHERE email = %s", (email,))
                    conn.commit()
                    print(f"Member with email {email} has been successfully deleted.")
                    time.sleep(1)
                except psycopg2.Error as e:
                    conn.rollback()
                    if 'foreign key constraint' in str(e).lower():
                        print("This member cannot be deleted due to related records in other tables. Please ensure all related data is removed before deleting.")
                    else:
                        print("Failed to delete member. Error:", e)
