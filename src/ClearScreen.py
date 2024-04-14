"""
The clear_screen function is a utility to clear the console screen across different operating systems.
This function enhances user experience by providing a clear visual context when navigating through various menus in the command-line interface of the fitness club management system.

Key Functionalities:
- Utilizes the 'os' module to send the appropriate command to the console depending on the operating system (Windows or Unix-based systems).
"""

import os

def clear_screen():
    # Clear the console screen
    os.system('cls' if os.name == 'nt' else 'clear')