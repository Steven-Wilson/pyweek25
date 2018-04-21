import model
import pyxelen

from view import *
from sounds import *
from utils import *


def set_scene(state, **kwargs):
    return state.set(scene=state.scene.set(**kwargs))


def selection(state):
    return state.scene.selection


def select_next(state):
    state = set_scene(state, selection=selection(state).next())
    return state.play_effect(FX_BLIP)


def select_prev(state):
    state = set_scene(state, selection=selection(state).prev())
    return state.play_effect(FX_BLIP)


def select(state):
    if selection(state) == model.MainMenuSelection.PLAY:
        return state.set(scene=model.ACT1).play_effect(FX_SELECT)
    elif selection(state) == model.MainMenuSelection.OPTIONS:
        return state.set(
            scene=model.Settings(
                selection=model.SettingsSelection.MUSIC_VOLUME
            )
        ).play_effect(FX_SELECT)
    elif selection(state) == model.MainMenuSelection.CREDITS:
        return state.set(scene=model.CREDITS)
    else:
        return state


def on_key_down(key, state):
    if key == pyxelen.Key.DOWN:
        return select_next(state)
    elif key == pyxelen.Key.UP:
        return select_prev(state)
    elif key == pyxelen.Key.RETURN:
        return select(state)
    else:
        return state


def on_update(state):
    return state.set_music(MUSIC_MENU)


def view(renderer, state):
    renderer.draw_sprite(MENU_BACKGROUND, FULLSCREEN)
    for i, s in enumerate(model.MainMenuSelection):
        renderer.draw_text(MAIN_FONT, s.value, 210, 144 + i * 20, False)
        if selection(state) == s:
            renderer.draw_sprite(RIGHT_ARROW, Box(190, 140 + i * 20, 16, 16))
