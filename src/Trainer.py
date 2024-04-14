import psycopg2
from DatabaseManager import DBManager
import bcrypt
import getpass
from ClearScreen import clear_screen
import time

class Trainer:
    def __init__(self, trainer_id):
        self.trainer_id = trainer_id

    @staticmethod
    def log_in():
        clear_screen()
        print("=============================================")
        print("Trainer Log In")

        trainer_id = input("Enter your Trainer ID: ").strip()
        password = getpass.getpass("Enter your password: ")

        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT password FROM trainer_accounts WHERE trainer_id = %s", (trainer_id,))
                record = cursor.fetchone()

                if record is None:
                    print("Trainer ID not found. Please try again. Redirecting...")
                    time.sleep(1)  # Pause for effect
                    return

                stored_password = record['password'].encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    print("Login successful! Accessing Trainer Dashboard...")
                    time.sleep(1)  # Pause for effect
                    trainer = Trainer(trainer_id)
                    trainer.run_dashboard()
                else:
                    print("Incorrect password. Please try again. Redirecting...")
                    time.sleep(1)  # Pause for effect

    def run_dashboard(self):
        while True:
            trainer_name = self.fetch_trainer_name()
            clear_screen()
            print("=============================================")
            print(f"Welcome to Trainer Dashboard, {trainer_name}! (ID: {self.trainer_id})")
            
            availability = self.fetch_availability()
            if not availability:
                print("No availability data found for this trainer.")
                return

            print("Your Current Availability:")
            print("| {:^5} | {:<14} |".format("Day", "Availability"))
            for day, available in availability.items():
                print("| {:^5} | {:<14} |".format(day[:3].capitalize(), 'Available' if available else 'Not Available'))
            print("----------------------------------------------------")

            print("1. Edit Availability")
            print("2. View Member Profiles")
            print("3. Give Member Achievement")
            print("4. Go back to Main Menu")
            print("5. Log Out")

            choice = input("Enter choice: ")

            if choice == "1":
                self.edit_availability(availability)
            elif choice == "2":
                self.view_member_profile()
            elif choice == "3":
                self.give_member_achievement()
            elif choice == "4":
                return  # Go back to main menu
            elif choice == "5":
                break  # Log out
            else:
                print("Invalid choice. Please choose again.")

    def fetch_trainer_name(self):
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name FROM trainer_accounts WHERE trainer_id = %s", (self.trainer_id,))
                record = cursor.fetchone()
                return record['name'] if record else "Trainer"

    def fetch_availability(self):
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT {', '.join([day + '_available' for day in days])} FROM trainer_accounts WHERE trainer_id = %s", (self.trainer_id,))
                availability = cursor.fetchone()
                return {day: availability[day] for day in availability} if availability else {}

    def edit_availability(self, current_availability):
        new_availability = {}
        for day in current_availability.keys():
            current_status = 'y' if current_availability[day] else 'n'
            choice = input(f"Available on {day.capitalize()[:3]} (y/n)? [current: {current_status}]: ").strip().lower()
            if choice in ['y', 'n']:
                new_availability[day] = True if choice == 'y' else False
            elif choice == '':
                new_availability[day] = current_availability[day]
            else:
                print("Invalid input, please enter 'y' for yes, 'n' for no, or press Enter to keep the current status.")

        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                update_query = f"UPDATE trainer_accounts SET {', '.join([f'{day} = %s' for day in new_availability.keys()])} WHERE trainer_id = %s"
                cursor.execute(update_query, list(new_availability.values()) + [self.trainer_id])
                conn.commit()
                print("Availability updated successfully.")

    def give_member_achievement(self):
        member_name = input("Enter the member's name to award an achievement: ").strip()
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                # First fetch member details to ensure they exist
                cursor.execute("SELECT email FROM member_accounts WHERE name ILIKE %s", (f'%{member_name}%',))
                member = cursor.fetchone()
                if not member:
                    print("No member found by that name.")
                    return
                
                # Fetch existing achievements for the member
                cursor.execute("SELECT * FROM fitness_achievements WHERE email = %s", (member['email'],))
                current_achievements = cursor.fetchone()
                
                if not current_achievements:
                    # Create a new row for the member's email if no achievements exist
                    cursor.execute("""
                        INSERT INTO fitness_achievements (email)
                        VALUES (%s)
                    """, (member['email'],))
                    conn.commit()
                    current_achievements = {'email': member['email']}  # Initialize empty achievements
                
                # Display available achievements
                print("Available Achievements:")
                achievements = {1: "first_fitness_goal_achieved",
                                2: "never_skipped_leg_day",
                                3: "can_do_pushup",
                                4: "can_do_pullup",
                                5: "can_touch_toes",
                                6: "achieved_weight_loss_goal",
                                7: "achieved_muscle_gain_goal"}
                available_achievements = []
                current_member_achievements = []
                for idx, (key, value) in enumerate(achievements.items(), 1):
                    if key != 'email':
                        formatted_key = value.replace('_', ' ').capitalize()
                        if current_achievements.get(value, False):
                            current_member_achievements.append(formatted_key)
                        else:
                            available_achievements.append((idx, formatted_key))

                if not current_member_achievements:
                    print("This member currently has no achievements.")
                else:
                    print("Current Member's Achievements:")
                    for achievement in current_member_achievements:
                        print("- " + achievement)

                if available_achievements:
                    print("\nAvailable Achievements:")
                    for idx, formatted_key in available_achievements:
                        print(f"{idx}. {formatted_key}")

                    # Let the trainer choose an achievement to grant
                    choice = input("Select an achievement to grant (enter the number): ")
                    if choice.isdigit():
                        choice_idx = int(choice)
                        if 1 <= choice_idx <= len(available_achievements):
                            achievement_to_grant = achievements[available_achievements[choice_idx - 1][0]]
                            # Update the member's achievements
                            cursor.execute(f"""
                                UPDATE fitness_achievements
                                SET {achievement_to_grant} = TRUE
                                WHERE email = %s
                            """, (member['email'],))
                            conn.commit()
                            print(f"Achievement '{achievement_to_grant.replace('_', ' ').capitalize()}' granted to {member_name}.")
                        else:
                            print("Invalid selection.")
                    else:
                        print("Invalid input.")
                else:
                    print("All achievements have been earned by this member.")



    def view_member_profile(self):
        member_name = input("Enter the member's name to view profiles: ").strip()
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                # Fetch all members with a similar name
                cursor.execute("""
                    SELECT email, name FROM member_accounts WHERE name ILIKE %s
                """, (f'%{member_name}%',))
                members = cursor.fetchall()

                if not members:
                    print("No members found with that name.")
                    return

                print("Select a member to view details:")
                for idx, member in enumerate(members, start=1):
                    print(f"{idx}. {member['name']} ({member['email']})")

                choice = input("Enter choice (number): ")
                if choice.isdigit() and 1 <= int(choice) <= len(members):
                    selected_member = members[int(choice) - 1]
                    self.display_member_details(selected_member['email'])
                else:
                    print("Invalid choice.")

    def display_member_details(self, email):
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                # Fetch and display personal information
                cursor.execute("""
                SELECT email, name, gender, age FROM member_accounts WHERE email = %s
                """, (email,))
                member_info = cursor.fetchone()

                # Fetch and display health stats
                cursor.execute("""
                    SELECT * FROM health_statistics WHERE email = %s
                """, (email,))
                health_stats = cursor.fetchone()

                # Fetch and display fitness goals
                cursor.execute("""
                    SELECT * FROM fitness_goals WHERE email = %s
                """, (email,))
                fitness_goals = cursor.fetchone()

                # Fetch and display exercise routines
                cursor.execute("""
                    SELECT * FROM exercise_routines WHERE email = %s
                """, (email,))
                exercise_routines = cursor.fetchone()

                # Displaying the details
                clear_screen()
                print("\nMember Details:")
                print("Name:", member_info['name'] if member_info else 'Not available')
                
                print("\nPersonal Information:")
                if member_info:
                    for key, value in member_info.items():
                        print(f"  {key}: {value}")
                else:
                    print("  No personal information available.")

                print("\nHealth Stats:")
                if health_stats:
                    for key, value in health_stats.items():
                        print(f"  {key}: {value}")
                else:
                    print("  No health statistics available.")

                print("\nFitness Goals:")
                if fitness_goals:
                    for key, value in fitness_goals.items():
                        print(f"  {key}: {value}")
                else:
                    print("  No fitness goals set.")

                print("\nExercise Routines:")
                if exercise_routines:
                    for key, value in exercise_routines.items():
                        print(f"  {key}: {value}")
                else:
                    print("  No exercise routines set.")
                
                input("Press enter to go back...")
