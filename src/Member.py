import sys
import getpass
import bcrypt
import time
import psycopg2
from datetime import datetime
from ClearScreen import clear_screen
from DatabaseManager import DBManager
from Fitness import Fitness

class Member:
    def __init__(self, email):
        self.email = email

    @staticmethod
    def log_in():
        clear_screen()
        print("====================================================")
        print("Member Log In Screen")

        email = input("Enter your email: ").strip()
        password = getpass.getpass("Enter your password: ")

        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT password FROM member_accounts WHERE email = %s", (email,))
                record = cursor.fetchone()

                if record is None:
                    print("Email not found. Please register or try a different email. Redirecting to Main Menu...")
                    time.sleep(1)
                    return

                if bcrypt.checkpw(password.encode('utf-8'), record['password'].encode('utf-8')):
                    print("Login successful! Opening Dashboard...")
                    time.sleep(1)
                    member_dashboard = Member(email)
                    member_dashboard.run_dashboard()
                else:
                    print("Incorrect password. Please try again. Redirecting to Main Menu...")
                    time.sleep(1)

    def run_dashboard(self):
        """ Method to display the dashboard menu and handle user actions. """
        while True:
            clear_screen()
            print("====================================================")
            print(f"Welcome to Your Dashboard, {self.get_member_name()}!")  
            print("1. Go to gym")
            print("2. My Personal Information")
            print("3. My Health Metrics")
            print("4. My Health Statistics")
            print("5. My Exercise Routines")
            print("6. My Fitness Goals")
            print("7. My Fitness Achievements")
            print("8. Log Out")

            choice = input("Enter choice: ")
            self.handle_dashboard_choice(choice)

    def get_member_name(self):
        """ Retrieves member's name from the database. """
        with DBManager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM member_accounts WHERE email = %s", (self.email,))
            name = cursor.fetchone()
            return name['name'] if name else "Member"

    def handle_dashboard_choice(self, choice):
        """ Handles the user's choice from the dashboard menu. """
        actions = {
            "1": lambda: Fitness.go_to_gym(self.email),
            "2": lambda: self.show_or_edit_personal_information(),
            "3": lambda: self.show_or_edit_health_info(),
            "4": lambda: self.show_or_edit_health_stats(),
            "5": lambda: self.show_or_edit_exercise_routines(),
            "6": lambda: self.show_or_edit_fitness_goals(),
            "7": lambda: self.view_fitness_achievements(self.email),
            "8": sys.exit
        }
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice. Please choose again.")
            time.sleep(1)  # Gives user time to read the message before clearing the screen

    def show_or_edit_personal_information(self):
        """ Shows or edits personal information. """
        while True:
            clear_screen()
            user_info = self.get_personal_info()
            if not user_info:
                print("No user found with this email.")
                time.sleep(1)
                return
            print("====================================================")
            print("Personal Information:")
            print("| {:<15} | {:<20} |".format("Field", "Value"))
            print("| {:<15} | {:<20} |".format("Email", self.email))
            print("| {:<15} | {:<20} |".format("Name", user_info['name'] if user_info['name'] is not None else "Not set"))
            print("| {:<15} | {:<20} |".format("Gender", user_info['gender'] if user_info['gender'] is not None else "Not set"))
            print("| {:<15} | {:<20} |".format("Age", user_info['age'] if user_info['age'] is not None else "Not set"))

            print("----------------------------------------------------")
            print("1. Edit Information")
            print("2. Return to Dashboard")

            choice = input("Enter choice: ")
            if choice == "1":
                self.edit_personal_information(user_info)
            elif choice == "2":
                return
            
    def get_personal_info(self):
        """ Fetches personal information from the database. """
        with DBManager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, gender, age FROM member_accounts WHERE email = %s", (self.email,))
            user_info = cursor.fetchone()
            # Ensure all keys are present, even if they are None
            return {key: (user_info[key] if user_info and key in user_info else "Not set") for key in ['name', 'gender', 'age']}


    def edit_personal_information(self, user_info):
        """ Edits personal information and updates the database. """
        # Request new name or keep current if none is entered
        new_name = input(f"Enter new name or press 'Enter' to keep current (current: {user_info.get('name', 'Not set')}): ").strip()
        new_name = new_name if new_name else user_info['name']

        # Handle gender input, allowing for 'Enter' to skip
        new_gender = self.get_new_gender(user_info)

        # Get a valid age or keep current if 'Enter' is pressed
        new_age = self.get_valid_age(user_info)

        with DBManager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE member_accounts 
                SET name = %s, gender = %s, age = %s 
                WHERE email = %s
            """, (new_name, new_gender, new_age, self.email))
            conn.commit()
            print("Personal information updated successfully. Redirecting...")
            time.sleep(1)

    def get_new_gender(self, user_info):
        """ Handles gender selection and input, allowing skip by pressing 'Enter'. """
        print("Gender Options: 1. Female 2. Male 3. Other")
        gender_choice = input(f"Select gender or press 'Enter' to keep current (current: {user_info.get('gender', 'Not set')}): ").strip()
        if not gender_choice:
            return user_info['gender']  # Return current gender if skipped

        gender_options = {'1': 'Female', '2': 'Male', '3': 'Other'}
        new_gender = gender_options.get(gender_choice, user_info['gender'])

        if new_gender == 'Other':
            other_gender = input("Please specify your gender: ").strip()
            return other_gender if other_gender else user_info['gender']

        return new_gender

    def get_valid_age(self, user_info):
        """ Validates and returns a proper age input, allows skipping by pressing 'Enter'. """
        while True:
            new_age_input = input(f"Enter new age or press 'Enter' to keep current (current: {user_info.get('age', 'Not set')}): ").strip()
            if not new_age_input:
                return user_info['age']  # Return current age if 'Enter' is pressed to skip
            if new_age_input.isdigit():
                return int(new_age_input)
            else:
                print("Invalid input. Please enter a valid age.")

        
    def show_or_edit_fitness_goals(self):
        clear_screen()
        """ Display and possibly edit fitness goals with robust connection handling. """
        try:
            with DBManager.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT goal1, goal2, goal3 FROM fitness_goals WHERE email = %s", (self.email,))
                    goals = cursor.fetchone()

                    if not goals:
                        print("No fitness goals found. Setting up initial goals.")
                        self.edit_fitness_goals()  # Directly go to edit if no goals found
                        return

                    print("Current Fitness Goals:")
                    print("| {:<15} | {:<50} |".format("Goal Number", "Goal"))
                    print("| {:<15} | {:<50} |".format("Goal 1", goals['goal1'] if goals['goal1'] else "Not set"))
                    print("| {:<15} | {:<50} |".format("Goal 2", goals['goal2'] if goals['goal2'] else "Not set"))
                    print("| {:<15} | {:<50} |".format("Goal 3", goals['goal3'] if goals['goal3'] else "Not set"))
                    print("------------------------------------------------")

                    edit_choice = input("Would you like to edit your goals? (1 to edit, Enter to go back): ")
                    if edit_choice == "1":
                        self.edit_fitness_goals()
        except psycopg2.Error as e:
            print(f"An error occurred while accessing the database: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


    def edit_fitness_goals(self):
        """ Allows the user to select preset fitness goals or input custom goals. """
        preset_goals = [
            "30-minute morning run.",
            "Weightlifting session.",
            "Yoga for flexibility.",
            "Drink 8 glasses of water daily.",
            "Include veggies in every meal."
        ]

        print("Edit Your Fitness Goals")
        print("You can choose from the following preset goals, enter your own, or keep the current ones.")
        for index, goal in enumerate(preset_goals, 1):
            print(f"{index}. {goal}")

        # Fetch current goals
        current_goals = self.get_current_fitness_goals()

        print("\nCurrent Goals:")
        for i, goal in enumerate(current_goals, start=1):
            print(f"Goal {i}: {goal if goal else 'Not set'}")

        # Allow editing goals
        goals = []
        print("\nChoose up to 3 goals by number, press 'C' to customize, or 'Enter' to skip:")
        while len(goals) < 3:
            choice = input(f"Enter Goal {len(goals)+1} (Press 'C' to customize, Enter to finish): ").strip()
            if choice.lower() == 'c':
                custom_goal = input("Enter your custom fitness goal: ").strip()
                if custom_goal:
                    goals.append(custom_goal)
            elif choice.isdigit() and 1 <= int(choice) <= len(preset_goals):
                goals.append(preset_goals[int(choice) - 1])
            elif choice == "":
                break  # Allows to skip and keep current if no input
            else:
                print("Invalid input. Please choose a valid number or 'C' for custom.")

        if len(goals) == 0:
            goals = current_goals  # If no new goals are entered, keep the current ones

        # Update the goals in the database
        self.update_fitness_goals(goals)

    def get_current_fitness_goals(self):
        """ Fetches current fitness goals from the database. """
        with DBManager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT goal1, goal2, goal3 FROM fitness_goals WHERE email = %s", (self.email,))
            goals = cursor.fetchone()
            return [goals['goal1'], goals['goal2'], goals['goal3']] if goals else [None, None, None]

    def update_fitness_goals(self, goals):
        """ Updates the fitness goals in the database. """
        with DBManager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fitness_goals (email, goal1, goal2, goal3)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE SET
                goal1 = EXCLUDED.goal1, goal2 = EXCLUDED.goal2, goal3 = EXCLUDED.goal3
            """, (self.email, goals[0], goals[1], goals[2]))
            conn.commit()
            print("Fitness goals updated successfully.")
            print("Redirecting back to My Dashboard...")
            time.sleep(1)
                    
    def view_fitness_achievements(self):
        """Displays the fitness achievements of the member."""
        try:
            with DBManager.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM fitness_achievements WHERE email = %s
                    """, (self.email,))
                    achievements = cursor.fetchone()

                    if not achievements:
                        print("No fitness achievements data found.")
                        return

                    print("🏅 Your Fitness Achievements 🏅")
                    print("--------------------------------")
                    attrs = {
                        'first_fitness_goal_achieved': 'First Fitness Goal Achieved',
                        'never_skipped_leg_day': 'Never Skipped Leg Day',
                        'can_do_pushup': 'Can Do Pushup',
                        'can_do_pullup': 'Can Do Pullup',
                        'can_touch_toes': 'Can Touch Toes',
                        'achieved_weight_loss_goal': 'Achieved Weight Loss Goal',
                        'achieved_muscle_gain_goal': 'Achieved Muscle Gain Goal'
                    }

                    for key, description in attrs.items():
                        status = "Achieved" if achievements[key] else "Not Achieved Yet"
                        print(f"{description}: {status}")

                    print("\n👉 Ask your trainer about how to achieve or improve your fitness goals!")
                    print("--------------------------------")

        except psycopg2.Error as e:
            print(f"An error occurred while accessing the database: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")



    def get_health_info(self):
        """Fetches health metrics from the database."""
        with DBManager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT height, weight, body_fat_percentage, resting_heart_rate FROM member_health_metrics WHERE email = %s", (self.email,))
            return cursor.fetchone()

    def show_or_edit_health_info(self):
        """Display and possibly edit health metrics."""
        while True:
            clear_screen()
            health_info = self.get_health_info()
            if not health_info:
                print("No health metrics found for this account. Please set up your health information:")
                self.edit_health_info()  # Directly go to edit if no health info found
                return

            print("====================================================")
            print("Health Metrics:")
            print("| {:<25} | {:<15} |".format("Metric", "Value"))
            print("| {:<25} | {:<15} |".format("Height (cm)", health_info.get('height', 'Not set')))
            print("| {:<25} | {:<15} |".format("Weight (kg)", health_info.get('weight', 'Not set')))
            print("| {:<25} | {:<15} |".format("Body Fat (%)", health_info.get('body_fat_percentage', 'Not set')))
            print("| {:<25} | {:<15} |".format("Resting Heart Rate", health_info.get('resting_heart_rate', 'Not set')))
            print("----------------------------------------------------")
            print("1. Edit Health Metrics")
            print("2. Return to My Dashboard")

            choice = input("Enter choice: ")
            if choice == "1":
                self.edit_health_info(health_info)
            elif choice == "2":
                return

    def edit_health_info(self, health_info=None):
        """Edits health metrics based on user input and updates them in the database."""
        if not health_info:
            health_info = {'height': None, 'weight': None, 'body_fat_percentage': None, 'resting_heart_rate': None}

        while True:
            try:
                new_height = input(f"Enter new height (cm) or press 'Enter' to keep current ({health_info.get('height', 'Not set')}): ").strip()
                new_height = float(new_height) if new_height else health_info['height']
                break
            except ValueError:
                print("Invalid input. Please enter a valid number for height.")

        while True:
            try:
                new_weight = input(f"Enter new weight (kg) or press 'Enter' to keep current ({health_info.get('weight', 'Not set')}): ").strip()
                new_weight = float(new_weight) if new_weight else health_info['weight']
                break
            except ValueError:
                print("Invalid input. Please enter a valid number for weight.")

        while True:
            try:
                new_body_fat = input(f"Enter new body fat percentage or press 'Enter' to keep current ({health_info.get('body_fat_percentage', 'Not set')}): ").strip()
                new_body_fat = float(new_body_fat) if new_body_fat else health_info['body_fat_percentage']
                break
            except ValueError:
                print("Invalid input. Please enter a valid number for body fat percentage.")

        while True:
            try:
                new_heart_rate = input(f"Enter new resting heart rate or press 'Enter' to keep current ({health_info.get('resting_heart_rate', 'Not set')}): ").strip()
                new_heart_rate = int(new_heart_rate) if new_heart_rate else health_info['resting_heart_rate']
                break
            except ValueError:
                print("Invalid input. Please enter a valid integer for resting heart rate.")

        with DBManager.connection() as conn:
            cursor = conn.cursor()
            update_query = """
                INSERT INTO member_health_metrics (email, height, weight, body_fat_percentage, resting_heart_rate)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE SET
                height = EXCLUDED.height, weight = EXCLUDED.weight, body_fat_percentage = EXCLUDED.body_fat_percentage, resting_heart_rate = EXCLUDED.resting_heart_rate
            """
            cursor.execute(update_query, (self.email, new_height, new_weight, new_body_fat, new_heart_rate))
            conn.commit()
            print("Health metrics updated successfully. Redirecting...")
            time.sleep(1)
            self.show_or_edit_health_info()


    def show_or_edit_exercise_routines(self):
        """Display and possibly edit exercise routines."""
        while True:
            clear_screen()
            routines = self.get_exercise_routines()
            if not any(routines):  # Check if all routines are unset
                print("No exercise routines found for this account. Please set up your exercise routines:")
                self.edit_exercise_routines()  # Directly go to edit if no routines found
                continue

            print("====================================================")
            print("Exercise Routines:")
            for i, routine in enumerate(routines, 1):
                print(f"Routine {i}: {routine if routine else 'Not set'}")
            print("----------------------------------------------------")
            print("1. Edit Routines")
            print("2. Return to Dashboard")

            choice = input("Enter choice: ")
            if choice == "1":
                self.edit_exercise_routines()
            elif choice == "2":
                return

    def get_exercise_routines(self):
        """Fetches current exercise routines from the database."""
        with DBManager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT routine1, routine2, routine3 FROM exercise_routines WHERE email = %s", (self.email,))
            routines = cursor.fetchone()
            return [routines['routine1'], routines['routine2'], routines['routine3']] if routines else ["", "", ""]

    def edit_exercise_routines(self):
        clear_screen()
        print("====================================================")
        """Allows the user to set or update exercise routines."""
        preset_routines = [
            "Full Body Blast", "Cardio Core Crusher", "Upper Body Burnout",
            "Lower Body Blitz", "HIIT Harder", "Strength and Stamina Circuit",
            "Legs Day Madness", "Core Chaos", "Total Body Toning", "Endurance Extreme"
        ]

        print("Edit Your Exercise Routines")
        print("You can choose from the following preset routines or enter your own:")
        for index, routine in enumerate(preset_routines, 1):
            print(f"{index}. {routine}")

        new_routines = []
        print("\nChoose up to 3 routines by number or enter your own. Press 'Enter' to finish.")
        
        while len(new_routines) < 3:
            choice = input(f"Enter Routine {len(new_routines)+1} (Press 'C' to customize): ").strip()
            if choice.lower() == 'c':
                custom_routine = input("Enter your custom exercise routine: ").strip()
                if custom_routine:
                    new_routines.append(custom_routine)
            elif choice.isdigit() and 1 <= int(choice) <= len(preset_routines):
                new_routines.append(preset_routines[int(choice) - 1])
            elif choice == "":
                if len(new_routines) == 0:
                    print("You must choose at least one routine.")
                    continue
                break
            else:
                print("Invalid input. Please choose a valid number or 'C' for custom.")

        # Updating the database with new routines
        with DBManager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO exercise_routines (email, routine1, routine2, routine3) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE SET
                routine1 = EXCLUDED.routine1, routine2 = EXCLUDED.routine2, routine3 = EXCLUDED.routine3
            """, (self.email, new_routines[0] if len(new_routines) > 0 else None, 
                new_routines[1] if len(new_routines) > 1 else None, 
                new_routines[2] if len(new_routines) > 2 else None))
            conn.commit()
            print("Exercise routines updated successfully.")
            time.sleep(1)

    @staticmethod
    def view_fitness_achievements(email):
        if not isinstance(email, str):
            print("Invalid email type. Email must be a string.")
            return
        
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("SELECT * FROM fitness_achievements WHERE email = %s", (email,))
                    achievements = cursor.fetchone()
                    if achievements:
                        print("Fitness Achievements:")
                        print("| {:<30} | {:<10} |".format("Achievement", "Status"))
                        for key, value in achievements.items():
                            print("| {:<30} | {:<10} |".format(key, 'Yes' if value else 'No'))
                    else:
                        print("No fitness achievements found for the provided email. Ask a trainer for more information!")
                        time.sleep(1)
                except psycopg2.Error as e:
                    print(f"Failed to retrieve fitness achievements. Error: {e}")


    def show_or_edit_health_stats(self):
        """ Display and possibly edit health statistics. """
        while True:
            clear_screen()
            health_stats = self.get_health_stats()

            if not health_stats:
                print("No health statistics found for your account.")
                print("Please set up your health information:")
                self.edit_health_stats(self.email)  # Directly go to edit if no stats found
                return

            print("====================================================")
            print("Health Statistics:")
            print("| {:<15} | {:<10} |".format("Metric", "Value"))
            for key, value in health_stats.items():
                print("| {:<15} | {:<10} |".format(key.capitalize(), value))
            print("----------------------------------------------------")
            print("1. Edit Health Statistics")
            print("2. Return to Dashboard")

            choice = input("Enter choice: ")
            if choice == "1":
                self.edit_health_stats(self.email)
            elif choice == "2":
                return

    def get_health_stats(self):
        """ Fetches health statistics from the database. """
        with DBManager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM health_statistics WHERE email = %s", (self.email,))
            stats = cursor.fetchone()
            return {key: val for key, val in stats.items()} if stats else None

    @staticmethod
    def edit_health_stats(email):
        """ Allows a member to edit their health statistics or sets up initial stats if none exist. """
        with DBManager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM health_statistics WHERE email = %s", (email,))
            stats = cursor.fetchone()

            if not stats:
                # No stats found, initialize with default values
                print("Setting up initial health statistics for the new member.")
                default_stats = {
                    'fitness_level': 1,  # Beginner
                    'strength': 1,
                    'flexibility': 1,
                    'endurance': 1,
                    'stamina': 1,
                    'Have water?': False,
                    'Have protein?': False,
                    'Injured?': False
                }
                cursor.execute("""
                    INSERT INTO health_statistics (email, fitness_level, strength, flexibility, endurance, stamina, has_water, has_protein, is_injured)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (email, *default_stats.values()))
                conn.commit()
                print("Initial health statistics have been set up.")
                time.sleep(1)
                return
            else:
                print("Your current stats:")
                print("| {:<15} | {:^10} |".format("Metric", "Value"))
                for key, value in stats.items():
                    print("| {:<15} | {:^10} |".format(key.capitalize(), value))

            metrics_info = {
                'fitness_level': ("Fitness Level (1: Beginner, 2: Intermediate, 3: Advanced): ", range(1, 4)),
                'strength': ("Strength (1-10): ", range(1, 11)),
                'flexibility': ("Flexibility (1-10): ", range(1, 11)),
                'endurance': ("Endurance (1-10): ", range(1, 11)),
                'stamina': ("Stamina (0-10): ", range(0, 11)),
                'has_water': ("Has Water (1: Yes, 2: No): ", ['1', '2']),
                'has_protein': ("Has Protein (1: Yes, 2: No): ", ['1', '2']),
                'is_injured': ("Is Injured (1: Yes, 2: No): ", ['1', '2'])
            }

            # Edit metrics one by one
            for key, (prompt, valid_inputs) in metrics_info.items():
                while True:  # Keep asking until valid input or skip
                    new_value = input(f"{prompt} Current ({stats[key]}): ").strip()
                    if new_value == "":
                        break  # Allow skipping
                    if isinstance(valid_inputs, range) and new_value.isdigit() and int(new_value) in valid_inputs:
                        new_value = int(new_value)  # Convert to integer and accept
                    elif new_value in valid_inputs:
                        new_value = True if new_value == '1' else False  # Convert to boolean
                    else:
                        print("Invalid input. Please enter a valid value.")
                        continue  # Reprompt on invalid input

                    cursor.execute(f"UPDATE health_statistics SET {key} = %s WHERE email = %s", (new_value, email))
                    conn.commit()
                    stats[key] = new_value  # Update for display
                    print(f"{key.replace('_', ' ').capitalize()} updated to {new_value}.")
                    break  # Move to the next metric after successful update