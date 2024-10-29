class CallbackManager:
    def __init__(self):
        self.value = 0
        self.callbacks = []

    def register_callback(self, callback):
        """注册回调函数"""
        if callable(callback):
            self.callbacks.append(callback)
        else:
            raise ValueError("Callback must be callable")

    def update_value(self, new_value):
        """更新数值并执行所有回调函数"""
        self.value = new_value
        self.execute_callbacks()

    def execute_callbacks(self):
        """执行所有已注册的回调函数"""
        for callback in self.callbacks:
            callback()

# 示例回调函数
def my_callback():
    print(f"Value updated to:")

def another_callback():
    print(f"Another callback received value:")

# 使用示例
manager = CallbackManager()
manager.register_callback(my_callback)
manager.register_callback(another_callback)

# 更新值，触发回调
manager.update_value(10)
manager.update_value(20)
