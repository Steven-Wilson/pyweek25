import importlib

import model
import view
import utils
import battle
import cut_scene
import main_menu
import options
import game_over


importlib.reload(view)
importlib.reload(utils)
importlib.reload(battle)
importlib.reload(cut_scene)
importlib.reload(main_menu)
importlib.reload(options)
importlib.reload(game_over)


screens = {
    model.Screen.MAIN_MENU: main_menu,
    model.Screen.OPTIONS: options,
    model.Screen.BATTLE: battle,
    model.Screen.CUT_SCENE: cut_scene,
    model.Screen.GAME_OVER: game_over,
}
