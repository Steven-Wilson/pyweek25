import model
import pyxelen

from view import *
from sounds import *
from utils import *


def dialog(state):
    return state.scene.dialog


def current(state):
    return dialog(state)[0]


def speaker(state):
    return current(state).speaker


def lines(state):
    return current(state).lines


def next_scene(state):
    return state.scene.next_scene


def on_key_down(key, state):
    if key == pyxelen.Key.RETURN:
        if len(dialog(state)) > 1:
            return set_scene(state, dialog=dialog(state)[1:])
        else:
            if state.scene.reset_health:
                characters = model.CHARACTERS
            else:
                characters = state.characters
            return state.set(
                scene=next_scene(state),
                characters=characters
            )
    else:
        return state


def on_update(state):
    return state.set_music(state.scene.music)


def view(renderer, state):
    renderer.draw_sprite(Image(state.scene.background, FULLSCREEN), FULLSCREEN)
    image = current(state).image
    if image != '':
        renderer.draw_sprite(Image(image, FULLSCREEN), FULLSCREEN)
    renderer.draw_sprite(CHARACTERS[speaker(state)], Box(10, 10, 64, 64))
    renderer.draw_text(MAIN_FONT, speaker(state), 42, 71, True)
    for i, line in enumerate(lines(state)):
        renderer.draw_text(MAIN_FONT, line, 100, 25 + i * 12, False)
