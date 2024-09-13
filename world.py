# world.py

import json

class World:
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.world_data = json.load(f)
        self.notes = []
        self.filename = filename  # Store the filename for saving changes

    def get_location(self, location_name):
        return self.world_data["locations"].get(location_name, None)

    def update_world(self, updates, current_location):
        # Process updates from the LLM
        if not updates:
            return

        # Update exits in the current location
        new_exits = updates.get("new_exits", {})
        if new_exits:
            self.world_data["locations"][current_location]["exits"].update(new_exits)

        # Add new locations
        new_locations = updates.get("new_locations", {})
        if new_locations:
            self.world_data["locations"].update(new_locations)

        # Add new items to locations
        new_items = updates.get("new_items", {})
        for loc, items in new_items.items():
            if loc in self.world_data["locations"]:
                self.world_data["locations"][loc]["items"].extend(items)
            else:
                # If the location doesn't exist, create it
                self.world_data["locations"][loc] = {
                    "description": "An unexplored area.",
                    "exits": {},
                    "items": items,
                    "npcs": [],
                    "monsters": []
                }

        # Add new NPCs to locations
        new_npcs = updates.get("new_npcs", {})
        for loc, npcs in new_npcs.items():
            if loc in self.world_data["locations"]:
                self.world_data["locations"][loc]["npcs"].extend(npcs)
            else:
                self.world_data["locations"][loc] = {
                    "description": "An unexplored area.",
                    "exits": {},
                    "items": [],
                    "npcs": npcs,
                    "monsters": []
                }

        # Add new monsters to locations
        new_monsters = updates.get("new_monsters", {})
        for loc, monsters in new_monsters.items():
            if loc in self.world_data["locations"]:
                self.world_data["locations"][loc]["monsters"].extend(monsters)
            else:
                self.world_data["locations"][loc] = {
                    "description": "An unexplored area.",
                    "exits": {},
                    "items": [],
                    "npcs": [],
                    "monsters": monsters
                }

        # Add world notes
        new_notes = updates.get("notes", [])
        self.notes.extend(new_notes)

        # Optionally, save the updated world data to the JSON file
        # self.save_world()

    def get_world_notes(self):
        return self.notes

    def save_world(self):
        with open(self.filename, 'w') as f:
            json.dump(self.world_data, f, indent=2)

