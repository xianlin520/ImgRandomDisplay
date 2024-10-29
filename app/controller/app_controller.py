class AppController:
    def __init__(self, view):
        self.root = view.root


    def exit_program(self, event=None):
        """
        退出程序
        """
        self.root.quit()