import pygame
import math
import pickle
import os
import abc
import functions
from functions.action import DanmakuAction
from functions.action import ElfAction
from functions.action import direction
# from functions.values import screenborder
# from functions.values import damagetype
from functions.values import *
from functions import snipe
from math import pi
import time

# under development
class position(list):
    def __init__(self):
        super().__init__()
        self.x = 0
        self.y = 0

    def set(self, value):
        if len(value)!=2:
            raise TypeError
        if isinstance(value, (tuple, list)):
            self.x, self.y = value
        elif isinstance(value, pygame.sprite.Sprite):
            self.x, self.y = tuple(value.center)
        else:
            raise TypeError

    def __getitem__(self, y):
        if y==0:
            return self.x
        elif y==1:
            return self.y
        else:
            raise IndexError

class Damage(object):
    """
    store damage per frame

    see ../functions/values.py
    """
    def __init__(self, sprite):
        super().__setattr__('sprite', sprite)
        self.init()

    def init(self):
        super().__setattr__('all_damage', 0)
        super().__setattr__('buff_damage', 0)
        super().__setattr__('physical_damage', 0)
        super().__setattr__('get_buff', functions.buff_debuff.BuffGroup())
        #=====================
        super().__setattr__('danmaku', 0)
        super().__setattr__('magic', 0)
        #=====================
        super().__setattr__('crash', 0)
        #=====================
        super().__setattr__('amulet', 0)
        super().__setattr__('cocoabomb', 0)
        super().__setattr__('boost', 0)
        #=====================
        super().__setattr__('poisond', 0)
        super().__setattr__('freeze', 0)
        super().__setattr__('burn', 0)
        super().__setattr__('cursed', 0)
        super().__setattr__('reflect', 0)
        #=====================
        super().__setattr__('endurance', 0)
        super().__setattr__('instant', 0)

    # damage count animation.
    def physical(self, layer):
        """
        damaku damage animation
        """
        pass

    def accident(self, layer):
        """
        crash damage animation
        """
        pass

    def weapen(self, layer):
        """
        amulet, cocoa bomb and boost damage animation
        """
        pass

    def buff(self, layer):
        """
        poison, burn, freeze, curse and reflect damage
        # not causing death
        """
        pass

    def special_buff(self, layer):
        """
        endurance and instant
        """
        pass

    def __setattr__(self, name, value):
        value = value.__int__()
        if value < 0:
            value = 0
        if name in ('damage', 'magic', 'crash', 'amulet', 'cocoabomb', 'boost'):
            super().__setattr__('physical_damage', self.physical_damage.__add__(value - self.__getattribute__(name)))
        elif name in ('poisond', 'freeze', 'burn', 'cursed', 'reflect'):
            super().__setattr__('buff_damage', self.buff_damage.__add__(value - self.__getattribute__(name)))
        super().__setattr__('all_damage', self.all_damage.__add__(value - self.__getattribute__(name)))
        return super().__setattr__(name, value)

    def __call__(self, layer):
        """
        calculate all damage and print count on screen
        """
        '''
        self.physical(layer)
        self.accident(layer)
        self.weapen(layer)
        self.buff(layer)
        self.special_buff(layer)
        '''
        if self.sprite.invincible:
            self.sprite.invincible -= 1
            return
        if self.buff_damage < self.sprite.hp:
            self.sprite.hp -= self.buff_damage
        else:
            self.sprite.hp = 1
        self.sprite.buff.add(self.get_buff)
        self.sprite.hp -= self.physical_damage
        self.init()

class Boss(pygame.sprite.Sprite):
    """
    use almost all the boss.
    """
    _type = 'boss'
    def __init__(self, name):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        """
        specify the name of the sprite
        """
        self.buff = functions.buff_debuff.BuffGroup()
        """
        the buffs boss have.
        """
        self.bgm = pygame.mixer.music  # maybe useless
        """
        boss bgm specify
        """
        self.invincible = 0
        """
        if boss in invincible,
        resist all damage
        """
        self.frame_count = 0
        """
        use for animation
        """
        self.timer = 0
    
    def SetLevel(self, erina, difficulty):
        """
        specify attack damage, crash danmage, local difficulty
        """
        # under development
        self.level = 0

    def SetSource(self, file_name):
        """
        specify the pictures that the boss sprite used
        boss size will be locked on 70*70 pixs
        
        boss stayed picture have 5 frames
        boss turn left or right have 2 frames
        
        boss illustration have 3 frames
        
        all the illustration will be turned into surface type and write in a file.
        each boss have their own file.
        """
        self.load_source(file_name)
        self.illustration_count = len(self.images['illustration'])
        self.pixel_count = len(self.images['pixel'])
        self.illustration = self.images['illustration']
        self.pixel = self.images['pixel']
        self.pixel_frame = 0
        """
        define image information and default position
        """
        self.image = self.pixel[self.pixel_frame]   # image will use in a list
        self.rect = self.image.get_rect()
        self.center = [-35.0, 35.0]
        self.direction = direction()
        self.temp_position = [255.0, 100.0]
        self.rect.top = self.center[0] - 35
        self.rect.left = self.center[1] - 35
    
    # new framework useless
    def SetDanmakuUse(self, *danmaku_name):
        """
        specify danmaku that boss used
        """
        temp_image = {'birth':[], 'live':[]}
        self.danmaku_images = {}
        for each in danmaku_name:
            file_name = "data/obj/danmaku/" + each + ".rbrb"
            f = open(file_name, 'rb')
            sources = pickle.load(f)
            f.close()
            self.danmaku_images[each] = temp_image
            for i in range(len(sources['birth'])):
                img_name = 'data/tmp/imgs/' + each + '_rank_' + str(i) + '.tmp'
                try:
                    f = open(img_name, 'wb')
                except:
                    os.makedirs('data/tmp/imgs/')
                    f = open(img_name, 'wb')
                f.write(sources['birth'][i])
                f.close()
                self.danmaku_images[each]['birth'].append(pygame.image.load(img_name).convert_alpha())
            for i in range(len(sources['live'])):
                img_name = 'data/tmp/imgs/' + each + '_rank_' + str(i) + '.tmp'
                try:
                    f = open(img_name, 'wb')
                except:
                    os.makedirs('data/tmp/imgs/')
                    f = open(img_name, 'wb')
                f.write(sources['live'][i])
                f.close()
                self.danmaku_images[each]['live'].append(pygame.image.load(img_name).convert_alpha())

    def SetValue(self, max_hp, crash_damage, bonus_energy):
        """
        define the local property for every boss.

        all of the value will be changed var local difficulty
        """
        self.max_hp = max_hp
        self.hp = int(self.max_hp)
        self.damage = Damage(self)
        self.crash_damage = crash_damage
        self.bonus_energy = bonus_energy
        self.damage_per_frame = 0
        """
        special value
        """
        self.collide = True
        self.in_screen = True
        self.speed = 0
        self.radius = 25
        self.defense = 1.00
    
    def SetSpell(self, *spell_list):
        """
        spell card count.
        the number will be different by local difficulty
        all spell and not-spell will all mark as spell card
        """
        self.spell_group = functions.spell_card.SpellGroup()
        self.spell_count = len(spell_list)
        """
        specify the time for each spell
        use a list to store spell time (second*frames)
        """
        self.spell_time = list(spell_list)
        self.spell_now = 1
    
    def InScreenCheck(self):
        """
        boss position usually stay in rect (50-420) (50-200)
        """
        if self.temp_position[0] < 50:
            self.temp_position[0] = 50
        elif self.temp_position[0] > 420:
            self.temp_position[0] = 420
        if self.temp_position[1] < 50:
            self.temp_position[1] = 50
        elif self.temp_position[1] > 200:
            self.temp_position[1] = 200
    
    def move(self, *erina):
        """
        move functions
        
            sprite's temp_position sets a destination for itself
            and use temp_position and center (last frame)
            to calculate the direction and speed
        """
        distance = math.sqrt(
                        (self.center[0] - self.temp_position[0]) ** 2 + \
                        (self.center[1] - self.temp_position[1]) ** 2 )
        if distance:
            self.direction.set(functions.snipe(self.center, self.temp_position))
            self.speed = math.log(distance + 1.0)
        else:
            self.speed = 0
        if self.in_screen:
            self.InScreenCheck()
        self.center[0] += self.direction.x * self.speed
        self.center[1] += self.direction.y * self.speed
        self.rect.left = self.center[0] - 35
        self.rect.top = self.center[1] - 35 + 5*math.sin(6.28*self.frame_count/100)
        self.change_image()
        self.Frame_Count()

    def print_screen(self, screen):
        screen.blit(self.image, self.rect)

    def buff_check(self, erina, *elf):
        for buff in self.buff:
            buff.check(erina, *elf)

    def collide_check(self, shouting_group):
        if self.collide:
            temp = pygame.sprite.spritecollide(self, shouting_group, True, pygame.sprite.collide_circle)
            
            self.damage_check(temp)

    def damage_check(self, shouting_group):
        """
        check the ribbon magic danmaku damage.
        when hp<0, spell count minus 1 and 3 seconds in invincible
        """
        '''
        if 'defense_large_boost' in self.buff:
            self.defense = 0.1
        elif 'defense_boost' in self.buff:
            self.defense = 0.5
        elif 'defense_up' in self.buff:
            self.defense = 0.75
        else:
            self.defense = 1
            '''
        for each in shouting_group:
            if each._type == damagetype.DANMAKU:
                self.damage.danmaku += each.damage
            elif each._type == damagetype.MAGIC:
                self.damage.magic += each.damage
            #self.buff.add(each.buff.buffs())

    def attack(self, difficulty, erina, birth_layer, boss_group, illustration_group, danmaku_layer):
        """
        prepared for every instance.
        """
        if self.hp > 0 and self.spell_group.__getattribute__('spell_%d' % self.spell_now).timer < self.spell_group.__getattribute__('spell_%s' % str(self.spell_now)).spell_time:
            self.spell_group.__getattribute__('spell_%d' % self.spell_now)(difficulty, erina, birth_layer, boss_group, illustration_group)
        elif self.hp <= 0 or self.spell_group.__getattribute__('spell_%d' % self.spell_now).timer == self.spell_group.__getattribute__('spell_%s' % str(self.spell_now)).spell_time:
            for sprite in danmaku_layer:
                sprite.kill()
            for sprite in birth_layer:
                sprite.kill()
            self.hp = self.max_hp
            self.spell_now += 1
        if self.spell_now > self.spell_group.count:
            self.death()

    def change_image(self):
        if not self.frame_count % 12:
            self.pixel_frame += 1
            if self.pixel_frame >= self.pixel_count:
                self.pixel_frame = 0
        self.image = self.pixel[self.pixel_frame]
    
    def Frame_Count(self):
        """
        some animations spell a time
        """
        self.frame_count += 1
        if self.frame_count == 300:
            self.frame_count = 0

    def death(self):
        # animation under development
        self.kill()

    def load_source(self, file_name):
        f = open('data/objs/boss/' + file_name, 'rb')
        sources = pickle.load(f)
        f.close()
        self.images = {'illustration':[], 'pixel':[], 'special':[]}
        for i in range(len(sources['illustration'])):
            img_name = 'data/tmp/imgs/' + self.name + '_illustration_' + str(i) + '.tmp'
            try:
                img_file = open(img_name, 'wb')
            except:
                os.makedirs('data/tmp/imgs/')
                img_file = open(img_name, 'wb')
            img_file.write(sources['illustration'][i])
            img_file.close()
            self.images['illustration'].append(pygame.image.load(img_name).convert_alpha())
        for i in range(len(sources['pixel'])):
            img_name = 'data/tmp/imgs/' + self.name + '_pixel_' + str(i) + '.tmp'
            try:
                img_file = open(img_name, 'wb')
            except:
                os.makedirs('data/tmp/imgs/')
                img_file = open(img_name, 'wb')
            img_file.write(sources['pixel'][i])
            img_file.close()
            self.images['pixel'].append(pygame.image.load(img_name).convert_alpha())
        for i in range(len(sources['special'])):
            img_name = 'data/tmp/imgs/' + self.name + '_special_' + str(i) + '.tmp'
            try:
                img_file = open(img_name, 'wb')
            except:
                os.makedirs('data/tmp/imgs/')
                img_file = open(img_name, 'wb')
            img_file.write(sources['special'][i])
            img_file.close()
            self.images['special'].append(pygame.image.load(img_name).convert_alpha())
        try:
            misc_name = 'data/tmp/misc/' + self.name + '.tmp'
            try:
                misc_file = open(misc_name, 'wb')
            except:
                os.makedirs('data/tmp/misc/')
                misc_file = open(misc_name, 'wb')
            misc_file.write(sources['music'])
            misc_file.close()
            self.music_name = misc_name
            #self.bgm.load(misc_name)
        except:
            del self.bgm

    def clear_cache(self):
        os.system("del data/tmp/imgs/" + self.name + "*.tmp")
        os.system("del data/tmp/misc/" + self.name + "*.tmp")

class Danmaku(pygame.sprite.Sprite, DanmakuAction):
    __metaclass__ = abc.ABCMeta
    """
    specify most of danmaku type.
    only danmaku be defined there.
    lazer next
    
    Danmaku(damage, energy, birth_layer, birth_place, *buff,
    image_change_fps=0, image_change_rotation=0, 
    liveborder=(screenborder.SCREEN_LEFT, screenborder.SCREEN_RIGHT,
    screenborder.SCREEN_TOP, screenborder.SCREEN_BOTTOM),
    birth_time=5, lazer=-1, birth_place_offset=((0),0), danmaku_layer=0,
    birth_speed=1.0, direction=pi/2, direction_offset=0, **kwargs): 
    return Danmaku instance

    usage:

        damage:     type float
            specify danmaku damage
        energy:     type int
            specify damaku bonus energy
        birth_layer:    type Group
            specify birth layer
        birth_place:    type (tuple, list, Sprite)
            specify danmaku birthplace
            e.g. birth_place = cocoa
                birth_place = [100,100]
                birth_place = screenborder.SCREEN_CENTER
        *buff:      type Buff
            specify buff(s) on opponent when damage taken
            e.g. buff = (SpeedDown(time=600))
        image_change_fps = 0:
            specify danmaku animation fps
        image_change_rotation = 0:
            specify damaku rotation speed per frame
            e.g. image_change_rotation = pi/30
        liveborder = (left<type int>, right<type int>, top<type int>, bottom<type int>):
            specify danmaku death border.
            default value will be the screen border
        birth_time = 5:
            when danmaku in birthing, no damage taken
        lazer = -1:
            if lazer value larger than 0,
            danmaku will die after <lazer value> frames
        birth_place_offset = (0,0):
            value will format in (radian, distance)
            e.g. birth_place_offset = (pi/3, 20)
        danmaku_layer = 0:
            specify danmaku in which screen layer
            small value on top
        birth_speed = 1.0:
            specify initial danmaku running speed (pixel/frame)
        direction = pi/2:
            specify initial danmaku direction (radian)
        direction_offset = 0:
            specify initial direction offset (radian)
        **kwargs:
            for more details see actions.py
            speedtime = (frame<type int>, frame<type int>, ...):
                e.g. speedtime = (30, 120)
            speedvalue = (<type float>, <type float>, ...)
                e.g. speedvalue = (5, 2)
            directiontime = (frame<type int>, frame<type int>, ...)
                e.g. directiontime = (60,)
            directionvalue = (<type float, tuple, list>, <type float, tuple, list>)
                e.g. directionvalue = (pi/2, (erina, pi/64), [pi/96, pi/256])
    """
    _type = 'danmaku'
    def __init__(self, 
                 damage,
                 energy,
                 birth_layer, 
                 birth_place, 
                 *buff, 
                 image_change_fps = 0,
                 image_change_rotation = 0,
                 liveborder = (
                               BATTLE_SCREEN_LEFT, 
                               BATTLE_SCREEN_RIGHT, 
                               BATTLE_SCREEN_TOP, 
                               BATTLE_SCREEN_BOTTOM,
                               ),
                 birth_time=5, 
                 lazer=-1,
                 birth_place_offset = ((0),0), 
                 danmaku_layer = 0, 
                 birth_speed = 1.0, 
                 direction = pi/2, 
                 direction_offset = 0, 
                 **kwargs):
        pygame.sprite.Sprite.__init__(self, birth_layer)
        DanmakuAction.__init__(self, birth_place,
                                birth_place_offset=birth_place_offset, 
                                danmaku_layer=danmaku_layer, 
                                birth_speed=birth_speed, 
                                direction=direction, 
                                direction_offset=direction_offset, 
                                **kwargs)
        self.buff_catch = functions.buff_debuff.BuffGroup(*buff)
        """
        specify when miss opponite will have some buff or debuff
        """
        self.birth_time = birth_time
        """
        any danmaku have their birth time.
        before birth time have no damage.
        """
        self.live_time = lazer
        """
        some lazer will use this
        """
        self.timer = 0
        self.SetValue(damage, energy, image_change_fps, image_change_rotation)
        self.SetImage()
        self.SetLiveCheck(*liveborder)
        #print('danmaku instance:', self.speed, self.center, self.direction)

        # music not specify
    
    def SetImage(self):
        """
        specify the pictures that danmaku sprite used.
        danmaku size will locked on a square shape

        some long danmaku also use circle collide check
        different color use different sprite.

        birth image will not at a size
        """
        #self.images = {'birth':[], 'live':[]}
        #if not self.read_source(danmaku_name, birth_frame, live_frame):
        #    self.load_source(danmaku_name)
        #    self.read_source(danmaku_name, birth_frame, live_frame)
        #self.load_source(danmaku_name)
        '''
        self.pixel = self.images['live']
        self.pixel_count = len(self.images['live'])
        self.birth = self.images['birth']
        self.birth_count = len(self.images['birth'])

        self.image = self.birth[0] # sometimes have more than 1 frame
        
        '''
        self.rect = self.image.get_rect()

        self.rect.left = self.center[0] - self.rect.width/2
        self.rect.top = self.center[1] - self.rect.height/2

    def SetValue(self, damage, energy, image_change_fps=0, image_change_rotation=0):
        """
        define local damage, removing energy, and birth position
        """
        self.damage = damage
        self.energy = energy
        # self.radius = radius

        """
        special value
        """
        self.image_change_fps = image_change_fps
        self.image_change_rotation = image_change_rotation
        self.live_time = -1
        self.collide = True
        self.collide_delete = True
        self.delete = False
        self.inscreen = True
        
    def SetLiveCheck(self, 
                     left = BATTLE_SCREEN_LEFT, 
                     right = BATTLE_SCREEN_RIGHT, 
                     top = BATTLE_SCREEN_TOP, 
                     bottom = BATTLE_SCREEN_BOTTOM,
                     ):
        """
        when danmaku move out of this area,
        change delete count
        free this sprite for save ram space
        """
        self.left_border = left - self.rect.width/2
        self.right_border = right + self.rect.width/2
        self.top_border = top - self.rect.height/2
        self.bottom_border = bottom + self.rect.height/2

    '''
    @classmethod
    def load_source(cls, danmaku_name):
        """
        load sources functions
        class method

            load_source(danmaku_name): return None
        """
        cls.images = {'birth':[], 'live':[]}
        f = open('data/objs/danmaku/' + danmaku_name + '.rbrb', 'rb')
        sources = pickle.load(f)
        f.close()
        for i in range(len(sources['birth'])):
            img_name = 'data/tmp/imgs/' + danmaku_name + '_birth_rank_' + str(i) + '.tmp'
            try:
                f = open(img_name, 'wb')
            except:
                os.makedirs('data/tmp/imgs/')
                f = open(img_name, 'wb')
            f.write(sources['birth'][i])
            f.close()
            cls.images['birth'].append(pygame.image.load(img_name).convert_alpha())
        for i in range(len(sources['live'])):
            img_name = 'data/tmp/imgs/' + danmaku_name + '_live_rank_' + str(i) + '.tmp'
            try:
                f = open(img_name, 'wb')
            except:
                os.makedirs('data/tmp/imgs/')
                f = open(img_name, 'wb')
            f.write(sources['live'][i])
            f.close()
            cls.images['live'].append(pygame.image.load(img_name).convert_alpha())
    '''

    @classmethod
    def load_source(cls, danmaku_name, radius):
        cls.images = []
        try:
            cls.image = pygame.image.load('data/tmp/imgs/'+danmaku_name+'.tmp')
        except pygame.error:
            with open('data/objs/danmaku.rbrb', 'rb') as file:
                rbrb = pickle.load(file)
            for key, value in rbrb.items():
                with open('data/tmp/imgs/'+key+'.tmp', 'wb') as f:
                    f.write(value)
            cls.load_source(danmaku_name, radius)
        cls.radius = radius
    '''
    def read_source(self):
        """
        read sources method:
            
            read_source(danmaku_name): return Bool

        if false, load sources first
        """
        for i in range(birth_frame):
            img_name = 'data/tmp/imgs/' + danmaku_name + '_birth_rank_' + str(i) + '.tmp'
            try: 
                self.images['birth'].append(pygame.image.load(img_name).convert_alpha())
            except:
                if i == 0:
                    return False
                break
        for i in range(live_frame):
            img_name = 'data/tmp/imgs/' + danmaku_name + '_live_rank_' + str(i) + '.tmp'
            try:
                self.images['live'].append(pygame.image.load(img_name).convert_alpha())
            except:
                if i == 0:
                    return False
        return True
    '''

    def image_change(self):
        """
        """
        '''
        if self.birth_time:
            if self.birth_time > 2:
                self.image = self.images['birth'][10-self.birth_time]
            else:
                self.image = self.images['birth'][8]
        else:
            '''
        if not self.image_change_fps:
            pass
        else:
            if self.timer % fps == 0:
                self.image = self.images['live'][(self.timer/self.image_change_fps)%self.pixel_count]
                self.image = pygame.transform.rotate(self.image, self.rotation)
        if not self.image_change_rotation:
            pass
        else:
            self.rotation += self.image_chagne_rotation
            self.image = pygame.transform.rotate(self.image, self.image_change_rotation)

    def live_check(self):
        """
        most danmaku have a constant moving area.
        """
        if self.live_time > 0:
            self.live_time -= 1
        if not self.live_time:
            self.delete = True
        elif self.rect.right < self.left_border or self.rect.left > self.right_border:
            self.delete = True
        elif self.rect.bottom < self.top_border or self.rect.top > self.bottom_border:
            self.delete = True
        else:
            self.delete = False

    def birth_check(self):
        if self.birth_time > 0:
            self.birth_time -= 1

    def death(self):
        """
        death animation
        """
        pass

    def move(self, *erina):
        """
        move function:

            it's different from boss sprite.
            it only can controled by speed and direction!
        """
        self.time_rip(*erina)
        self.image_change()
        self.center[0] += self.speed * self.direction.x
        self.center[1] += self.speed * self.direction.y
        self.rect.left = self.center[0] - self.rect.width/2
        self.rect.top = self.center[1] - self.rect.height/2
        self.birth_check()
        self.live_check()
        self.timer += 1

    def print_screen(self, screen):
        screen.blit(self.image, self.rect)

###

class Elf(pygame.sprite.Sprite, ElfAction):
    __metaclass__ = abc.ABCMeta
    """
    use for almost all mid boss
    """
    _type = 'elf'
    def __init__(self, elf_group, *args, 
                 birth_place = (30, -30),
                 birth_direction = pi/2, 
                 birth_speed = 2,
                 birth_place_offset = (0,0),
                 birth_direction_offset = 0,
                 speedtime = (),
                 speedvalue = (),
                 directiontime = (),
                 directionvalue = (),
                 **kwargs):
        pygame.sprite.Sprite.__init__(self, elf_group)
        ElfAction.__init__(self, 
                            birth_place = birth_place,
                            birth_direction = birth_direction, 
                            birth_speed = birth_speed,
                            birth_place_offset = birth_place_offset,
                            birth_direction_offset = birth_direction_offset,
                            speedtime = speedtime,
                            speedvalue = speedvalue,
                            directiontime = directiontime,
                            directionvalue = directionvalue,
                            **kwargs
                            )
        #self.name = name
        self.buff = functions.buff_debuff.BuffGroup()
        self.invincible = 0
        #self.frame_count = 0
        self.timer = 0
        #self.SetSource(file_name)

    def SetLevel(self, erina, difficulty):
        self.level = 0

    def SetSource(self):
        """
        SetSource(): return None
        """
        #self.load_source(file_name)
        self.pixel_count = len(self.images['pixel'])
        self.pixel = self.images['pixel']
        self.pixel_frame = 0
        self.image = self.pixel[self.pixel_count-1]
        self.rect = self.image.get_rect()
        #self.direction = direction()
        #self.temp_position = [-10.0,-10.0]
        #self.center = [-10.0, 10.0]
        self.rect.top = self.center[0] - 10
        self.rect.left = self.center[1] - 10

    def SetValue(self, max_hp, crash_damage, bonus_energy, live_time = -1):
        """
        SetValue(max_hp, crash_damage, bonus_energy): return None

        specify parament for elf
        """
        self.max_hp = max_hp
        self.hp = int(self.max_hp)
        self.damage = Damage(self)
        self.crash_damage = crash_damage
        self.bonus_energy = bonus_energy
        self.collide = True
        self.in_screen = False
        self.live_time = live_time
        #self.speed = 0
        self.radius = 8
        self.damage = Damage(self)

    def move(self, *erina):
        '''
        self.time_rip(*erina)
        distance = sqrt( \
                        (self.center[0] - self.temp_position[0]) ** 2 + \
                        (self.center[1] - self.temp_position[1]) ** 2 )
        if distance:
            self.direction.set(functions.snipe(self.temp_position, self.center))
            self.speed = math.log(distance + 1.0)/3
        else:
            self.speed = 0
        self.center[0] += self.direction.x * self.speed
        self.center[1] += self.direction.y * self.speed
        self.rect.left = self.center[0] - 35
        self.rect.top = self.center[1] - 35 + 5*math.sin(6.28*self.frame_count/100)
        self.Frame_Count()
        '''
        self.time_rip(*erina)
        self.image_change()
        self.center[0] += self.speed * self.direction.x
        self.center[1] += self.speed * self.direction.y
        self.rect.left = self.center[0] - self.rect.width/2
        self.rect.top = self.center[1] - self.rect.height/2 + 5*math.sin(6.28*self.timer/100)
        self.timer += 1


    @classmethod
    def load_source(self, file_name):
        f = open('data/objs/elf/' + file_name + '.rbrb' ,'rb')
        sources = pickle.load(f)
        f.close()
        self.images = {"pixel":[]}
        for i in range(len(sources['pixel'])):
            img_name = 'data/tmp/imgs/' + file_name + '_pixle' + str(i) + '.tmp'
            try:
                img_file = open(img_name, 'wb')
            except:
                os.makedirs('data/tmp/imgs/')
                img_file = open(img_name, 'wb')
            img_file.write(sources['pixel'][i])
            img_file.close()
            self.images['pixel'].append(pygame.image.load(img_name).convert_alpha())

    def image_change(self):
        if not self.timer %12:
            self.pixel_frame += 1
            if self.pixel_frame >= self.pixel_count:
                self.pixel_frame = 0
        self.image = self.pixel[self.pixel_frame]
        
    def attack(self, difficulty, erina, birth_layer, elf_group, danmaku_layer):
        """
        specify attack methods
        """
        self.__getattribute__("attack_%s" % difficulty)(difficulty, erina, birth_layer, elf_group, danmaku_layer)

    def buff_check(self, erina, *elf):
        for buff in self.buff:
            buff.check(erina, *elf)

    def collide_check(self, shouting_group):
        if self.collide:
            temp = pygame.sprite.spritecollide(self, shouting_group, True, pygame.sprite.collide_circle)
            self.damage_check(temp)

    def damage_check(self, shoutings):
        if self.hp <= 0:
            return self.death()
        for each in shoutings:
            self.damage.danmaku += each.damage

    def death(self):
        # animation under development
        self.kill()

    def attack(self, difficulty, erina, birth_layer, elf_group, danmaku_layer):
        self.__getattribute__('attack_%s' % difficulty)(erina, birth_layer, elf_group, danmaku_layer)

    def attack_easy(self, erina, birth_layer, elf_group, danmaku_layer):
        pass

    def attack_normal(self, erina, birth_layer, elf_group, danmaku_layer):
        pass

    def attack_hard(self, erina, birth_layer, elf_group, danmaku_layer):
        pass

    def attack_hell(self, erina, birth_layer, elf_group, danmaku_layer):
        pass

    def attack_bunny(self, erina, birth_layer, elf_group, danmaku_layer):
        pass

    def print_screen(self, screen):
        screen.blit(self.image, self.rect)
