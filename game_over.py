import model
import pyxelen

from view import *
from sounds import *
from utils import *


def on_key_down(key, state):
    return model.initial_model


def view(renderer, state):
    renderer.draw_sprite(Image('images/game-over.png', FULLSCREEN), FULLSCREEN)


def on_update(state):
    return state.set_music(MUSIC_GAME_OVER)
