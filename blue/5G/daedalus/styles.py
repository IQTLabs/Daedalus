from inquirer.themes import load_theme_from_dict
# custom_style = { #get_style({
#     "separator": '#6C6C6C',
#     "questionmark": '#FF9D00 bold',
#     "selected": '#5F819D',
#     "pointer": '#FF9D00 bold',
#     #"instruction": '',  # default
#     "answer": '#5F819D bold',
#     #"question": '',
# } #, style_override=False)

custom_style = load_theme_from_dict({
    "Question": {
        "mark_color": "darkorange_bold",
        "brackets_color": "darkorange_bold",
        "default_color": "darkorange"
    },
    "Checkbox": {
        "selection_color": "bright_black",
        "selection_icon": "❯",
        "selected_icon": "◉",
        "selected_color": "bright_black",
        "unselected_color": "normal",
        "unselected_icon": "◯",
    },
    "List": {
        "selection_cursor": "❯",
        "selection_color": "lightblue",
    }
})
