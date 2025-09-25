import math

# import player
import pyxel
import random

import simple_window_status_ui
from MouseDirectionControl import MouseDirectionControl
from game_log import battle_log
# from simple_dialog_ui import SimpleDialog
from constants import BGM_NONE, BGM_TITLE, BGM_DUNGEON, MODE_TITLE, MODE_SELECT, PLAYER_JOB_FIGHTER, \
    PLAYER_JOB_WIZARD, MODE_FIELD, MODE_DEAD, WEAPON_NAME_GREATSWORD, WEAPON_NAME_SLASHAXE, WEAPON_NAME_FLASHSPEAR, \
    WEAPON_NAME_BOOKOFFIRE, WEAPON_NAME_BOOKOFTHUNDER, WEAPON_NAME_BOOKOFLIGHT, WEAPON_NAME_BEAM, MODE_CAMP, \
    PLAYER_JOB_THIEF, WEAPON_NAME_KNIFE, WEAPON_NAME_ARROW, WEAPON_NAME_CRAW, WEAPON_NAME_THROWING_KNIFE
from item import DropItem
from map import create_maze, find_spawn_point_2, checkMapTile_pixel, checkMapStairs_pixel, get_treasure_simple, \
    checkMapNPC_pixel
from simple_window_status_ui import SimpleStatus, SimpleWeaponLevelUpWindow, \
    CampSceneWindow
from sin_system import sins, draw_sin_icons, get_sin_modifier, clear_sins
from sound import load_musics, play_bgm_dungeon, play_bgm_title, play_bgm_gameover, play_bgm_camp

# Web
from SimpleEnemy import SimpleEnemy
# from attack import Attack, AttackType
import attack
from SimplePlayer import SimplePlayer  # プレイヤーも軽量版
# from event_treasure import trigger_treasure_event, update as update_treasure, dialog as treasure_dialog
import event_treasure
import event_npc
from text_renderer import start_floor_flavor_display, draw_floor_flavor
from util import draw_text_with_border
import prologue

# ゲーム初期化（画面サイズ160x120）
pyxel.init(128, 228)
pyxel.load('pyxel.pyxres')
pyxel.image(1).load(0, 0, "image/dungeon1_1.png")


# 音楽ファイルの読み込み及び設定
play_sound = BGM_NONE
load_musics()

# グローバル変数
game_mode= MODE_TITLE
depth = 1
timer = 0

# グローバル変数
last_key = None
last_frame = 0
move_key = None
move_frame = 0

# キーコードと名前の対応辞書
KEY_NAME_MAP = {
    pyxel.KEY_LEFT: "KEY_LEFT",
    pyxel.KEY_RIGHT: "KEY_RIGHT",
    pyxel.KEY_UP: "KEY_UP",
    pyxel.KEY_DOWN: "KEY_DOWN",
    pyxel.KEY_SPACE: "KEY_SPACE",
    pyxel.KEY_A: "A",
    pyxel.KEY_B: "B",
    pyxel.KEY_C: "C",
    pyxel.KEY_D: "D",
    pyxel.KEY_W: "W",
    pyxel.KEY_S: "S",
    pyxel.KEY_E: "E",
    pyxel.KEY_RETURN: "ENTER",
    pyxel.KEY_SHIFT: "SHIFT",
    pyxel.MOUSE_BUTTON_LEFT: "MOUSE_LEFT",
    pyxel.GAMEPAD1_BUTTON_DPAD_LEFT: "PAD LEFT",
    pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT: "PAD RIGHT",
    pyxel.GAMEPAD1_BUTTON_DPAD_DOWN: "PAD DOWN",
    pyxel.GAMEPAD1_BUTTON_DPAD_UP: "PAD UP",
    pyxel.GAMEPAD1_BUTTON_A: "PAD A",
    pyxel.GAMEPAD1_BUTTON_B: "PAD B",
    pyxel.GAMEPAD1_BUTTON_X: "PAD X",
    pyxel.GAMEPAD1_BUTTON_Y: "PAD Y",
}


# 調べたいキー一覧
KEY_LIST = list(KEY_NAME_MAP.keys())

control = MouseDirectionControl()
mouse_drag_control = True

# Web向け
simpleplayer = SimplePlayer(64, 64, job=PLAYER_JOB_FIGHTER, speed=1)
# enemies = [SimpleEnemy(80, 60), SimpleEnemy(50, 72)]
enemies = [
    # SimpleEnemy(100, 100, "skeleton"),
    # SimpleEnemy(80, 60, "bat",target=simpleplayer),
    # SimpleEnemy(120, 80, "bat")
]

ENEMY_BY_DEPTH = {
    0: ["bat", "skeleton"],
    5: ["bat", "skeleton", "ghost"],
    10: ["orc", "ghost"],
    15: ["orc", "spider"],
    20: ["spector", "spider"],
    25: ["spector", "rich"],
    30: ["spector", "rich", "dragon"]
}

#todo 武器の一覧
# interval = 攻撃間隔
# duration = 持続フレーム数
# radius = 射程

#戦士
attack_sword = attack.Attack(simpleplayer, enemies, WEAPON_NAME_GREATSWORD , attack.AttackType.MELEE, 30, 12, math.radians(90), 32)
attack_axe = attack.Attack(simpleplayer, enemies, WEAPON_NAME_SLASHAXE, attack.AttackType.SPIN_SLASH, 50, 20, math.radians(90), 32)
attack_spire = attack.Attack(simpleplayer, enemies, WEAPON_NAME_FLASHSPEAR, attack.AttackType.PROJECTILE_RANDOM, 20, 10, math.radians(90), 50)

#魔法使い
attack_thunder = attack.Attack(simpleplayer, enemies, WEAPON_NAME_BOOKOFTHUNDER, attack.AttackType.AREA_MAGIC, 60, 15, math.radians(90), 32)
attack_light = attack.Attack(simpleplayer, enemies, WEAPON_NAME_BOOKOFLIGHT, attack.AttackType.THRUST_CROSS, 20, 30, math.radians(90), 20)
attack_getter = attack.Attack(simpleplayer, enemies, WEAPON_NAME_BEAM, attack.AttackType.BEAM, 60, 30, math.radians(90), 100)
attack_fire = attack.Attack(simpleplayer, enemies, WEAPON_NAME_BOOKOFFIRE, attack.AttackType.FAN_FIRE, 50, 40, math.radians(90), 20)

#シーフ
attack_knife = attack.Attack(simpleplayer, enemies, WEAPON_NAME_KNIFE, attack.AttackType.PROJECTILE, 12, 12, math.radians(90), 20)
attack_arrow = attack.Attack(simpleplayer, enemies, WEAPON_NAME_ARROW, attack.AttackType.PROJECTILE, 50, 12, math.radians(90), 50)
attack_craw = attack.Attack(simpleplayer, enemies, WEAPON_NAME_CRAW, attack.AttackType.MELEE, 20, 12, math.radians(90), 20)
attack_throw_knife = attack.Attack(simpleplayer, enemies, WEAPON_NAME_THROWING_KNIFE, attack.AttackType.PROJECTILE_RANDOM, 20, 12, math.radians(90), 30)


attack.player_attack = attack_sword


# job = PLAYER_JOB_FIGHTER
enemy_spawn_timer = 0

MAX_ENEMY_COUNT = 20

drop_item_manager = DropItem()

KEY_COOLDOWN = 10  # 10フレーム（約0.16秒）だけ入力間隔を空ける
key_timer = 0      # 最初は0
# dialog = None  # 最初は存在しないので None

# 共通アイテム
common_drops = [
    {"name": "精神の欠片", "type": "item"},
    {"name": "精神の結晶", "type": "item"},
    {"name": "精神の塊", "type": "item"},
    {"name": "ポーション", "type": "item"},
    {"name": "秘伝の書", "type": "item"},
]

# ジョブ別テーブル
drop_table = {
    PLAYER_JOB_FIGHTER: [
        # {"name": WEAPON_NAME_GREATSWORD, "type": "weapon", "attack_obj": attack_sword},
        # {"name": WEAPON_NAME_SLASHAXE, "type": "weapon", "attack_obj": attack_axe},
        # {"name": WEAPON_NAME_FLASHSPEAR, "type": "weapon", "attack_obj": attack_spire},
        {"name": "深淵の真珠", "type": "item"}
    ],
    PLAYER_JOB_WIZARD: [
        # {"name": WEAPON_NAME_BOOKOFFIRE, "type": "weapon", "attack_obj": attack_fire},
        # {"name": WEAPON_NAME_BOOKOFTHUNDER, "type": "weapon", "attack_obj": attack_thunder},
        # {"name": WEAPON_NAME_BOOKOFLIGHT, "type": "weapon", "attack_obj": attack_light},
        # {"name": WEAPON_NAME_BEAM, "type": "weapon", "attack_obj": attack_getter},
        {"name": "深淵の真珠", "type": "item"}
    ],
    PLAYER_JOB_THIEF: [
        # {"name": WEAPON_NAME_BOOKOFFIRE, "type": "weapon", "attack_obj": attack_fire},
        # {"name": WEAPON_NAME_BOOKOFTHUNDER, "type": "weapon", "attack_obj": attack_thunder},
        # {"name": WEAPON_NAME_BOOKOFLIGHT, "type": "weapon", "attack_obj": attack_light},
        # {"name": WEAPON_NAME_BEAM, "type": "weapon", "attack_obj": attack_getter},
        {"name": "深淵の真珠", "type": "item"}
    ]

}

simple_window_status_ui.StatusWindow = SimpleStatus(simpleplayer)
simple_window_status_ui.WeaponLevelUpWindow = SimpleWeaponLevelUpWindow(simpleplayer)
simple_window_status_ui.CampScene = CampSceneWindow(simpleplayer)


def get_treasure_drop():
    job_items = drop_table.get(simpleplayer.job, [])
    all_candidates = job_items + common_drops
    return random.choice(all_candidates) if all_candidates else None

def get_current_enemy_list():
    available_levels = sorted(ENEMY_BY_DEPTH.keys())
    for level in reversed(available_levels):
        if depth >= level:
            return ENEMY_BY_DEPTH[level]
    return ["bat"]  # デフォルト

def reset_games():
    global depth, simpleplayer, enemies
    simpleplayer.hp = simpleplayer.max_hp
    enemies.clear()
    depth = 1
    drop_item_manager.clear_item()
    clear_sins()
    attack_sword.reset()
    attack_axe.reset()
    attack_spire.reset()
    attack_fire.reset()
    attack_light.reset()
    attack_thunder.reset()
    attack_getter.reset()
    attack_knife.reset()
    attack_arrow.reset()
    attack_craw.reset()
    attack_throw_knife.reset()
    simpleplayer.reset_attacks()
    simpleplayer.money = 0

# 更新関数
def update():
    global game_mode, play_sound, last_key, last_frame, enemies, enemy_spawn_timer, depth, timer,\
    key_timer, last_key, move_key, move_frame, simpleplayer, StatusWindow, WeaponLevelUpWindow, CampScene

    move_key = None
    for key in KEY_LIST:
        if pyxel.btn(key):
            move_key = key
            move_frame = pyxel.frame_count
            # print(last_key)
            break

    last_key = None
    if key_timer > 0:
        key_timer -= 1
    else:
        for key in KEY_LIST:
            if pyxel.btn(key):
                last_key = key
                key_timer = KEY_COOLDOWN
                # 実行処理などここに
                break

    #ゲームモード：タイトル
    if game_mode== MODE_TITLE:

        if play_sound != BGM_TITLE:
            play_bgm_title()
            play_sound = BGM_TITLE
            pyxel.mouse(True)

        prologue.update()

        # if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
        if last_key == pyxel.KEY_SPACE or last_key == pyxel.MOUSE_BUTTON_LEFT:
            game_mode= MODE_SELECT

    #ゲームモード：キャラセレクト
    elif game_mode== MODE_SELECT:

        if last_key == pyxel.MOUSE_BUTTON_LEFT:
            mouse_select_x = pyxel.mouse_x
            mouse_select_y = pyxel.mouse_y
            if 15 < mouse_select_x < 100 and 7 < mouse_select_y < 29:
                simpleplayer.job = PLAYER_JOB_FIGHTER
                simpleplayer.base_v = 0
                attack.player_attack = attack_sword
                simpleplayer.gain_weapon(attack_sword.name, attack_sword)
                simpleplayer.gain_weapon(attack_spire.name, attack_spire)
                simpleplayer.gain_weapon(attack_axe.name, attack_axe)
                # simpleplayer.gain_weapon(attack.player_attack.name, attack.player_attack)
                sins["憤怒"]["power"] = 4

            elif 15 < mouse_select_x < 100 and 27 < mouse_select_y < 49:
                simpleplayer.job = PLAYER_JOB_WIZARD
                simpleplayer.base_v = 8
                attack.player_attack = attack_fire
                simpleplayer.gain_weapon(attack_fire.name, attack_fire)
                simpleplayer.gain_weapon(attack_light.name, attack_light)
                simpleplayer.gain_weapon(attack_thunder.name, attack_thunder)
                simpleplayer.gain_weapon(attack_getter.name, attack_getter)
                sins["傲慢"]["power"] = 4

            elif 15 < mouse_select_x < 100 and 47 < mouse_select_y < 69:
                simpleplayer.job = PLAYER_JOB_THIEF
                simpleplayer.base_v = 16
                # simpleplayer.speed = 2
                attack.player_attack = attack_knife
                attack.player_attack_sub = attack_arrow
                simpleplayer.gain_weapon(attack_knife.name, attack_knife)
                simpleplayer.gain_weapon(attack_arrow.name, attack_arrow)
                simpleplayer.gain_weapon(attack_craw.name, attack_craw)
                simpleplayer.gain_weapon(attack_throw_knife.name, attack_throw_knife)
                sins["強欲"]["power"] = 4

            game_mode = MODE_FIELD
            create_maze()
            s_x, s_y = find_spawn_point_2()
            simpleplayer.x = s_x * simpleplayer.size
            simpleplayer.y = s_y * simpleplayer.size
            if play_sound != BGM_DUNGEON:
                play_bgm_dungeon()
                play_sound = BGM_DUNGEON
            # start_floor_flavor_display(depth)

    #ゲームモード：フィールド
    elif game_mode== MODE_FIELD:

        event_treasure.update(simpleplayer)
        event_npc.update(sins)
        if event_treasure.dialog and event_treasure.dialog.active:
            return
        if event_npc.dialog_npc and event_npc.dialog_npc.active:
            return

        simple_window_status_ui.StatusWindow.update()
        if simple_window_status_ui.StatusWindow.active:
            return

        simple_window_status_ui.WeaponLevelUpWindow.update()
        if simple_window_status_ui.WeaponLevelUpWindow.active:
            return

        control.update(move_key)
        if move_key==pyxel.MOUSE_BUTTON_LEFT:
            center_x = pyxel.width // 2
            center_y = pyxel.height // 2

            # if 0 <= pyxel.mouse_x <= 8 and \
            #         116 <= pyxel.mouse_y <= 126:
            #     if attack.attack_type == AttackType.MELEE:
            #         attack = attack_fire
            #     elif attack.attack_type == AttackType.SHOCKWAVE:
            #         attack = attack_thunder
            #     elif attack.attack_type == AttackType.AREA_MAGIC:
            #         attack = attack_sword
            #     return

            if not mouse_drag_control:
                # マウスの位置から、主人公（画面中央）との相対位置を計算
                dx = pyxel.mouse_x - center_x
                dy = pyxel.mouse_y - center_y

                # 現在の主人公の座標に相対位置を足して、実際の移動先を算出
                target_x = simpleplayer.x + dx
                target_y = simpleplayer.y + dy

                simpleplayer.move_to(target_x, target_y)
                # print(str(pyxel.mouse_x) + ","+str(pyxel.mouse_y))
                # print(str(simpleplayer.x) + ","+str(simpleplayer.y)+ ","+str(simpleplayer.angle))
            else:
                target_x, target_y = control.get_target_position(simpleplayer.x, simpleplayer.y)
                simpleplayer.move_to(target_x, target_y)

        attack.player_attack.update(enemies)
        if attack.player_attack_sub:
            attack.player_attack_sub.update(enemies)
        simpleplayer.update()

        # ループの前に、一番近い敵の距離と角度を保持する変数を初期化
        closest_dist_sq = float('inf')
        closest_angle = None

        for e in enemies:
            e.update()
            # プレイヤーと現在の敵の距離の2乗を計算
            dist_sq = (e.x - simpleplayer.x) ** 2 + (e.y - simpleplayer.y) ** 2

            # 既存の最も近い距離よりも近ければ、情報を更新
            if dist_sq < closest_dist_sq:
                closest_dist_sq = dist_sq
                closest_angle = math.atan2(e.y - simpleplayer.y, e.x - simpleplayer.x)

        enemies = [e for e in enemies if e.is_alive()]
        # ループ終了後、最終的な角度をsimpleplayerに代入
        if closest_angle is not None:
            simpleplayer.near_enemy_angle = closest_angle

        if len(enemies) < MAX_ENEMY_COUNT:
            enemy_spawn_timer += 1
            anger_modifier = get_sin_modifier("憤怒", "enemy_spawn_rate")
            spawn_interval = max(5, int(30 / anger_modifier))  # 最小5フレーム保証

            if enemy_spawn_timer % spawn_interval == 0:
                while True:
                    enemy_types = get_current_enemy_list()
                    new_enemy = SimpleEnemy(random.randint(16, 320),
                                            random.randint(16, 200),
                                            random.choice(enemy_types),
                                            target=simpleplayer,
                                            drop_item=drop_item_manager)
                    if not checkMapTile_pixel(new_enemy.x, new_enemy.y):
                        enemies.append(new_enemy)
                        break

        #プレイヤーの死亡
        if not simpleplayer.is_alive():
            game_mode = MODE_DEAD
            play_bgm_gameover()

        #階段
        if checkMapStairs_pixel(simpleplayer.x, simpleplayer.y):
            pyxel.play(3, 5)
            create_maze()
            s_x, s_y = find_spawn_point_2()
            simpleplayer.x = s_x * simpleplayer.size
            simpleplayer.y = s_y * simpleplayer.size
            enemies.clear()
            drop_item_manager.clear_item()
            depth += 1
            # start_floor_flavor_display(depth)
            if depth % 5 == 1: # TODO デバッグ用に１へ
                game_mode = MODE_CAMP
                play_bgm_camp()
                simple_window_status_ui.CampScene.active = True


        if get_treasure_simple(simpleplayer.x, simpleplayer.y):
            # todo ここに宝箱イベントを記述。
            treasure_obj = get_treasure_drop()

            #確率で罠
            is_trap_box = random.random() < 0.0 # 罠宝箱は未実装

            if is_trap_box:
                event_treasure.trigger_treasure_event(treasure_obj)
            else:
                drop_item_manager.items.append({"x": simpleplayer.x, "y": simpleplayer.y, "name": treasure_obj['name']})
            # if treasure_obj["type"]=="weapon":
            #     simpleplayer.gain_weapon(treasure_obj["name"], treasure_obj["attack_obj"])

        if checkMapNPC_pixel(simpleplayer.x, simpleplayer.y):
            npc_event = event_npc.get_npc()
            event_npc.trigger_npc_event(npc_event)

        # event_treasure.update()

        drop_item_manager.update(simpleplayer)

        if move_key == pyxel.MOUSE_BUTTON_LEFT:
            mouse_select_x = pyxel.mouse_x
            mouse_select_y = pyxel.mouse_y
            if 0 < mouse_select_x < 20 and 10 < mouse_select_y < 20:
                simple_window_status_ui.StatusWindow.active = True

        #debug機能
        if last_key == pyxel.KEY_E:
            attack.player_attack.add_exp(10)
            print("DEBUG:"+attack.player_attack.display_name + "=" +str(attack.player_attack.exp))
        elif last_key == pyxel.KEY_A:
            treasure_obj = get_treasure_drop()
            event_treasure.trigger_treasure_event(treasure_obj)
            if treasure_obj["type"]=="weapon":
                simpleplayer.gain_weapon(treasure_obj["name"], treasure_obj["attack_obj"])
        # elif last_key == pyxel.KEY_S:
        #     simple_window_status_ui.WeaponLevelUpWindow.active = True
        elif last_key == pyxel.KEY_C:
            simpleplayer.money += 10
            print("DEBUG:"+str(simpleplayer.money))


    elif game_mode == MODE_DEAD:
        # simpleplayer.update()

        if last_key == pyxel.MOUSE_BUTTON_LEFT:
            game_mode = MODE_TITLE
            pyxel.camera(0, 0)
            reset_games()

    elif game_mode == MODE_CAMP:
        simple_window_status_ui.CampScene.update()
        if not simple_window_status_ui.CampScene.active:
            game_mode = MODE_FIELD
            play_bgm_dungeon()

# 描画関数
def draw():
    # global dialog

    pyxel.cls(0)  # 画面を黒色でクリア

    if game_mode== MODE_TITLE:
        pyxel.blt(0, 0, 1, 0, 0, 128, 128)  # 画像を表示
        pyxel.text(20, 30, "  plz hit space key   ", pyxel.frame_count % 16)  # メッセージ
        pyxel.text(20, 70, "  ver.1.30 build.4    ", pyxel.frame_count % 16)  # メッセージ
        # draw_text_with_border(20, 50, "キーをおしてください", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK, systemfont)
        prologue.draw()


    #ゲームモード：キャラセレクト
    elif game_mode== MODE_SELECT:

        # 各職業毎の描画
        pyxel.blt(20, 10, 0, 120, 0, 8, 8, 0)
        pyxel.text(20, 20, "Fighter", pyxel.COLOR_WHITE)
        # writer.draw(50, 10, "体力が高い", 8, 7)

        pyxel.blt(20, 30, 0, 120, 8, 8, 8, 0)
        pyxel.text(20, 40, "Wizard", pyxel.COLOR_WHITE)
        # writer.draw(50, 30, "魔法で離れて攻撃", 8, 7)

        pyxel.blt(20, 50, 0, 120, 16, 8, 8, 0)
        pyxel.text(20, 60, "Thief", pyxel.COLOR_WHITE)


    elif game_mode== MODE_FIELD:

        # カメラを動的に表示するエリア
        pyxel.camera(simpleplayer.x - pyxel.width // 2, simpleplayer.y - pyxel.height // 2)

        pyxel.bltm(0, 0, 0, 0, 0, 320, 200)
        simpleplayer.draw()
        for enemy in enemies:
            if enemy.is_alive():
                enemy.draw()
        attack.player_attack.draw()
        if attack.player_attack_sub:
            attack.player_attack_sub.draw()

        drop_item_manager.draw()

        # カメラを固定で表示するエリア
        pyxel.camera(0,0)
        control.draw()

        draw_sin_icons()
        if event_treasure.dialog:
            event_treasure.dialog.draw()
        if event_npc.dialog_npc:
            event_npc.dialog_npc.draw()

        # 情報の表示
        # info_base_x = simpleplayer.x - pyxel.width // 2
        # info_base_y = simpleplayer.y - pyxel.height // 2
        info_base_x = pyxel.width // 2
        info_base_y = pyxel.height // 2

        # 階層表示
        pyxel.rect(1 , 1, 20, 10, pyxel.COLOR_WHITE)
        pyxel.rect(1 +1 , 1 +1, 18, 8, pyxel.COLOR_BLACK)
        pyxel.text(1+3, 1+2, f"B{depth}F", pyxel.COLOR_WHITE)

        #status
        pyxel.rect(1, 10, 20, 10, pyxel.COLOR_BLACK)
        pyxel.rectb(1 , 10, 20, 10, pyxel.COLOR_WHITE)
        pyxel.text(1+3, 10+2, "MENU", pyxel.COLOR_WHITE)

        #お金
        pyxel.blt(1, 25, 0, 8, 24, 8, 8, 0)
        draw_text_with_border(10, 25, f":{simpleplayer.money}", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)

        base_height = 1
        base_width = pyxel.width - 20
        key_list = simpleplayer.attacks.keys()
        for key in key_list:
            pyxel.rect(base_width , base_height, 20, 13, pyxel.COLOR_WHITE)
            pyxel.rect(base_width +1 , base_height +1, 18, 11, pyxel.COLOR_BLACK)
            # level = simpleplayer.attacks[key].traits.get("強化", 0) % 5
            # level = int(simpleplayer.attacks[key].exp / 5)
            level = int(((simpleplayer.attacks[key].exp / simpleplayer.attacks[key].get_next_level_exp())*100)/5)
            if level >= 20:
                pyxel.rect(base_width + 1, base_height + 1, level, 11, pyxel.frame_count % 16)
            else:
                pyxel.rect(base_width +1 , base_height +1, level, 11, pyxel.COLOR_CYAN)
            if key == WEAPON_NAME_GREATSWORD:
                pyxel.blt(base_width +3, base_height +1, 0, 16, 40, 16, 8, 0)
            elif key== WEAPON_NAME_SLASHAXE:
                pyxel.blt(base_width +3, base_height +2, 0, 16, 32, 16, 8, 0)
            elif key== WEAPON_NAME_FLASHSPEAR:
                pyxel.blt(base_width +3, base_height +3, 0, 16, 48, 16, 8, 0)
            elif key== WEAPON_NAME_BOOKOFFIRE:
                pyxel.blt(base_width +3, base_height +3, 0, 0, 32, 8, 8, 0)
            elif key== WEAPON_NAME_BOOKOFTHUNDER:
                pyxel.blt(base_width +3, base_height +3, 0, 8, 32, 8, 8, 0)
            elif key== WEAPON_NAME_BOOKOFLIGHT:
                pyxel.blt(base_width +3, base_height +3, 0, 0, 40, 8, 8, 0)
            elif key== WEAPON_NAME_BEAM:
                pyxel.blt(base_width +3, base_height +3, 0, 8, 40, 8, 8, 0)
            elif key== WEAPON_NAME_KNIFE:
                pyxel.blt(base_width +3, base_height +3, 0, 32, 48, 8, 8, 0)
            elif key== WEAPON_NAME_ARROW:
                pyxel.blt(base_width +3, base_height +3, 0, 40, 48, 8, 8, 0)
            elif key== WEAPON_NAME_CRAW:
                pyxel.blt(base_width +3, base_height +3, 0, 32, 56, 8, 8, 0)
            elif key== WEAPON_NAME_THROWING_KNIFE:
                pyxel.blt(base_width +3, base_height +3, 0, 40, 56, 8, 8, 0)
            draw_text_with_border(base_width -5, base_height+2, f"{int(simpleplayer.attacks[key].traits.get("強化", 0))}", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
            # draw_text_with_border(base_width -5, base_height+2, f"{int(simpleplayer.attacks[key].exp)}", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)

            base_height += 10

        if event_treasure.dialog and event_treasure.dialog.active:
            return
        if event_npc.dialog_npc and event_npc.dialog_npc.active:
            return

        draw_floor_flavor(0, 150)
        battle_log.draw()

        simple_window_status_ui.StatusWindow.draw()
        # WeaponLevelUpWindow.draw()

    elif game_mode == MODE_DEAD:
        pyxel.camera(simpleplayer.x - pyxel.width // 2, simpleplayer.y - pyxel.height // 2)
        pyxel.bltm(0, 0, 0, 0, 0, 320, 200)
        pyxel.blt(simpleplayer.x-32, simpleplayer.y-30, 0, 0, 80, 64, 8, 0)
        simpleplayer.draw()

    elif game_mode == MODE_CAMP:
        simple_window_status_ui.CampScene.draw()


    # Debug情報
    # if last_key is not None:
    #     key_name = KEY_NAME_MAP.get(last_key, f"KEY_{last_key}")
    #     pyxel.text(10, 10, f"key: {key_name}", 7)
    #     pyxel.text(10, 20, f"frame: {last_frame}", 7)
    # else:
    #     pyxel.text(10, 10, "none", 6)


# ゲーム実行
pyxel.run(update, draw)