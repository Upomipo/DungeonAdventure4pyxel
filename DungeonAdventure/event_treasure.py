# event_treasure.py

from simple_dialog_ui import SimpleDialog

from game_log import battle_log
import attack
from sin_system import get_sin_modifier

# import attack

# ダイアログを保持して、描画用にも外部公開（mainから描画できるように）
dialog = None
treasure_obj = None

def trigger_treasure_event(obj):
    global dialog, treasure_obj
    treasure_obj = obj  # ← update() 側で参照できるように保存！
    dialog = SimpleDialog(
        f"{treasure_obj['name']} を入手しますか？",
        ["はい", "いいえ"],
        # face_info={"img": 2, "u": 0, "v": 0, "w": 16, "h": 16}
    )

def update(player):
    global dialog, treasure_obj
    if not dialog:
        return

    if dialog.active:
        dialog.update()
    elif dialog.result:
        if dialog.result == "はい":
            if treasure_obj["type"] == "weapon":
                attack.player_attack = treasure_obj["attack_obj"]  # ← グローバル変数を切り替え！
                # attack.player.gain_weapon(treasure_obj["attack_name"],treasure_obj["attack_obj"])
                battle_log.add_log(f"{treasure_obj['name']} を装備した！")
            elif treasure_obj["type"] == "item":
                if treasure_obj["name"] == "憤怒の結晶":
                    player.max_hp += 5
                    battle_log.add_log(f"{treasure_obj['name']} を自らの力に変えた")
                elif treasure_obj["name"] == "傲慢の欠片":
                    player.max_hp += 5
                    battle_log.add_log(f"{treasure_obj['name']} を自らの力に変えた")
                elif treasure_obj["name"] == "ポーション":
                    healing_boost = get_sin_modifier("怠惰", "healing_effect")
                    heal_amount = int(10 * healing_boost)
                    player.hp += min(player.max_hp, player.hp + heal_amount)
                    if player.hp > player.max_hp:
                        player.hp = player.max_hp
                    battle_log.add_log(f"{treasure_obj['name']} を使用した！")
                elif treasure_obj["name"] == "秘伝の書":
                    key_list = player.attacks.keys()
                    for key in key_list:
                        player.attacks[key].add_exp(10)
                    battle_log.add_log(f"{treasure_obj['name']} を使用した！")
                elif treasure_obj["name"] == "精神の欠片":
                    player.money += 5
                elif treasure_obj["name"] == "精神の結晶":
                    player.money += 10
                elif treasure_obj["name"] == "精神の塊":
                    player.money += 20

                # attack.player_attack = treasure_obj["attack_obj"]  # ← グローバル変数を切り替え！
                # battle_log.add_log(f"{treasure_obj['name']} を装備した！")
            # 他のタイプにも分岐可能（item, key など）
        dialog = None
        treasure_obj = None
