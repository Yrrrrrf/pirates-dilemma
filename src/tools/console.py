

# create some lambda functions to add some asqii format

# styles
bold = lambda text: f"\033[1m{text}\033[0m"
italic = lambda text: f"\033[3m{text}\033[0m"
underline = lambda text: f"\033[4m{text}\033[0m"
strike = lambda text: f"\033[9m{text}\033[0m"

# colors
black = lambda text: f"\033[30m{text}\033[0m"
red = lambda text: f"\033[31m{text}\033[0m"
green = lambda text: f"\033[32m{text}\033[0m"
yellow = lambda text: f"\033[33m{text}\033[0m"
blue = lambda text: f"\033[34m{text}\033[0m"
magenta = lambda text: f"\033[35m{text}\033[0m"
cyan = lambda text: f"\033[36m{text}\033[0m"
white = lambda text: f"\033[37m{text}\033[0m"
gray = lambda text: f"\033[90m{text}\033[0m"

# background colors
bg_black = lambda text: f"\033[40m{text}\033[0m"
bg_red = lambda text: f"\033[41m{text}\033[0m"
bg_green = lambda text: f"\033[42m{text}\033[0m"
bg_yellow = lambda text: f"\033[43m{text}\033[0m"
bg_blue = lambda text: f"\033[44m{text}\033[0m"
bg_magenta = lambda text: f"\033[45m{text}\033[0m"
bg_cyan = lambda text: f"\033[46m{text}\033[0m"
bg_white = lambda text: f"\033[47m{text}\033[0m"

# text decorations
reset = lambda text: f"\033[0m{text}\033[0m"
clear = lambda text: f"\033[2J{text}\033[0m"
# clear_line = lambda text: f"\033[2K{text}\033[0m"
# save_cursor = lambda text: f"\033[s{text}\033[0m"
# restore_cursor = lambda text: f"\033[u{text}\033[0m"
# hide_cursor = lambda text: f"\033[?25l{text}\033[0m"
# show_cursor = lambda text: f"\033[?25h{text}\033[0m"

