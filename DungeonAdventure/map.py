import math
import random

import numpy as np
import pyxel
from sin_system import get_sin_modifier

meiro_width, meiro_height = 40, 25
maze = np.ones((meiro_height, meiro_width), dtype=int)
tile_FLOOR = (3, 0)
tile_WALL = (2, 0)
tile_BOX = (2, 1)
tile_BOX_OPEN = (3, 1)
tile_DARK_FLOOR = (5, 0)
tile_DARK_WALL = (4, 0)
tile_DARK_BOX = (4, 1)
tile_OUT_WALL = (0, 0)
tile_STAIRES = (3, 2)
tile_DOOR = (4, 2)
tile_KEY = (0, 1)
tile_DARK_KEY = (1, 1)
tile_NPC = (4, 3)
spawn_x = 1
spawn_y = 1

MAZE_FLOOR = 0
MAZE_WALL = 1
MAZE_BOX = 2
MAZE_BOX_OPEN = 3
MAZE_STAIRES = 4
MAZE_KEY = 5
MAZE_NPC = 6

def create_maze():
    global maze, spawn_y, spawn_x
    # generate_maze()
    maze = create_simple_bsp_maze(meiro_width, meiro_height)


def generate_maze():
    global maze
    # 迷路のサイズ
    # meiro_width, meiro_height = 50, 50
    # 迷路を壁で埋める（1:壁, 0:通路）
    maze = np.ones((meiro_height, meiro_width), dtype=int)
    # 開始位置（入口）
    start_x, start_y = 1, 1
    maze[start_y, start_x] = 0
    # 壁リストを作成
    walls = [(start_x, start_y, dx, dy) for dx, dy in [(2, 0), (-2, 0), (0, 2), (0, -2)]]
    # 迷路生成（Prim法）
    while walls:
        x, y, dx, dy = random.choice(walls)
        nx, ny = x + dx, y + dy
        if 0 <= nx < meiro_width and 0 <= ny < meiro_height and maze[ny, nx] == 1:
            maze[ny, nx] = 0
            maze[y + dy // 2, x + dx // 2] = 0
            walls.extend([(nx, ny, dxx, dyy) for dxx, dyy in [(2, 0), (-2, 0), (0, 2), (0, -2)]])
        walls.remove((x, y, dx, dy))
    # 出口を設定（右下）
    maze[meiro_height - 2, meiro_width - 2] = 4
    # チェックポイント（宝箱）をランダムに配置
    num_checkpoints = 5  # 設置するチェックポイントの数
    checkpoints = []
    key_chest = True
    while len(checkpoints) < num_checkpoints:
        cx, cy = random.randint(1, meiro_width - 2), random.randint(1, meiro_height - 2)
        if maze[cy, cx] == 0:  # 通路のみに配置
            if key_chest:
                maze[cy, cx] = 5
                key_chest = False
            else:
                maze[cy, cx] = 2
            checkpoints.append((cx, cy))

    for index_y in range(len(maze)):
        for index_x in range(len(maze[index_y])):
            if maze[index_y, index_x] == 0:
                pyxel.tilemaps[0].pset(index_x, index_y, tile_DARK_FLOOR)
            elif maze[index_y, index_x] == 1:
                pyxel.tilemaps[0].pset(index_x, index_y, tile_DARK_WALL)
            elif maze[index_y, index_x] == 2:
                pyxel.tilemaps[0].pset(index_x, index_y, tile_DARK_BOX)
            elif maze[index_y, index_x] == 5:
                pyxel.tilemaps[0].pset(index_x, index_y, tile_DARK_KEY)

def create_simple_bsp_maze(width, height, max_depth=4, min_room=5):
    global maze, spawn_y, spawn_x
    class Leaf:
        def __init__(self, x, y, w, h, depth):
            self.x, self.y, self.w, self.h = x, y, w, h
            self.room = None
            self.children = []
            self.depth = depth

            if depth < max_depth and w > min_room * 2 and h > min_room * 2:
                if random.choice([True, False]):
                    split = random.randint(min_room, w - min_room)
                    self.children = [
                        Leaf(x, y, split, h, depth + 1),
                        Leaf(x + split, y, w - split, h, depth + 1),
                    ]
                else:
                    split = random.randint(min_room, h - min_room)
                    self.children = [
                        Leaf(x, y, w, split, depth + 1),
                        Leaf(x, y + split, w, h - split, depth + 1),
                    ]

        def generate_rooms(self, maze):
            if self.children:
                for c in self.children:
                    c.generate_rooms(maze)
                connect(self.children[0].center(), self.children[1].center(), maze)
            else:
                rw, rh = random.randint(3, self.w - 2), random.randint(3, self.h - 2)
                rx, ry = random.randint(self.x + 1, self.x + self.w - rw - 1), random.randint(self.y + 1, self.y + self.h - rh - 1)
                self.room = (rx, ry, rw, rh)
                maze[ry:ry + rh, rx:rx + rw] = MAZE_FLOOR  # 床

        def center(self):
            if self.room:
                x, y, w, h = self.room
                return x + w // 2, y + h // 2
            if self.children:
                return self.children[0].center()

    def connect(c1, c2, maze):
        x1, y1 = c1
        x2, y2 = c2
        if random.choice([True, False]):
            maze[y1, min(x1, x2):max(x1, x2)+1] = MAZE_FLOOR
            maze[min(y1, y2):max(y1, y2)+1, x2] = MAZE_FLOOR
        else:
            maze[min(y1, y2):max(y1, y2)+1, x1] = MAZE_FLOOR
            maze[y2, min(x1, x2):max(x1, x2)+1] = MAZE_FLOOR

    maze = np.ones((height, width), dtype=int)
    root = Leaf(0, 0, width, height, 0)
    root.generate_rooms(maze)

    # カギの生成
    # while True:
    #     rx, ry = random.randint(2, width-2), random.randint(2, height-2)
    #     if maze[ry, rx]==0:
    #         maze[ry, rx] = 5
    #         break

    # 箱の生成
    # 暴食の補正値を加える
    base_min: int = 3
    base_max: int = 6
    # ① 補正倍率取得（内部で power を参照）
    boost = get_sin_modifier("暴食", "chest_spawn_rate")

    # ② boost が1.0未満なら1.0にする
    boost = max(boost, 1.0)

    # ③ raw_count を乱数で取得
    raw_count = random.randint(base_min, base_max)

    # ④ 切り上げして個数算出
    num_chest = math.ceil(raw_count * boost)

    num_chest = max(1, num_chest)
    print(num_chest)

    while num_chest >= 0:
        rx, ry = random.randint(2, width-2), random.randint(2, height-2)
        if maze[ry, rx]==MAZE_FLOOR:
            maze[ry, rx] = MAZE_BOX
            num_chest-=1
            continue

    # 出口の生成
    # while True:
    #     rx, ry = random.randint(2, width-2), random.randint(2, height-2)
    #     if maze[ry, rx]==MAZE_FLOOR:
    #         maze[ry, rx] = MAZE_STAIRES
    #         break
    # 出口の生成
    while True:
        rx, ry = random.randint(2, width - 2), random.randint(2, height - 2)

        # 候補地が床であるかを確認
        if maze[ry, rx] == MAZE_FLOOR:
            is_surrounded_by_floor = True

            # 候補地の周囲8マスをチェック
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue  # 中心はスキップ

                    nx, ny = rx + dx, ry + dy

                    # 迷路の範囲外ではないか、かつ床であるかを確認
                    if not (0 <= nx < width and 0 <= ny < height and maze[ny, nx] == MAZE_FLOOR):
                        is_surrounded_by_floor = False
                        break
                if not is_surrounded_by_floor:
                    break

            # 周囲8マスが全て床であれば階段を設置し、ループを抜ける
            if is_surrounded_by_floor:
                maze[ry, rx] = MAZE_STAIRES
                break

    # npcの生成
    base_spawn_rate = 0.3  # 今は必ず1体 → この値を色欲補正の前提確率とする

    spawn_npc(maze, width, height)

    # 補正倍率を取得（例: power=10で2倍になる設計）
    lust_boost = get_sin_modifier("色欲", "npc_event_rate")
    final_spawn_rate = min(base_spawn_rate * lust_boost, 1.0)

    for _ in range(3):
        if random.random() <= final_spawn_rate:
            print("npc create")
            spawn_npc(maze, width, height)


    for index_y in range(len(maze)):
        for index_x in range(len(maze[index_y])):
            if maze[index_y, index_x] == MAZE_FLOOR:
                pyxel.tilemaps[0].pset(index_x, index_y, tile_FLOOR)
            elif maze[index_y, index_x] == MAZE_WALL:
                pyxel.tilemaps[0].pset(index_x, index_y, tile_WALL)
            elif maze[index_y, index_x] == MAZE_BOX:
                pyxel.tilemaps[0].pset(index_x, index_y, tile_BOX)
            elif maze[index_y, index_x] == MAZE_STAIRES:
                pyxel.tilemaps[0].pset(index_x, index_y, tile_STAIRES)
            elif maze[index_y, index_x] == MAZE_KEY:
                pyxel.tilemaps[0].pset(index_x, index_y, tile_KEY)
            elif maze[index_y, index_x] == MAZE_NPC:
                pyxel.tilemaps[0].pset(index_x, index_y, tile_NPC)

    # spawn_x, spawn_y = find_spawn_point(maze)
    # maze[spawn_y, spawn_x] = 0
    return maze


def spawn_npc(maze, width, height):
    while True:
        rx, ry = random.randint(2, width - 2), random.randint(2, height - 2)
        if maze[ry, rx] == MAZE_FLOOR:
            maze[ry, rx] = MAZE_NPC
            break


def find_spawn_point(maze):
    height, width = maze.shape
    while True:
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)
        if maze[y, x] == MAZE_FLOOR:  # 床だったらOK
            return x, y

def find_spawn_point_2():
    height, width = maze.shape
    while True:
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)
        if maze[y, x] == MAZE_FLOOR:  # 床だったらOK
            return x, y


def checkMapTile_pixel(target_x, target_y):
    move_map_x = int(target_x / 8)
    move_map_y = int(target_y / 8)
    tile_info = pyxel.tilemap(0).pget(move_map_x, move_map_y)
    tile_x, tile_y = tile_info  # タイルIDのX, Y座標を取得
    # if tile_x == 2 and tile_y == 0:
    #     return True
    # else:
    #     return False
    if tile_info == tile_WALL or tile_info == tile_DARK_WALL or tile_info == tile_OUT_WALL:
        return True
    else:
        return False


def checkMapTile_point(target_x, target_y):
    move_map_x = target_x
    move_map_y = target_y
    tile_info = pyxel.tilemap(0).pget(move_map_x, move_map_y)
    tile_x, tile_y = tile_info  # タイルIDのX, Y座標を取得
    # if tile_x == 2 and tile_y == 0:
    #     return True
    # else:
    #     return False
    if tile_info == tile_WALL or tile_info == tile_DARK_WALL or tile_info == tile_OUT_WALL:
        return True
    else:
        return False


def checkMapStairs_pixel(target_x, target_y):
    return checkMapStairs_point(int(target_x / 8),int(target_y / 8))

def checkMapStairs_point(target_x, target_y):
    move_map_x = target_x
    move_map_y = target_y
    tile_info = pyxel.tilemap(0).pget(move_map_x, move_map_y)
    if tile_info == tile_STAIRES:
        return True
    else:
        return False


def checkMapKey_point(target_x, target_y):
    move_map_x = target_x
    move_map_y = target_y
    tile_info = pyxel.tilemap(0).pget(move_map_x, move_map_y)
    if tile_info == tile_KEY:
        return True
    else:
        return False

def checkMapNPC_pixel(target_x, target_y):
    move_map_x = int(target_x / 8)
    move_map_y = int(target_y / 8)
    tile_info = pyxel.tilemap(0).pget(move_map_x, move_map_y)
    if tile_info == tile_NPC:
        # print(tile_info)
        clearNPC(move_map_x, move_map_y)
        return True
    else:
        return False

def clearNPC(target_x, target_y):
    pyxel.tilemaps[0].pset(target_x, target_y, tile_FLOOR)
    set_maze(target_x,target_y, MAZE_FLOOR)


def get_treasure_simple(pixel_x,pixel_y):
    global maze
    x = int(pixel_x // 8)
    y = int(pixel_y // 8)
    if maze[y, x] == MAZE_BOX:
        pyxel.tilemaps[0].pset(x, y, tile_BOX_OPEN)
        maze[y, x] = MAZE_BOX_OPEN
        # player.cure(5)
        pyxel.play(3,2)
        return True
    else:
        return False

def get_treasure(x,y, player):
    global maze
    if maze[y, x] == MAZE_BOX:
        pyxel.tilemaps[0].pset(x, y, tile_BOX_OPEN)
        maze[y, x] = MAZE_BOX_OPEN
        # player.cure(5)
        pyxel.play(3,2)

        if random.randint(0, 3)==0:
            player.add_item("ポーション")
            # print("現在のインベントリ:", player.inventory)
        elif random.randint(0, 6)==0:
            player.add_item("エリクサー")
            # print("現在のインベントリ:", player.inventory)
        else:
            player.cure_hp(3)

def set_maze(x,y, val):
    global  maze
    maze[y,x]=val

def get_maze(x,y):
    return maze[y,x]