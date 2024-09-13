# utils.py

from colorama import Fore, Style

def colored_text(text, color):
    return f"{color}{text}{Style.RESET_ALL}"

def display_separator():
    print(Fore.MAGENTA + "-" * 50)

