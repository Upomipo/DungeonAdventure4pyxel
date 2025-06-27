import random

import pyxel


class DropItem:
    """敵のアイテムドロップを管理するクラス"""
    def __init__(self):
        # ドロップテーブルの定義
        self.drop_table = {
            "Bat": [
                {"アイテム": "ポーション", "ドロップ率": 0.1},
            ],
            "Skeleton": [
                {"アイテム": "ポーション", "ドロップ率": 0.3},
                {"アイテム": "エリクサー", "ドロップ率": 0.1},
            ],
        }
        self.items = []  # ドロップしたアイテムを管理するリスト

    def get_drop(self, enemy_type, x, y):
        """敵の種類に応じたドロップアイテムを決定し、アイテムリストに追加"""
        items = self.drop_table.get(enemy_type, [])
        roll = random.random()
        cumulative = 0.0
        for item in items:
            cumulative += item["ドロップ率"]
            if roll < cumulative:
                self.items.append({"x": x, "y": y, "name": item["アイテム"]})
                return

    def draw(self, player_x, player_y):
        for item in self.items:
            item_pixel_x = item["x"] * 8 - (player_x - 32)
            item_pixel_y = item["y"] * 8 - (player_y - 32)
            if item["name"] == "ポーション":
                pyxel.blt(item_pixel_x, item_pixel_y, 0, 0, 16, 8, 8, 0)
            elif item["name"] == "エリクサー":
                pyxel.blt(item_pixel_x, item_pixel_y, 0, 0, 24, 8, 8, 0)


    def remove_item(self, x, y):
        """指定された座標にあるアイテムを削除"""
        self.items = [item for item in self.items if not (item["x"] == x and item["y"] == y)]
