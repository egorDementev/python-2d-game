import os
import ctypes
from gameobjects import *
from camera import *
import random


def load_image(filename, color_key=None):
    """загрузка картинки из filename"""
    fullname = os.path.join('data/sprites/', filename)
    image = pygame.image.load(fullname).convert()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
screen_size = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))

pygame.init()
size = WIDTH, HEIGHT = screen_size
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
black = pygame.Color('black')
screen.fill(black)


def get_data():
    return (load_image('box.png'), load_image('grass.png'), load_image('movingbox.png'), load_image('player.png'),
            load_image('botx.png'), load_image('boty.png'))


wall_image, empty_image, box_image, player_image, botx_image, boty_image = get_data()
names = {'player': player_image, 'box': box_image, 'botx': botx_image, 'boty': boty_image,
         'empty': empty_image, 'wall': wall_image}


class TimeMachine:
    """класс для перемещений во времени"""

    def __init__(self, objects, timer, level, moving_objects, past_objects, all_grp, past_grp, tile_size, player):
        """все аргументы - это переменные в классе GameLevel"""
        self.player = player
        self.all_grp = all_grp
        self.past_grp = past_grp
        self.tile_size = tile_size
        self.objects = objects
        self.level = level
        self.moving_objects = moving_objects
        self.past_objects = past_objects
        self.timer = timer
        self.data = dict()  # все данные об объектах в прошлом хранятся здесь
        # время в мс это ключи, в значениях хранятся списки данных об объектах
        self.trig = False
        self.trig2 = False
        self.count = 2

    def backup(self):
        """сохранение данных об объектах в текущее время в self.data"""
        time = self.timer.get_time()
        if not self.is_past():
            self.data[time] = list()
            for y in range(len(self.objects)):
                for x in range(len(self.objects[0])):
                    # в self.data[time] записываются данные обо всех объектах
                    # self.objects[y][x].get_data() - название объекта и номер его фрейма
                    if self.objects[y][x]:
                        self.data[time].append([self.objects[y][x].get_data(), (x, y)])

    def set_reverse(self, n):
        """если n == True, то начинается перемещение в прошлое, иначе время начинает идти вперёд"""
        if (n and not self.is_past()) or (not n and self.is_past()):
            print(123)
            self.past = n
            self.timer.set_reverse(n)
            if n:
                self.trig = True
                # в self.backup_objects записываются все текущие объекты,
                # чтобы потом можно было вернуться в нормальное состояние
                self.backup_objects = [[None for j in range(len(self.level[0]))] for i in range(len(self.level))]
                for y in range(len(self.objects)):
                    for x in range(len(self.objects[0])):
                        if self.objects[y][x]:
                            self.backup_objects[y][x] = self.objects[y][x]
                            if self.objects[y][x].get_name() != 'player':
                                self.objects[y][x] = None

    def is_past(self):
        """возвращает true, если сейчас прошлое, false, если нстоящее"""
        return self.timer.is_past()

    def update(self):
        """обновляет self.past_objects"""
        self.msk = 25
        time = self.timer.get_time()
        if self.is_past():  # если сейчас прошлое
            if time // self.msk in [i // self.msk for i in self.data.keys()]:
                # если в self.data есть запись об объектах в текущее время
                for y in range(len(self.past_objects)):  # очистка self.past_objects
                    for x in range(len(self.past_objects[0])):
                        self.past_objects[y][x] = None
                self.past_grp.remove(*self.past_grp.sprites())
                for j in self.data[[(i // self.msk, i) for i in self.data.keys()  # запись в self.past_objects
                                    if i // self.msk == time // self.msk][0][1]]:
                    if j[0][0] != 'player' and j[1] == self.player.get_coords():
                        self.trig2 = True
                    self.past_objects[j[1][1]][j[1][0]] = Tile(j[1][0], j[1][1], self.past_grp, self.all_grp,
                                                               self.tile_size[0], self.tile_size[1],
                                                               names[j[0][0]], j[0][2], 1, deg=j[0][3])
                    # игроку нельзя сталкиваться с чем-либо в прошлом, поэтому, если координаты игрока совпадают с
                    # координатами объекта, который записывается в self.past_objects, функция возвращает False,
                    # после чего игрок умирает и уровень презапускается
                    if self.player.get_coords() == (j[1][0], j[1][1]) and self.trig2:
                        return False
                    self.past_objects[j[1][1]][j[1][0]].set_image(j[0][1], deg=j[0][3])
        else:  # если сейчас не прошлое
            self.trig2 = False
            for y in range(len(self.past_objects)):  # очистка self.past_objects
                for x in range(len(self.past_objects[0])):
                    self.past_objects[y][x] = None
            self.past_grp.remove(*self.past_grp.sprites())
        if not self.is_past() and self.trig:  # если сейчас не прошлое и ещё не было пeрезаписи из self.backup_objects
            # в self.objects
            self.trig = False
            for y in range(len(self.objects)):  # self.objects восстанавливается из self.backup_objects
                for x in range(len(self.objects[0])):
                    if self.backup_objects[y][x]:
                        if self.backup_objects[y][x].get_name() != 'player':
                            self.objects[y][x] = self.backup_objects[y][x]
        return True

    def set_trig2(self):
        self.trig2 = True


class TTimer:
    """таймер с функцией перемотки времение назад"""

    def __init__(self):
        self.t1 = pygame.time.get_ticks()
        self.time = pygame.time.get_ticks()
        self.reverse = False  # false - время идёт вперёд, true - время идёт назад
        self.stop_time = self.time  # время на котором начлось премещение в прошлое

    def get_time(self):
        """возвращет текущее время в мс"""
        self.t2 = pygame.time.get_ticks()
        if self.reverse:
            self.time -= self.t2 - self.t1
        else:
            self.time += self.t2 - self.t1
        if self.time > self.stop_time:
            self.stop_time = self.time
        self.t1 = self.t2
        return self.time

    def set_reverse(self, n):
        """установка нормального или обратного течения времени"""
        self.reverse = n

    def is_past(self):
        """возвращает true, если сейчас прошлое, false, если нстоящее"""
        return self.get_time() < self.stop_time


class GameLevel:
    """ класс уровня """

    def __init__(self, filename):
        self.filename = filename  # файл, где храниться уровень

        self.level = self.load_level()  # преобразование файла в лист листов

        self.tile_size = [50, 50]

        self.restart()  # все основные настройки для начала игры

        self.blocks = ('.', '@')

    def play(self):  # здесь основной игровой цикл
        """запуск игры"""
        running = True

        t1 = self.timer.get_time()
        t21 = pygame.time.get_ticks()
        count = 0
        count2 = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:  # движение вверх
                        self.player.move(0, -1)
                        self.time_machine.backup()
                        self.time_machine.set_trig2()
                    elif event.key == pygame.K_DOWN:  # движение вниз
                        self.player.move(0, 1)
                        self.time_machine.backup()
                        self.time_machine.set_trig2()
                    elif event.key == pygame.K_LEFT:  # движение влево
                        self.player.move(-1, 0)
                        self.time_machine.backup()
                        self.time_machine.set_trig2()
                    elif event.key == pygame.K_RIGHT:  # движение вправо
                        self.player.move(1, 0)
                        self.time_machine.backup()
                        self.time_machine.set_trig2()
                    elif event.key == pygame.K_RETURN:  # презапуск уровня
                        self.restart()
                    elif event.key == pygame.K_SPACE:  # начало перемотки времени назад
                        self.time_machine.set_reverse(True)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:  # возвращение времени в нормальное положение
                        self.time_machine.set_reverse(False)
            if not self.time_machine.update():
                self.restart()
            t2 = self.timer.get_time()
            t22 = pygame.time.get_ticks()
            count += t2 - t1
            count2 += t22 - t21
            t1 = t2
            t21 = t22
            if count2 > 25:  # каждые 25мс запускается метод у камеры
                count2 = 0
                for i in range(len(self.camera_move_list)):
                    self.camera_move_list[i].update()
                    # if not self.camera_move_list[i].update():
                    #    self.camera_move_list.pop(i)
                self.camera.process_xy()
            if count > 300:  # каждые 300мс происходит движение всех движущихся объектов
                count = 0
                self.time_machine.backup()
                for elem in self.moving_objects:
                    elem.move_event()

            for sprite in self.all_grp:  # сдвиг всех игровых объектов для эффекта камеры
                self.camera.apply(sprite)

            screen.fill(black)
            # self.all_grp.draw(screen)
            self.tiles_grp.draw(screen)
            if not self.time_machine.is_past():  # если сейчас не прошлое, то отрисовываются обычные объекты
                self.moving_grp.draw(screen)
            else:
                self.past_grp.draw(screen)  # если прошлое, то объекты из соответствующей группы
            self.player_grp.draw(screen)

            for sprite in self.all_grp:  # сдвиг всех спрайтов обратно
                self.camera.reapply(sprite)
            pygame.display.flip()
        pygame.quit()

    def restart(self):
        """сброс всех настоек уровня или их инициализация при первом запуске"""
        self.all_grp = pygame.sprite.Group()  # создание всех групп спарйтов
        self.moving_grp = pygame.sprite.Group()
        self.tiles_grp = pygame.sprite.Group()
        self.player_grp = pygame.sprite.Group()
        self.past_grp = pygame.sprite.Group()

        self.objects = [[None for j in range(len(self.level[0]))] for i in range(len(self.level))]
        # матрица из игровых объектов
        # там хранятся все объекты, которые в процессе игры могут как-то двигаться
        self.moving_objects = list()  # список двужущихся объектов
        self.camera_move_list = list()
        self.camera = Camera(WIDTH, HEIGHT, self.tile_size[0], len(self.level[0]), len(self.level))
        # создаётся камера
        self.past_objects = [[None for j in range(len(self.level[0]))] for i in range(len(self.level))]
        # список объектов, которые отображаются при перемещении в прошлое
        self.player, self.x, self.y = self.generate_level(self.level)  # генерация уровня, тут заполняются self.objects
        # и self.moving_objects
        self.camera.set_target(self.player)  # установка игрока как цели у камеры
        self.camera.process()
        self.timer = TTimer()  # создание таймера
        self.time_machine = TimeMachine(self.objects, self.timer, self.level, self.moving_objects, self.past_objects,
                                        self.all_grp, self.past_grp, self.tile_size, self.player)
        # time_machine отвечает за сохранение всех игровых позиций в прошлом и за заполнение self.past_objects, когда
        # происходит премещение в прошлое
        self.player.set_time_machine(self.time_machine)

    def stop(self):
        pass

    def load_level(self):
        """загрузка уровня из self.filename"""
        with open(self.filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        max_width = max(map(len, level_map))
        level = list(map(lambda x: x.ljust(max_width, '.'), level_map))
        level = ([('#' * (len(level[0]) + 30))] * 15 + [('#' * 15) + i + ('#' * 15) for i in level] +
                 [('#' * (len(level[0]) + 30))] * 15)
        return level

    def wall(self, level, x, y):
        res = ['.' * (len(level[0]) + 2)] + ['.' + i + '.' for i in level] + ['.' * (len(level[0]) + 2)]
        s8, s6, s2, s4, s7, s9, s3, s1 = (res[y][x + 1], res[y + 1][x + 2], res[y + 2][x + 1], res[y + 1][x],
                                          res[y][x], res[y][x + 2], res[y + 2][x + 2], res[y + 2][x])
        s8, s6, s2, s4, s7, s9, s3, s1 = (s8 == '#', s6 == '#', s2 == '#', s4 == '#',
                                          s7 == '#', s9 == '#', s3 == '#', s1 == '#')
        if not (s8 or s6 or s2 or s4):  # 0
            return 0, 0
        elif not (s8 or s6 or s4) and s2:  # 1
            return 1, 0
        elif not (s8 or s6 or s2) and s4:
            return 1, -90
        elif not (s4 or s2 or s6) and s8:
            return 1, 180
        elif not (s8 or s4 or s2) and s6:
            return 1, 90
        elif not (s4 or s2) and s8 and s9 and s6:  # 2
            return 2, 0
        elif not (s4 or s8) and s6 and s3 and s2:
            return 2, -90
        elif not (s8 or s6) and s2 and s1 and s4:
            return 2, 180
        elif not (s6 or s2) and s4 and s7 and s8:
            return 2, 90
        elif not (s4 or s2 or s9) and s8 and s6:  # 3
            return 3, 0
        elif not (s4 or s8 or s3) and s6 and s2:
            return 3, -90
        elif not (s8 or s6 or s1) and s2 and s4:
            return 3, 180
        elif not (s6 or s2 or s7) and s4 and s8:
            return 3, 90
        elif not (s4 or s6) and s8 and s2:  # 4
            return 4, 0
        elif not (s8 or s2) and s4 and s6:
            return 4, 90
        elif not (s4 or s9) and s8 and s6 and s3 and s2:  # 5
            return 5, 0
        elif not (s8 or s3) and s6 and s2 and s1 and s4:
            return 5, -90
        elif not (s6 or s2) and s2 and s4 and s7 and s8:
            return 5, 180
        elif not (s2 or s4) and s4 and s8 and s9 and s6:
            return 5, 90
        elif not (s4 or s3) and s8 and s6 and s9 and s2:  # 6
            return 6, 0
        elif not (s8 or s1) and s6 and s2 and s3 and s4:
            return 6, -90
        elif not (s6 or s7) and s2 and s4 and s2 and s8:
            return 6, 180
        elif not (s2 or s9) and s4 and s8 and s4 and s6:
            return 6, 90
        elif not (s4 or s9 or s3) and s8 and s6 and s2:  # 7
            return 7, 0
        elif not (s8 or s3 or s1) and s6 and s2 and s4:
            return 7, -90
        elif not (s6 or s2 or s7) and s2 and s4 and s8:
            return 7, 180
        elif not (s2 or s4 or s9) and s4 and s8 and s6:
            return 7, 90
        elif not s4 and s9 and s8 and s6 and s3 and s2:  # 8
            return 8, 0
        elif not s8 and s3 and s6 and s2 and s1 and s4:
            return 8, -90
        elif not s6 and s2 and s2 and s4 and s7 and s8:
            return 8, 180
        elif not s2 and s4 and s4 and s8 and s9 and s6:
            return 8, 90
        elif s7 and s8 and not s9 and s6 and s3 and s2 and s1 and s4:  # 9
            return 9, 0
        elif s7 and s8 and s9 and s6 and not s3 and s2 and s1 and s4:
            return 9, -90
        elif s7 and s8 and s9 and s6 and s3 and s2 and not s1 and s4:
            return 9, 180
        elif not s7 and s8 and s9 and s6 and s3 and s2 and s1 and s4:
            return 9, 90
        elif s7 and s8 and not s9 and s6 and not s3 and s2 and s1 and s4:  # 10
            return 10, 0
        elif s7 and s8 and s9 and s6 and not s3 and s2 and not s1 and s4:
            return 10, -90
        elif not s7 and s8 and s9 and s6 and s3 and s2 and not s1 and s4:
            return 10, 180
        elif not s7 and s8 and not s9 and s6 and s3 and s2 and s1 and s4:
            return 10, 90
        elif not (s7 or s3) and s8 and s9 and s6 and s2 and s1 and s4:  # 11
            return 11, 0
        elif not (s9 or s1) and s7 and s8 and s6 and s3 and s2 and s4:
            return 11, 90
        elif not (s7 or s9 or s3) and s8 and s6 and s2 and s1 and s4:  # 12
            return 12, 0
        elif not (s9 or s3 or s1) and s6 and s2 and s4 and s7 and s8:
            return 12, -90
        elif not (s3 or s1 or s7) and s2 and s4 and s8 and s9 and s6:
            return 12, 180
        elif not (s1 or s7 or s9) and s4 and s8 and s6 and s3 and s2:
            return 12, 90
        elif s7 and s8 and s9 and s6 and s3 and s2 and s1 and s4:  # 13
            return 13, 0
        elif not (s7 or s9 or s3 or s1) and s8 and s6 and s2 and s4:  # 14
            return 14, 0
        else:
            return 15, 0  # 15

    def generate_level(self, level):
        """генерация уровня из level, тут заполняются self.objects и self.moving_objects,
        возвращает игрока и размеры уровня"""
        new_player, x, y = None, None, None
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '.':  # пустая клетка
                    Tile(x, y, self.tiles_grp, self.all_grp, self.tile_size[0], self.tile_size[1],
                         empty_image, 4, 4, name='empty', frame=random.randint(0, 15))
                elif level[y][x] == '#':  # стена
                    kk = self.wall(level, x, y)
                    Tile(x, y, self.tiles_grp, self.all_grp, self.tile_size[0], self.tile_size[1],
                         wall_image, 4, 4, name='wall', frame=kk[0], deg=kk[1])
                elif level[y][x] == '@':  # игрок
                    Tile(x, y, self.tiles_grp, self.all_grp, self.tile_size[0], self.tile_size[1],
                         empty_image, 4, 4, name='empty', frame=random.randint(0, 15))  # создание пустой клетки
                    new_player = Player(x, y, self.player_grp, self.all_grp, self.tile_size[0], self.tile_size[1],
                                        player_image, 1, 1, self.objects, self.level, self.camera,
                                        self.camera_move_list, self.past_objects)  # создание игрока
                    self.objects[y][x] = new_player
                elif level[y][x] == '>':  # стена, двигающаяся по горизонтали
                    Tile(x, y, self.tiles_grp, self.all_grp, self.tile_size[0], self.tile_size[1],
                         empty_image, 4, 4, name='empty', frame=random.randint(0, 15))
                    self.objects[y][x] = BotX(x, y, self.moving_grp, self.all_grp, self.tile_size[0], self.tile_size[1],
                                              botx_image, 1, 1, self.objects, self.level, self, 0)
                    self.moving_objects.append(self.objects[y][x])
                elif level[y][x] == '^':  # стена, двигающаяся по вертикали
                    Tile(x, y, self.tiles_grp, self.all_grp, self.tile_size[0], self.tile_size[1],
                         empty_image, 4, 4, name='empty', frame=random.randint(0, 15))
                    self.objects[y][x] = BotY(x, y, self.moving_grp, self.all_grp, self.tile_size[0], self.tile_size[1],
                                              boty_image, 1, 1, self.objects, self.level, self, 0)
                    self.moving_objects.append(self.objects[y][x])
                elif level[y][x] == '&':  # коробка
                    Tile(x, y, self.tiles_grp, self.all_grp, self.tile_size[0], self.tile_size[1],
                         empty_image, 4, 4, name='empty', frame=random.randint(0, 15))
                    self.objects[y][x] = Box(x, y, self.moving_grp, self.all_grp, self.tile_size[0], self.tile_size[1],
                                             box_image, 1, 1, self.objects, self.level)
        return new_player, x, y
