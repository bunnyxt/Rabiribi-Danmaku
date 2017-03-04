from functions import buff_debuff
from functions import run
from functions import spell_card
from functions import sprites
from math import sqrt
from math import asin
from os import remove

def snipe(origin_sprite, enemy_sprite):
    """
    snipe function here:

        snipe(Sprite, Sprite): return int

        return a rad value
    """
    delta_x = enemy_sprite.center[0] - origin_sprite.center[0]
    delta_y = enemy_sprite.center[1] - origin_sprite.center[1]
    distance = sqrt(delta_x ** 2 + delta_y ** 2)
    temp_snipe = asin(delta_y/distance)
    if delta_x < 0:
        if delta_y > 0:
            snipe = pi - temp_snipe
        elif delta_y < 0:
            snipe = -pi - temp_snipe
    else:
        snipe = temp_snipe
    return snipe

def clear_cache(*dir):
    if dir:
        for each in dir:
            ch = 'data/tmp/' + each + '/*.tmp'
            remove(ch)
    else:
        remove('del data/tmp/*/*.tmp')
    
"""
some local static number here.
"""
# Screen border
SCREEN_LEFT = 35
SCREEN_RIGHT = 415
SCREEN_TOP = 15
SCREEN_BOTTOM = 465

# Control
MOVE_LEFT = 'K_LEFT'
MOVE_RIGHT = 'K_RIGHT'
MOVE_UP = 'K_UP'
MOVE_DOWN = 'K_DOWN'

MOVE_SLOW = 'L_SHIFT'
SHOUTING = 'K_z'
AMULET = 'K_x'
BOOST = 'K_c'

SWITCH_MAGIC_LEFT = 'K_a'
SWITCH_MAGIC_RIGHT = 'K_s'