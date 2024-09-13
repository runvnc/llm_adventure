# llm_interface.py

import openai
import os
import json

openai.api_key = os.getenv('OPENAI_API_KEY')

def interpret_command(command, player, world, time_of_day):
    prompt = f"""
You are an interpreter for a text-based adventure game.

Player State:
- Location: {player.location}
- Health: {player.health}/{player.max_health}
- Effects: {', '.join(player.effects) if player.effects else 'None'}
- Inventory: {', '.join(player.inventory) if player.inventory else 'Empty'}
- Time of Day: {time_of_day}
- Notes: {', '.join(world.notes) if world.notes else 'None'}

Available Actions:
- move [direction]
- look
- attack [monster]
- take [item]
- drop [item]
- use [item]
- inventory
- stats
- explore
- examine [object]
- effects

Game Data:
- Current Location Description: {world.get_location(player.location)['description']}
- Exits: {', '.join(world.get_location(player.location)['exits'].keys())}
- Items at Location: {', '.join(world.get_location(player.location)['items'])}
- Monsters at Location: {', '.join(world.get_location(player.location)['monsters'])}
- NPCs at Location: {', '.join(world.get_location(player.location)['npcs'])}
- World Notes: {world.get_world_notes()}

Instruction:
Interpret the player's command: "{command}"

If appropriate, you may suggest updates to the game world, such as adding new locations, items, NPCs, or events that enhance the storytelling and engagement.

Respond with a JSON object in the format:
{{
  "action": "action_name",
  "details": {{}},
  "response": "Text to display to the player.",
  "state_changes": {{}},
  "world_updates": {{}}
}}

- "action": One of the available actions or "unknown_command".
- "details": Any additional details needed for the action.
- "response": A descriptive response to the player's command.
- "state_changes": Any changes to the player's state (e.g., health reduction, added effects).
- "world_updates": Any changes to the game world (e.g., new locations, items, NPCs).

Examples:
- If the player explores and discovers a hidden path:
{{
  "action": "explore",
  "details": {{}},
  "response": "While exploring, you discover a hidden path leading east.",
  "state_changes": {{}},
  "world_updates": {{
    "new_exits": {{"east": "hidden_path"}},
    "new_locations": {{
      "hidden_path": {{
        "description": "A narrow, winding path that seems seldom traveled.",
        "exits": {{"west": "{player.location}"}},
        "items": [],
        "npcs": [],
        "monsters": ["shadow_beast"]
      }}
    }}
  }}
}}

Now, interpret the player's command.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        assistant_message = response['choices'][0]['message']['content']
        action_response = json.loads(assistant_message)
        return action_response
    except Exception as e:
        print("An error occurred while interpreting your command.")
        print(str(e))
        return {
            "action": "unknown_command",
            "details": {},
            "response": "I don't understand that command.",
            "state_changes": {},
            "world_updates": {}
        }

