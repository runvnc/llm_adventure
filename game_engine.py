# game_engine.py

from utils import colored_text, display_separator
#term
from constants import TIME_CYCLE, TIME_ADVANCE_PER_ACTION, MAX_TIME
import copy
from blessed import Terminal
term = Terminal()

class GameEngine:
    def __init__(self, player, world):
        self.player = player
        self.world = world
        self.time_index = 0  # Start at 'Morning'
        self.messages = []  # Store messages to display in the scrolling area

    def get_time_of_day(self):
        return TIME_CYCLE[self.time_index % MAX_TIME]

    def advance_time(self):
        self.time_index = (self.time_index + TIME_ADVANCE_PER_ACTION) % MAX_TIME

    def modify_description(self, description):
        time_of_day = self.get_time_of_day()
        if time_of_day == 'Night':
            return description.replace('You are', 'It is night. You are')
        elif time_of_day == 'Evening':
            return description.replace('You are', 'The sun sets as you are')
        else:
            return description

    def display_screen(self):
        print("Attempting to display game screen")
        print(f"Terminal size: {term.height}x{term.width}")
        print(f"Is terminal capable of fullscreen? {term.fullscreen()}")
        try:
            term.fullscreen()
            term.cbreak()
            print(term.home + term.clear)
            # Top section
            print(colored_text(f"🌟 Adventure Game 🌟", term.cyan))
            print(colored_text(f"⏰ Time of Day: {self.get_time_of_day()}", term.magenta))
            display_separator()

            # Left pane - Location and world details
            loc = self.world.get_location(self.player.location)
            description = self.modify_description(loc['description'])
            left_pane = f"{colored_text('📍 Location:', term.green)}\n{colored_text(description.strip(), term.green)}\n"
            if loc["items"]:
                left_pane += f"{colored_text('You see the following items:', term.yellow)}\n- " + "\n- ".join(loc["items"]) + "\n"
            if loc["monsters"]:
                left_pane += f"{colored_text('Danger! Monsters present:', term.red)}\n- " + "\n- ".join(loc["monsters"]) + "\n"
            if loc["npcs"]:
                left_pane += f"{colored_text('You see the following people:', term.blue)}\n- " + "\n- ".join(loc["npcs"]) + "\n"

            # Right pane - Player stats and inventory
            right_pane = colored_text(self.player.display_stats(), term.cyan)
            right_pane += colored_text(self.player.display_inventory(), term.cyan)

            # Layout panes
            left_width = int(term.width * 0.6)
            right_width = term.width - left_width - 1
            left_lines = left_pane.splitlines()
            right_lines = right_pane.splitlines()
            max_lines = max(len(left_lines), len(right_lines))
            for i in range(max_lines):
                left_line = left_lines[i] if i < len(left_lines) else ''
                right_line = right_lines[i] if i < len(right_lines) else ''
                print(left_line.ljust(left_width) + '|' + right_line.ljust(right_width))

            display_separator()
            print()

            if self.messages:
                print(colored_text(self.messages[-1], term.blue))
            #for msg in self.messages[-(term.height - max_lines - 10):]:  # Adjust number based on TUI size
            #    print(msg)
            
        except Exception as e:
            print(f"Error in fullscreen mode: {str(e)}")

    def handle_action(self, action_response):
        action = action_response.get("action", "unknown_command")
        details = action_response.get("details", {})
        response = action_response.get("response", "")
        state_changes = action_response.get("state_changes", {})
        world_updates = action_response.get("world_updates", {})

        # Apply state changes
        if 'health' in state_changes:
            self.player.health += state_changes['health']
            self.player.health = max(0, min(self.player.health, self.player.max_health))
            if state_changes['health'] < 0:
                self.messages.append(colored_text(f"You lost {-state_changes['health']} health.", term.red))
            elif state_changes['health'] > 0:
                self.messages.append(colored_text(f"You gained {state_changes['health']} health.", term.green))
        if 'effects' in state_changes:
            for effect in state_changes['effects']:
                if effect not in self.player.effects:
                    self.player.effects.append(effect)
                    self.messages.append(colored_text(f"You are now affected by {effect}.", term.magenta))
        if 'remove_effects' in state_changes:
            for effect in state_changes['remove_effects']:
                if effect in self.player.effects:
                    self.player.effects.remove(effect)
                    self.messages.append(colored_text(f"The effect {effect} has worn off.", term.magenta))
        if 'notes' in state_changes:
            self.world.notes.extend(state_changes['notes'])

        # Apply world updates
        if world_updates:
            self.world.update_world(world_updates, self.player.location)
            self.messages.append(colored_text("The world around you seems to change...", term.magenta))

        # Handle action
        if response:
            self.messages.append(response)

        if action == "move":
            direction = details.get("direction")
            loc = self.world.get_location(self.player.location)
            if direction in loc["exits"]:
                self.player.location = loc["exits"][direction]
                # Optionally, you can provide a description of the new location
                new_loc = self.world.get_location(self.player.location)
                new_description = self.modify_description(new_loc['description'])
                self.messages.append(colored_text(new_description.strip(), term.green))
            else:
                self.messages.append(colored_text("You can't go that way.", term.yellow))
        elif action == "attack":
            monster = details.get("monster")
            loc = self.world.get_location(self.player.location)
            if monster in loc["monsters"]:
                # Simple combat simulation
                loc["monsters"].remove(monster)
                self.player.experience += 50  # Example experience gain
                self.messages.append(colored_text(f"You have defeated the {monster}!", term.green))
                # Optionally, you can check for level up
            else:
                self.messages.append(colored_text(f"There is no {monster} here.", term.yellow))
        elif action == "take":
            item = details.get("item")
            loc = self.world.get_location(self.player.location)
            if item in loc["items"]:
                loc["items"].remove(item)
                self.player.inventory.append(item)
                self.messages.append(colored_text(f"You have taken the {item}.", term.green))
            else:
                self.messages.append(colored_text(f"There is no {item} here.", term.yellow))
        elif action == "drop":
            item = details.get("item")
            if item in self.player.inventory:
                self.player.inventory.remove(item)
                loc = self.world.get_location(self.player.location)
                loc["items"].append(item)
                self.messages.append(colored_text(f"You have dropped the {item}.", term.green))
            else:
                self.messages.append(colored_text(f"You don't have {item}.", term.yellow))
        elif action == "use":
            item = details.get("item")
            if item in self.player.inventory:
                # Implement item usage effects
                if item == "ale":
                    if "Drunk" not in self.player.effects:
                        self.player.effects.append("Drunk")
                        self.messages.append(colored_text("You drink the ale and feel a bit tipsy.", term.magenta))
                    else:
                        self.messages.append(colored_text("You're already drunk.", term.yellow))
                else:
                    self.messages.append(response)
            else:
                self.messages.append(colored_text(f"You don't have {item}.", term.yellow))
        elif action == "inventory":
            self.messages.append(colored_text(self.player.display_inventory(), term.cyan))
        elif action == "stats":
            self.messages.append(colored_text(self.player.display_stats(), term.cyan))
        elif action == "effects":
            effects = ', '.join(self.player.effects) if self.player.effects else 'None'
            self.messages.append(colored_text(f"Current Effects: {effects}", term.cyan))
        elif action == "look":
            loc = self.world.get_location(self.player.location)
            description = self.modify_description(loc['description'])
            self.messages.append(colored_text(description.strip(), term.green))
            if loc["items"]:
                self.messages.append(colored_text("You see the following items:", term.yellow))
                self.messages.append("- " + "\n- ".join(loc["items"]))
            if loc["monsters"]:
                self.messages.append(colored_text("Danger! Monsters present:", term.red))
                self.messages.append("- " + "\n- ".join(loc["monsters"]))
            if loc["npcs"]:
                self.messages.append(colored_text("You see the following people:", term.blue))
                self.messages.append("- " + "\n- ".join(loc["npcs"]))
        elif action == "explore" or action == "examine":
            # Exploration and examination are handled via the response from the LLM
            pass
        elif action == "unknown_command":
            self.messages.append(colored_text("I don't understand that command.", term.yellow))
        else:
            self.messages.append(colored_text("I don't understand that action.", term.yellow))

        # Check for player death
        if self.player.health <= 0:
            self.messages.append(colored_text("You have perished...", term.red))
            # Optionally handle game over logic
            # For now, we'll exit the game
            self.game_over()

    def game_over(self):
        self.messages.append(colored_text("Game Over", term.red))
        self.display_screen()
        # Wait for a moment before exiting
        import time
        time.sleep(2)
        exit()
