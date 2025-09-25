import random

import pyxel

from simple_dialog_ui import SimpleDialog

from game_log import battle_log
from sin_system import sins

npc_event_table = {
    "npc_001": {
        "face_info": {"img": 2, "u": 16, "v": 0, "w": 16, "h": 16},
        "question": "目の前に魅惑的な悪魔が\n現れた\n手には貴重な魔導書を\n持っている\n悪魔はこの世の快楽を\n全て与えると言う",
        "choices": ["快楽に身を委ねる", "殺して魔導書を奪う"],
        "sin_effects": [  # 選択に応じた罪への影響
            {"type": "色欲", "delta": +2, "msg": "悪魔の嘲り笑う声だけが響いた"},
            {"type": "強欲", "delta": +1, "msg": "手に入れた魔導書は砂となって消えた"}
        ]
    },

    "npc_002": {
        "face_info": {"img": 2, "u": 0, "v": 0, "w": 16, "h": 16},
        "question": "目の前にかつての仲間が\n倒れている\n"
                    "その傍らには返り血を浴びた\n男が佇んでいた\n",
        "choices": ["怒りに身を任せ敵を討つ", "自分には関係のない男だ"],
        "sin_effects": [
            {"type": "憤怒", "delta": +2, "msg": "そこには二つの肉塊だけが存在している"},
            {"type": "怠惰", "delta": +1, "msg": "立ち去る背中に嘲笑が聞こえた気がした"}
        ]
    },
    "npc_003": {
        "face_info": {"img": 2, "u": 32, "v": 0, "w": 16, "h": 16},
        "question": "古い友人が、穏やかな笑みを\n浮かべて近づいてくる\n"
                    "今や彼は英雄として\n讃えられる存在となっていた\n"
                    "そんな彼が、あなたに静かに\nこう告げる\n"
                    "「君は誰より優れている」",
        "choices": ["そんな言葉、今さら要らない", "当然だ"],
        "sin_effects": [
            {"type": "嫉妬", "delta": +2, "msg": "友人は悲しげな表情を浮かべた"},
            {"type": "傲慢", "delta": +1, "msg": "「変わらないな」と、友人は優しく微笑んだ"}
        ]
    },
    "npc_004": {
        "face_info": {"img": 2, "u": 48, "v": 0, "w": 16, "h": 16},
        "question": "あなたの人生を狂わせた男が\n膝をついて頭を下げている。\n"
                    "「我が一族をお救いください。\n私が忠誠を誓えば…\nそれで良いはずです」\n"
                    "彼の声は震えているが、\n意識的な媚びを感じる。\n",
        "choices": ["屈服こそが正義だ", "復讐は終わっていない"],
        "sin_effects": [
            {"type": "傲慢", "delta": +2, "msg": "男は涙を流すが、一族は絶望している"},
            {"type": "憤怒", "delta": +1, "msg": "男は崩れ落ち、一族は死を覚悟した"}
        ]
    },
    "npc_005": {
        "face_info": {"img": 2, "u": 16, "v": 0, "w": 16, "h": 16},
        "question": "夜の城下町の小路\n"
                    "理想的な容姿を持つ人物と、\nあなたの想い人が笑顔で語らいながら\n歩いている。\n"
                    "手元には、悪魔に与えられた\n「姿を変える薬」と\n「渇望を殺す黒曜の刃」。\n",
        "choices": ["薬を飲み、想い人に近づく", "影から2人へ刃を向ける"],
        "sin_effects": [
            {"type": "色欲", "delta": +2, "msg": "薬は一夜しか効果が得られない"},
            {"type": "嫉妬", "delta": +1, "msg": "空虚な達成感、それだけが残る"}
        ]
    },
    "npc_006": {
        "face_info": {"img": 2, "u": 0, "v": 16, "w": 16, "h": 16},
        "question": "封印が解かれた魔法の保存食\n一欠片で、空腹は消えた\n"
                    "だが奇妙だった\n胃は満たされているのに\n心が疼く、もっと欲しい\n"
                    "魔法の保存食は尽きず\n延々に飢えを満たしてくれる\n",
        "choices": ["飢えを満たし続ける", "売却して金を得る"],
        "sin_effects": [
            {"type": "暴食", "delta": +2, "msg": "満腹なのになぜか幸福じゃない"},
            {"type": "強欲", "delta": +1, "msg": "飢えと引き換えに金を得た"}
        ]
    },
    "npc_007": {
        "face_info": {"img": 2, "u": 48, "v": 0, "w": 16, "h": 16},
        "question": "自分から栄光を奪った友人が\n胸を押さえ苦しんでいる。\n"
                    "周囲には誰もいない。\n",
        "choices": ["見て見ぬふりをする", "好機と捉えとどめを刺す"],
        "sin_effects": [
            {"type": "怠惰", "delta": +2, "msg": "関わり合いにはもうごめんだ"},
            {"type": "嫉妬", "delta": +1, "msg": "自分より優れているのは許せない"}
        ]
    },
    "npc_008": {
        "face_info": {"img": 2, "u": 0, "v": 16, "w": 16, "h": 16},
        "question": "「食べるとどんな願いも\n叶う果実」を手にいれた。\n"
                    "何を願う？\n",
        "choices": ["永遠に食欲を満たす", "他者より自らの幸福"],
        "sin_effects": [
            {"type": "暴食", "delta": +2, "msg": "満たされることのない渇望"},
            {"type": "嫉妬", "delta": +1, "msg": "その幸福は本物なのか"}
        ]
    },
}
# npc_id_current = None
current_event = None
dialog_npc = None
def trigger_npc_event(event_data):
    global dialog_npc, current_event

    # npc_id_current = npc_id
    data = event_data
    current_event = event_data

    color_1_type = data["sin_effects"][0]["type"]
    color_2_type = data["sin_effects"][1]["type"]
    choice_color_1 = sins[color_1_type]["color"]
    choice_color_2 = sins[color_2_type]["color"]
    sin_choice_colors = [choice_color_1, choice_color_2]

    dialog_npc = SimpleDialog(
        data["question"],
        data["choices"],
        choices_color=sin_choice_colors,
        face_info=data["face_info"]
    )

def update(sins):
    global dialog_npc, current_event
    if not dialog_npc:
        return

    if dialog_npc.active:
        dialog_npc.update()
    elif dialog_npc.result and not current_event is None:
        data = current_event
        data_effect = None
        if dialog_npc.result == data["choices"][0]:
            data_effect = data["sin_effects"][0]
        elif dialog_npc.result == data["choices"][1]:
            data_effect = data["sin_effects"][1]
        # print(data_effect)
        battle_log.add_log(data_effect["msg"])
        sins[data_effect["type"]]["power"] += data_effect["delta"]
        current_event = None

def get_npc():
    key = random.choice(list(npc_event_table.keys()))
    return npc_event_table[key]

