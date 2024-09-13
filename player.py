# player.py

class Player:
    def __init__(self, starting_location):
        self.name = "Hero"
        self.location = starting_location
        self.health = 100
        self.max_health = 100
        self.strength = 10
        self.agility = 10
        self.intelligence = 10
        self.experience = 0
        self.level = 1
        self.inventory = []
        self.effects = []

    def display_stats(self):
        effects = ', '.join(self.effects) if self.effects else 'None'
        stats = f"""
👤 {self.name} | 🏅 Level: {self.level} | ❤️ Health: {self.health}/{self.max_health}
💪 Strength: {self.strength} | 🏃 Agility: {self.agility} | 🧠 Intelligence: {self.intelligence}
🌀 Effects: {effects}
"""
        return stats

    def display_inventory(self):
        inventory = ', '.join(self.inventory) if self.inventory else 'Empty'
        return f"🎒 Inventory: {inventory}"

