import sys

from ClearScreen import clear_screen
from Guest import Guest
from Member import Member
from Trainer import Trainer
from Admin import Admin

def main_menu():
    
    while True:
        clear_screen()
        print("=========================================================")
        print("🔥 Welcome to Pain to Progress Health and Fitness Club!🔥")
        print("I am ...")
        print("1. a Guest")
        print("2. a Member")
        print("3. a Trainer")
        print("4. an Administrator")
        print("5. Leaving (Exit)")

        choice = input("Enter choice: ")

        if choice == "1":
            Guest.menu()
        elif choice == "2":
            Member.log_in()
        elif choice == "3":
            Trainer.log_in()
        elif choice == "4":
            Admin.log_in()
        elif choice == "5":
            print("Thank you for visiting Pain to Progress Health and Fitness Club! We hope to see you again soon.")
            sys.exit(0)
        else:
            print("Invalid choice. Please choose again.")  
          
def main():
    # Admin.add_admin_password()
    print("thonk")
    main_menu()

if __name__ == "__main__":
    main()