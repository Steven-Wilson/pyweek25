import random
import enum
import pyrsistent

import utils
from sounds import *


class Action(pyrsistent.PClass):
    effect_description = pyrsistent.field(type=str, initial='', mandatory=True)

    @property
    def name(self):
        return 'Action'

    def apply(self, state):
        return state


class EnemyAction(Action):
    countdown = pyrsistent.field(type=int, mandatory=True, initial=10)

    @property
    def name(self):
        return 'Enemy Turn'


class PendingAction(Action):
    countdown = pyrsistent.field(type=int, mandatory=True, initial=30)
    action = pyrsistent.field(type=Action, mandatory=True)
    result = pyrsistent.field(mandatory=True)


class ChooseAction(Action):
    selection = pyrsistent.field(type=int, mandatory=True, initial=0)


class TargetAction(Action):
    target = pyrsistent.field(type=int, mandatory=True, initial=0)

    def characters(self, state):
        raise NotImplemented('Do not use TargetAction Directly')

    def character(self, state):
        chars = self.characters(state)
        if len(chars) > self.target:
            return chars[self.target]
        else:
            return chars[len(chars) - 1]

    def set_character(self, state, character):
        target = self.character(state)
        return self.set_characters(
            state,
            pyrsistent.pvector(
                character if c is target else c
                for c in self.characters(state)
            )
        )

    def set_description(self, state, description):
        return state.set(
            scene=state.scene.set(
                action=state.scene.action.set(
                    effect_description=description
                )
            )
        )

    def damage(self, state, amount):
        amount -= 10
        if amount < 0:
            amount = 0
            desc = 'Missed'
        elif amount < 3:
            amount = 3
            desc = f'Did {amount} Damage'
        else:
            desc = f'Did {amount} Damage'
        return self.set_description(self.set_character(state, self.character(state).damage(amount)), desc)

    def heal(self, state, amount):
        amount -= 10
        if amount < 0:
            amount = 0
            desc = 'Fizzled'
        elif amount < 3:
            amount = 3
            desc = f'Did {amount} Healing'
        else:
            desc = f'Did {amount} Healing'
        return self.set_description(self.set_character(state, self.character(state).heal(amount)), desc)

class TargetEnemyAction(TargetAction):

    def characters(self, state):
        return state.scene.enemies

    def set_characters(self, state, characters):
        return state.set(
            scene=state.scene.set(
                enemies=characters
            )
        )


class TargetFriendlyAction(TargetAction):

    def characters(self, state):
        return state.characters

    def set_characters(self, state, characters):
        return state.set(characters=characters)


class KickAction(TargetEnemyAction):

    DESCRIPTION = [
        '''Kick or stomp your target''',
        '''Effective against small targets''',
        '''Ineffective against large targets''',
    ]

    @property
    def name(self):
        return 'Kick'

    def apply(self, state):
        if self.character(state).is_small:
            damage = utils.roll(1, 6, advantage=2)
        elif self.character(state).is_large:
            damage = utils.explode_roll(1, 20, disadvantage=1)
        elif self.character(state).is_medium:
            damage = utils.roll(1, 6)
        else:
            damage = 0
        return self.damage(state, damage)


class SlashAction(TargetEnemyAction):

    DESCRIPTION = [
        '''Swing you sword at a target''',
        '''Exceptionally effective against both''',
        '''    large and medium creatures''',
    ]

    @property
    def name(self):
        return 'Slash'

    def apply(self, state):
        return self.damage(state, utils.roll(1, 10, advantage=2))


SUMMON_INDEX = 100

class SummonAction(Action):

    DESCRIPTION = [
        '''Animates a pile of bones into a skeleton''',
    ]

    @property
    def name(self):
        return 'Animate Dead'

    def apply(self, state):
        global SUMMON_INDEX
        SUMMON_INDEX += 1
        return state.set(
            scene=state.scene.set(
                action=state.scene.action.set(
                    effect_description=f'Summoned a Skeleton Minion'
                ),
                enemies=state.scene.enemies.append(SKELETON_1.set(index=SUMMON_INDEX))
            )
        )


class FireballAction(Action):

    DESCRIPTION = [
        '''Create a small explosion centered on all enemies''',
        '''Less effective then fire bolt but hits all enemies''',
    ]

    @property
    def name(self):
        return 'Fireball'

    def apply(self, state):
        enemies = []
        total_damage = 0
        for enemy in state.scene.enemies:
            raw_damage = utils.roll(1, 10, disadvantage=1) - 10
            if raw_damage < 0:
                damage = 0
            elif raw_damage < 3:
                damage = 3
            else:
                damage = raw_damage
            enemy = enemy.set(health=enemy.health - damage)
            total_damage += damage
            if enemy.health < 0:
                enemy = enemy.set(health=0)
            enemies.append(enemy)
        return state.set(
            scene=state.scene.set(
                action=state.scene.action.set(
                    effect_description=f'Did {total_damage} Damage'
                ),
                enemies=pyrsistent.pvector(enemies)
            )
        )


class FireboltAction(TargetEnemyAction):

    DESCRIPTION = [
        '''Sling a ball of fire at your target''',
        '''Generally effective against all sizes''',
    ]

    @property
    def name(self):
        return 'Firebolt'

    def apply(self, state):
        return self.damage(state, utils.roll(1, 10))


class PunchAction(TargetFriendlyAction):

    DESCRIPTION = ['''Punch your target''']

    @property
    def name(self):
        return 'Punch'

    def apply(self, state):
        return self.damage(state, utils.roll(1, 6))


class EngulfAction(TargetFriendlyAction):

    DESCRIPTION = ['''''']

    @property
    def name(self):
        return 'Engulf'

    def apply(self, state):
        return self.damage(state, utils.roll(2, 6))


class CongealAction(TargetEnemyAction):

    DESCRIPTION = ['''''']

    @property
    def name(self):
        return 'Congeal'

    def apply(self, state):
        return state.set(
            scene=state.scene.set(
                action=state.scene.action.set(
                    effect_description=f'Congealed with other Oozes to Solidify'
                ),
                enemies=pyrsistent.pvector(
                    e.set(health=e.health + 10) for e in state.scene.enemies
                )
            )
        )


class BiteAction(TargetFriendlyAction):

    DESCRIPTION = ['''Bite your target''']

    @property
    def name(self):
        return 'Bite'

    def apply(self, state):
        return self.damage(state, utils.roll(1, 4))


class ThunderCannonAction(TargetEnemyAction):

    DESCRIPTION = [
        '''Fire a small cannonball out of a handheld cannon.''',
        '''Exceptionally effective against large targets.''',
        '''Loud and may draw additional attention.''',
        '''Ineffective against small targets.''',
    ]

    @property
    def name(self):
        return 'Thunder Cannon'

    def apply(self, state):
        return self.damage(state, utils.roll(2, 6))


class HealAction(TargetFriendlyAction):

    DESCRIPTION = [
        '''Covers your target in a radiant aura.''',
        '''Mends broken bones and closes wounds.''',
    ]

    @property
    def name(self):
        return 'Heal'

    def apply(self, state):
        return self.heal(state, utils.roll(1, 4))


class StabilizeAction(TargetFriendlyAction):

    DESCRIPTION = [
        '''Binds the wounds of target friend.''',
        '''Restores minimal hit points.''',
        '''Only works on friends who are unconscious''',
    ]

    @property
    def name(self):
        return 'Stabilize'

    def apply(self, state):
        if self.character(state).is_dead:
            return self.heal(state, 11)
        else:
            return state


class Character(pyrsistent.PClass):
    name = pyrsistent.field(type=str, mandatory=True)
    index = pyrsistent.field(type=int, mandatory=True, initial=1)
    health = pyrsistent.field(type=int, mandatory=True)
    max_health = pyrsistent.field(type=int, mandatory=True)
    size = pyrsistent.field(type=str, mandatory=True)
    actions = pyrsistent.pvector_field(Action)

    def damage(self, amount):
        if self.health - amount < 0:
            return self.set(health=0)
        else:
            return self.set(health=self.health - amount)

    def heal(self, amount):
        if self.health + amount > self.max_health:
            return self.set(health=self.max_health)
        else:
            return self.set(health=self.health + amount)

    @property
    def is_dead(self):
        return self.health <= 0

    @property
    def is_small(self):
        return self.size == 'Small'

    @property
    def is_medium(self):
        return self.size == 'Medium'

    @property
    def is_large(self):
        return self.size == 'Large'



class DialogItem(pyrsistent.PClass):
    speaker = pyrsistent.field(type=str, mandatory=True)
    lines = pyrsistent.pvector_field(str)
    image = pyrsistent.field(type=str, mandatory=True, initial='')


class Selection(enum.Enum):

    def next(self):
        options = list(self.__class__)
        for i, item in enumerate(options):
            if item == self:
                return options[(i + 1) % len(options)]

    def prev(self):
        options = list(self.__class__)
        for i, item in enumerate(options):
            if item == self:
                return options[(i - 1) % len(options)]


class Screen(Selection):
    MAIN_MENU = 'Main Menu'
    OPTIONS = 'Options'
    BATTLE = 'Battle'
    CUT_SCENE = 'Cut Scene'
    GAME_OVER = 'Game Over'


class MainMenuSelection(Selection):
    PLAY = 'PLAY'
    OPTIONS = 'OPTIONS'
    CREDITS = 'CREDITS'


class SettingsSelection(Selection):
    MUSIC_VOLUME = 'Music Volume'
    EFFECTS_VOLUME = 'Effects Volume'


class Scene(pyrsistent.PClass):
    pass


class CutScene(Scene):
    screen = Screen.CUT_SCENE
    music = pyrsistent.field(type=str, mandatory=True)
    background = pyrsistent.field(type=str, mandatory=True)
    next_scene = pyrsistent.field(type=Scene, mandatory=True)
    reset_health =pyrsistent.field(type=bool, mandatory=True, initial=False)
    dialog = pyrsistent.pvector_field(DialogItem)


class Battle(Scene):
    screen = Screen.BATTLE
    background = pyrsistent.field(type=str, mandatory=True)
    initiative = pyrsistent.field(type=int, mandatory=True)
    enemies = pyrsistent.pvector_field(Character)
    action = pyrsistent.field(type=Action, mandatory=True)
    next_scene = pyrsistent.field(type=Scene, mandatory=True)


class Settings(Scene):
    screen = Screen.OPTIONS
    selection = pyrsistent.field(type=(SettingsSelection,), mandatory=True)


class MainMenu(Scene):
    screen = Screen.MAIN_MENU
    selection = pyrsistent.field(type=(MainMenuSelection,), mandatory=True)


class GameOver(Scene):
    screen = Screen.GAME_OVER


class Model(pyrsistent.PClass):
    scene = pyrsistent.field(type=Scene, mandatory=True)
    effects = pyrsistent.pvector_field(str)
    music = pyrsistent.field(type=str, mandatory=True)
    music_volume = pyrsistent.field(type=int, mandatory=True)
    effects_volume = pyrsistent.field(type=int, mandatory=True)
    characters = pyrsistent.pvector_field(Character)

    def clear_effects(self):
        return self.set(effects=pyrsistent.pvector([]))

    def play_effect(self, effect):
        return self.set(effects=self.effects.append(effect))

    def set_music(self, music):
        return self.set(music=music)


CHARACTERS = pyrsistent.pvector([
    Character(
        name='Kerr',
        health=24,
        max_health=24,
        size="Medium",
        actions=pyrsistent.pvector([
            SlashAction(),
            KickAction(),
            StabilizeAction(),
        ])
    ),
    Character(
        name='Kivash',
        health=20,
        max_health=20,
        size="Medium",
        actions=pyrsistent.pvector([
            FireboltAction(),
            FireballAction(),
            StabilizeAction(),
        ])
    ),
    Character(
        name='Nyx',
        health=16,
        max_health=16,
        size="Small",
        actions=pyrsistent.pvector([
            ThunderCannonAction(),
            HealAction(),
            StabilizeAction(),
        ])
    ),
])


PIRATE_1 = Character(
    name='Pirate',
    health=20,
    max_health=20,
    size="Medium",
    actions=pyrsistent.pvector([
        SlashAction(),
        ThunderCannonAction(),
        HealAction(),
    ])
)

PIRATE_2 = PIRATE_1.set(index=2)
PIRATE_3 = PIRATE_1.set(index=3)
PIRATE_4 = PIRATE_1.set(index=4)


GIANT_RAT_1 = Character(
    name='Giant Rat',
    health=7,
    max_health=7,
    size="Small",
    actions=pyrsistent.pvector([
        BiteAction(),
    ])
)

GIANT_RAT_2 = GIANT_RAT_1.set(index=2)
GIANT_RAT_3 = GIANT_RAT_1.set(index=3)
GIANT_RAT_4 = GIANT_RAT_1.set(index=4)
GIANT_RAT_5 = GIANT_RAT_1.set(index=5)
GIANT_RAT_6 = GIANT_RAT_1.set(index=6)


SHIH_TZU_1 = Character(
    name='Feral Shih-Tzu',
    health=10,
    max_health=10,
    size="Small",
    actions=pyrsistent.pvector([
        BiteAction(),
    ])
)

SHIH_TZU_2 = SHIH_TZU_1.set(index=2)
SHIH_TZU_3 = SHIH_TZU_1.set(index=3)
SHIH_TZU_4 = SHIH_TZU_1.set(index=4)

SKELETON_1 = Character(
    name='Skeleton',
    health=5,
    max_health=5,
    size="Medium",
    actions=pyrsistent.pvector([
        PunchAction(),
    ])
)

SKELETON_2 = SKELETON_1.set(index=2)
SKELETON_3 = SKELETON_1.set(index=3)
SKELETON_4 = SKELETON_1.set(index=4)


OOZE_1 = Character(
    name='Ooze',
    health=20,
    max_health=20,
    size="Large",
    actions=pyrsistent.pvector([
        EngulfAction(),
        EngulfAction(),
        CongealAction()
    ])
)

OOZE_2 = OOZE_1.set(index=2)



CREDITS = CutScene(
    reset_health=True,
    background='images/outdoors.png',
    music=MUSIC_CREDITS,
    next_scene=MainMenu(selection=MainMenuSelection.PLAY),
    dialog=pyrsistent.pvector([
        DialogItem(speaker='Kerr', lines=[
            '''Thank you for playing my game''']),
        DialogItem(speaker='Pirate', lines=[
            '''Music is the generic 8-bit JRPG soundtrack by avgvst CC 3.0 license''',
            '''Music can be found at OpenGameArt.com''']),
        DialogItem(speaker='Feral Shih-Tzu', lines=[
            '''Sounds are courtesy of Juhana Junkala CC0 license''',
            '''The Essential Retro Video Game Sound Effects Collection [512 sounds]''']),
        DialogItem(speaker='Ghost', lines=[
            '''Cython was used for binding to SDL2. Thanks Cython Devs!''',
            '''SDL2 was used for binding to the platform.  Thanks SDL Devs!''']),
        DialogItem(speaker='DM', lines=[
            '''Apologies to Matthew Mercer of Critical Role Fame.''',
            '''I drew bad art of you and used it as my DM character.''']),
        DialogItem(speaker='Kivash', lines=[
            '''Finally, Apologies to my Dungeons and Dragons group.''',
            '''   Your characters were super railroaded.''',
            '''   I will never be forgiven. But I'll offer Pizza''']),
    ])
)


NECROMANCER = Character(
    name='Necromancer',
    health=100,
    max_health=100,
    size="Medium",
    actions=pyrsistent.pvector([
        SummonAction(),
    ])
)


ACT7 = CutScene(
    background="images/cave.png",
    music=MUSIC_VICTORY,
    next_scene=CREDITS,
    dialog=pyrsistent.pvector([
        DialogItem(
            speaker='DM',
            lines=[
                '''With the necromancer vanquished, the party searches''',
                '''the cave for their friends.  Both are found tied up to''',
                '''Pillars in a central room''']),
        DialogItem(
            speaker='DM',
            lines=[
                '''The party unties them, and devises a plan to get out of''',
                '''the cave.''']),
        DialogItem(
            speaker='Nyx',
            lines=[
                '''Feng, get in the bag, like you always do.''',
                '''-Feng jumps into the bag of excess carrying capacity.''']),
        DialogItem(
            speaker='Kivash',
            lines=[
                '''Hang on to me Nyx.  I'll come back for you Kerr and Malrich''',
                '-Nyx and Kivash go through a dimension window-',
                '-Kivash Ping-Pongs back and forth picking up the others-']),
    ])
)


FINAL_BATTLE = Battle(
    initiative = 0,
    action=ChooseAction(),
    background='images/cave.png',
    next_scene=ACT7,
    enemies=pyrsistent.pvector([
        NECROMANCER
    ])
)


ACT6 = CutScene(
    background="images/cave.png",
    music=MUSIC_BOSS,
    next_scene=FINAL_BATTLE,
    dialog=pyrsistent.pvector([
        DialogItem(
            speaker='Necromancer',
            lines=['''You dare destroy my assistants?''']),
        DialogItem(
            speaker='Necromancer',
            lines=['''I can fix them.  Once I've fixed you.''']),
    ])
)



SKELETON_BATTLE = Battle(
    initiative = 3,
    action=EnemyAction(countdown=30),
    background='images/cave.png',
    next_scene=ACT6,
    enemies=pyrsistent.pvector([
        SKELETON_1, SKELETON_2, SKELETON_3
    ])
)


ACT5A = CutScene(
    background="images/cave.png",
    next_scene=SKELETON_BATTLE,
    music=MUSIC_DANGER,
    reset_health=True,
    dialog=pyrsistent.pvector([
        DialogItem(
            speaker='DM',
            lines=[
                '''As the party steps into the cave, a tripwire is broken by''',
                '''Kerr and the cave entrance collapses.''']),
        DialogItem(
            speaker='Ghost',
            lines=[
                '''I told that bumbling imbecile to bring you here dead.''']),
        DialogItem(
            speaker='Ghost',
            lines=[
                '''No matter. You can still join my army.''']),
        DialogItem(
            speaker='Ghost',
            lines=[
                '''I'll have my assitants help sign you up.''']),
        DialogItem(
            speaker='DM',
            lines=[
                '''3 Skeletons emerge from dark nooks in the cave entrance.'''])
    ])
)



ACT5 = CutScene(
    background="images/outdoors.png",
    next_scene=ACT5A,
    music=MUSIC_SAFE,
    reset_health=True,
    dialog=pyrsistent.pvector([
        DialogItem(
            speaker='DM',
            lines=[
                '''The party catches their breath after killing such''',
                '''Demonic creatrues.''']),
        DialogItem(
            speaker='DM',
            lines=[
                '''Eventually they get on their way and finally reach the cave.''']),
    ])
)


SHIH_TZU_BATTLE = Battle(
    initiative = 0,
    action=ChooseAction(),
    background='images/outdoors.png',
    next_scene=ACT5,
    enemies=pyrsistent.pvector([
        SHIH_TZU_1, SHIH_TZU_2, SHIH_TZU_3, SHIH_TZU_4
    ])
)


ACT4A = CutScene(
    background="images/outdoors.png",
    next_scene=SHIH_TZU_BATTLE,
    music=MUSIC_SAFE,
    dialog=pyrsistent.pvector([
        DialogItem(
            speaker='DM',
            lines=[
                '''The moon is especially brilliant tonight.''',
                '''You hear the howling of wolves in the distance.''']),
        DialogItem(
            speaker='DM',
            lines=[
                '''The party travels along the path lit by the moon and''',
                '''a torch carried by Kivash.''']),
        DialogItem(
            speaker='Kerr',
            lines=[
                '''The cave is only another couple miles from here up that path.''']),
        DialogItem(
            speaker='DM',
            lines=[
                '''The howling turns into barking as a pack of small dogs''',
                '''approaches the party.''']),
    ])
)


ACT4 = CutScene(
    background="images/sewer.png",
    next_scene=ACT4A,
    music=MUSIC_SAFE,
    reset_health=True,
    dialog=pyrsistent.pvector([
        DialogItem(
            speaker='DM',
            lines=[
                '''The party searches the bodies of the dead pirates.''',
                '''They find a piece of parchment on one of them.''']),
        DialogItem(
            speaker='Kivash',
            image="images/note2.png",
            lines=[
                '''The note says "Find the advanturers.  Kill them and''',
                '''bring them to me at Knifepoint Cave. -Whisper"''']),
        DialogItem(
            speaker='Kivash',
            lines=['''Knifepoint Cave... Where is that?''']),
        DialogItem(
            speaker='Kerr',
            lines=[
                '''It's a cave my clan used to use as a stronghold.''',
                '''We haven't used it in years because it's haunted.''',
                '''The only person to have left it since speaks of a ghost.''',
                '''Everyone else is dead.''']),
        DialogItem(
            speaker='Kivash',
            lines=['''Haunted or not, we need to go.''']),
        DialogItem(
            speaker='DM',
            lines=[
            '''The party finds their way out of the sewer and leaves''',
            '''For Knifepoint Cave, a dozen miles north of Ryu along the''',
            '''base of the Crescent Mountains.'''])
    ])
)


RAT_PIRATE_BATTLE = Battle(
    initiative = 0,
    action=ChooseAction(),
    background='images/sewer.png',
    next_scene=ACT4,
    enemies=pyrsistent.pvector([
        PIRATE_1, PIRATE_2, GIANT_RAT_1, GIANT_RAT_2
    ])
)


ACT3 = CutScene(
    background="images/sewer.png",
    next_scene=RAT_PIRATE_BATTLE,
    music=MUSIC_REST,
    reset_health=True,
    dialog=pyrsistent.pvector([
        DialogItem(
            speaker='DM',
            lines=pyrsistent.pvector([
                '''The group decided to take a break to see to their wounds.'''])),
        DialogItem(
            speaker='DM',
            lines=pyrsistent.pvector([
                '''An hour goes by and the party is feeling rejuvinated.'''])),
        DialogItem(
            speaker='Nyx',
            lines=pyrsistent.pvector([
                '''Let's go.  We need to find the pirates before it is too late.'''])),
        DialogItem(
            speaker='DM',
            lines=pyrsistent.pvector([
                '''A few tunnels down a faint light eminates from a side room.''',
                '''You can hear squeaking and a couple of human voices.'''])),
        DialogItem(
            speaker='Kerr',
            lines=pyrsistent.pvector([
                '''No questions.  We go in there fighting.'''])),
        DialogItem(
            speaker='Nyx',
            lines=pyrsistent.pvector([
                '''I don't hear Feng.'''])),
        DialogItem(
            speaker='Kivash',
            lines=pyrsistent.pvector([
                '''If we run in there, kill them, and Feng isn't there...'''])),
        DialogItem(
            speaker='Nyx',
            lines=pyrsistent.pvector([
                '''So we try to talk then.'''])),
        DialogItem(
            speaker='DM',
            lines=pyrsistent.pvector([
                '''The party enters the room and sees 2 pirates feeding giant rats.''',
                '''One of the pirates turns to the party.'''])),
        DialogItem(
            speaker='Pirate',
            lines=pyrsistent.pvector([
                '''Idiots.  All adventurers are idiots.''',
                '''You really think your friend would be here?''',
                '''I have my orders.'''])),
        DialogItem(
            speaker='DM',
            lines=pyrsistent.pvector([
                '''The pirate shakes a piece of parchment as he says he has orders.''',
                '''He then pulls a scimitar from his belt and barks an order at the rats.''']))
    ])
)


RAT_BATTLE = Battle(
    initiative = 0,
    background='images/sewer.png',
    action=ChooseAction(),
    next_scene=ACT3,
    enemies=pyrsistent.pvector([
        GIANT_RAT_1, GIANT_RAT_2, GIANT_RAT_3, GIANT_RAT_4, GIANT_RAT_5, GIANT_RAT_6
    ])
)


ACT2 = CutScene(
    background='images/sewer.png',
    next_scene=RAT_BATTLE,
    music=MUSIC_BATTLE,
    dialog=pyrsistent.pvector([
        DialogItem(
            speaker='DM',
            lines=pyrsistent.pvector([
                '''With the oozes dead, the 3 friends continued through the sewer.''',
                ''' ''',
                '''A realization then came over Nyx.''',
            ])
        ),
        DialogItem(
            speaker='Nyx',
            lines=pyrsistent.pvector(['''We're literally in a sewer.'''])
        ),
        DialogItem(
            speaker='Kerr',
            lines=pyrsistent.pvector(['''Yea. So what?'''])
        ),
        DialogItem(
            speaker='Nyx',
            lines=pyrsistent.pvector([
                '''Well, it's starting to feel like we're in a game.''',
                '''Next thing you know, we're going to be killing rats.'''])
        ),
        DialogItem(
            speaker='Kivash',
            lines=pyrsistent.pvector([
                '''That would explain that squeaking sound that's getting closer.'''
            ])
        )
    ]),
)


OOZE_BATTLE = Battle(
    initiative=3,
    background='images/sewer.png',
    action=EnemyAction(countdown=30),
    next_scene=ACT2,
    enemies=pyrsistent.pvector([
        OOZE_1, OOZE_2
    ])
)


ACT1_A = CutScene(
    background='images/sewer.png',
    next_scene=OOZE_BATTLE,
    music=MUSIC_SAFE,
    dialog=pyrsistent.pvector([
        DialogItem(
            speaker='DM',
            lines=pyrsistent.pvector([
                '''The party hurries to the sewer grate, slides it open, and''',
                '''   jumps into the sewer.'''])
        ),
        DialogItem(
            speaker='DM',
            lines=pyrsistent.pvector([
                '''Just as you get off the ladder,  you realize it is dark''',
                '''Kivash lights a torch and that's when you notice''',
                '''two large gelatinous blobs approaching.'''])
        )
    ])
)

ACT1 = CutScene(
    background='images/bar.png',
    next_scene=ACT1_A,
    music=MUSIC_SAFE,
    dialog=pyrsistent.pvector([
        DialogItem(
            speaker='DM',
            lines=pyrsistent.pvector([
                '''3 friends gathered in the roaring hearth tavern in Ryu, a pirate city''',
                '''on the southern edge of Runia to discuss a plan to rescue a friend who''',
                '''was taken by a secretive cult that most people believe a myth.'''])
        ),
        DialogItem(
            speaker='Kerr',
            lines=pyrsistent.pvector([
                '''I don't care why they took him.  We have to get him back.'''])
        ),
        DialogItem(
            speaker='Kerr',
            lines=pyrsistent.pvector([
                '''Malrich is my friend...  He would come save me.''',
                '''I don't want to wait.''',
                '''I'll just go shake down some thugs for information.'''])
        ),
        DialogItem(
            speaker='Nyx',
            lines=pyrsistent.pvector([
                '''He was taken by the whisper not some everyday thugs.''',
                '''We can't just go get him.  For one, we don't know where he is.''',
                '''Even if we did, it's unlikely we can just stroll in and get him.''',
                '''We're dealing with a cult that was a myth until tonight.'''])
        ),
        DialogItem(
            speaker='Kivash',
            lines=pyrsistent.pvector([
                '''We all care about him, but Malrich is a survivor.''',
                '''We need to be smart.  Gather information, make a plan.'''])
        ),
        DialogItem(
            speaker='Kivash',
            lines=pyrsistent.pvector([
                '''Once we have a plan, we won't hesitate.''',
                '''They will regret crossing you Kerr.  I promise.'''])
        ),
        DialogItem(
            speaker='Nyx',
            lines=pyrsistent.pvector([
                '''Give Feng time. He has a knack for obtaining information.''',
                '''We need that. We need to know where to find the whispered court.''',
                '''He should be back any minute.'''])
        ),
        DialogItem(
            speaker='DM',
            lines=pyrsistent.pvector([
                '''At that point, a burly man with a limp drops a piece''',
                '''of parchment on the table casually as he walks by.''',
                '''He hurries out of the establishment before anyone can stop him.'''])
        ),
        DialogItem(
            speaker='Kivash',
            lines=pyrsistent.pvector([
                '''-Kivash picks up the parchment-''',
                '''It's a note.'''
            ])
        ),
        DialogItem(
            speaker='Kivash',
            image='images/note1.png',
            lines=pyrsistent.pvector([
                '''The note says "If you ever want to see your feline friend again,''',
                '''come find me in the sewers tonight."'''])
        ),
        DialogItem(
            speaker='Kerr',
            lines=pyrsistent.pvector(['''First Malrich is taken.'''])
        ),
        DialogItem(
            speaker='Kerr',
            lines=pyrsistent.pvector(['''Now Feng is taken.'''])
        ),
        DialogItem(
            speaker='Kerr',
            lines=pyrsistent.pvector([
                '''This night keeps getting worse.''',
                '''...''',
                '''-Runs out of the tavern after the man-'''])
        ),
        DialogItem(
            speaker='Nyx',
            lines=pyrsistent.pvector([
                '''Ugh. Come back Kerr!  We need to stick together!''',
                '''...''',
                '''-Runs after Kerr-'''])
        ),
        DialogItem(
            speaker='Kivash',
            lines=pyrsistent.pvector([
                '''-Drops 10 gold on the table for the tab and hurries after them-'''])
        ),
        DialogItem(
            speaker='DM',
            lines=pyrsistent.pvector([
                '''Kerr chases after the pirate, but ends up at the next intersection''',
                '''Kerr looks around but is completely unsure of where he went.'''])
        ),
        DialogItem(
            speaker='DM',
            lines=pyrsistent.pvector([
                '''After a momemnt passes, Nyx and Kivash catch up with Kerr.'''])
        ),
        DialogItem(
            speaker='Kivash',
            lines=pyrsistent.pvector([
                '''Calm down Kerr.  We're going.''',
                '''There's a sewer grate a couple blocks the other way.'''])
        ),
    ])
)


initial_model = Model(
    scene=MainMenu(selection=MainMenuSelection.PLAY),
    music=MUSIC_MENU,
    music_volume=10,
    effects_volume=5,
    characters=CHARACTERS,
)

