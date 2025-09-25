import pyxel
from util import draw_text_with_border

sins = {
    "憤怒": {"power": 0, "color": pyxel.COLOR_RED},
    "傲慢": {"power": 0, "color": pyxel.COLOR_PURPLE},
    "強欲": {"power": 0, "color": pyxel.COLOR_YELLOW},
    "色欲": {"power": 0, "color": pyxel.COLOR_PINK},
    "暴食": {"power": 0, "color": pyxel.COLOR_ORANGE},
    "嫉妬": {"power": 0, "color": pyxel.COLOR_GREEN},
    "怠惰": {"power": 0, "color": pyxel.COLOR_NAVY},  # pyxel標準色で代替
}


def draw_sins():
    # 罪の数値が高い順に並び替え
    top_sins = sorted(sins.items(), key=lambda x: x[1], reverse=True)[:3]
    for i, (sin, value) in enumerate(top_sins):
        x = 30 + i * 20
        y = 4
        # pyxel.text(x, y, sin, pyxel.COLOR_RED if value >= 5 else pyxel.COLOR_GRAY)
        draw_text_with_border(x, y, sin, pyxel.COLOR_RED if value >= 5 else pyxel.COLOR_GRAY, pyxel.COLOR_BLACK)


def draw_sin_icons():
    # print(sins)
    # 数値順に並び替えて上位3つを表示
    top_sins = sorted(sins.items(), key=lambda x: x[1]["power"], reverse=True)[:3]
    for i, (name, data) in enumerate(top_sins):
        x = 30 + i * 20
        y = 4
        if data["power"] >= 4:
            pyxel.circ(x+7, y+4, 4 + data["power"], data["color"])  # 数値に応じて肥大化
            draw_text_with_border(x, y, name, data["color"], pyxel.COLOR_BLACK)
            txt_x = 10
            txt_y = pyxel.height -40 + (i*10)
            if name == "憤怒":
                draw_text_with_border(txt_x, txt_y, "ダメージ/敵出現率アップ", data["color"], pyxel.COLOR_BLACK)
            elif name == "嫉妬":
                draw_text_with_border(txt_x, txt_y, "武器熟練度上昇値アップ", data["color"], pyxel.COLOR_BLACK)
            elif name == "傲慢":
                draw_text_with_border(txt_x, txt_y, "被ダメージ無効化率アップ", data["color"], pyxel.COLOR_BLACK)
            elif name == "強欲":
                draw_text_with_border(txt_x, txt_y, "アイテムドロップ率アップ", data["color"], pyxel.COLOR_BLACK)
            elif name == "怠惰":
                draw_text_with_border(txt_x, txt_y, "回復力アップ", data["color"], pyxel.COLOR_BLACK)
            elif name == "暴食":
                draw_text_with_border(txt_x, txt_y, "宝箱出現率アップ", data["color"], pyxel.COLOR_BLACK)
            elif name == "色欲":
                draw_text_with_border(txt_x, txt_y, "NPC出現率アップ", data["color"], pyxel.COLOR_BLACK)

        elif data["power"] > 0:
            draw_text_with_border(x, y, name, data["color"], pyxel.COLOR_BLACK)
        else:
            pass


sin_effect_map = {
    "憤怒": ["enemy_spawn_rate", "player_attack_boost"],
    "嫉妬": ["weapon_mastery_gain"],
    "傲慢": ["damage_nullify_chance"],
    "強欲": ["item_drop_rate"],
    "怠惰": ["healing_effect", "auto_heal_rate"],
    "暴食": ["chest_spawn_rate"],
    "色欲": ["npc_event_rate"],
}


def get_sin_modifier(sin_type, modifier_type):
    power = sins.get(sin_type, {}).get("power", 0)

    if modifier_type == "enemy_spawn_rate":
        return 1.0 + power * 0.02

    elif modifier_type == "player_attack_boost":
        return 1.0 + power * 0.07

    elif modifier_type == "weapon_mastery_gain":
        return 1.0 + power * 0.07

    elif modifier_type == "damage_nullify_chance":
        return min(0.5, power * 0.03)  # 最大50%でダメージ無効化

    elif modifier_type == "item_drop_rate":
        return 1.0 + power * 0.02

    elif modifier_type == "healing_effect":
        return 1.0 + power / 10

    elif modifier_type == "auto_heal_rate":
        return power * 0.01

    elif modifier_type == "chest_spawn_rate":
        return 1.0 + power * 0.055

    elif modifier_type == "npc_event_rate":
        return 1.0 + power * 0.04

    return 1.0  # デフォルト補正なし

def clear_sins():
    global sins
    sins = {
        "憤怒": {"power": 0, "color": pyxel.COLOR_RED},
        "傲慢": {"power": 0, "color": pyxel.COLOR_PURPLE},
        "強欲": {"power": 0, "color": pyxel.COLOR_YELLOW},
        "色欲": {"power": 0, "color": pyxel.COLOR_PINK},
        "暴食": {"power": 0, "color": pyxel.COLOR_ORANGE},
        "嫉妬": {"power": 0, "color": pyxel.COLOR_GREEN},
        "怠惰": {"power": 0, "color": pyxel.COLOR_NAVY},  # pyxel標準色で代替
    }
