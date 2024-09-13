# main.py

import sys
from colorama import init, Fore
from player import Player
from world import World
from game_engine import GameEngine
from llm_interface import interpret_command
from utils import display_separator, colored_text

def main():
    init(autoreset=True)

    # Scenario selection
    print(colored_text("🌟 Welcome to the Adventure Game! 🌟", Fore.CYAN))
    print("Please select a scenario:")
    print("1. The Lost Heir of Eldoria")
    print("2. The Shadows Over Ravenswood")
    print("3. The Clockwork City of Aetherion")

    scenario_choice = None
    while scenario_choice not in ['1', '2', '3']:
        scenario_choice = input("Enter the number of your choice: ").strip()

    scenario_files = {
        '1': 'scenarios/scenario1.json',
        '2': 'scenarios/scenario2.json',
        '3': 'scenarios/scenario3.json'
    }

    starting_locations = {
        '1': 'village_square',
        '2': 'ravenswood_entrance',
        '3': 'airship_docks'
    }

    scenario_file = scenario_files[scenario_choice]
    starting_location = starting_locations[scenario_choice]

    player = Player(starting_location=starting_location)
    world = World(scenario_file)
    game_engine = GameEngine(player, world)

    while True:
        try:
            game_engine.display_screen()
            command = input().strip()
            time_of_day = game_engine.get_time_of_day()
            action_response = interpret_command(command, player, world, time_of_day)
            game_engine.handle_action(action_response)
            game_engine.advance_time()
        except KeyboardInterrupt:
            print("\nThanks for playing!")
            sys.exit()
        except Exception as e:
            print("An unexpected error occurred.")
            print(str(e))

if __name__ == "__main__":
    main()

