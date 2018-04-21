import random


def rolls(quantity, size):
    return list(sorted([
        random.randint(1, size)
        for _ in range(quantity)
    ]))


def explode_roll(quantity, size, advantage=0, disadvantage=0):
    advantage = advantage - disadvantage
    if advantage > 0:
        initial_rolls = rolls(quantity + abs(advantage), size)[-quantity:]
    elif advantage == 0:
        initial_rolls = rolls(quantity, size)
    else:
        initial_rolls = rolls(quantity + abs(advantage), size)[:quantity]

    num_max_rolls = sum(1 for r in initial_rolls if r == size)
    if num_max_rolls > 0:
        return explode_roll(num_max_rolls, size) + sum(initial_rolls)

    else:
        return sum(initial_rolls)


def roll(quantity, size, advantage=0, disadvantage=0):
    return explode_roll(1, 20) + explode_roll(
        quantity,
        size,
        advantage=advantage,
        disadvantage=disadvantage
    )


def clamp(value, minimum, maximum):
    if value < minimum:
        return minimum
    elif value > maximum:
        return maximum
    else:
        return value

def set_scene(state, **kwargs):
    return state.set(scene=state.scene.set(**kwargs))
