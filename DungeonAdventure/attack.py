import random
from operator import truediv

import pyxel

import math

from constants import WEAPON_NAME_GREATSWORD, WEAPON_NAME_SLASHAXE, WEAPON_NAME_FLASHSPEAR, WEAPON_NAME_BOOKOFFIRE, \
    WEAPON_NAME_BOOKOFTHUNDER, WEAPON_NAME_BOOKOFLIGHT, WEAPON_NAME_BEAM, WEAPON_NAME_KNIFE, WEAPON_NAME_ARROW, \
    WEAPON_NAME_CRAW, WEAPON_NAME_THROWING_KNIFE
from game_log import battle_log
from sin_system import get_sin_modifier
from map import checkMapTile_pixel
from util import angle_diff

player_attack = None
player_attack_sub = None

class AttackType:
    MELEE = "melee"
    SHOCKWAVE = "shockwave"
    FAN_FIRE = "fan_fire"
    AREA_MAGIC = "area_magic"
    THRUST = "thrust"
    THRUST_CROSS = "thrust_cross"
    PROJECTILE = "projectile"       # 飛び道具
    PROJECTILE_RANDOM = "projectile_random"
    SPIN_SLASH = "spin_slash"       # 回転斬り
    BEAM = "beam"                   # 貫通ビーム


class Attack:
    def __init__(self, player, enemies, name,
                 attack_type=AttackType.MELEE,
                 interval=30,
                 duration=5,
                 cone_angle=math.radians(90),
                 radius=32,
                 traits=None):
        self.player = player              # SimplePlayerインスタンス
        # self.enemies = enemies            # SimpleEnemyインスタンスのリスト
        self.attack_type = attack_type
        self.interval = interval          # 攻撃間隔（フレーム単位）
        self.duration = duration          # 持続フレーム数
        self.cone_angle = cone_angle      # 扇の角度（MELEE用）
        self.radius = radius              # 射程（各攻撃共通）

        self.timer = 0                    # 攻撃タイミング管理
        self.frame = -1                   # 攻撃中フレーム（-1で非攻撃）
        self.is_attacking = False
        self.knockback = self.get_knockback_value()
        self.multi_angles = []
        self.projectile_angles = []
        self.fixed_angle = player.angle

        self.traits = traits if traits else {}
        self.damage = 10
        self.base_damage = 10
        # self.enhancement = 0
        self.name = name
        self.display_name=name
        # self.apply_traits()
        self.exp = 0

    def add_exp(self, base_exp=1):
        # if self.exp < self.get_next_level_exp():
        #     modifier = get_sin_modifier("嫉妬","weapon_mastery_gain")
        #     gained_exp = max(base_exp, round(base_exp * modifier))
        #
        # self.exp += gained_exp
        modifier = get_sin_modifier("嫉妬","weapon_mastery_gain")
        gained_exp = max(base_exp, round(base_exp * modifier))

        self.exp += gained_exp

    def reset(self):
        self.reset_traits()
        self.reset_exp()

    def reset_exp(self):
        self.exp = 0

    def reset_traits(self):
        self.traits = {}

    def apply_traits(self):

        if self.exp < self.get_next_level_exp():
            return
        else:
            self.reset_exp()

        if not self.has_max_apply():
            battle_log.add_log(f"{self.display_name} はこれ以上強化できない")
            return

        self.traits["強化"] = self.traits.get("強化", 0) +1
        # level = self.traits.get("強化", 0)
        # print(level)

        # print("強化")
        if self.traits:
            if self.name == WEAPON_NAME_GREATSWORD:
                self.traits["攻撃力"] = self.traits.get("攻撃力", 0) + 20
            elif self.name == WEAPON_NAME_SLASHAXE:
                self.traits["攻撃力"] = self.traits.get("攻撃力", 0) + 10
                self.traits["範囲"] = self.traits.get("範囲", 0) + 1
            elif self.name == WEAPON_NAME_FLASHSPEAR:
                self.traits["攻撃力"] = self.traits.get("攻撃力", 0) + 10
                self.traits["速度"] = self.traits.get("速度", 0) + 1
            elif self.name == WEAPON_NAME_BOOKOFFIRE:
                self.traits["攻撃力"] = self.traits.get("攻撃力", 0) + 10
                # self.traits["速度"] = self.traits.get("速度", 0) + 1
                self.traits["範囲"] = self.traits.get("範囲", 0) + 1
            elif self.name == WEAPON_NAME_BOOKOFTHUNDER:
                self.traits["攻撃力"] = self.traits.get("攻撃力", 0) + 20
                self.traits["範囲"] = self.traits.get("範囲", 0) + 1
            elif self.name == WEAPON_NAME_BOOKOFLIGHT:
                self.traits["攻撃力"] = self.traits.get("攻撃力", 0) + 7
                self.traits["速度"] = self.traits.get("速度", 0) + 1
                self.traits["範囲"] = self.traits.get("範囲", 0) + 1
            elif self.name == WEAPON_NAME_BEAM:
                self.traits["攻撃力"] = self.traits.get("攻撃力", 0) + 30
                self.traits["速度"] = self.traits.get("速度", 0) + 1
            elif self.name == WEAPON_NAME_KNIFE:
                self.traits["攻撃力"] = self.traits.get("攻撃力", 0) + 5
                self.traits["範囲"] = self.traits.get("範囲", 0) + 1
            elif self.name == WEAPON_NAME_ARROW:
                self.traits["攻撃力"] = self.traits.get("攻撃力", 0) + 20
            elif self.name == WEAPON_NAME_CRAW:
                self.traits["攻撃力"] = self.traits.get("攻撃力", 0) + 7
                self.traits["範囲"] = self.traits.get("範囲", 0) + 1
                self.traits["速度"] = self.traits.get("速度", 0) + 1
            elif self.name == WEAPON_NAME_THROWING_KNIFE:
                self.traits["攻撃力"] = self.traits.get("攻撃力", 0) + 5
                self.traits["範囲"] = self.traits.get("範囲", 0) + 1

            # 攻撃力の強化
            self.damage = self.base_damage + self.traits.get("攻撃力", 0) * 1

            # 攻撃間隔（速度特性）
            self.interval = int(self.interval * (0.95 ** min(self.traits.get("速度", 0),5)))

            # 射程（範囲特性）
            # self.radius += 2 * self.traits.get("範囲", 0)
            self.radius += self.traits.get("範囲", 0) ** 0.5 * 3

            # 強化段階を名前に反映
            enhancement = self.traits.get("強化", 0)
            self.display_name = f"{self.name}+{enhancement}" if enhancement > 0 else self.name
            battle_log.add_log(f"{self.display_name} に強化された")

    def has_max_apply(self):
        if self.traits.get("強化", 0) < 5:
            return True
        else:
            return False

    def get_next_level_exp(self):
        return int((self.traits.get("強化", 0)+1) * 100)

    def get_knockback_value(self):
        kb_table = {
            AttackType.MELEE: 8,
            AttackType.SHOCKWAVE: 4,
            AttackType.FAN_FIRE: 3,
            AttackType.AREA_MAGIC: 1,
            AttackType.PROJECTILE: 3,
            AttackType.PROJECTILE_RANDOM: 2,
            AttackType.SPIN_SLASH: 2,
            AttackType.BEAM: 3,
            AttackType.THRUST: 6,
            AttackType.THRUST_CROSS: 3,
        }
        return kb_table.get(self.attack_type, 0)

    def apply_knockback(self, enemy):
        dx = enemy.x - self.player.x
        dy = enemy.y - self.player.y
        length = max(1, (dx**2 + dy**2) ** 0.5)
        nx = dx / length
        ny = dy / length
        new_x = enemy.x + nx * self.knockback
        new_y = enemy.y + ny * self.knockback

        # 壁判定関数（マップ構造に合わせて）
        if not checkMapTile_pixel(new_x, new_y):
            enemy.x = new_x
            enemy.y = new_y

    def is_in_cone(self, enemy):
        return self._in_cone(
            self.player.x, self.player.y,
            enemy.x, enemy.y,
            self.player.angle,  # ← ここが変更ポイント！
            self.cone_angle,
            self.radius
        )

    def update(self, enemies):
        self.timer += 1

        # 攻撃開始
        if not self.is_attacking and self.timer >= self.interval:
            self.frame = 0
            self.timer = 0
            self.is_attacking = True

            if self.attack_type == AttackType.MELEE:
                pyxel.play(3, 4)

            elif self.attack_type == AttackType.SHOCKWAVE:
                pyxel.play(3, 3)

            elif self.attack_type == AttackType.FAN_FIRE:
                pyxel.play(3, 3)

            elif self.attack_type == AttackType.AREA_MAGIC:
                pyxel.play(3, 0)

            elif self.attack_type == AttackType.PROJECTILE or \
                    self.attack_type == AttackType.PROJECTILE_RANDOM:
                pyxel.play(3, 2)
            elif self.attack_type == AttackType.SPIN_SLASH:
                pyxel.play(3, 2)
            elif self.attack_type == AttackType.BEAM:
                pyxel.play(3, 0)
            elif self.attack_type == AttackType.THRUST:
                pyxel.play(3, 2)
            elif self.attack_type == AttackType.THRUST_CROSS:
                pyxel.play(3, 4)

            if self.attack_type == AttackType.THRUST_CROSS and self.frame == 0:
                self.multi_angles = [
                    0,  # →
                    math.pi,  # ←
                    math.pi / 2,  # ↓
                    -math.pi / 2  # ↑
                ]

            if self.attack_type == AttackType.PROJECTILE_RANDOM and self.frame == 0:
                self.projectile_angles = []
                angle_offset_range = math.radians(70) / 2
                for _ in range(3):  # 3発分など、調整可能
                    rand_angle = random.uniform(0, 2 * math.pi)
                    # self.projectile_angles.append(rand_angle)

                    # プレイヤーの角度から+/-50度の範囲でランダムなオフセットを生成
                    rand_offset = random.uniform(-angle_offset_range, angle_offset_range)

                    # プレイヤーの角度にオフセットを加えて新しい発射角度を決定
                    new_angle = self.player.angle + rand_offset

                    self.projectile_angles.append(new_angle)

        # 攻撃中
        if self.frame >= 0:
            self._handle_attack(enemies)
            self.frame += 1
            if self.frame >= self.duration:
                self.frame = -1
                self.is_attacking = False
        else:
            # self.fixed_angle = self.player.angle
            self.fixed_angle = self.player.near_enemy_angle


    def _handle_attack(self,enemies):
        px, py = self.player.x, self.player.y
        facing = self.player.angle

        # print(str(len(enemies)))
        for enemy in enemies:
            if not enemy.is_alive():
                continue
            if self._check_hit(px, py, enemy, facing):
                anger_modifier = get_sin_modifier("憤怒", "player_attack_boost")
                modified_damage = round(self.damage * anger_modifier)

                enemy.on_hit(modified_damage)
                if self.is_in_cone(enemy):
                    self.apply_knockback(enemy)

    def _check_hit(self, px, py, enemy, facing):
        ex, ey = enemy.x, enemy.y

        if self.attack_type == AttackType.MELEE:
            return self._in_cone(px, py, ex, ey, facing, self.cone_angle, self.radius)
        elif self.attack_type == AttackType.SHOCKWAVE:
            return self._in_line(px, py, ex, ey, facing, self.radius)
        elif self.attack_type == AttackType.FAN_FIRE:
            return self._in_cone(px, py, ex, ey, self.fixed_angle, self.cone_angle, self.radius)
        elif self.attack_type == AttackType.AREA_MAGIC:
            return self._in_circle(px, py, ex, ey, self.radius)
        elif self.attack_type == AttackType.PROJECTILE:
            return self._in_line(px, py, ex, ey, self.player.near_enemy_angle, self.radius)
        elif self.attack_type == AttackType.PROJECTILE_RANDOM:
            for projectile_angle in self.projectile_angles:
                if self._in_line(px, py, ex, ey, projectile_angle, self.radius):
                    return True
            return False
        elif self.attack_type == AttackType.SPIN_SLASH:
            return self._in_circle(px, py, ex, ey, self.radius)
        elif self.attack_type == AttackType.BEAM:
            return self._in_line(px, py, ex, ey, facing, self.radius * 1.5)
        elif self.attack_type == AttackType.THRUST:
            return self._in_line(px, py, ex, ey, facing, self.radius)
        elif self.attack_type == AttackType.THRUST_CROSS:
            for thrust_angle in self.multi_angles:
                if self._in_line(px, py, ex, ey, thrust_angle, self.radius):
                    return True
            return False
        return False

    def _in_cone(self, px, py, ex, ey, facing, angle, radius):
        dx, dy = ex - px, ey - py
        dist = math.hypot(dx, dy)
        if dist > radius:
            return False
        theta = math.atan2(dy, dx)
        diff = abs((theta - facing + math.pi) % (2 * math.pi) - math.pi)
        return diff <= (angle / 2)

    def _in_line(self, px, py, ex, ey, facing, radius):
        dx, dy = ex - px, ey - py
        dist = math.hypot(dx, dy)
        if dist > radius:
            return False
        theta = math.atan2(dy, dx)
        diff = angle_diff(theta, facing)
        if diff > math.radians(15):
            return False

        # ← ここから壁判定チェック（step進めながら確認）
        steps = int(dist / 4)
        for i in range(1, steps + 1):
            check_x = px + math.cos(theta) * i * 4
            check_y = py + math.sin(theta) * i * 4
            if checkMapTile_pixel(int(check_x), int(check_y)):
                return False  # 壁にぶつかる → 判定不可！

        return True  # 範囲内＆向きOK＆遮蔽なし！

    def _in_circle(self, px, py, ex, ey, radius):
        return math.hypot(ex - px, ey - py) <= radius

    def draw(self):
        if self.frame < 0:
            return

        # if self.attack_type == AttackType.MELEE:
        #     self._draw_melee_area()
        #
        # elif self.attack_type == AttackType.SHOCKWAVE:
        #     self._draw_shockwave_area()
        #
        # elif self.attack_type == AttackType.FAN_FIRE:
        #     self._draw_fan_fire()
        #
        # elif self.attack_type == AttackType.AREA_MAGIC:
        #     self._draw_area_magic()
        #
        # elif self.attack_type == AttackType.PROJECTILE:
        #     self._draw_projectile()
        #
        # elif self.attack_type == AttackType.PROJECTILE_RANDOM:
        #     self._draw_projectile_random()
        #
        # elif self.attack_type == AttackType.SPIN_SLASH:
        #     self._draw_spin_slash()
        #
        # elif self.attack_type == AttackType.BEAM:
        #     self._draw_beam()
        #
        # elif self.attack_type == AttackType.THRUST:
        #     self._draw_thrust()
        #
        # elif self.attack_type == AttackType.THRUST_CROSS:
        #     # self._draw_thrust_cross()
        #     self._draw_thrust_cross()

        if self.name == WEAPON_NAME_GREATSWORD:
            self._draw_melee_area()

        # elif self.attack_type == AttackType.SHOCKWAVE:
        #     self._draw_shockwave_area()
        #
        elif self.name == WEAPON_NAME_SLASHAXE:
            self._draw_spin_slash()

        elif self.name == WEAPON_NAME_FLASHSPEAR:
            self._draw_projectile_random()

        elif self.name == WEAPON_NAME_BOOKOFFIRE:
            self._draw_fan_fire()

        elif self.name == WEAPON_NAME_BOOKOFTHUNDER:
            self._draw_area_magic()

        elif self.name == WEAPON_NAME_BOOKOFLIGHT:
            # self._draw_thrust_cross()
            self._draw_thrust_cross()

        elif self.name == WEAPON_NAME_BEAM:
            self._draw_beam()

        elif self.name == WEAPON_NAME_KNIFE:
            self._draw_projectile_knife()

        elif self.name == WEAPON_NAME_ARROW:
            self._draw_projectile_arrow()

        elif self.name == WEAPON_NAME_CRAW:
            self._draw_melee_claw()

        elif self.name == WEAPON_NAME_THROWING_KNIFE:
            self._draw_projectile_throw_knife()

        # elif self.attack_type == AttackType.THRUST:
        #     self._draw_thrust()
        #

    def _draw_melee_area(self):
        x, y = self.player.x, self.player.y
        angle = self.player.angle
        radius = self.radius
        cone_angle = self.cone_angle

        ease_out = lambda t: 1 - (1 - t) * (1 - t)  # 加速カーブ（ease-out）
        frame_ratio = ease_out(min(self.frame / self.duration, 1.0))
        sweep_angle = angle - cone_angle / 2 + cone_angle * frame_ratio
        shake = math.sin(self.frame * 0.5) * 1.5  # 微振動

        enhancement = self.traits.get("強化", 0) / 5 # Attack クラス側から参照する想定
        enhancement_scale = min(enhancement, 5) * 0.05  # 最大 +0.25まで
        scale = 0.9 + frame_ratio * 0.4 + enhancement_scale  # 強化で少しだけ大きくなる

        # scale = 0.9 + frame_ratio * 0.4  # 最大1.3倍ほど
        fx = x + math.cos(sweep_angle) * radius / 2 - 4
        fy = y + math.sin(sweep_angle) * radius / 2 - 4 + shake

        # pyxel.blt(int(fx), int(fy), 0, 16, 40, 16, 8, 0, math.degrees(sweep_angle), 1.5)
        pyxel.blt(int(fx), int(fy), 0, 16, 40, 16, 8, 0, math.degrees(sweep_angle), scale)

    def _draw_melee_claw(self):
        x, y = self.player.x, self.player.y
        angle = self.player.angle
        radius = self.radius
        cone_angle = self.cone_angle

        ease_out = lambda t: 1 - (1 - t) * (1 - t)  # 加速カーブ（ease-out）
        frame_ratio = ease_out(min(self.frame / self.duration, 1.0))
        # sweep_angle = angle - cone_angle / 2 + cone_angle * frame_ratio
        # shake = math.sin(self.frame * 0.5) * 1.5  # 微振動

        # enhancement = self.traits.get("強化", 0) / 5 # Attack クラス側から参照する想定
        # enhancement_scale = min(enhancement, 5) * 0.05  # 最大 +0.25まで
        # scale = 0.9 + frame_ratio * 0.4 + enhancement_scale  # 強化で少しだけ大きくなる

        # scale = 0.9 + frame_ratio * 0.4  # 最大1.3倍ほど
        # fx = x + math.cos(sweep_angle) * radius / 2 - 4
        # fy = y + math.sin(sweep_angle) * radius / 2 - 4 + shake

        # 斬撃を複数回描画
        for _ in range(3):  # 5つの斬撃を生成
            # プレイヤーからの距離をランダムに決定
            dist = radius * pyxel.rndi(50, 100) / 100.0

            # プレイヤーの向きからランダムな角度を決定
            # cone_angle / 2 で、プレイヤーの正面から左右に広がる範囲を指定
            rand_angle = angle + math.radians(pyxel.rndi(-45, 45))

            # 斬撃の位置を計算
            fx = x + math.cos(rand_angle) * dist -4
            fy = y + math.sin(rand_angle) * dist -4

            # 斬撃のサイズをランダムに調整
            scale = 0.8 + pyxel.rndi(0, 40) / 100.0

            # pyxel.blt(int(fx), int(fy), 0, 40, 56, 16, 8, 0, math.degrees(rand_angle), scale)
            pyxel.blt(int(fx), int(fy), 0, 32, 56, 8, 8, 0, math.degrees(rand_angle), scale)
        # # pyxel.blt(int(fx), int(fy), 0, 16, 40, 16, 8, 0, math.degrees(sweep_angle), 1.5)
        # pyxel.blt(int(fx), int(fy), 0, 32, 56, 16, 8, 0, math.degrees(sweep_angle), scale)

    def _draw_fan_fire(self):
        x, y = self.player.x, self.player.y
        angle = self.fixed_angle
        radius = self.radius
        cone_angle = self.cone_angle
        frame_ratio = min(self.frame / self.duration, 1.0)

        ease_out = lambda t: 1 - (1 - t) * (1 - t)  # 広がり感に使う
        spread = ease_out(frame_ratio) * radius  # 前進距離

        num_flames = 9  # 本数（角度方向の分布密度）

        for i in range(num_flames):
            flame_ratio = i / (num_flames - 1)
            flame_angle = angle - cone_angle / 2 + cone_angle * flame_ratio

            # プレイヤーから前方へ一定距離進む
            fx = x + math.cos(flame_angle) * spread
            fy = y + math.sin(flame_angle) * spread

            # ちょっと迫力感を付ける（大きさ or 振動）
            scale = 1.0 + math.sin(frame_ratio * math.pi) * 0.2

            pyxel.blt(int(fx), int(fy), 0, 0, 32, 8, 8, 0,
                      None, scale)

    def _draw_shockwave_area(self):
        x, y = self.player.x, self.player.y
        angle = self.player.angle
        radius = self.radius
        end_x = x + math.cos(angle) * radius
        end_y = y + math.sin(angle) * radius

        # スケール調整
        _scale = 1.0 + self.frame * 0.05

        # 武器の出現スタート位置（中心より少し奥）
        start_offset = radius * 0.3
        step_per_wave = radius * 0.2

        # フレームごとに描画数を増やす
        wave_count = min(self.frame, 5)  # 例：最大5個まで表示

        for i in range(wave_count):
            distance = start_offset + i * step_per_wave
            fx = x + math.cos(angle) * distance - 4
            fy = y + math.sin(angle) * distance - 4

            pyxel.blt(int(fx) + self.player.size // 2,
                      int(fy) + self.player.size // 2,
                      0, 0, 32, 8, 8, 0, None, _scale)

    def _draw_area_magic(self):
        x, y = self.player.x, self.player.y
        r = self.radius

        # pyxel.circ(x, y, r, 13)
        # pyxel.circb(x, y, r + 1, 7)

        particle_count = min(self.frame * 5, 20)  # 数増やす（例：最大40個）

        for i in range(particle_count):
            angle = math.radians(random.uniform(0, 360))  # ランダム配置
            dist = random.uniform(r * 0.3, r * 0.9)  # 内側〜外側まで広く

            fx = x + math.cos(angle) * dist - 4
            fy = y + math.sin(angle) * dist - 4
            scale = 1.0 + self.frame * 0.01

            pyxel.blt(int(fx), int(fy), 0, 8, 32, 8, 8, 0, None, scale)

    def _draw_projectile(self):
        x, y = self.player.x, self.player.y
        angle = self.player.near_enemy_angle
        radius = self.radius

        # # 距離ごとに壁衝突チェック
        max_distance = radius
        # for step in range(0, int(radius), 4):  # 4px刻み
        #     px = x + math.cos(angle) * step
        #     py = y + math.sin(angle) * step
        #     if checkMapTile_pixel(int(px), int(py)):
        #         max_distance = step
        #         break

        # 実際の進行距離（frame制限＆壁制限）
        step_per_frame = radius * 0.2
        distance = min(self.frame * step_per_frame, max_distance)

        # 座標計算＋演出（回転・拡大・揺らぎ）
        fx = x + math.cos(angle) * distance - 4
        fy = y + math.sin(angle) * distance - 4
        scale = 1.0 + self.frame * 0.05
        shake = math.sin(self.frame * 0.4) * 0.5
        fy += shake
        spin_rotation_deg = self.frame * 12

        # スプライト表示（回転付き）
        pyxel.blt(
            int(fx) + self.player.size // 2,
            int(fy) + self.player.size // 2,
            0, 32, 48, 8, 8, 0,
            # rotate=spin_rotation_deg % 360,
            rotate=math.degrees(self.player.near_enemy_angle),
            scale=scale
        )

        # 💥 衝突時の爆発演出（初回のみ）
        # if self.frame == 1 and max_distance < radius:
        #     boom_x = x + math.cos(angle) * max_distance
        #     boom_y = y + math.sin(angle) * max_distance
        #     pyxel.circ(boom_x, boom_y, 6, 10)
        #     pyxel.circb(boom_x, boom_y, 10, 7)
        #     pyxel.play(3, 6)

    def _draw_projectile_knife(self):
        x, y = self.player.x, self.player.y
        angle = self.player.near_enemy_angle
        radius = self.radius

        # # 距離ごとに壁衝突チェック
        max_distance = radius

        # 実際の進行距離（frame制限＆壁制限）
        step_per_frame = radius * 0.2
        distance = min(self.frame * step_per_frame, max_distance)

        # 座標計算＋演出（回転・拡大・揺らぎ）
        fx = x + math.cos(angle) * distance - 4
        fy = y + math.sin(angle) * distance - 4
        scale = 1.0 + self.frame * 0.05
        shake = math.sin(self.frame * 0.4) * 0.5
        fy += shake
        spin_rotation_deg = self.frame * 12

        # スプライト表示（回転付き）
        pyxel.blt(
            int(fx) + self.player.size // 2,
            int(fy) + self.player.size // 2,
            0, 32, 48, 8, 8, 0,
            # rotate=spin_rotation_deg % 360,
            rotate=math.degrees(self.player.near_enemy_angle),
            scale=scale
        )

    def _draw_projectile_arrow(self):
        x, y = self.player.x, self.player.y
        angle = self.player.near_enemy_angle
        radius = self.radius

        # # 距離ごとに壁衝突チェック
        max_distance = radius

        # 実際の進行距離（frame制限＆壁制限）
        step_per_frame = radius * 0.2
        distance = min(self.frame * step_per_frame, max_distance)

        # 座標計算＋演出（回転・拡大・揺らぎ）
        fx = x + math.cos(angle) * distance - 4
        fy = y + math.sin(angle) * distance - 4
        scale = 1.0 + self.frame * 0.05
        shake = math.sin(self.frame * 0.4) * 0.5
        fy += shake
        spin_rotation_deg = self.frame * 12

        # スプライト表示（回転付き）
        pyxel.blt(
            int(fx) + self.player.size // 2,
            int(fy) + self.player.size // 2,
            0, 40, 48, 8, 8, 0,
            # rotate=spin_rotation_deg % 360,
            rotate=math.degrees(self.player.near_enemy_angle),
            scale=scale
        )


    def _draw_projectile_random(self):
        x, y = self.player.x, self.player.y
        radius = self.radius
        step = radius * 0.2

        for angle in self.projectile_angles:
            # 衝突チェック：stepで壁までを探す
            max_distance = radius
            for test_step in range(0, int(radius), 4):  # 4px刻みで進行
                tx = x + math.cos(angle) * test_step
                ty = y + math.sin(angle) * test_step
                if checkMapTile_pixel(int(tx), int(ty)):
                    max_distance = test_step
                    break

            # 実際の描画距離（frame進行と壁制限の最小値）
            distance = min(self.frame * step, max_distance)
            fx = x + math.cos(angle) * distance - 4
            fy = y + math.sin(angle) * distance - 4

            rotation = math.degrees(angle)
            scale = 1.0 + self.frame * 0.05

            # pyxel.blt(int(fx), int(fy), 0, 0, 40, 8, 8, 0,
            pyxel.blt(int(fx), int(fy), 0, 16, 48, 16, 8, 0,
                      rotate=rotation, scale=scale)

            # 衝突した瞬間に爆ぜる演出（frame == 1 で一度だけ）
            if self.frame == 1 and max_distance < radius:
                boom_x = x + math.cos(angle) * max_distance
                boom_y = y + math.sin(angle) * max_distance
                pyxel.circ(boom_x, boom_y, 6, 10)
                pyxel.circb(boom_x, boom_y, 10, 7)
                # pyxel.play(3, 6)

    def _draw_projectile_throw_knife(self):
        x, y = self.player.x, self.player.y
        radius = self.radius
        step = radius * 0.2

        for angle in self.projectile_angles:
            # 衝突チェック：stepで壁までを探す
            max_distance = radius
            for test_step in range(0, int(radius), 4):  # 4px刻みで進行
                tx = x + math.cos(angle) * test_step
                ty = y + math.sin(angle) * test_step
                if checkMapTile_pixel(int(tx), int(ty)):
                    max_distance = test_step
                    break

            # 実際の描画距離（frame進行と壁制限の最小値）
            distance = min(self.frame * step, max_distance)
            fx = x + math.cos(angle) * distance - 4
            fy = y + math.sin(angle) * distance - 4

            rotation = math.degrees(angle)
            # scale = 1.0 + self.frame * 0.05
            scale = 1.0

            # pyxel.blt(int(fx), int(fy), 0, 0, 40, 8, 8, 0,
            pyxel.blt(int(fx), int(fy), 0, 40, 56, 8, 8, 0,
                      rotate=rotation, scale=scale)

            # 衝突した瞬間に爆ぜる演出（frame == 1 で一度だけ）
            if self.frame == 1 and max_distance < radius:
                boom_x = x + math.cos(angle) * max_distance
                boom_y = y + math.sin(angle) * max_distance
                pyxel.blt(int(boom_x), int(boom_y), 0, 40, 56, 8, 8, 0,
                          rotate=rotation, scale=scale)
                # pyxel.circ(boom_x, boom_y, 6, 10)
                # pyxel.circb(boom_x, boom_y, 10, 7)
                # pyxel.play(3, 6)


    def _draw_spin_slash(self):
        x, y = self.player.x, self.player.y
        angle = self.player.angle
        radius = self.radius

        # 1フレームごとに回転角度を増やす
        spin_angle = angle + self.frame * math.radians(20)  # ずつ回転

        # 回転に応じて刃の位置を決める
        fx = x + math.cos(spin_angle) * radius - 4
        fy = y + math.sin(spin_angle) * radius - 4

        # 回転演出（degrees）と拡大率
        rotation = math.degrees(spin_angle)
        scale = 1.0 + self.frame * 0.05

        # 微振動で迫力追加
        shake = math.sin(self.frame * 0.5) * 1.5
        fx += shake
        fy += shake

        # 軌跡ライン本数（過去フレーム分）
        trail_count = 5
        for i in range(trail_count):
            trail_frame = self.frame - i * 2
            if trail_frame < 0:
                continue

            trail_angle_start = angle + trail_frame * math.radians(15)
            trail_angle_end = angle + (trail_frame + 1) * math.radians(15)

            # 線の始点と終点（回転に沿った軌跡）
            x1 = int(x + math.cos(trail_angle_start) * radius)
            y1 = int(y + math.sin(trail_angle_start) * radius)
            x2 = int(x + math.cos(trail_angle_end) * radius)
            y2 = int(y + math.sin(trail_angle_end) * radius)

            # 軌跡の色は過去ほど暗めにして視覚的な“残像感”演出
            color = 10 - i  # pyxelカラーID（お好みで調整）

            pyxel.line(x1, y1, x2, y2, color)

        # 表示（スプライトは斬撃系がベスト）
        pyxel.blt(
            int(fx) + self.player.size // 2,
            int(fy) + self.player.size // 2,
            0,  # イメージバンク
            16, 32,  # スプライト座標
            16, 8,  # サイズ
            0,  # colkey（透過色）
            rotation,  # 回転角度
            scale  # 拡大率
        )

    def _draw_beam(self):
        x, y = self.player.x, self.player.y
        angle = self.player.angle
        radius = self.radius

        # --- 衝突判定 ---
        hit_x, hit_y = None, None
        for step in range(0, int(radius), 4):
            bx = x + math.cos(angle) * step
            by = y + math.sin(angle) * step

            if checkMapTile_pixel(int(bx), int(by)):  # ← ここで壁判定
                hit_x, hit_y = bx, by
                break

        # --- ビーム終端の座標（壁に当たったらそこまで） ---
        beam_length = min(
            radius,
            math.hypot(hit_x - x, hit_y - y) if hit_x else radius
        )
        end_x = x + math.cos(angle) * beam_length
        end_y = y + math.sin(angle) * beam_length

        # --- 太いビーム描画（線を並べて太くする） ---
        color_beam = pyxel.COLOR_GREEN
        for offset in range(-2, 3):
            pyxel.line(
                int(x), int(y + offset),
                int(end_x), int(end_y + offset),
                color_beam
            )

        # --- 爆ぜる演出（障害物に当たったとき） ---
        if hit_x:
            pyxel.circ(hit_x, hit_y, 5 + math.sin(self.frame * 0.3) * 2, 10)
            pyxel.circb(hit_x, hit_y, 10 + math.cos(self.frame * 0.2) * 3, 7)
            if self.frame == 1:
                pyxel.play(3, 6)

        # --- ビーム先端の光球（必要なら） ---
        pyxel.circ(end_x, end_y, 4 + self.frame * 0.5, 7)

        # --- ビーム中心部のゆらぎ粒子（オプション） ---
        if self.frame % 2 == 0:
            fx = x + math.cos(angle) * (radius * 0.5) + math.sin(self.frame * 0.3) * 3
            fy = y + math.sin(angle) * (radius * 0.5) + math.cos(self.frame * 0.3) * 3
            pyxel.circ(fx, fy, 2.5 + math.sin(self.frame * 0.2), color_beam)

    def _draw_thrust(self):
        x, y = self.player.x, self.player.y
        angle = self.player.angle
        radius = self.radius

        # スムーズ突き移動演出
        progress = min(self.frame / self.duration, 1.0)
        distance = radius * 0.6 + progress * radius * 0.4  # 最初は近く、後に奥まで

        fx = x + math.cos(angle) * distance - 4
        fy = y + math.sin(angle) * distance - 4

        # 微振動やシャープ効果（オプション）
        shake = math.sin(self.frame * 0.6) * 1.0
        fy += shake

        # 表示（スプライトは槍っぽいものにしてね！）
        pyxel.blt(int(fx), int(fy), 0, 16, 40, 16, 8, 0, None, 1.0)

    def _draw_thrust_cross_old(self):
        x, y = self.player.x, self.player.y
        radius = self.radius
        dist = radius * 0.9

        for angle in self.multi_angles:
            distance = self.radius * 0.6  # ← 距離を調整
            fx = x + math.cos(angle) * distance - 16 // 2
            fy = y + math.sin(angle) * distance - 8 // 2

            pyxel.blt(
                int(fx),
                int(fy),
                0, 16, 48, 16, 8, 0, rotate=math.degrees(angle), scale=1.5
            )

    def _draw_thrust_cross(self):
        x, y = self.player.x, self.player.y
        radius = self.radius
        sprite_w, sprite_h = 8, 8

        # 徐々に距離が進む（0→最大距離まで）
        progress = min(self.frame / self.duration, 1.0)
        # distance = radius * 0.3 + progress * radius * 0.5  # 最初短く→滑って伸びる
        distance = self.frame * progress

        for angle in self.multi_angles:
            fx = x + math.cos(angle) * distance - sprite_w // 2
            fy = y + math.sin(angle) * distance - sprite_h // 2

            spin_rotation_deg = self.frame * 12
            rotation = spin_rotation_deg % 360

            pyxel.blt(
                int(fx),
                int(fy),
                0,
                0, 40,  # スプライト位置
                sprite_w, sprite_h,
                0,
                rotate=rotation,
                scale=1.0 + progress * 0.3  # 徐々に大きく
            )