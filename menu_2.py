import pygame
import ctypes
import os

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
screen_size = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
pygame.init()
size = WIDTH, HEIGHT = screen_size
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)


def load_image(name, color_key=None):
    fullname = os.path.join('data/', name)
    image = pygame.image.load(fullname).convert()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


class AnimatedSprite(pygame.sprite.Sprite):  # класс анимации кнопок
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


all_sprites = pygame.sprite.Group()  # создаем группу спрайтов и подгружаем кнопки
sprite_1 = AnimatedSprite(load_image("buttons/level1_btn.png"), 1, 3, size[0] // 2 - 100, size[1] / 10 * 3)
all_sprites.add(sprite_1)
sprite_2 = AnimatedSprite(load_image("buttons/level2_btn.png"), 1, 3, size[0] // 2 - 100, size[1] / 10 * 4)
all_sprites.add(sprite_2)
sprite_3 = AnimatedSprite(load_image("buttons/level3_btn.png"), 1, 3, size[0] // 2 - 100, size[1] / 10 * 5)
all_sprites.add(sprite_3)
sprite_4 = AnimatedSprite(load_image("buttons/level4_btn.png"), 1, 3, size[0] // 2 - 100, size[1] / 10 * 6)
all_sprites.add(sprite_4)
sprite_5 = AnimatedSprite(load_image("buttons/level5_btn.png"), 1, 3, size[0] // 2 - 100, size[1] / 10 * 7)
all_sprites.add(sprite_5)
sprite_6 = AnimatedSprite(load_image("buttons/back_btn.png"), 1, 3, size[0] // 2 - 100, size[1] / 10 * 8)
all_sprites.add(sprite_6)
f1, f2, f3, f4, f5, f6 = 0, 0, 0, 0, 0, 0  # флаги для кнопок
fon = pygame.transform.scale(load_image('buttons/background.png'), (size[0], size[1]))
screen.blit(fon, (0, 0))  # создаем фон


def proverka():  # проверяем, где сейчас находится мышка
    if size[0] // 2 - 100 <= cor[0] <= size[0] // 2 + 100 and size[1] / 10 * 3 <= cor[1] <= size[1] / 10 * 3 + 50:
        return 1
    if size[0] // 2 - 100 <= cor[0] <= size[0] // 2 + 100 and size[1] / 10 * 4 <= cor[1] <= size[1] / 10 * 4 + 50:
        return 2
    if size[0] // 2 - 100 <= cor[0] <= size[0] // 2 + 100 and size[1] / 10 * 5 <= cor[1] <= size[1] / 10 * 5 + 50:
        return 3
    if size[0] // 2 - 100 <= cor[0] <= size[0] // 2 + 100 and size[1] / 10 * 6 <= cor[1] <= size[1] / 10 * 6 + 50:
        return 4
    if size[0] // 2 - 100 <= cor[0] <= size[0] // 2 + 100 and size[1] / 10 * 7 <= cor[1] <= size[1] / 10 * 7 + 50:
        return 5
    if size[0] // 2 - 100 <= cor[0] <= size[0] // 2 + 100 and size[1] / 10 * 8 <= cor[1] <= size[1] / 10 * 8 + 50:
        return 6
    return 0


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        all_sprites.draw(screen)
        if event.type == pygame.MOUSEMOTION:
            cor = event.pos
            a = proverka()
            if a == 1:
                if f1 == 0:
                    f1 = 1
                    sprite_1.update()  # если на кнопке уровень, то меняем цвет
            elif a == 2:
                if f2 == 0:
                    f2 = 1
                    sprite_2.update()
            elif a == 3:
                if f3 == 0:
                    f3 = 1
                    sprite_3.update()
            elif a == 4:
                if f4 == 0:
                    f4 = 1
                    sprite_4.update()
            elif a == 5:
                if f5 == 0:
                    f5 = 1
                    sprite_5.update()
            elif a == 6:
                if f6 == 0:
                    f6 = 1
                    sprite_6.update()
            else:  # если нет, то меняем обратно
                all_sprites = pygame.sprite.Group()
                sprite_1 = AnimatedSprite(load_image("buttons/level1_btn.png"), 1, 3, size[0] // 2 - 100,
                                          size[1] / 10 * 3)
                all_sprites.add(sprite_1)
                sprite_2 = AnimatedSprite(load_image("buttons/level2_btn.png"), 1, 3, size[0] // 2 - 100,
                                          size[1] / 10 * 4)
                all_sprites.add(sprite_2)
                sprite_3 = AnimatedSprite(load_image("buttons/level3_btn.png"), 1, 3, size[0] // 2 - 100,
                                          size[1] / 10 * 5)
                all_sprites.add(sprite_3)
                sprite_4 = AnimatedSprite(load_image("buttons/level4_btn.png"), 1, 3, size[0] // 2 - 100,
                                          size[1] / 10 * 6)
                all_sprites.add(sprite_4)
                sprite_5 = AnimatedSprite(load_image("buttons/level5_btn.png"), 1, 3, size[0] // 2 - 100,
                                          size[1] / 10 * 7)
                all_sprites.add(sprite_5)
                sprite_6 = AnimatedSprite(load_image("buttons/back_btn.png"), 1, 3, size[0] // 2 - 100,
                                          size[1] / 10 * 8)
                all_sprites.add(sprite_6)
                f1, f2, f3, f4, f5, f6 = 0, 0, 0, 0, 0, 0
        if event.type == pygame.MOUSEBUTTONDOWN:
            cor = event.pos
            a = proverka()
            if a == 1:
                sprite_1.update()
                all_sprites = pygame.sprite.Group()
                from main import *  # если выбрали уровень, то открываем его
                level1()
            elif a == 2:
                sprite_2.update()
                all_sprites = pygame.sprite.Group()
                from main import *
                level2()
            elif a == 3:
                sprite_3.update()
                all_sprites = pygame.sprite.Group()
                from main import *
                level3()
            elif a == 4:
                sprite_4.update()
                all_sprites = pygame.sprite.Group()
                from main import *
                level4()
            elif a == 5:
                sprite_5.update()
                all_sprites = pygame.sprite.Group()
                from main import *
                level5()
            elif a == 6:
                sprite_6.update()
                all_sprites = pygame.sprite.Group()
                from Menu import *
        pygame.display.flip()
pygame.quit()