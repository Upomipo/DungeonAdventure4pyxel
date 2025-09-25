import json

import pyxel


def load_musics():
    global music_dungeon
    with open(f"./music/dungeon1.json", "rt") as fin:
        music_dungeon = json.loads(fin.read())
    for ch, sound in enumerate(music_dungeon):
        pyxel.sound(ch + 50).set(*sound)
        # pyxel.play(ch, ch+50, loop=True)
    with open(f"./music/title.json", "rt") as fin:
        music_title = json.loads(fin.read())
    for ch, sound in enumerate(music_title):
        pyxel.sound(ch + 53).set(*sound)
    with open(f"./music/gameover.json", "rt") as fin:
        music_title = json.loads(fin.read())
    for ch, sound in enumerate(music_title):
        pyxel.sound(ch + 56).set(*sound)
    with open(f"./music/camp.json", "rt") as fin:
        music_camp = json.loads(fin.read())
    for ch, sound in enumerate(music_camp):
        pyxel.sound(ch + 59).set(*sound)
        # pyxel.play(ch, ch+60, loop=True)
# gameover.json

def play_bgm_dungeon():
    for ch, sound in enumerate(music_dungeon):
        pyxel.play(ch, ch + 50, loop=True)

def play_bgm_title():
    for ch, sound in enumerate(music_dungeon):
        pyxel.play(ch, ch + 53, loop=True)

def play_bgm_gameover():
    for ch, sound in enumerate(music_dungeon):
        pyxel.play(ch, ch + 56, loop=True)

def play_bgm_camp():
    for ch, sound in enumerate(music_dungeon):
        pyxel.play(ch, ch + 56, loop=True)
