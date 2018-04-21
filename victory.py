import model
import pyxelen

from view import *
from sounds import *
from utils import *


def on_key_down(key, state):
    return state.set(scene=model.MainMenu(selection=model.MainMenuSelection.PLAY))


def view(renderer, state):
    renderer.draw_text(MAIN_FONT, 'you win!', 10, 10, False)


def on_update(state):
    return state
