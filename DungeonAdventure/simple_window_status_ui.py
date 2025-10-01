import attack
import pyxel
from constants import PLAYER_JOB_FIGHTER, PLAYER_JOB_WIZARD, PLAYER_JOB_THIEF
from sin_system import draw_sin_icons, sins
from util import draw_text_with_border

StatusWindow=None
WeaponLevelUpWindow=None
CampScene=None
class SimpleStatus:
    def __init__(self, player):
        self.active = False
        self.player = player
        self.window_margin = 10

    def update(self):
        if not self.active:
            return

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            close_btn_width = 25
            close_btn_height = 10
            close_btn_x = pyxel.width - self.window_margin - close_btn_width
            close_btn_y = self.window_margin
            if close_btn_x < mx < (close_btn_x+close_btn_width) and close_btn_y < my < (close_btn_y+close_btn_height):
                self.active=False
            elif self.window_margin < mx < pyxel.width-self.window_margin and 75 < my < 120:
                # keys()で取得したオブジェクトをリストに変換する
                key_list = list(self.player.attacks.keys())

                for index, key in enumerate(key_list):
                    if attack.player_attack.name == key:
                        # 現在のインデックスを1増やし、% 演算子で終端処理を行う
                        next_index = (index + 1) % len(key_list)

                        # 修正：変換したリストのインデックスを使ってキーを取得
                        next_key = key_list[next_index]
                        # 取得したキーを使って辞書から次の攻撃を取得
                        attack.player_attack = self.player.attacks[next_key]

                        if self.player.job == PLAYER_JOB_THIEF:
                            next_sub_key = key_list[(next_index+1)%len(key_list)]
                            attack.player_attack_sub = self.player.attacks[next_sub_key]


                        break

    def draw(self):
        if not self.active:
            return

        #枠
        x, y, w, h = self.window_margin, self.window_margin, pyxel.width - (self.window_margin*2), pyxel.height - (self.window_margin*2)
        pyxel.rect(x, y, w, h, pyxel.COLOR_BLACK)
        pyxel.rectb(x, y, w, h, pyxel.COLOR_WHITE)

        #閉じるボタン
        close_btn_width = 25
        close_btn_height = 10
        close_btn_x = pyxel.width - self.window_margin - close_btn_width
        close_btn_y = self.window_margin
        pyxel.rect(close_btn_x, close_btn_y, close_btn_width, close_btn_height, pyxel.COLOR_BLACK)
        pyxel.rectb(close_btn_x, close_btn_y, close_btn_width, close_btn_height, pyxel.COLOR_WHITE)
        pyxel.text(close_btn_x+3, close_btn_y+3, "CLOSE", pyxel.COLOR_WHITE)

        #status表示
        #キャラクターと名前
        personality = ""
        if self.player.job == PLAYER_JOB_FIGHTER:
            pyxel.blt(20, 30, 2, 0, 72, 16, 32, 0, 0, 2.0)
            personality = "熱血漢、肉が好き"
        elif self.player.job == PLAYER_JOB_WIZARD:
            pyxel.blt(20, 30, 2, 16, 72, 16, 32, 0, 0, 2.0)
            personality = "天才肌、自信家"
        elif self.player.job == PLAYER_JOB_THIEF:
            pyxel.blt(20, 30, 2, 32, 72, 16, 32, 0, 0, 2.0)
            personality = "孤高、しつこい"
        # pyxel.text(20, 35, self.player.job, pyxel.COLOR_WHITE)
        draw_text_with_border(20, 35, f"職業：{self.player.job}", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
        draw_text_with_border(20, 45, f"性格：{personality}", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)

        #各種ステータス
        base_y = 55
        # pyxel.text(20, base_y, f"hp:{self.player.max_hp}", pyxel.COLOR_WHITE)
        draw_text_with_border(20, base_y, f"最大体力：{self.player.max_hp}", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
        base_y += 10
        draw_text_with_border(20, base_y, f"精神の残滓：{self.player.money}", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)

        # pyxel.text(20, 55, f"hp:{self.player.weapon}", pyxel.COLOR_WHITE)
        base_y += 20
        key_list = self.player.attacks.keys()
        for key in key_list:
            if key==attack.player_attack.name:
                draw_text_with_border(20, base_y,
                                      f"{self.player.attacks[key].display_name}:{self.player.attacks[key].exp}/{self.player.attacks[key].get_next_level_exp()}",
                                      pyxel.COLOR_WHITE, pyxel.frame_count % 16)
            elif attack.player_attack_sub and key == attack.player_attack_sub.name:
                    draw_text_with_border(20, base_y,
                                          f"{self.player.attacks[key].display_name}:{self.player.attacks[key].exp}/{self.player.attacks[key].get_next_level_exp()}",
                                          pyxel.COLOR_WHITE, pyxel.frame_count % 16)
            else:
                draw_text_with_border(20, base_y,
                                      f"{self.player.attacks[key].display_name}:{self.player.attacks[key].exp}/{self.player.attacks[key].get_next_level_exp()}",
                                      pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
            base_y += 10

        base_y += 10
        top_sins = sorted(sins.items(), key=lambda x: x[1]["power"], reverse=True)[:7]
        for i, (name, data) in enumerate(top_sins):
            x = 30 + i * 20
            y = 4
            if data["power"] >= 1:
                txt_x = 20
                txt_y = base_y + (i * 10)
                draw_text_with_border(txt_x, txt_y, f"{name}:{data["power"]}", data["color"], pyxel.COLOR_BLACK)

            elif data["power"] > 0:
                draw_text_with_border(x, y, name, data["color"], pyxel.COLOR_BLACK)
            else:
                pass

class SimpleWeaponLevelUpWindow:
    def __init__(self, player):
        self.active = False
        self.player = player
        self._window_margin = 10
        # self._levelUp_attack = attack.player_attack

    def update(self):
        if not self.active:
            return

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            close_btn_width = 50
            close_btn_height = 15
            close_btn_x = pyxel.width - self._window_margin - close_btn_width
            close_btn_y = pyxel.height - self._window_margin - 10
            level_up_btn_width = 50
            level_up_btn_height = 15
            level_up_btn_x = self._window_margin
            level_up_btn_y = pyxel.height - self._window_margin - 10

            if close_btn_x < mx < (close_btn_x+close_btn_width) and close_btn_y < my < (close_btn_y+close_btn_height):
                self.active=False
            elif level_up_btn_x < mx < (level_up_btn_x + level_up_btn_width) and level_up_btn_y < my < (
                        level_up_btn_y + level_up_btn_height):

                if self._levelUp_attack.exp >= self._levelUp_attack.get_next_level_exp() and self.player.money >= 100:
                    self._levelUp_attack.apply_traits()
                    self.player.money -= 100

            elif self._window_margin < mx < pyxel.width-self._window_margin and 125 < my < 185:
                # keys()で取得したオブジェクトをリストに変換する
                key_list = list(self.player.attacks.keys())

                if not self._levelUp_attack:
                    self._levelUp_attack = attack.player_attack
                for index, key in enumerate(key_list):
                    if self._levelUp_attack.name == key:
                        # 現在のインデックスを1増やし、% 演算子で終端処理を行う
                        next_index = (index + 1) % len(key_list)

                        # 修正：変換したリストのインデックスを使ってキーを取得
                        next_key = key_list[next_index]

                        # 取得したキーを使って辞書から次の攻撃を取得
                        self._levelUp_attack = self.player.attacks[next_key]

                        break

    def draw(self):
        if not self.active:
            return

        #枠
        x, y, w, h = self._window_margin, self._window_margin, pyxel.width - (self._window_margin * 2), pyxel.height - (self._window_margin * 2)
        pyxel.rect(x, y, w, h, pyxel.COLOR_BLACK)
        pyxel.rectb(x, y, w, h, pyxel.COLOR_WHITE)

        #閉じるボタン
        close_btn_width = 50
        close_btn_height = 15
        close_btn_x = pyxel.width - self._window_margin - close_btn_width
        close_btn_y = pyxel.height - self._window_margin - 10
        pyxel.rect(close_btn_x, close_btn_y-5, close_btn_width, close_btn_height, pyxel.COLOR_BLACK)
        pyxel.rectb(close_btn_x, close_btn_y-5, close_btn_width, close_btn_height, pyxel.COLOR_WHITE)
        draw_text_with_border(close_btn_x+10, close_btn_y, "用は無い", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)

        pyxel.blt(20, 30, 2, 0, 104, 16, 24, 0, 0, 2.0)

        #強化ボタン
        if self._levelUp_attack.exp >= self._levelUp_attack.get_next_level_exp():
            level_up_btn_width = 50
            level_up_btn_height = 15
            level_up_btn_x = self._window_margin
            level_up_btn_y = pyxel.height - self._window_margin - 10
            if self.player.money >= 100:
                pyxel.rect(level_up_btn_x, level_up_btn_y-5, level_up_btn_width, level_up_btn_height, pyxel.COLOR_BLACK)
                pyxel.rectb(level_up_btn_x, level_up_btn_y-5, level_up_btn_width, level_up_btn_height, pyxel.COLOR_WHITE)
                draw_text_with_border(level_up_btn_x+10, level_up_btn_y, "強化する", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
            else:
                draw_text_with_border(level_up_btn_x+10, level_up_btn_y-15, "よどんだ精神の数が足りない", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)


        pyxel.blt(20, 20, 2, 0, 104, 16, 24, 0, 0, 2.0)

        #語り
        base_y = 25
        base_x = 15
        draw_text_with_border(base_x, base_y, "仮面を被った女が語りかけ", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
        base_y += 10
        draw_text_with_border(base_x, base_y, "てきた", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
        base_y += 10
        draw_text_with_border(base_x, base_y, "「私はよどんだ精神を浄化", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
        base_y += 10
        draw_text_with_border(base_x, base_y, "して旅をしています", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
        base_y += 10
        draw_text_with_border(base_x, base_y, "百の精神が浄化されると、", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
        base_y += 10
        draw_text_with_border(base_x, base_y, "理性の残り火 が残ります", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
        base_y += 10
        draw_text_with_border(base_x, base_y, "それを武器に宿らせれば", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
        base_y += 10
        draw_text_with_border(base_x, base_y, "旅の助けとなりましょう」", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
        base_y += 20
        draw_text_with_border(base_x, base_y,
                              f"精神の残滓：{self.player.money}",
                              pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
        base_y += 10
        draw_text_with_border(base_x, base_y, "強化可能な武器は、", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
        base_y += 10
        draw_text_with_border(base_x, base_y, "赤く輝いています。", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
        base_y += 10
        key_list = self.player.attacks.keys()
        for key in key_list:
            font_color = pyxel.COLOR_WHITE
            back_color = pyxel.COLOR_BLACK
            if self.player.attacks[key].exp >= self.player.attacks[key].get_next_level_exp():
                font_color = pyxel.COLOR_RED
            if key==self._levelUp_attack.name:
                back_color = pyxel.frame_count % 16
            draw_text_with_border(20, base_y,
                                  f"{self.player.attacks[key].display_name}",
                                  font_color, back_color)
            base_y += 10

class CampSceneWindow:
    def __init__(self, player):
        self.active = False
        self.player = player
        self._window_margin = 0


    def update(self):
        global WeaponLevelUpWindow, StatusWindow
        if not self.active:
            return

        WeaponLevelUpWindow.update()
        if WeaponLevelUpWindow.active:
            return
        StatusWindow.update()
        if StatusWindow.active:
            return

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            close_btn_width = 50
            close_btn_height = 15
            close_btn_x = pyxel.width - self._window_margin - close_btn_width
            close_btn_y = pyxel.height - self._window_margin - 10

            if close_btn_x < mx < (close_btn_x+close_btn_width) and close_btn_y < my < (close_btn_y+close_btn_height):
                self.active=False
            elif self._window_margin -5 < mx < 120 and 70 < my < 80:
                print("実装予定")
            elif self._window_margin -5 < mx < 120 and 80 < my < 100:
                WeaponLevelUpWindow._levelUp_attack = attack.player_attack # TODO 暫定
                WeaponLevelUpWindow.active = True
            elif self._window_margin -5 < mx < 120 and 110 < my < 120:
                StatusWindow.active = True


    def draw(self):
        if not self.active:
            return

        WeaponLevelUpWindow.draw()
        if WeaponLevelUpWindow.active:
            return

        StatusWindow.draw()
        if StatusWindow.active:
            return

        #枠
        x, y, w, h = self._window_margin, self._window_margin, pyxel.width - (self._window_margin * 2), pyxel.height - (self._window_margin * 2)
        pyxel.rect(x, y, w, h, pyxel.COLOR_BLACK)
        pyxel.rectb(x, y, w, h, pyxel.COLOR_WHITE)
        base_x = x + 10
        base_y = y + 10

        # イメージ画像
        pyxel.blt(base_y, base_x, 2, 0, 128, 16, 16, 0, 0, 2.0)

        #閉じるボタン
        close_btn_width = 50
        close_btn_height = 15
        close_btn_x = pyxel.width - self._window_margin - close_btn_width
        close_btn_y = pyxel.height - self._window_margin - 10
        pyxel.rect(close_btn_x, close_btn_y-5, close_btn_width, close_btn_height, pyxel.COLOR_BLACK)
        pyxel.rectb(close_btn_x, close_btn_y-5, close_btn_width, close_btn_height, pyxel.COLOR_WHITE)
        draw_text_with_border(close_btn_x+10, close_btn_y, "出発する", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)

        base_y += 10
        draw_text_with_border(base_x, base_y, "君たちは焚火を囲んだ。", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
        base_y += 10
        draw_text_with_border(base_x, base_y, "その光が、和やかな", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
        base_y += 10
        draw_text_with_border(base_x, base_y, "安息のひとときを照らし出す。", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)

        # フレーバーテキスト確認ボタン（x=10, y=70)
        base_y += 30
        pyxel.rect(base_x-5, base_y-5, 110, 15, pyxel.COLOR_GRAY)
        pyxel.rectb(base_x-5, base_y-5, 110, 15, pyxel.COLOR_DARK_BLUE)
        draw_text_with_border(base_x, base_y, "入手した記録を確認する", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)

        # 浄化士ボタン（x=10, y=90)
        base_y += 20
        pyxel.rect(base_x-5, base_y-5, 110, 15, pyxel.COLOR_GRAY)
        pyxel.rectb(base_x-5, base_y-5, 110, 15, pyxel.COLOR_DARK_BLUE)
        draw_text_with_border(base_x, base_y, "武器の強化", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)

        # ステータスを確認（x=10, y=110)
        base_y += 20
        pyxel.rect(base_x-5, base_y-5, 110, 15, pyxel.COLOR_GRAY)
        pyxel.rectb(base_x-5, base_y-5, 110, 15, pyxel.COLOR_DARK_BLUE)
        draw_text_with_border(base_x, base_y, "ステータス", pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)

        #下部に景色の描画、今は特に代わりを表示
        pyxel.blt(base_x, pyxel.height-16, 2, 0, 72, 16, 16, 0, 0, 2.0)
        pyxel.blt(base_x+14, pyxel.height-16, 2, 16, 72, 16, 16, 0, 0, 2.0)
        pyxel.blt(base_x+28, pyxel.height-16, 2, 32, 72, 16, 16, 0, 0, 2.0)
