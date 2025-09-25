import math

import game_log
# import player
import pyxel
import random

# import PyxelUniversalFont as puf

from constants import D_UP, D_DOWN, MODE_TITLE, MODE_SELECT, MODE_FIELD, MODE_TEST, \
    PLAYER_STATE_NORMAL, PLAYER_WEAPON_SWORD, PLAYER_WEAPON_MAGIC_FIRE, PLAYER_WEAPON_MAGIC_THUNDER, PLAYER_JOB_FIGHTER, PLAYER_JOB_WIZARD, \
    BGM_NONE, BGM_TITLE, BGM_DUNGEON
from data import MOB_DATA
from item import DropItem
from map import checkMapStairs_point, checkMapKey_point, \
    get_treasure, meiro_width, meiro_height, tile_FLOOR, tile_WALL, tile_BOX, tile_BOX_OPEN, \
    tile_STAIRES, tile_DOOR, tile_KEY, create_maze, set_maze, get_maze, spawn_x, spawn_y, find_spawn_point_2
from mob import mob, generate_mob
from player import player
from sound import load_musics, play_bgm_dungeon, play_bgm_title

# テスト向け
from SimpleEnemy import SimpleEnemy
from attack import Attack, AttackType
from SimplePlayer import SimplePlayer  # プレイヤーも軽量版


# ゲーム初期化（画面サイズ160x120）
pyxel.init(128, 128)
pyxel.load('pyxel.pyxres')
pyxel.image(1).load(0, 0, "image/dungeon1_1.png")


# フォントを指定
# writer = puf.Writer("misaki_gothic.ttf")

# 音楽ファイルの読み込み及び設定
play_sound = BGM_NONE
load_musics()

floor_key = False

# ドロップアイテムの管理
drop_item_manager = DropItem()

# クラスを用いてプレイヤーを定義
# プレイヤーの座標を初期化
player = player(10, 0, PLAYER_STATE_NORMAL, 1, 1, D_UP, PLAYER_JOB_FIGHTER, PLAYER_WEAPON_SWORD)

# グローバル変数
score = 0
depth = 1
game_mode= MODE_TITLE

mobs = [
    mob(0, 5, 6, D_UP),
    mob(1, 6, 6, D_DOWN),
]
disp_mob_mng = [0, mob(0, 5, 6, D_UP)]



# グローバル変数
last_key = None
last_frame = 0

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

# テスト向け
simpleplayer = SimplePlayer(64, 64, 1)
enemies = [SimpleEnemy(80, 60), SimpleEnemy(50, 72)]

attack_sword = Attack(simpleplayer, enemies, AttackType.MELEE, 30, 12, math.radians(90), 32)
attack_fire = Attack(simpleplayer, enemies, AttackType.SHOCKWAVE, 30, 20, math.radians(90), 32)
attack_thunder = Attack(simpleplayer, enemies, AttackType.AREA_MAGIC, 60, 32, math.radians(90), 32)
attack = attack_sword

enemies = [
    SimpleEnemy(80, 60, "bat"),
    # SimpleEnemy(100, 100, "skeleton"),
    # SimpleEnemy(120, 80, "bat")
]


# 更新関数
def update():
    global mobs, score, depth, game_mode, disp_mob_mng, play_sound, drop_item_manager, floor_key, last_key, last_frame, attack, enemies

    last_key = None
    for key in KEY_LIST:
        if pyxel.btn(key):
            last_key = key
            last_frame = pyxel.frame_count
            # print(last_key)
            break

    #ゲームモード：タイトル
    if game_mode== MODE_TITLE:
        # player.init(10, PLAYER_STATE_NORMAL, 1, 1, D_UP, PLAYER_WEAPON_MAGIC_FIRE)
        # player.init(10, PLAYER_STATE_NORMAL, 1, 1, D_UP, PLAYER_WEAPON_SWORD)
        score = 0
        depth = 1
        floor_key = False

        if play_sound != BGM_TITLE:
            play_bgm_title()
            play_sound = BGM_TITLE

        # if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
        if last_key == pyxel.KEY_SPACE or last_key == pyxel.MOUSE_BUTTON_LEFT:
            game_mode= MODE_SELECT
            player.init(10, 0, PLAYER_STATE_NORMAL, 1, 1, D_UP, PLAYER_JOB_FIGHTER, PLAYER_WEAPON_SWORD)
        elif pyxel.btn(pyxel.KEY_1):
            game_mode= MODE_TEST
            pyxel.mouse(True)
            create_maze()
            s_x, s_y = find_spawn_point_2()
            simpleplayer.x = s_x * simpleplayer.size
            simpleplayer.y = s_y * simpleplayer.size
            attack = attack_sword
            if play_sound != BGM_DUNGEON:
                play_bgm_dungeon()
                play_sound = BGM_DUNGEON


    #ゲームモード：キャラセレクト
    elif game_mode== MODE_SELECT:

        # if pyxel.btnp(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
        if last_key == pyxel.KEY_UP or last_key == pyxel.GAMEPAD1_BUTTON_DPAD_UP:
            if player.job == PLAYER_JOB_FIGHTER:
                player.init(5, 10, PLAYER_STATE_NORMAL, 1, 1, D_UP, PLAYER_JOB_WIZARD, PLAYER_WEAPON_MAGIC_FIRE)
            elif player.job == PLAYER_JOB_WIZARD:
                player.init(10, 0, PLAYER_STATE_NORMAL, 1, 1, D_UP, PLAYER_JOB_FIGHTER, PLAYER_WEAPON_SWORD)

        # elif pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
        elif last_key == pyxel.KEY_DOWN or last_key == pyxel.GAMEPAD1_BUTTON_DPAD_DOWN:
            if player.job == PLAYER_JOB_FIGHTER:
                player.init(5, 10, PLAYER_STATE_NORMAL, 1, 1, D_UP, PLAYER_JOB_WIZARD, PLAYER_WEAPON_MAGIC_FIRE)
            elif player.job == PLAYER_JOB_WIZARD:
                player.init(10, 0, PLAYER_STATE_NORMAL, 1, 1, D_UP, PLAYER_JOB_FIGHTER, PLAYER_WEAPON_SWORD)

        # elif pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A):
        elif last_key == pyxel.KEY_SPACE or last_key == pyxel.GAMEPAD1_BUTTON_A:
            game_mode= MODE_FIELD
            create_maze()
            s_x, s_y = find_spawn_point_2()
            player.jump(s_x, s_y)
            game_log.battle_log.clear_logs()
            if play_sound != BGM_DUNGEON:
                play_bgm_dungeon()
                play_sound = BGM_DUNGEON


    #ゲームモード：フィールド
    elif game_mode== MODE_FIELD:

        #ターゲットへ向けて歩く
        player.move_act()

        # 矢印キーでプレイヤーを移動
        # if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
        if last_key == pyxel.KEY_LEFT or last_key == pyxel.GAMEPAD1_BUTTON_DPAD_LEFT:
            player.set_move_left()

        # elif pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
        elif last_key == pyxel.KEY_RIGHT or last_key == pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT:
            player.set_move_right()

        # elif pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
        elif last_key == pyxel.KEY_UP or last_key == pyxel.GAMEPAD1_BUTTON_DPAD_UP:
            player.set_move_up()

        # elif pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
        elif last_key == pyxel.KEY_DOWN or last_key == pyxel.GAMEPAD1_BUTTON_DPAD_DOWN:
            player.set_move_down()

        # elif pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A):
        elif last_key == pyxel.KEY_SPACE or last_key == pyxel.GAMEPAD1_BUTTON_A:
            player.attack()

        # elif pyxel.btnp(pyxel.KEY_Z):
        elif last_key == pyxel.KEY_Z:
            player.attack()

        # elif pyxel.btn(pyxel.KEY_1) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_B):
        #     player.use_item_index(0)
        # elif pyxel.btn(pyxel.KEY_2) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_X):
        #     player.use_item_index(1)
        # elif pyxel.btn(pyxel.KEY_3) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_Y):
        #     player.use_item_index(2)
        # elif pyxel.btn(pyxel.KEY_4):
        #     player.use_item_index(3)
        elif last_key == pyxel.KEY_1 or last_key == pyxel.GAMEPAD1_BUTTON_B:
            player.use_item_index(0)
        elif last_key == pyxel.KEY_2 or last_key == pyxel.GAMEPAD1_BUTTON_X:
            player.use_item_index(1)
        elif last_key == pyxel.KEY_3 or last_key == pyxel.GAMEPAD1_BUTTON_Y:
            player.use_item_index(2)
        elif last_key == pyxel.KEY_4:
            player.use_item_index(3)

        get_treasure(player.point_x, player.point_y, player)

        #mobの移動
        for index, target_mob in enumerate(mobs):

            if not target_mob.live():
                del mobs[index]
                score += 1
                if score % 10 == 0:
                    player.level_up()
                continue

            if (player.point_x < target_mob.point_x -10 or player.point_x > target_mob.point_x + 10
                    or player.point_y < target_mob.point_y - 10 or player.point_y > target_mob.point_y + 10):
                    del mobs[index]
                    continue

            target_mob.act()

            #playerとmobの当たり判定
            if target_mob.live() and player.collision(target_mob.pixel_x(), target_mob.pixel_y()):
                player.damage(1)
                # target_mob.nock_back()
                disp_mob_mng = [100, target_mob]
                if not player.live():
                    game_mode = MODE_TITLE

            #playerの攻撃とmobの当たり判定
            if player.collision_attack (target_mob.pixel_x(), target_mob.pixel_y()):
                target_mob.damage(1, game_log.battle_log, drop_item_manager)
                disp_mob_mng = [100, target_mob]

        if checkMapStairs_point(player.point_x, player.point_y):
            pyxel.play(3, 5)
            create_maze()
            s_x, s_y = find_spawn_point_2()
            player.jump(s_x, s_y)
            # player.jump(1, 1)
            depth+=1

        if checkMapKey_point(player.point_x, player.point_y):
            pyxel.tilemaps[0].pset(player.point_x, player.point_y, tile_BOX_OPEN)
            set_maze(player.point_x, player.point_y, 0)
            floor_key = True
            pyxel.play(3, 2)
            game_log.battle_log.add_log("カギを手に入れた！")
            game_log.battle_log.add_log("どこかで扉の開く音がする")

        #Playerとitemの当たり判定
        for item in drop_item_manager.items[:]:
            if abs(player.point_x - item["x"]) <= 0 and abs(player.point_y - item["y"]) <= 0:
                drop_item_manager.remove_item(item["x"], item["y"])  # アイテム削除
                player.add_item(item["name"])
                pyxel.play(3, 2)

        # mobの生成
        if len(mobs) < 5 and (random.random() < 0.2):
            generate_x = random.randint(player.point_x - 4, player.point_x + 4)
            generate_y = random.randint(player.point_y - 4, player.point_y + 4)
            if generate_x < 0:
                generate_x = 0
            if generate_y < 0:
                generate_y = 0
            generate_mob(generate_x, generate_y, mobs, player)

        for index_x in range(player.point_x - 1, player.point_x + 2):
            for index_y in range(player.point_y - 1, player.point_y + 2):

                if index_x < 0 or index_x >= meiro_width or index_y < 0 or index_y >= meiro_height:
                     continue
                if get_maze(index_x, index_y) == 0:
                    pyxel.tilemaps[0].pset(index_x, index_y, tile_FLOOR)
                elif get_maze(index_x, index_y) == 1:
                    pyxel.tilemaps[0].pset(index_x, index_y, tile_WALL)
                elif get_maze(index_x, index_y) == 2:
                    pyxel.tilemaps[0].pset(index_x, index_y, tile_BOX)
                elif get_maze(index_x, index_y) == 4:
                    pyxel.tilemaps[0].pset(index_x, index_y, tile_STAIRES)
                    # if floor_key:
                    #     pyxel.tilemaps[0].pset(index_x, index_y, tile_STAIRES)
                    # else:
                    #     pyxel.tilemaps[0].pset(index_x, index_y, tile_DOOR)
                elif get_maze(index_x, index_y) == 5:
                    pyxel.tilemaps[0].pset(index_x, index_y, tile_KEY)

    elif game_mode == MODE_TEST:
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            center_x = 64
            center_y = 64

            if 0 <= pyxel.mouse_x <= 8 and \
                    116 <= pyxel.mouse_y <= 126:
                if attack.attack_type == AttackType.MELEE:
                    attack = attack_fire
                elif attack.attack_type == AttackType.SHOCKWAVE:
                    attack = attack_thunder
                elif attack.attack_type == AttackType.AREA_MAGIC:
                    attack = attack_sword
                return

            # マウスの位置から、主人公（画面中央）との相対位置を計算
            dx = pyxel.mouse_x - center_x
            dy = pyxel.mouse_y - center_y

            # 現在の主人公の座標に相対位置を足して、実際の移動先を算出
            target_x = simpleplayer.x + dx
            target_y = simpleplayer.y + dy

            simpleplayer.move_to(target_x, target_y)
            print(str(pyxel.mouse_x) + ","+str(pyxel.mouse_y))
            print(str(simpleplayer.x) + ","+str(simpleplayer.y)+ ","+str(simpleplayer.angle))

            # attack = Attack(simpleplayer, enemies, AttackType.MELEE, 30, 12, math.radians(90), 32)
            # menubar_base_x = simpleplayer.x - 64
            # menubar_base_y = simpleplayer.y + 56


        for e in enemies:
            e.update()
        enemies = [e for e in enemies if e.is_alive()]
        attack.update()
        simpleplayer.update()


# 描画関数
def draw():
    global disp_mob_mng, drop_item_manager

    pyxel.cls(0)  # 画面を黒色でクリア

    if game_mode== MODE_TITLE:
        pyxel.blt(0, 0, 1, 0, 0, 128, 128)  # 画像を表示
        pyxel.text(20, 30, "  plz hit space key   ", pyxel.frame_count % 16)  # メッセージ

    #ゲームモード：キャラセレクト
    elif game_mode== MODE_SELECT:

        # 選択する四角を描画
        if player.job == PLAYER_JOB_FIGHTER:
            pyxel.rect(15, 7, 102, 22, pyxel.COLOR_RED)
            pyxel.rect(16, 8, 100, 20, pyxel.COLOR_BLACK)

        elif player.job == PLAYER_JOB_WIZARD:
            pyxel.rect(15, 27, 102, 22, pyxel.COLOR_RED)
            pyxel.rect(16, 28, 100, 20, pyxel.COLOR_BLACK)

        # 各職業毎の描画
        pyxel.blt(20, 10, 0, 56, 0, 8, 8, 0)
        pyxel.text(20, 20, "Fighter", pyxel.COLOR_WHITE)
        # writer.draw(50, 10, "体力が高い", 8, 7)

        pyxel.blt(20, 30, 0, 56, 16, 8, 8, 0)
        pyxel.text(20, 40, "Wizard", pyxel.COLOR_WHITE)
        # writer.draw(50, 30, "魔法で離れて攻撃", 8, 7)




    elif game_mode== MODE_FIELD:
        #マップ表示
        pyxel.bltm(0, 0, 0, player.pixel_x() - 32, player.pixel_y() - 32, 64, 64)


        pyxel.rect(5,0,20,7, pyxel.COLOR_BLACK)

        player.draw_player()
        drop_item_manager.draw(player.pixel_x(), player.pixel_y())

        # mobの描画
        for target_mob in mobs:
            target_mob.draw(player.pixel_x(), player.pixel_y())

        #プレイヤーステータスの表示
        if player.job == PLAYER_JOB_FIGHTER:
            pyxel.blt(70, 0, 0, 56, 0, 8, 8, 0)
            pyxel.text(80, 2, "Fighter", pyxel.COLOR_WHITE)
            pyxel.text(70, 10, "HP", pyxel.COLOR_WHITE)
            pyxel.rect(85, 10, player.max_hp, 5, pyxel.COLOR_RED)
            pyxel.rect(85, 10, player.hp, 5, pyxel.COLOR_GREEN)
        elif player.job == PLAYER_JOB_WIZARD:
            pyxel.blt(70, 0, 0, 56, 16, 8, 8, 0)
            pyxel.text(80, 2, "Wizard", pyxel.COLOR_WHITE)
            pyxel.text(70, 10, "HP", pyxel.COLOR_WHITE)
            pyxel.rect(85, 10, player.max_hp, 5, pyxel.COLOR_RED)
            pyxel.rect(85, 10, player.hp, 5, pyxel.COLOR_GREEN)
            pyxel.text(75, 10, "MP", pyxel.COLOR_WHITE)
            pyxel.rect(85, 15, player.max_mp, 5, pyxel.COLOR_GRAY)
            pyxel.rect(85, 15, player.mp, 5, pyxel.COLOR_ORANGE)

        pyxel.text(70, 20, "EXP", pyxel.COLOR_WHITE)
        pyxel.rect(85, 20, 30,5, pyxel.COLOR_WHITE)
        pyxel.rect(86, 21, 28,3, pyxel.COLOR_BLACK)
        pyxel.rect(85, 20, (score % 10) * 3,5, pyxel.COLOR_CYAN)

        pyxel.rect(69, 26, 11, 10, pyxel.COLOR_RED)
        pyxel.rect(70, 27, 9, 8, pyxel.COLOR_BLACK)
        pyxel.text(73, 37, "1", pyxel.COLOR_WHITE)

        pyxel.rect(79, 26, 11, 10, pyxel.COLOR_RED)
        pyxel.rect(80, 27, 9, 8, pyxel.COLOR_BLACK)
        pyxel.text(83, 37, "2", pyxel.COLOR_WHITE)

        pyxel.rect(89, 26, 11, 10, pyxel.COLOR_RED)
        pyxel.rect(90, 27, 9, 8, pyxel.COLOR_BLACK)
        pyxel.text(93, 37, "3", pyxel.COLOR_WHITE)

        pyxel.rect(99, 26, 11, 10, pyxel.COLOR_RED)
        pyxel.rect(100, 27, 9, 8, pyxel.COLOR_BLACK)
        pyxel.text(103, 37, "4", pyxel.COLOR_WHITE)

        player.draw_inventory()

        #階層の情報
        pyxel.text(5, 1, "B"+str(depth)+"F", pyxel.COLOR_WHITE)

        #敵モブのステータス表示
        disp_flg = disp_mob_mng[0]
        disp_mob = disp_mob_mng[1]
        if disp_flg > 0:
            pyxel.blt(70, 45, 0, MOB_DATA[disp_mob.id][disp_mob._MOB_U], MOB_DATA[disp_mob.id][disp_mob._MOB_V], 8, 8,
                      0)
            pyxel.blt(70, 45, 0, MOB_DATA[disp_mob.id][disp_mob._MOB_U], MOB_DATA[disp_mob.id][disp_mob._MOB_V], 8, 8,
                      0)
            pyxel.text(80, 48, disp_mob.name, pyxel.COLOR_WHITE)
            pyxel.text(70, 55, "HP", pyxel.COLOR_WHITE)
            pyxel.rect(80, 55, disp_mob.hp, 5, pyxel.COLOR_GREEN)
            disp_mob_mng[0] -= 1

        y = 70
        for log in game_log.battle_log.logs:
            # print(log)
            # writer.draw(5, y, log, 8, 7)
            y += 10


    elif game_mode== MODE_TEST:
        pyxel.bltm(0, 0, 0, 0, 0, 320, 200)
        simpleplayer.draw()
        for enemy in enemies:
            if enemy.is_alive():
                enemy.draw()
        attack.draw()

    # ボタン？
    menubar_base_x = simpleplayer.x -64
    menubar_base_y = simpleplayer.y +56
    menu_btn_size = 3

    pyxel.rect(menubar_base_x, menubar_base_y, 8, 8, pyxel.COLOR_BLACK)
    if attack.attack_type == AttackType.MELEE:
        pyxel.blt(menubar_base_x, menubar_base_y, 0, 40, 32, 8, 8, 0)
    elif  attack.attack_type == AttackType.SHOCKWAVE:
        pyxel.blt(menubar_base_x, menubar_base_y, 0, 0, 32, 8, 8, 0)
    elif  attack.attack_type == AttackType.AREA_MAGIC:
        pyxel.blt(menubar_base_x, menubar_base_y, 0, 8, 32, 8, 8, 0)


    # Debug情報
    if last_key is not None:
        key_name = KEY_NAME_MAP.get(last_key, f"KEY_{last_key}")
        pyxel.text(10, 10, f"key: {key_name}", 7)
        pyxel.text(10, 20, f"frame: {last_frame}", 7)
    else:
        pyxel.text(10, 10, "none", 6)


# ゲーム実行
pyxel.run(update, draw)