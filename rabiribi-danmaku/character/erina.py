import pygame
import platform
import functions
import objects
#from objects.sprites import Damage

from pygame.locals import *

class HP(object):
    """
    specify erina hp
    """
    _base_hp = 100
    def __init__(self, erina):
        self.erina = erina
        self.hp = 100
        self.max_hp = 100
        self.base_hp = 100

    def __setattr__(self, name, value):
        if name in ('hp','max_hp'):
            if self.hp > self.max_hp:
                super().__setattr__('hp', self.max_hp)
        value = value.__int__()
        return super().__setattr__(name, value)

    def add(self, value):
        self.hp += value

    def sub(self, value):
        self.hp -= value
        if self.hp < 0:
            self.erina.death = True

    def full(self):
        self.hp = self.max_hp

    def __repr__(self):
        return '< Erina HP: %d/%d >' % (self.hp, self.max_hp)

    def __str__(self):
        return "HP: %d,\n MaxHP: %d,\n BaseHP: %d,\n" % (self.hp, self.max_hp, self.base_hp)
        
class Erina(pygame.sprite.Sprite):
    """ 
    Erina kawaii
    Erina ore no yome!!

    player control character
        
    """
    _type = 'erina'
    def __init__(self, ribbon):
        pygame.sprite.Sprite.__init__(self)

        self.name = 'Erina'

        if platform.system()=='Windows':
            oimage = pygame.image.load("images\\character\\Erina\\Erina.png").convert_alpha()
        if platform.system()=='Linux' or platform.system()=='Darwin':
            oimage = pygame.image.load("images/character/Erina/Erina.png").convert_alpha()

        self.oimage = pygame.transform.scale(oimage, (40,50)) # load source under development
        self.image = self.oimage
        self.rect = self.image.get_rect()
        self.center = [245.0, 425.0]
        self.rect.left, self.rect.top = self.center[0]-20, self.center[1]-25
        # balance unfit
        self.fast = 4
        self.slow = 2
        
        self.hp = 100
        self.max_hp = 100
        self.damage = objects.sprites.Damage(self)
        self.spell = 2.0
        self.max_spell = 4.0
        self.buff = functions.buff_debuff.BuffGroup()
        
        self.key_pressed = {}
        self.LeftRight_control = 0
        self.UpDown_control = 0
        self.LR_control = False
        self.UD_control = False
        
        self.radius = 2

        self.invincible = 0

        self.ribbon = ribbon

    def moveSpeed(self):
        if self.key_pressed[K_LSHIFT]:
            self.speed = self.slow
        else:
            self.speed = self.fast

    def moveUp(self):#8
        if (self.rect.top - self.speed) > 15:
            self.center[1] -= self.speed
        else:
            self.center[1] = 15
        self.rect.left, self.rect.top = self.center[0]-20, self.center[1]-25

    def moveDown(self):#2
        if (self.rect.bottom + self.speed) < 465:
            self.center[1] += self.speed
        else:
            self.center[1] = 440
        self.rect.left, self.rect.top = self.center[0]-20, self.center[1]-25
        
    def moveLeft(self):#4
        if (self.rect.left - self.speed) > 35:
            self.center[0] -= self.speed
        else:
            self.center[0] = 35
        self.rect.left, self.rect.top = self.center[0]-20, self.center[1]-25

    def moveRight(self):#6
        if (self.rect.right + self.speed) < 415:
            self.center[0] += self.speed
        else:
            self.center[0] = 395
        self.rect.left, self.rect.top = self.center[0]-20, self.center[1]-25

    def UpDownControl(self, num):
        self.UpDown_control = num
        
    def LeftRightControl(self, num):
        self.LeftRight_control = num

    def moveUpDown(self):     
        if self.UpDown_control == 8:
            self.moveUp()
        if self.UpDown_control == 2:
            self.moveDown()

    def moveLeftRight(self):
        if self.LeftRight_control == 4:
            self.moveLeft()
        if self.LeftRight_control == 6:
            self.moveRight()

    def move(self, key_pressed):
        self.key_pressed = key_pressed
        self.moveSpeed()
        if self.key_pressed[K_UP] or self.key_pressed[K_DOWN]:  
            if self.key_pressed[K_UP] and self.key_pressed[K_DOWN]:
                if self.UD_control:
                    if self.UpDown_control == 8:
                        self.UpDownControl(2)
                    elif self.UpDown_control == 2:
                        self.UpDownControl(8)
                    self.UD_control = False
            else:
                if self.key_pressed[K_UP]:
                    self.UpDownControl(8)
                    self.UD_control = True
                if self.key_pressed[K_DOWN]:
                    self.UpDownControl(2)
                    self.UD_control = True
        else:
            self.UpDownControl(0)
        if self.key_pressed[K_LEFT] or self.key_pressed[K_RIGHT]: 
            if self.key_pressed[K_LEFT] and self.key_pressed[K_RIGHT]:
                if self.LR_control:
                    if self.LeftRight_control == 6:
                        self.LeftRightControl(4)
                    elif self.LeftRight_control == 4:
                        self.LeftRightControl(6)                  
                    self.LR_control = False
            else:
                if self.key_pressed[K_RIGHT]:
                    self.LeftRightControl(6)
                    self.LR_control = True
                if self.key_pressed[K_LEFT]:
                    self.LeftRightControl(4)
                    self.LR_control = True
        else:       
            self.LeftRightControl(0)
        self.moveUpDown()
        self.moveLeftRight()

    # useless
    '''
    def reset(self, time):
        if time > 30:
            self.image = self.oimage
            self.image = pygame.transform.scale(\
                        self.image, (int(self.rect.width * (time-30)*3 / 100), int(self.rect.height)))
            self.rect.left += 1
        if time == 30:
            self.rect.left, self.rect.top = 225, 400
        self.center = [self.rect.left+20, self.rect.top+25]
        if time < 30 and time > 1:
            self.image = self.oimage
            self.image = pygame.transform.scale(\
                        self.image, (int(self.rect.width * (100 - time*3.33) / 100),int(self.rect.height)))
            self.rect.left -= 2.0/3
        if time == 1:
            self.image = self.oimage
    '''
    def buff_check(self, *enemy):
        for b in self.buff:
            b.check(self, *enemy)
               
    def image_change(self, frame_count):
        """
        erina animation
        """
        # under development
        # momochi ?
        pass

    def collide_check(self, danmaku_group, boss_group):
        if not self.invincible:
            pass
            self.damage_check(danmaku_group, boss_group)
        else:
            self.invincible -= 1
            pygame.sprite.spritecollide(self, danmaku_group, True, pygame.sprite.collide_circle)

    def damage_check(self, danmaku_layer, boss_layer):
        temp_danmaku = pygame.sprite.spritecollide(self, danmaku_layer, False, pygame.sprite.collide_circle) 
        temp_boss = pygame.sprite.spritecollide(self, boss_layer, False, pygame.sprite.collide_circle)
        if temp_danmaku or temp_boss:
            self.invincible = 180
            for each in temp_danmaku:
                # print(each.damage)
                for b in each.buff_catch:
                    b.owner = self
                    self.damage.get_buff.add(b)
                self.damage.danmaku += each.damage
            for each in temp_boss:
                # self.buff.add(each.buff_catch)
                self.damage.crash += each.crash_damage