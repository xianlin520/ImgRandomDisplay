from app.init_var import InitVar


class OptionsController:
    def __init__(self, view):
        self.view = view
        self.root = view.root

    def update_display_option(self, value):
        """更新数值并执行所有回调函数"""
        InitVar.options = value

