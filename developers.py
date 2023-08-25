import pygame
import ctypes

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


all_sprites = pygame.sprite.Group()
sprite = pygame.sprite.Sprite()
sprite.image = load_image("buttons/developers_btn.png")
sprite.rect = sprite.image.get_rect()
sprite.rect.x = size[0] / 2 - 100
sprite.rect.y = size[1] / 10 * 4
all_sprites.add(sprite)

sprite_1 = AnimatedSprite(load_image("buttons/back_btn.png"), 1, 3, size[0] // 2 - 100, size[1] / 10 * 7)
all_sprites.add(sprite_1)
f1 = 0
fon = pygame.transform.scale(load_image('buttons/background.png'), (size[0], size[1]))
screen.blit(fon, (0, 0))  # делаем фон


def proverka():  # функция, чтобы проверять, где  сейчас мышка
    if size[0] // 2 - 100 <= cor[0] <= size[0] // 2 + 100 and size[1] / 10 * 7 - 25 <= cor[1] <= size[1] / 10 * 7 + 25:
        return 1
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
            else:  # если нет, то меняем обратно
                all_sprites = pygame.sprite.Group()
                sprite_1 = AnimatedSprite(load_image("buttons/back_btn.png"), 1, 3, size[0] // 2 - 100,
                                          size[1] / 10 * 7)
                all_sprites.add(sprite_1)
                f1 = 0
        if event.type == pygame.MOUSEBUTTONDOWN:
            cor = event.pos
            a = proverka()
            if a == 1:
                sprite_1.update()
                from Menu import *  # если мы нажали играть, то открываем новое окно с выбором уровня
        pygame.display.flip()
pygame.quit()