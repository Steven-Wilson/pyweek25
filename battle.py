import random
import model
import pyxelen

from view import *
from sounds import *
from utils import *


RAMP = [80, 75, 68, 59, 48, 35, 20, 3, 8, 15, 23, 33, 45, 56, 65, 72, 77]
RAMP += [78, 78, 80, 80, 80, 80, 81, 81, 81, 81, 81, 81, 81]
RAMP = list(reversed(RAMP))


def action(state):
    return state.scene.action


def target(state):
    if targeting_enemy(state):
        return enemies(state)[action(state).target]
    elif targeting_friend(state):
        return friends(state)[action(state).target]
    else:
        raise ValueError('Battle currently does not have a target')


def choosing_action(state):
    return isinstance(action(state), model.ChooseAction)


def pending_action(state):
    return isinstance(action(state), model.PendingAction)


def is_enemy_turn(state):
    return isinstance(action(state), model.EnemyAction)


def targeting(state):
    return isinstance(action(state), model.TargetAction)


def targeting_enemy(state):
    return isinstance(action(state), model.TargetEnemyAction)


def targeting_friend(state):
    return isinstance(action(state), model.TargetFriendlyAction)


def active_character(state):
    return initiative_order(state)[0]


def next_character(state):
    if len(initiative_order(state)) > 1:
        return initiative_order(state)[1]
    else:
        return initiative_order(state)[0]


def friends(state):
    return state.characters


def enemies(state):
    return state.scene.enemies


def initiative(state):
    return state.scene.initiative


def initiative_order(state):
    cut = initiative(state)
    everyone = friends(state) + enemies(state)
    return everyone[cut:] + everyone[:cut]


def next_turn_initiative(state):
    return (initiative(state) + 1) % len(initiative_order(state))


def next_turn_action(state):
    if next_character(state) in enemies(state):
        return model.EnemyAction(countdown=30)
    else:
        return model.ChooseAction()


def all_dead(lst):
    return all(c.health == 0 for c in lst)


def all_players_dead(state):
    return all_dead(friends(state))


def all_enemies_dead(state):
    return all_dead(enemies(state))


def set_action(state, action):
    return set_scene(state, action=action)


def choose_action(state):
    character = active_character(state)
    selection = action(state).selection
    return set_action(state, character.actions[selection])


def queue_action(state):
    return set_action(
        state,
        action=model.PendingAction(
            countdown=len(RAMP) - 1,
            action=action(state),
            result=action(state).apply(state)
        )
    ).play_effect(FX_SELECT)


def valid_selection(state, character):
    if choosing_action(state):
        return False
    elif pending_action(state):
        return False
    elif targeting_enemy(state):
        return character in enemies(state)
    elif targeting_friend(state):
        return character in friends(state)
    else:
        return False


def choose_action_key_down(key, state):
    if key == pyxelen.Key.RETURN:
        return choose_action(state).play_effect(FX_BLIP)
    elif key == pyxelen.Key.ESCAPE:
        return state
    elif key == pyxelen.Key.DOWN:
        return set_action(state, action(state).set(
            selection=(action(state).selection + 1) % len(active_character(state).actions)
        )).play_effect(FX_BLIP)
    elif key == pyxelen.Key.UP:
        return set_action(state, action(state).set(
            selection=(action(state).selection - 1) % len(active_character(state).actions)
        )).play_effect(FX_BLIP)
    else:
        return state


def target_key_down(key, state, options):
    if key == pyxelen.Key.RETURN:
        return queue_action(state)
    elif key == pyxelen.Key.RIGHT:
        return set_action(state, action(state).set(
            target=(action(state).target + 1) % len(options)
        )).play_effect(FX_BLIP)
    elif key == pyxelen.Key.LEFT:
        return set_action(state, action(state).set(
            target=(action(state).target - 1) % len(options)
        )).play_effect(FX_BLIP)
    elif key == pyxelen.Key.ESCAPE:
        return set_action(state, model.ChooseAction())
    else:
        return state


def target_enemy_key_down(key, state):
    return target_key_down(key, state, enemies(state))


def target_friend_key_down(key, state):
    return target_key_down(key, state, friends(state))


def on_key_down(key, state):
    if active_character(state).is_dead:
        return next_turn(state)
    if is_enemy_turn(state):
        return state
    elif pending_action(state):
        if key == pyxelen.Key.RETURN:
            return next_turn(action(state).result)
        else:
            return state
    elif choosing_action(state):
        return choose_action_key_down(key, state)
    elif targeting_enemy(state):
        return target_enemy_key_down(key, state)
    elif targeting_friend(state):
        return target_friend_key_down(key, state)
    else:
        return state


def next_turn(state):
    return set_scene(
        state,
        action=next_turn_action(state),
        initiative=next_turn_initiative(state)
    )


def alive_friends(state):
    return model.pyrsistent.pvector(c for c in friends(state) if not c.is_dead)


def remove_dead_enemies(state):
    return set_scene(state, enemies=model.pyrsistent.pvector(
        e for e in enemies(state) if not e.is_dead
    ))


def select_target(state):
    friendlies = [
        (i, c)
        for i, c in zip(range(100), friends(state))
        if not c.is_dead
    ]
    index, _ = random.choice(friendlies)
    return index


def on_update(state):
    state = state.set_music(MUSIC_BATTLE)
    state = remove_dead_enemies(state)
    if active_character(state).is_dead:
        return next_turn(state)
    elif pending_action(state):
        act = action(state)
        if action(state).countdown > 0:
            return set_action(state, act.set(countdown=act.countdown - 1))
        else:
            return state
    elif all_players_dead(state):
        return state.set(scene=model.GameOver())
    elif all_enemies_dead(state):
        return state.set(scene=state.scene.next_scene)
    elif is_enemy_turn(state):
        act = random.choice(active_character(state).actions)
        if isinstance(act, model.TargetAction):
            target=select_target(state)
            act = act.set(target=target)
        return set_action(
            state,
            action=model.PendingAction(
                countdown=len(RAMP) - 1,
                action=act,
                result=act.apply(state)
            )
        )
    elif not targeting(state) and not choosing_action(state):
        return queue_action(state)
    else:
        return state


def draw_player_status(renderer, state):
    for i, character in enumerate(friends(state)):
        renderer.draw_sprite(
            CHARACTERS[character.name],
            Box(400, i * 64, 64, 64)
        )
        renderer.draw_text(MAIN_FONT, str(character.health) + ' HP', 468, i * 64 + 20, False),
        renderer.draw_text(MAIN_FONT, 'of', 480, i * 64 + 32, False),
        renderer.draw_text(MAIN_FONT, str(character.max_health) + ' HP', 468, i * 64 + 44, False),


def draw_initiative_tracker(renderer, state):
    for i, character in reversed(list(enumerate(initiative_order(state)))):
        xpos = 96 + i * 32
        ypos = 230 - (32 if valid_selection(state, character) else 0)

        if character == active_character(state):
            box = Box(xpos - 32, 198, 96, 96)
        else:
            box = Box(xpos, ypos, 64, 64)
        renderer.draw_sprite(CHARACTERS[character.name], box)
        if character.health == 0:
            renderer.draw_sprite(DEAD_OVERLAY, box)

        arrow_box = Box(box.x + int(box.w / 2) - 8, box.y - 16, 16, 16)
        if targeting_enemy(state):
            if enemies(state)[action(state).target] == character:
                renderer.draw_sprite(DOWN_ARROW, arrow_box)
        elif targeting_friend(state):
            if friends(state)[action(state).target] == character:
                renderer.draw_sprite(DOWN_ARROW, arrow_box)


def draw_status_header(renderer, text):
    renderer.draw_sprite(TITLE_BAR, Box(72, 0, 256, 32))
    renderer.draw_text(MAIN_FONT, text, 200, 15, True)


def draw_target_info(renderer, state):
    character = target(state)
    percent_health = character.health / character.max_health
    if percent_health < 0.1:
        descriptor = "Near-Death"
    elif percent_health < 0.5:
        descriptor = "Bloodied"
    elif percent_health < 1.0:
        descriptor = "Healthy"
    else:
        descriptor = "Untouched"
    renderer.draw_text(
        MAIN_FONT,
        f'{active_character(state).name} using {action(state).name} on {character.name}',
        200,
        50, True
    )
    renderer.draw_text(MAIN_FONT, "Target Health: " + descriptor, 200, 62, True)
    renderer.draw_text(MAIN_FONT, "Target Size: " + character.size, 200, 74, True)


def draw_action_selector(renderer, state):
    act = action(state)
    character = active_character(state)
    for i, a in enumerate(character.actions):
        renderer.draw_text(MAIN_FONT, a.name, 42, 42 + 20 * i, False)
        if act.selection == i:
            renderer.draw_sprite(RIGHT_ARROW, Box(24, 38 + 20 * i, 16, 16))
    for i, line in enumerate(character.actions[act.selection].DESCRIPTION):
        renderer.draw_text(MAIN_FONT, line, 100, 60 + i * 12, False)


def draw_pending_action(renderer, state):
    act = action(state).action
    countdown = action(state).countdown
    desc = action(state).result.scene.action.effect_description
    renderer.draw_sprite(
        RIGHT_ARROW,
        Box(200 - 16, 104 - 16, 32, 32)
    )
    if hasattr(act, 'character'):
        renderer.draw_sprite(
            CHARACTERS[act.character(state).name],
            Box(200 - 64 + (20 + RAMP[countdown]), 104 - 64, 128, 128)
        )
    renderer.draw_sprite(
        CHARACTERS[active_character(state).name],
        Box(200 - 64 - (20 + RAMP[countdown]), 104 - 64, 128, 128)
    )
    draw_status_header(renderer, act.name)
    renderer.draw_text(MAIN_FONT, desc, 200, 104 + 64 + 12, True)


def view(renderer, state):
    renderer.draw_sprite(Image(state.scene.background, FULLSCREEN), FULLSCREEN)
    draw_player_status(renderer, state)
    draw_initiative_tracker(renderer, state)
    if targeting(state):
        draw_target_info(renderer, state)
        draw_status_header(renderer, "Pick a Target")
    elif choosing_action(state):
        draw_action_selector(renderer, state)
        draw_status_header(renderer, "Pick an Action for " + active_character(state).name)
    elif pending_action(state):
        draw_pending_action(renderer, state)
