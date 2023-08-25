import pygame
import ctypes
import os

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
screen_size = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
# screen_size = (1280, 720)
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


class AnimatedSprite(pygame.sprite.Sprite):  # класс для анимации кнопок
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


all_sprites = pygame.sprite.Group()  # создаем группу спрайтов и подгружаем все картинки
sprite_1 = AnimatedSprite(load_image("buttons/play_btn.png"), 1, 3, size[0] // 2 - 100, size[1] / 10 * 4)
all_sprites.add(sprite_1)
sprite_2 = AnimatedSprite(load_image("buttons/about_developers_btn.png"), 1, 3, size[0] // 2 - 100, size[1] / 10 * 5)
all_sprites.add(sprite_2)
sprite_3 = AnimatedSprite(load_image("buttons/exit_btn.png"), 1, 3, size[0] // 2 - 100, size[1] / 10 * 6)
all_sprites.add(sprite_3)
f1, f2, f3 = 0, 0, 0  # флаги для кнопок
fon = pygame.transform.scale(load_image('buttons/background.png'), (size[0], size[1]))
screen.blit(fon, (0, 0))  # делаем фон


def proverka():  # функция, чтобы проверять, где  сейчас мышка
    if size[0] // 2 - 100 <= cor[0] <= size[0] // 2 + 100 and size[1] / 10 * 4 <= cor[1] <= size[1] / 10 * 4 + 50:
        return 1
    if size[0] // 2 - 100 <= cor[0] <= size[0] // 2 + 100 and size[1] / 10 * 5 <= cor[1] <= size[1] / 10 * 5 + 50:
        return 2
    if size[0] // 2 - 100 <= cor[0] <= size[0] // 2 + 100 and size[1] / 10 * 6 <= cor[1] <= size[1] / 10 * 6 + 50:
        return 3
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
                    sprite_1.update()  # если мышка на кнопке, то меняем цвет
            elif a == 2:
                if f2 == 0:
                    f2 = 1
                    sprite_2.update()
            elif a == 3:
                if f3 == 0:
                    f3 = 1
                    sprite_3.update()
            else:  # если нет, то меняем обратно
                all_sprites = pygame.sprite.Group()
                sprite_1 = AnimatedSprite(load_image("buttons/play_btn.png"), 1, 3,
                                          size[0] // 2 - 100, size[1] / 10 * 4)
                all_sprites.add(sprite_1)
                sprite_2 = AnimatedSprite(load_image("buttons/about_developers_btn.png"), 1, 3, size[0] // 2 - 100,
                                          size[1] / 10 * 5)
                all_sprites.add(sprite_2)
                sprite_3 = AnimatedSprite(load_image("buttons/exit_btn.png"), 1, 3, size[0] // 2 - 100,
                                          size[1] / 10 * 6)
                all_sprites.add(sprite_3)
                f1, f2, f3 = 0, 0, 0
        if event.type == pygame.MOUSEBUTTONDOWN:
            cor = event.pos
            a = proverka()
            if a == 1:
                sprite_1.update()
                all_sprites = pygame.sprite.Group()
                from menu_2 import *  # если мы нажали играть, то открываем новое окно с выбором уровня
            elif a == 2:
                sprite_2.update()
                from developers import *
            elif a == 3:
                sprite_3.update()
                pygame.quit()  # если нажали выход, то закрываем программу
        pygame.display.flip()
pygame.quit()
