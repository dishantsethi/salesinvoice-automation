import os
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    RED = '\033[91m'

def print_bold_warning(txt):
    os.system('')
    print(Colors.BOLD + Colors.WARNING + str(txt) + Colors.RESET)

def print_bold_blue(txt):
    os.system('')
    print(Colors.BOLD + Colors.OKBLUE + str(txt) + Colors.RESET)

def print_bold_red(txt):
    os.system('')
    print(Colors.BOLD + Colors.RED + str(txt) + Colors.RESET)

def print_bold_header(txt):
    os.system('')
    print(Colors.BOLD + Colors.HEADER + str(txt) + Colors.RESET)

def print_bold_green(txt):
    os.system('')
    print(Colors.BOLD + Colors.OKGREEN + str(txt) + Colors.RESET)