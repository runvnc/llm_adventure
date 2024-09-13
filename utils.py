# utils.py

from blessed import Terminal

term = Terminal()

def colored_text(text, color):
    return f"{color}{text}{term.normal}"

def display_separator():
    print(term.magenta("-" * term.width))

