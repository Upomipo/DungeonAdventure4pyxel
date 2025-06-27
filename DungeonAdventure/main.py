import game_log
# import player
import pyxel
import random

import PyxelUniversalFont as puf

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

# ゲーム初期化（画面サイズ160x120）
pyxel.init(128, 128)
pyxel.load('pyxel.pyxres')
pyxel.image(1).load(0, 0, "image/dungeon1_1.png")

# フォントを指定
writer = puf.Writer("misaki_gothic.ttf")

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


# 共通関数


# 更新関数
def update():
    global mobs, score, depth, game_mode, disp_mob_mng, play_sound, drop_item_manager, floor_key

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

        if pyxel.btnp(pyxel.KEY_SPACE):
            game_mode= MODE_SELECT
            player.init(10, 0, PLAYER_STATE_NORMAL, 1, 1, D_UP, PLAYER_JOB_FIGHTER, PLAYER_WEAPON_SWORD)
        elif pyxel.btn(pyxel.KEY_1):
            game_mode= MODE_TEST

    #ゲームモード：キャラセレクト
    elif game_mode== MODE_SELECT:

        if pyxel.btnp(pyxel.KEY_UP):
            if player.job == PLAYER_JOB_FIGHTER:
                player.init(5, 10, PLAYER_STATE_NORMAL, 1, 1, D_UP, PLAYER_JOB_WIZARD, PLAYER_WEAPON_MAGIC_FIRE)
            elif player.job == PLAYER_JOB_WIZARD:
                player.init(10, 0, PLAYER_STATE_NORMAL, 1, 1, D_UP, PLAYER_JOB_FIGHTER, PLAYER_WEAPON_SWORD)

        elif pyxel.btnp(pyxel.KEY_DOWN):
            if player.job == PLAYER_JOB_FIGHTER:
                player.init(5, 10, PLAYER_STATE_NORMAL, 1, 1, D_UP, PLAYER_JOB_WIZARD, PLAYER_WEAPON_MAGIC_FIRE)
            elif player.job == PLAYER_JOB_WIZARD:
                player.init(10, 0, PLAYER_STATE_NORMAL, 1, 1, D_UP, PLAYER_JOB_FIGHTER, PLAYER_WEAPON_SWORD)

        elif pyxel.btnp(pyxel.KEY_SPACE):
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
        if pyxel.btn(pyxel.KEY_LEFT):
            player.set_move_left()

        elif pyxel.btn(pyxel.KEY_RIGHT):
            player.set_move_right()

        elif pyxel.btn(pyxel.KEY_UP):
            player.set_move_up()

        elif pyxel.btn(pyxel.KEY_DOWN):
            player.set_move_down()

        elif pyxel.btn(pyxel.KEY_SPACE):
            player.attack()

        elif pyxel.btnp(pyxel.KEY_Z):
            player.attack()

        elif pyxel.btn(pyxel.KEY_1):
            player.use_item_index(0)
        elif pyxel.btn(pyxel.KEY_2):
            player.use_item_index(1)
        elif pyxel.btn(pyxel.KEY_3):
            player.use_item_index(2)
        elif pyxel.btn(pyxel.KEY_4):
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
        #ターゲットへ向けて歩く
        player.move_act()

        # 矢印キーでプレイヤーを移動
        if pyxel.btn(pyxel.KEY_LEFT):
            player.set_move_left()

        elif pyxel.btn(pyxel.KEY_RIGHT):
            player.set_move_right()

        elif pyxel.btn(pyxel.KEY_UP):
            player.set_move_up()

        elif pyxel.btn(pyxel.KEY_DOWN):
            player.set_move_down()

        elif pyxel.btn(pyxel.KEY_SPACE):
            player.attack()

        #debug
            #print(str(player_damage_cnt))


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
        writer.draw(50, 10, "体力が高い", 8, 7)

        pyxel.blt(20, 30, 0, 56, 16, 8, 8, 0)
        pyxel.text(20, 40, "Wizard", pyxel.COLOR_WHITE)
        writer.draw(50, 30, "魔法で離れて攻撃", 8, 7)




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
            writer.draw(5, y, log, 8, 7)
            y += 10


    elif game_mode== MODE_TEST:
        #マップ表示
        pyxel.bltm(0, 0, 1, player.pixel_x() - 32, player.pixel_y() - 32, 64, 64)


        # for index, mob in enumerate(mobs):
        for index_x in range(8):
            for index_y in range(8):
                tmp_x = player.point_x - 4 + index_x
                tmp_y = player.point_y - 4 + index_y
                if tmp_x < 0 or tmp_y <0:
                    continue
                if get_maze(tmp_x, tmp_y) == 0:
                    pyxel.blt(index_x*8, index_y*8, 0, 24, 0, 8, 8, 0)

        player.draw_player()

# ゲーム実行
pyxel.run(update, draw)