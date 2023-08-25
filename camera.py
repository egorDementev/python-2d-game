class Camera:
    """объект камеры"""
    def __init__(self, width, height, sprite_size, x_map_size, y_map_size):
        """width, height - размеры экрана
        sprite_size - размер спрайта
        x_map_size, y_map_size - размеры уровня"""
        self.sprite_size = sprite_size
        self.width = width
        self.height = height
        self.x_map_size = x_map_size
        self.y_map_size = y_map_size
        self.dx = 0
        self.dy = 0

        self.k = 100
        self.x = 0  # смещение по x
        self.vx = 0  # скорость по x
        self.ax = 0  # ускорение по x
        self.y = 0  # смещение по y
        self.vy = 0  # скорость по y
        self.ay = 0  # ускорение по y

        self.x50 = 0  # смещение по 1 клетке (50 пикселей)
        self.y50 = 0

    def change_xy50(self, x, y):
        self.x50 -= x * 50
        self.y50 -= y * 50

    def change_ax(self, a):
        """измененние ускорения по x на a"""
        self.ax += a

    def change_ay(self, a):
        """измененние ускорения по y на a"""
        self.ay += a

    def process_xy(self):
        """расчёт смещения по x и y исходя из ускорения и скорости"""
        if 0.1 < self.x - self.x50 < 100:  # если игрок находиться практичекски в центре, то смещение подгоняется так,
            # чтобы игрок находился ровно по центру
            self.x -= 0.1
        elif -100 < self.x - self.x50 < -0.1:
            self.x += 0.1
        self.dx -= round(self.x)  # разчёт смещения из скорости и ускорения
        self.vx += self.ax
        self.x += self.vx
        self.dx += round(self.x)

        if 0.1 < self.y - self.y50 < 10:  # то же самое для y
            self.y -= 0.1
        elif -10 < self.y - self.y50 < -0.1:
            self.y += 0.1
        self.dy -= round(self.y)
        self.vy += self.ay
        self.y += self.vy
        self.dy += round(self.y)

    def process(self):
        """расчёт начального смещения, для того, чтобы игрок находился по центру экрана"""
        self.dx = self.width // 2 - self.target.rect.x - 25
        self.dy = self.height // 2 - self.target.rect.y - 25

    def apply(self, obj):
        """изменяет координаты obj на смещение"""
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def reapply(self, obj):
        """изменяет координаты obj на изначальные"""
        obj.rect.x -= self.dx
        obj.rect.y -= self.dy

    def set_target(self, target):
        """установка объекта для слежения"""
        self.target = target


class CameraMove:
    """Объект для плавного премещения камеры;
    увеличивает ускорение на определённое время, поле чего уменьшает его(возвращает обратно),
    так, чтобы камера сдвинулась ровно на 50 пикселей.
    Создаётся при движении игрока"""
    def __init__(self, camera, x, y):
        """camera, x, y - из GameLevel"""
        self.camera = camera
        self.camera.change_xy50(x, y)
        self.x = x
        self.y = y
        self.count = 0
        self.k1 = 0.01
        self.k2 = 72
        if x == -1:
            self.camera.change_ax(self.k1)
        elif x == 1:
            self.camera.change_ax(self.k1 * -1)
        if y == -1:
            self.camera.change_ay(self.k1)
        elif y == 1:
            self.camera.change_ay(self.k1 * -1)

    def update(self):
        """увеличивает или уменьшает ускорение камеры"""
        self.count += 1
        if self.count == self.k2:
            if self.x == -1:
                self.camera.change_ax(self.k1 * -2)
            elif self.x == 1:
                self.camera.change_ax(self.k1 * 2)
            if self.y == -1:
                self.camera.change_ay(self.k1 * -2)
            elif self.y == 1:
                self.camera.change_ay(self.k1 * 2)
        elif self.count == self.k2 * 2 - 1:
            if self.x == -1:
                self.camera.change_ax(self.k1)
            elif self.x == 1:
                self.camera.change_ax(self.k1 * -1)
            if self.y == -1:
                self.camera.change_ay(self.k1)
            elif self.y == 1:
                self.camera.change_ay(self.k1 * -1)
        elif self.count > self.k2 * 2:
            return False
        return True
