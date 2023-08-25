import pygame
from camera import *


class GameObject(pygame.sprite.Sprite):
    """базовый игровой объект
    x, y - координаты по сетке
    grp1, grp2 - группы спрайтов, в которые объект будет записан
    width, height - замеры объекта в пикселях
    sheet, rows, cols - основа спрайта(картика с несеолькими состояниями), её размеры"""
    def __init__(self, x, y, grp1, grp2, width, height, sheet, cols, rows):
        super().__init__(grp1, grp2)
        self.sheet = sheet
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.rows = rows
        self.cols = cols
        self.sheet = sheet
        self.frames = list()
        self.cut_sheet()
        self.deg = 0
        self.set_image(0)

    def cut_sheet(self):
        """разрезает основу спрайта на отдельные части"""
        self.rect = pygame.Rect(0, 0, self.sheet.get_width() // self.cols,
                                self.sheet.get_height() // self.rows)
        for j in range(self.rows):
            for i in range(self.cols):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(self.sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def get_coords(self):
        """возвращает кортеж координат"""
        return (self.x, self.y)

    def set_image(self, n, deg=0):
        """установить фрейм с номером n"""
        self.deg = deg
        self.n_frame = n
        self.image = self.frames[n]
        self.image = pygame.transform.rotate(self.image, deg)
        self.rect = self.image.get_rect().move(self.width * self.x, self.height * self.y)

    def get_data(self):
        """возвращает данные о себе - имя, номер фрейма, количество стлобцов у фрейма"""
        return (self.get_name(), self.n_frame, self.cols, self.deg)


class GameObjectMoving(GameObject):
    """основа для двигающихся объектов"""
    def __init__(self, x, y, grp1, grp2, width, height, sheet, cols, rows, objects, level):
        """objects и level из GameLevel"""
        super().__init__(x, y, grp1, grp2, width, height, sheet, cols, rows)

        self.objects = objects
        self.level = level

        self.rect = self.image.get_rect().move(width * x, height * y)

    def move(self, x, y, mode=0, past=None):
        """попытка передвижения на x по горизонтали и по y по вертикали,
        возвращает True, если получилось, False, если не получилось,
        если mode == 0, то при передвижении двигает коробки,
        если mode == 1, то не двигает"""
        if 0 <= self.y + y < len(self.level) and 0 <= self.x + x < len(self.level[0]):
            if mode == 0:
                elem = self.objects[self.y + y][self.x + x]
                if elem:
                    if elem.get_name() == 'box':
                        elem.move(x, y)
            if self.level[self.y + y][self.x + x] != '#' and self.objects[self.y + y][self.x + x] is None:
                if past is None or past[self.y + y][self.x + x] is None:
                    self.objects[self.y][self.x] = None
                    self.x += x
                    self.y += y
                    self.objects[self.y][self.x] = self
                    self.rect = self.image.get_rect().move(self.width * self.x, self.height * self.y)
                else:
                    return False
            else:
                return False
        else:
            return False
        return True

    def get_name(self):
        """возвращает имя"""
        return 'game_object_moving'


class Tile(GameObject):
    """статичный объект(пустая клетка или стена)"""
    def __init__(self, x, y, grp1, grp2, width, height, sheet, cols, rows, name='tile', frame=0, deg=0):
        super().__init__(x, y, grp1, grp2, width, height, sheet, cols, rows)
        self.name = name
        self.set_image(frame, deg=deg)

    def get_name(self):
        """возвращает имя"""
        return self.name


class Player(GameObjectMoving):
    """объект игрока"""
    def __init__(self, x, y, grp1, grp2, width, height, sheet, cols, rows, objects, level, camera, camera_move_list,
                 past_objects):
        """camera, camera_move_list и past_objects из GameLevel"""
        super().__init__(x, y, grp1, grp2, width, height, sheet, cols, rows, objects, level)
        self.camera = camera
        self.camera_move_list = camera_move_list
        self.past_objects = past_objects

    def get_name(self):
        """возвращает имя"""
        return 'player'

    def set_time_machine(self, time_machine):
        """установить текущий объект time_machine"""
        self.time_machine = time_machine

    def move(self, x, y):
        """движение"""
        # при разных типах движения меняется фреймz
        if x == 1:
            self.set_image(0, deg=-90)
        elif x == -1:
            self.set_image(0, deg=90)
        elif y == 1:
            self.set_image(0, deg=180)
        elif y == -1:
            self.set_image(0)
        if self.time_machine.is_past():
            past_arg = self.past_objects
        else:
            past_arg = self.objects
        # если сейчас прошлое, то при движении использует self.past_objects, иначе self.objects
        if super().move(x, y, past=past_arg):
            self.camera_move_list.append(CameraMove(self.camera, x, y))


class Box(GameObjectMoving):
    """объект коробки"""
    def __init__(self, x, y, grp1, grp2, width, height, sheet, cols, rows, objects, level):
        super().__init__(x, y, grp1, grp2, width, height, sheet, cols, rows, objects, level)

    def get_name(self):
        """возвращает имя"""
        return 'box'


class Bot(GameObjectMoving):
    """объект двигающейся стены"""
    def __init__(self, x, y, grp1, grp2, width, height, sheet, cols, rows, objects, level, game_level, dir):
        super().__init__(x, y, grp1, grp2, width, height, sheet, cols, rows, objects, level)
        """game_level - текущий объект GameLevel
        dir - напрвление движения"""
        self.game_level = game_level
        self.direction = dir

    def move_kill(self, x, y):
        """движение, при котором встреча с игроком приводит к концу игры"""
        if 0 <= self.y + y < len(self.level) and 0 <= self.x + x < len(self.level[0]):
            elem = self.objects[self.y + y][self.x + x]
            if elem:
                if elem.get_name() == 'player':
                    self.game_level.restart()
        return self.move(x, y, mode=1)

    def get_name(self):
        """возвращает имя"""
        return 'bot'


class BotX(Bot):
    """объект стены, перемещающейся по горизонтали"""
    def __init__(self, x, y, grp1, grp2, width, height, sheet, cols, rows, objects, level, game_level, dir):
        super().__init__(x, y, grp1, grp2, width, height, sheet, cols, rows, objects, level, game_level, dir)

    def move_event(self):
        """передвижение"""
        if self.direction == 0:
            if not self.move_kill(1, 0):
                self.direction = 1
                self.move_kill(-1, 0)
        else:
            if not self.move_kill(-1, 0):
                self.direction = 0
                self.move_kill(1, 0)

    def get_name(self):
        """возвращает имя"""
        return 'botx'


class BotY(Bot):
    """объект стены, перемещающейся по вертикали"""
    def __init__(self, x, y, grp1, grp2, width, height, sheet, cols, rows, objects, level, game_level, dir):
        super().__init__(x, y, grp1, grp2, width, height, sheet, cols, rows, objects, level, game_level, dir)

    def move_event(self):
        """передвижение"""
        if self.direction == 0:
            if not self.move_kill(0, 1):
                self.direction = 1
                self.move_kill(0, -1)
        else:
            if not self.move_kill(0, -1):
                self.direction = 0
                self.move_kill(0, 1)

    def get_name(self):
        """возвращает имя"""
        return 'boty'
