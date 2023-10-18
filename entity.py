# entity.py stores relevant information about entities in the game

# Imports
import pygame
import random
import weapons

# Constants
RIGHT_BORDER, BOTTOM_BORDER = 500, 750
GRAVITY = BOTTOM_BORDER / 1000

# Entity images
entity_imgs = {"Boss": pygame.image.load('ship.png'),
               "Player 0": pygame.image.load('spongebob.png'),
               "Player 1": pygame.image.load('patrick.png')}

# Entity sounds and channels to play the sounds in
pygame.mixer.init()
entity_sounds = {"Dutchman": pygame.mixer.Sound('dutchman_sound.wav'),
                 "Spongebob": pygame.mixer.Sound('spongebob_sound.wav'),
                 "Patrick": pygame.mixer.Sound('patrick_sound.wav'),
                 "Ship": pygame.mixer.Sound('ship_sound.wav')}

entity_channels = {"Dutchman": pygame.mixer.Channel(0),
                 "Spongebob": pygame.mixer.Channel(1),
                 "Patrick": pygame.mixer.Channel(2),
                 "Ship": pygame.mixer.Channel(3)}

class Entity:
    def __init__(self, start_pos, size, health, vel_vector):

        self.x, self.y = start_pos
        self.width, self.height = size
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.health = health
        self.total_health = health
        self.health_bar_height = self.height / 10

        self.x_vel, self.y_vel = vel_vector


    def draw(self, win):
        draw_loaded_img(entity_imgs[self.img_key], self.x, self.y, self.width, self.height, win)

        # Draw grey health bar with green bar showing the health
        pygame.draw.rect(win, "grey", (self.x, self.y, self.width, self.health_bar_height))
        pygame.draw.rect(win, "green", (self.x, self.y, self.width * (self.health / self.total_health), self.health_bar_height))

    # Determine if an entity is colliding with an object
    def is_colliding_with(self, obj):
        return pygame.Rect(self.x, self.y, self.width, self.height).colliderect(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

# Helper function for draw
def draw_loaded_img(loaded_img, x, y, width, height, win):
    win.blit(pygame.transform.scale(loaded_img, (width, height)), (x, y))

# The entities

# Boss weapon constants
BOSS_MISSILE_SIZE = (RIGHT_BORDER / 50, BOTTOM_BORDER / 10)
BOOMERANG_SIZE = (RIGHT_BORDER / 25, BOTTOM_BORDER / 10)
BOMB_SIZE = (RIGHT_BORDER / 5, RIGHT_BORDER / 5)

class Boss(Entity):
    def __init__(self, start_pos, size, health, vel_vector):
        super().__init__(start_pos, size, health, vel_vector)
        self.directions = ["Left", "Right"]
        self.direction = self.directions[random.randint(0, len(self.directions) - 1)]
        self.weapon_keys = ["Missile", "Boomerang", "Bomb"]
        self.active_weapons = []
        self.img_key = "Boss"
        self.still_alive = True

    # The boss moves sideways randomly and launches weapons at random times
    def handle_movement(self):
        # Move the boss sideways between the left and right borders
        if self.direction == "Left":
            self.x -= self.x_vel
        if self.x + self.width + self.x_vel > RIGHT_BORDER:
            self.direction = self.directions[0]
        if self.direction == "Right":
            self.x += self.x_vel
        if self.x - self.x_vel < 0:
            self.direction = self.directions[1]

    def handle_weapons(self):
        # 1 percent chance a weapon will randomly be shot every frame
        if random.randint(1, 100) == 1:
            self.shoot()

        # Handle the movement for all active weapons
        for weapon in self.active_weapons:
            weapon.handle_movement()


    # Shoot a random weapon from the middle-bottom of the boss
    def shoot(self):
        # 50% chance missile will be shot, 30% chance boomerang will be shot, 20% chance bomb will be dropped
        rand_num = random.random()
        if rand_num <= .5:
            random_weapon_key = self.weapon_keys[self.weapon_keys.index("Missile")]
        elif rand_num <= .8:
            random_weapon_key = self.weapon_keys[self.weapon_keys.index("Boomerang")]
        else:
            random_weapon_key = self.weapon_keys[self.weapon_keys.index("Bomb")]

        new_weapon = None

        if random_weapon_key == "Missile":
            new_weapon = weapons.Missile(start_pos=(self.x + self.width / 2 - BOSS_MISSILE_SIZE[0] / 2, self.y + self.height), size=BOSS_MISSILE_SIZE, vel_vector=(0, BOTTOM_BORDER / 400), type_of_missile="Boss")
        elif random_weapon_key == "Boomerang":
            new_weapon = weapons.Boomerang(start_pos=(self.x + self.width / 2 - BOOMERANG_SIZE[0] / 2, self.y + self.height), size=BOOMERANG_SIZE, vel_vector=(RIGHT_BORDER / 200, BOTTOM_BORDER / 400))
        elif random_weapon_key == "Bomb":
            new_weapon = weapons.Bomb(start_pos=(self.x + self.width / 2 - BOMB_SIZE[0] / 2, self.y + self.height), size=BOMB_SIZE, vel_vector=(0, BOTTOM_BORDER / 400))

        self.active_weapons.append(new_weapon)
        new_weapon.launch_weapon()

    def handle_health(self, damage):
        self.health -= damage


# Player constants
PLAYER_MISSILE_SIZE = (RIGHT_BORDER / 100, BOTTOM_BORDER / 20)

class Player(Entity):
    def __init__(self, start_pos, size, health, vel_vector, num):
        super().__init__(start_pos, size, health, vel_vector)
        self.start_pos = start_pos
        self.lives = 5
        self.has_landed = False
        self.in_air = True
        self.fall_count = 0
        self.num = num
        self.active_missiles = []
        self.img_key = ""
        if self.num == 0:
            self.img_key = "Player 0"
        elif self.num == 1:
            self.img_key = "Player 1"

        self.sound_key = None
        if num == 0:
            self.sound_key = "Spongebob"
        elif num == 1:
            self.sound_key = "Patrick"

        self.timer = Timer() # Keep track of when a player can shoot
        self.timer.start()
        self.shoot_time = .5 # players have to wait a second before shooting again

        self.still_alive = True
        self.game_over = False
        self.connected = False
        self.has_shot = False
        self.sound_played = False
        self.sounds_playing = []
        self.explosion = False

    def handle_movement(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] and self.x + self.width + self.x_vel <= RIGHT_BORDER:
            self.x += self.x_vel
        if keys[pygame.K_LEFT] and self.x - self.x_vel >= 0:
            self.x -= self.x_vel

        # Jumping
        if keys[pygame.K_UP] and not self.in_air and self.y_vel == 0:
            self.y_vel = 8*GRAVITY
            self.has_landed = False
            self.in_air = True

        # Shooting (sound played when shooting), killing missiles, and handling their movement
        if keys[pygame.K_SPACE] and self.timer.elapsed_time() >= self.shoot_time:
            self.shoot()
            self.timer.reset()
            self.timer.start()
        for missile in self.active_missiles:
            missile.handle_movement()
            if missile.kill_weapon():
                del self.active_missiles[self.active_missiles.index(missile)]

    def apply_gravity(self, fps):
        self.y_vel -= min(1, (self.fall_count / fps) * GRAVITY)
        self.y -= self.y_vel
        self.fall_count += 1

    def shoot(self):
        new_missile = weapons.Missile(start_pos=(self.x + self.width / 2 - PLAYER_MISSILE_SIZE[0] / 2, self.y - PLAYER_MISSILE_SIZE[1]), size=PLAYER_MISSILE_SIZE, vel_vector=(0, -BOTTOM_BORDER / 200), type_of_missile="Player")
        self.active_missiles.append(new_missile)
        new_missile.launch_weapon()
        self.has_shot = True

    def handle_landing(self, block):
        self.y_vel = 0
        self.y = block.y - self.height
        self.in_air = False
        self.has_landed = True
        self.fall_count = 0

    def handle_hitting_head(self, block):
        self.y_vel *= -1
        self.y = block.y + block.height
        self.y -= self.y_vel

    def will_collide_horizontally(self, obj, dx):
        return pygame.Rect(self.x + dx, self.y, self.width, self.height).colliderect(pygame.Rect(obj.x, obj.y, obj.width, obj.height)) and not self.is_colliding_with(obj)

    def handle_health(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.lives -= 1
            self.health = self.total_health

    def play_sound(self, key):
        entity_channels[key].play(entity_sounds[key])


# Timer object to be used for the entities
import time
class Timer:

    # Default constructor
    def __init__(self):
        self.start_time = 0

    # Function starts the timer
    def start(self):
        self.start_time = time.time()

    # Function returns the elapsed time of the timer
    def elapsed_time(self):
        if self.start_time != 0:
            return time.time() - self.start_time
        else:
            return 0

    # Function resets the timer
    def reset(self):
        self.start_time = 0


