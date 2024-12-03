"""Main module for Pirate's Dilemma"""
from project.settings.constants import GameInfo  # import global variables
from app import App  # import app
from project import app_data  # import app data


def main() -> None:
    app_dt()  # print app data
    app: App = App(app_data=app_data)  # create app instance
    app.run() # run app

def app_dt() -> None:
    print("\033[2J\033[1;1H", end="")  # clear terminal
    print(f"\033[92m{GameInfo.NAME}\033[0m", end=" ")  # print n puzzle solver in green
    print(f"\033[97m{GameInfo.VERSION}\033[0m", end="\n\n")  # print version in white


if __name__ == "__main__":
    main()  # * If the script is run directly, run the main function
