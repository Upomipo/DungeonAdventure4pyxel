import random

import pyxel
from game_log import battle_log
from sin_system import get_sin_modifier
from util import check_collision


class DropItem:
    """敵のアイテムドロップを管理するクラス"""
    def __init__(self):
        # ドロップテーブルの定義
        self.drop_table = {
            "bat": [
                {"アイテム": "ポーション", "ドロップ率": 0.1},
            ],
            "skeleton": [
                {"アイテム": "精神の欠片", "ドロップ率": 0.3},
                {"アイテム": "ポーション", "ドロップ率": 0.2},
                {"アイテム": "エリクサー", "ドロップ率": 0.1},
                {"アイテム": "秘伝の書", "ドロップ率": 0.1},
            ],
            "ghost": [
                {"アイテム": "精神の欠片", "ドロップ率": 0.3},
                {"アイテム": "ポーション", "ドロップ率": 0.2},
                {"アイテム": "エリクサー", "ドロップ率": 0.1},
            ],
            "orc": [
                {"アイテム": "精神の結晶", "ドロップ率": 0.2},
                {"アイテム": "ポーション", "ドロップ率": 0.2},
                {"アイテム": "エリクサー", "ドロップ率": 0.1},
                {"アイテム": "秘伝の書", "ドロップ率": 0.1},
            ],
            "spider": [
                {"アイテム": "精神の結晶", "ドロップ率": 0.2},
                {"アイテム": "ポーション", "ドロップ率": 0.2},
                {"アイテム": "エリクサー", "ドロップ率": 0.1},
            ],
            "spector": [
                {"アイテム": "精神の塊", "ドロップ率": 0.2},
                {"アイテム": "ポーション", "ドロップ率": 0.2},
                {"アイテム": "エリクサー", "ドロップ率": 0.1},
                {"アイテム": "秘伝の書", "ドロップ率": 0.1},
            ],
            "rich": [
                {"アイテム": "精神の塊", "ドロップ率": 0.2},
                {"アイテム": "ポーション", "ドロップ率": 0.2},
                {"アイテム": "エリクサー", "ドロップ率": 0.1},
                {"アイテム": "秘伝の書", "ドロップ率": 0.1},
            ],
            "dragon": [
                {"アイテム": "エリクサー", "ドロップ率": 0.2},
            ],
        }
        self.items = []  # ドロップしたアイテムを管理するリスト
        self.get_effect_items = []

    def clear_item(self):
        self.items.clear()

    def get_drop(self, enemy_type, x, y):
        """敵の種類に応じたドロップアイテムを決定し、アイテムリストに追加"""
        items = self.drop_table.get(enemy_type, [])
        roll = random.random()
        cumulative = 0.0
        greed_boost = get_sin_modifier("強欲", "item_drop_rate")

        for item in items:
            cumulative += (item["ドロップ率"]*greed_boost)
            if roll < cumulative:
                self.items.append({"x": x, "y": y, "name": item["アイテム"]})
                return

    def apply_effect(self, name, player):

        healing_boost = get_sin_modifier("怠惰", "healing_effect")

        if name == "ポーション":
            heal_amount = int(3 * healing_boost)
            player.hp = min(player.max_hp, player.hp + heal_amount)
            battle_log.add_log(f"{name}を使用した")
            pyxel.play(3, 6)
        elif name == "エリクサー":
            heal_amount = int(10 * healing_boost)
            player.hp = min(player.max_hp, player.hp + heal_amount)
            pyxel.play(3, 6)
            battle_log.add_log(f"{name}を使用した")
        elif name == "秘伝の書":
            key_list = player.attacks.keys()
            for key in key_list:
                player.attacks[key].add_exp(5)
            pyxel.play(3, 6)
            battle_log.add_log(f"{name}を手に入れた")
        elif name == "精神の欠片":
            player.money += 5
            pyxel.play(3, 6)
            battle_log.add_log(f"{name}を手に入れた")
        elif name == "精神の結晶":
            player.money += 10
            pyxel.play(3, 6)
            battle_log.add_log(f"{name}を手に入れた")
        elif name == "精神の塊":
            player.money += 20
            pyxel.play(3, 6)
            battle_log.add_log(f"{name}を手に入れた")
        elif name == "深淵の真珠":
            player.max_hp += 5
            pyxel.play(3, 6)
            battle_log.add_log(f"{name}が生命力を高める")
        # 他のアイテム拡張もここで可能



    def update(self, player):
        # プレイヤーのタイル座標
        px = player.x
        py = player.y

        # 拾えるアイテムをチェック
        for item in self.items[:]:
            ix = item["x"]
            iy = item["y"]
            # if ix == px and iy == py:
            if check_collision(ix, iy, px,py):
                self.apply_effect(item["name"], player)
                self.remove_item(ix, iy)
                self.get_effect_items.append({'item': item, 'frame_count': pyxel.frame_count})

        self.get_effect_items = [
            effect_item for effect_item in self.get_effect_items
            if pyxel.frame_count - effect_item['frame_count'] <= 8
        ]
    def draw(self):
        for item in self.items:
            # item_pixel_x = item["x"] * 8 - (player_x - pyxel.width //2)
            # item_pixel_y = item["y"] * 8 - (player_y - pyxel.height)
            item_pixel_x = item["x"]
            item_pixel_y = item["y"]
            if item["name"] == "ポーション":
                pyxel.blt(item_pixel_x, item_pixel_y, 0, 0, 16, 8, 8, 0)
            elif item["name"] == "エリクサー":
                pyxel.blt(item_pixel_x, item_pixel_y, 0, 0, 24, 8, 8, 0)
            elif item["name"] == "秘伝の書":
                pyxel.blt(item_pixel_x, item_pixel_y, 0, 8, 16, 8, 8, 0)
            elif item["name"] == "精神の欠片":
                pyxel.blt(item_pixel_x, item_pixel_y, 0, 8, 24, 8, 8, 0)
            elif item["name"] == "精神の結晶":
                pyxel.blt(item_pixel_x, item_pixel_y, 0, 8, 24, 8, 8, 0)
            elif item["name"] == "精神の塊":
                pyxel.blt(item_pixel_x, item_pixel_y, 0, 8, 24, 8, 8, 0)
            elif item["name"] == "深淵の真珠":
                pyxel.blt(item_pixel_x, item_pixel_y, 0, 40, 16, 8, 8, 0)

        draw_frame_count = pyxel.frame_count
        for effect_item in self.get_effect_items:
            item_pixel_x = effect_item['item']["x"]
            item_pixel_y = effect_item['item']["y"]
            draw_offset = draw_frame_count - effect_item['frame_count']
            # if draw_offset % 2 == 0:
            #     continue
            if effect_item['item']["name"] == "ポーション":
                pyxel.blt(item_pixel_x, item_pixel_y-draw_offset, 0, 0, 16, 8, 8, 0)
            elif effect_item['item']["name"] == "エリクサー":
                pyxel.blt(item_pixel_x, item_pixel_y-draw_offset, 0, 0, 24, 8, 8, 0)
            elif effect_item['item']["name"] == "秘伝の書":
                pyxel.blt(item_pixel_x, item_pixel_y-draw_offset, 0, 8, 16, 8, 8, 0)
            elif effect_item['item']["name"] == "精神の欠片":
                pyxel.blt(item_pixel_x, item_pixel_y-draw_offset, 0, 8, 24, 8, 8, 0)
            elif effect_item['item']["name"] == "精神の結晶":
                pyxel.blt(item_pixel_x, item_pixel_y-draw_offset, 0, 8, 24, 8, 8, 0)
            elif effect_item['item']["name"] == "精神の塊":
                pyxel.blt(item_pixel_x, item_pixel_y-draw_offset, 0, 8, 24, 8, 8, 0)
            elif effect_item['item']["name"] == "深淵の真珠":
                pyxel.blt(item_pixel_x, item_pixel_y-draw_offset, 0, 40, 16, 8, 8, 0)


    def remove_item(self, x, y):
        """指定された座標にあるアイテムを削除"""
        self.items = [item for item in self.items if not (item["x"] == x and item["y"] == y)]
