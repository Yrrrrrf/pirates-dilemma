"""
Main module for Pirate's Dilemma

Date: Friday 09/08/2024
"""

#? Imports ------------------------------------------------------------------------------------

from globals import *  # import global variables
from components.app import App  # import app

#? Logic --------------------------------------------------------------------------------------
 

def main() -> None:
    """
    Application entry point. 

    It is also responsible for setting up the logging system and configuring it.
    """
    # Once created, the app will run until the user closes the window
    app: App = App()  # create app instance
    app.run() # run app


if __name__ == "__main__":
    """
    This is the entry point of the application.m
    Clean the terminal and print app data before running the main function.
    """
    print("\033[2J\033[1;1H", end="")  # clear terminal
    print(f"\033[92m{GameInfo.name}\033[0m", end=" ")  # print n puzzle solver in green
    print(f"\033[97m{GameInfo.version}\033[0m", end="\n\n")  # print version in white

    main()  # run main function
