from blessed import Terminal
from inquirer.themes import Theme

term = Terminal()

class custom_style(Theme):
    def __init__(self):
        super().__init__()
        self.Question.mark_color = term.darkorange + term.bold
        self.Question.brackets_color = term.darkorange + term.bold
        self.Question.default_color = term.darkorange + term.bold
        self.Checkbox.selection_color = term.lightskyblue4
        self.Checkbox.selection_icon = "❯"
        self.Checkbox.selected_icon = "◉"
        self.Checkbox.selected_color = term.lightskyblue4
        self.Checkbox.unselected_color = term.normal
        self.Checkbox.unselected_icon = "◯"
        self.List.selection_color = term.lightskyblue4
        self.List.selection_cursor = "❯"
        self.List.unselected_color = term.normal
        self.Editor.opening_prompt_color = term.lightskyblue4
