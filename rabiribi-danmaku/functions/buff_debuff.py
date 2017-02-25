import pygame
import pickle
from _operator import truth

class Buff(pygame.sprite.Sprite):
    """
    use this to define buffs and debuffs
    """
    def __init__(self, name, owner='boss'):
        pygame.sprite.Sprite.__init__()
        self.name = name
        # if timer > 10 or timer == -1, it's buff time
        self.timer = 0
        # if active is true, changing value now
        self.active = False
        # if owner is erina, something different
        self.owner = owner
    
    def SetImage(self, file_name):
        """
        set buff icon
        """
        f = open(file_name, 'rb')
        images = pickle.load(f)
        f.close()
        img_name = 'data/tmp/bf/' + self.name + '.tmp'
        img = open(img_name, 'wb')
        img.write(images[self.name])
        img.close()
        self.image = pygame.image.load(img_name).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left = 0
        self.rect.top = 0
        self.temp_left = 0
        self.temp_right = 0
        self.temp_top = 0


    def buff_check(self, owner):
        """
        Buff.buff_check(origin, *enemy): Return None

        origin is buff who owned
        *enemy store opponity(s)
        """    
        pass
            
class BuffGroup():
    """
    use this to restore buffs
    the group support following standard python operations:

        in      test if a buff is contained
        len     the number of buffs contained
        bool    test if any buffs are contained
        iter    iterate through all the buffs

    """
    _buffgroup = True

    def __init__(self):
        self.buffdict = {}

    def buffs(self):
        return list(self.buffdict)

    def add_internal(self, buff):
        self.buffdict[buff] = len(self)+1

    def remove_internal(self, buff):
        for b in self.buffdict:
            if b.name == buff:
                count = self.buffdict[b]
                del self.buffdict[b]
                break
        for b in self.buffdict:
            if self.buffdict[b] > count:
                self.buffdict[b] -= 1

    def has_internal(self, buff):
        for b in self.buffdict:
            if b.name == buff:
                return True

    def copy(self):
        """
        copy a group with all the same sprites

        BuffGroup.copy(): return BuffGroup

        Returns a copy of the group that is an instance of the same
        and has the same buffs in it.
        """
        return self.__class__(self.buffs())

    def __iter__(self):
        return iter(self.buffs())

    def __contains__(self, buff):
        return self.has_internal(buff)

    def add(self, *buffs):
        """
        add buff(s) to group
        
        BuffGroup.add(buff, list, group, ...): return none
        """
        for buff in buffs:
            if isinstance(buff, Buff):
                if not self.has_internal(buff):
                    self.add_internal(buff)
            else:
                try:
                    self.add(*buffs)
                except (TypeError, AttributeError):
                    if hasattr(buff, '_spritegroup'):
                        for b in buff.buffs():
                            if not self.has_internal(b):
                                self.add_internal(b)
                    elif not self.has_internal(buff):
                        self.add_internal(buff)

    def remove(self, *buffs):
        """
        remove buff(s) from group

        BuffGroup.remove(buff, ...): return None
        """
        for buff in buffs:
            if isinstance(buff, Buff):
                if self.has_internal(buff):
                    self.remove_internal(buff)
            else:
                try:
                    self.remove(*buffs)
                except (TypeError, AttributeError):
                    if hasattr(buff, '_buffgroup'):
                        for b in buff.buffs():
                            if self.has_internal(b):
                                self.remove_internal(b)
                    elif self.has_internal(buff):
                        self.remove_internal(buff)

    def has(self, *buffs):
        """
        ask if group has a buff

        BuffGroup.has(buff, ...): return bool
        """
        return_value = False

        for buff in buffs:
            if isinstance(buff, Buff):
                if self.has_internal(buff):
                    return_value = True
                else:
                    return False
            else:
                pass
        
        return return_value

    def empty(self):
        """
        remove all buffs
        
        BuffGroup.empty(): return None
        """
        for b in self.buffs():
            self.remove_internal(b)

    def print(self, owner):
        pass

    def __nonzero__(self):
        return truth(self.buffs())

    def __len__(self):
        """
        return number of buffs in group

        BuffGroup.len(group): return int
        """
        return len(self.buffs())

    def __repr__(self):
        return "<%s(%d buffs)>" % (self.__class__.__name__, len(self))

#
# all buffs here:
#

class SpeedDown(Buff):
    """
    Speed lowered by 20%
    """
    def __init__(self, owner='boss'):
        Buff.__init__(self, 'speed down')
        self.owner = owner
        self.image = images[0]
        self.rect = self.image.get_rect()
        
    def move_in(self, owner):
        pass

    def move_out(self, owner):
        pass

    def check(self, origin, *enemy):
        if self.timer > 0 and self.timer < 10:
            pass
        elif self.timer == 10:
            self.active = False
            origin.speed *= 1.25
        elif self.timer > 10 or self.timer == -1:
            if self.active:
                pass
            else:
                origin.speed *= 0.8
                self.active = True
        self.timer -= 1

class Numb(Buff):
    """
    All movement ceases intermittently
    """
    def __init__(self):
        Buff.__init__(self, 'numb')