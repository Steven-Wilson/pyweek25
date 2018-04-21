import model
import pyxelen

from view import *
from sounds import *
from utils import *


def selection(state):
    return state.scene.selection


def select_next_option(state):
    return set_scene(state, selection=selection(state).next())


def select_prev_option(state):
    return set_scene(state, selection=selection(state).prev())


def music_volume(state):
    return state.music_volume


def set_music_volume(state, volume):
    return state.set(music_volume=volume)


def effects_volume(state):
    return state.effects_volume


def set_effects_volume(state, volume):
    return state.set(effects_volume=volume)


def adjust(getter, setter, state, amount):
    value = getter(state)
    value_adjusted = value + amount
    value_clamped = clamp(value_adjusted, 0, 127)
    if value_clamped != value:
        return setter(state, value_clamped).play_effect(FX_BLIP)
    else:
        return state


def increase_music_volume(state):
    return adjust(music_volume, set_music_volume, state, 1)


def decrease_music_volume(state):
    return adjust(music_volume, set_music_volume, state, -1)

def increase_effects_volume(state):
    return adjust(effects_volume, set_effects_volume, state, 1)


def decrease_effects_volume(state):
    return adjust(effects_volume, set_effects_volume, state, -1)


def increase_option(state):
    if selection(state) == model.SettingsSelection.MUSIC_VOLUME:
        return increase_music_volume(state)
    elif selection(state) == model.SettingsSelection.EFFECTS_VOLUME:
        return increase_effects_volume(state)
    else:
        return state


def decrease_option(state):
    if selection(state) == model.SettingsSelection.MUSIC_VOLUME:
        return decrease_music_volume(state)
    elif selection(state) == model.SettingsSelection.EFFECTS_VOLUME:
        return decrease_effects_volume(state)
    else:
        return state


def menu(state):
    return state.set(
        scene=model.MainMenu(
            selection=model.MainMenuSelection.OPTIONS
        )
    )


def on_key_down(key, state):
    if key == pyxelen.Key.DOWN:
        return select_next_option(state)
    elif key == pyxelen.Key.UP:
        return select_prev_option(state)
    elif key == pyxelen.Key.RIGHT:
        return increase_option(state)
    elif key == pyxelen.Key.LEFT:
        return decrease_option(state)
    elif key == pyxelen.Key.ESCAPE:
        return menu(state)
    else:
        return state


def on_update(state):
    return state


def view(renderer, state):
    renderer.draw_sprite(BAR, FULLSCREEN)
    renderer.draw_text(
        MAIN_FONT,
         'Options..................................ESC to Save',
         20, 20, False
    )

    renderer.draw_text(
        MAIN_FONT,
        '    Music Volume: ' + str(state.music_volume),
        20, 40, False
    )

    renderer.draw_text(
        MAIN_FONT,
        '    Effects Volume: ' + str(state.effects_volume),
        20, 60, False
    )

    if state.scene.selection == model.SettingsSelection.MUSIC_VOLUME:
        renderer.draw_sprite(RIGHT_ARROW, Box(16, 36, 16, 16))
    else:
        renderer.draw_sprite(RIGHT_ARROW, Box(16, 56, 16, 16))
