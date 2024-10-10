import os


def clear_console():
    # Check the platform and run the appropriate clear command
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For macOS and Linux
        os.system('clear')
