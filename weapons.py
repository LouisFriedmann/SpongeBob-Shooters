# weapons.py stores all relevant information about the weapons used in the game

# Imports
import pygame

# Weapon images
weapon_imgs = {"Player Missile": pygame.image.load('player_missile.png'),
                    "Boss Missile": pygame.image.load('boss_missile.png'),
                    "Boomerang": pygame.image.load('red_boomerang.png'),
                    "Bomb": pygame.image.load('bomb.png')}

# Constants
RIGHT_BORDER, BOTTOM_BORDER = 500, 750

class Weapon:
    def __init__(self, start_pos, size, vel_vector, img_key):
        self.x, self.y = start_pos
        self.width, self.height = size
        self.x_vel, self.y_vel = vel_vector

        self.launch = False

        self.kill_self = False
        self.img_key = None

    def draw(self, win):
        draw_img(weapon_imgs[self.img_key], self.x, self.y, self.width, self.height, win)

    def launch_weapon(self):
        self.launch = True

    def kill_weapon(self):
        return self.kill_self


# Helper function for draw()
def draw_img(img, x, y, width, height, win):
    win.blit(pygame.transform.scale(img, (width, height)), (x, y))

class Missile(Weapon):
    def __init__(self, start_pos, size, vel_vector, type_of_missile):
        super().__init__(start_pos, size, vel_vector, img_key="Missile")
        if type_of_missile == "Player":
            self.img_key = "Player Missile"
        elif type_of_missile == "Boss":
            self.img_key = "Boss Missile"
        self.damage = 1

    def handle_movement(self):
        if self.launch:
            self.y += self.y_vel

        # Missile needs to be killed if it falls off of bottom border or goes through the top border
        if self.y + self.height >= BOTTOM_BORDER or self.y <= 0:
            self.kill_self = True


class Boomerang(Weapon):
    def __init__(self, start_pos, size, vel_vector):
        super().__init__(start_pos, size, vel_vector, img_key="Boomerang")
        self.img_key = "Boomerang"
        self.damage = 1

    def handle_movement(self):
        if self.launch:
            # Check borders, boomerangs can bounce off of all borders except the top one
            if self.x + self.width + self.x_vel >= RIGHT_BORDER or self.x + self.x_vel <= 0:
                self.x_vel *= -1
            if self.y + self.height + self.y_vel >= BOTTOM_BORDER:
                self.y_vel *= -1

            # Boomerang needs to be killed when it bounces back past the top border
            if self.y + self.y_vel <= 0:
                self.kill_self = True

            self.x += self.x_vel
            self.y += self.y_vel


class Bomb(Weapon):
    def __init__(self, start_pos, size, vel_vector):
        super().__init__(start_pos, size, vel_vector, img_key="Bomb")
        self.img_key = "Bomb"
        self.damage = 2

    def handle_movement(self):
        if self.launch:
            self.y += self.y_vel

        # Bomb needs to be killed if it falls off of bottom border
        if self.y + self.height >= BOTTOM_BORDER:
            self.kill_self = True