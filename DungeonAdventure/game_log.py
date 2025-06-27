from collections import deque

class BattleLog:
    def __init__(self, max_logs=5):
        self.logs = deque(maxlen=max_logs)  # 最大ログ数を設定

    def add_log(self, message):
        self.logs.append(message)

    def clear_logs(self):
        self.logs.clear()


battle_log = BattleLog(max_logs=5)
