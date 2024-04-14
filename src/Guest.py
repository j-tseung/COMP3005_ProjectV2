import sys
import getpass
from datetime import datetime
import bcrypt
from ClearScreen import clear_screen

from DatabaseManager import DBManager
from Member import Member
from Fitness import Fitness
import psycopg2
import time

class Guest:

    @staticmethod
    def menu():
        while True:
            clear_screen()
            print("====================================================")
            print("Guest Menu")
            print("1. About Us")
            print("2. Create Account")
            print("3. 1-Day Pass")
            print("4. Go back to Main Menu")
            print("5. Exit")

            choice = input("Choose an option: ")

            if choice == "1":
                Guest.about_us()
            elif choice == "2":
                Guest.create_account()
            elif choice == "3":
                Fitness.go_to_gym("guest")
            elif choice == "4":
                return  # Return to main menu
            elif choice == "5":
                print("Thank you for visiting us! We hope to see you again soon.")
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")

    @staticmethod
    def about_us():
        clear_screen()
        print("====================================================")
        print("About Us")
        about_us_text = """
        At Pain to Progress Health and Fitness Club, we understand the journey from struggle to strength. 
        We believe that true growth often comes from overcoming challenges and pushing past limitations. 
        Our mission is to provide a tough and grueling environment where individuals can transform 
        their pain into progress, both physically and mentally. Please give me a good grade :)
        """
        print(about_us_text)
        input("\nPress Enter to continue...")

    @staticmethod
    def create_account():
        clear_screen()
        print("====================================================")
        print("Creating New Account")

        email = input("Enter your email: ")
        if email == "admin" or email == "guest":
            print("Invalid email. Please use a different email.")
        password = getpass.getpass("Enter your password: ")
        name = input("Full Name: ")

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insert the new member and their health metrics into the database
        with DBManager.connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(
                        "INSERT INTO member_accounts (email, password, name) VALUES (%s, %s, %s)",
                        (email, hashed_password, name)
                    )
                    conn.commit()
                    print("Account created successfully! Please log in with your new account as a Member.")
                    time.sleep(1)
                    Member.log_in()
                    # return # back to main menu
                except psycopg2.Error as e:
                    conn.rollback()
                    if e.pgcode == '23505':  # Unique violation
                        print("An account with this email already exists.")
                        time.sleep(1)
                    else:
                        print(e)
                        print("Failed to create an account due to a database error.")
                        time.sleep(1)
                finally:
                    cursor.close()


    @staticmethod
    def get_health_metrics():
        age = Guest.get_valid_integer("Age: ")
        fitness_levels = ['Beginner', 'Intermediate', 'Advanced']
        fitness_level = Guest.choose_option("Fitness Level", fitness_levels)
        additional_health_info = input("Any additional health information (leave blank if none): ")
        return age, fitness_level, additional_health_info

    @staticmethod
    def get_valid_integer(prompt):
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Please enter a valid integer.")

    @staticmethod
    def choose_option(prompt, options):
        for index, option in enumerate(options, 1):
            print(f"{index}. {option}")
        while True:
            choice = input(f"Select {prompt} (1-{len(options)}): ")
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                return options[int(choice) - 1]
            print("Invalid choice. Please try again.")
