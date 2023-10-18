# client.py is responsible for the GUI and sending information to the server

# Imports
import pygame
from network import Network
from block import Block
from entity import Player
from entity import Boss
import entity
import random


# Constants
RIGHT_BORDER, BOTTOM_BORDER = 500, 750
BOSS_SIZE = (RIGHT_BORDER / 5, BOTTOM_BORDER / 5)
BLOCK_HEIGHT = BOTTOM_BORDER / 30
BROKEN_ROWS = 5
BROKEN_BLOCK_WIDTH = RIGHT_BORDER / 10
BROKEN_BLOCKS_PER_ROW = 4
SPACE_FOR_LIVES = BOTTOM_BORDER / 10
GRAVITY = BOTTOM_BORDER / 1000
LIFE_WIDTH, LIFE_HEIGHT = RIGHT_BORDER / 20, BOTTOM_BORDER / 30 # Size of all lives of players at bottom of screen

pygame.init()

# Make window and caption
win = pygame.display.set_mode((RIGHT_BORDER, BOTTOM_BORDER))
pygame.display.set_caption("Spongebob Shooters")


# Redraw everything on window
background_img = pygame.transform.scale(pygame.image.load('background.png'), (RIGHT_BORDER, BOTTOM_BORDER))
def redraw_window(win, map, entities, p1_weapons, p2_weapons, boss_weapons, lives, game_over):
    win.blit(background_img, (0, 0))

    # Redraw all entities
    for entity in entities:
        entities[entity].draw(win)

    # Redraw map of blocks
    for row_idx in range(len(map)):
        for block in map[row_idx]:
            block.draw(win)

    # Redraw weapons
    if entities["Player 1"].still_alive:
        for weapon in p1_weapons:
            weapon.draw(win)
    if entities["Player 2"].still_alive:
        for weapon in p2_weapons:
            weapon.draw(win)
    if entities["Boss"].still_alive:
        for weapon in boss_weapons:
            weapon.draw(win)

    # Redraw lives
    if entities["Player 1"].still_alive:
        space_between_lives = (RIGHT_BORDER - lives*LIFE_WIDTH) / (lives + 1)
        for i in range(lives):
            pygame.draw.rect(win, "green", (space_between_lives*(i + 1) + LIFE_WIDTH*i, (BOTTOM_BORDER - SPACE_FOR_LIVES) + SPACE_FOR_LIVES/ 2 - LIFE_WIDTH / 2,
                                            LIFE_WIDTH, LIFE_HEIGHT))

    # Tell the user if player 2 is still alive when player 1 is out
    if not entities["Player 1"].still_alive and entities["Player 2"].still_alive:
        font = pygame.font.SysFont(None, int(BOTTOM_BORDER / 15))
        font_text = font.render("Player 2 is still in", True, "red")
        win.blit(font_text, (RIGHT_BORDER / 2 - font_text.get_width() / 2,
                                BOTTOM_BORDER / 2 - font_text.get_width() / 2))

    font = pygame.font.SysFont(None, int(BOTTOM_BORDER / 15))
    if game_over and (entities["Player 1"].still_alive or entities["Player 2"].still_alive) and entities["Boss"].still_alive:
        font_text = font.render("You Tied", True, "orange")
        win.blit(font_text, (RIGHT_BORDER / 2 - font_text.get_width() / 2,
                             BOTTOM_BORDER / 2 - font_text.get_width() / 2))
    elif game_over and entities["Boss"].still_alive:
        font_text = font.render("You Lost", True, "red")
        win.blit(font_text, (RIGHT_BORDER / 2 - font_text.get_width() / 2,
                             BOTTOM_BORDER / 2 - font_text.get_width() / 2))
    elif game_over and (entities["Player 1"].still_alive or entities["Player 2"].still_alive):
        font_text = font.render("You Won", True, "green")
        win.blit(font_text, (RIGHT_BORDER / 2 - font_text.get_width() / 2,
                             BOTTOM_BORDER / 2 - font_text.get_width() / 2))

    pygame.display.update()

def menu_screen(win):
    win.fill("black")

    font = pygame.font.SysFont(None, int(BOTTOM_BORDER / 15))
    font_text = font.render("Waiting for player 2", True, "red")
    win.blit(font_text, (RIGHT_BORDER / 2 - font_text.get_width() / 2,
                         BOTTOM_BORDER / 2 - font_text.get_width() / 2))

    pygame.display.update()


def main():
    if __name__ == "__main__":
        network = Network()

        # Get boss from server
        entities = network.get_entities()
        boss = entities["Boss"]

        # Draw the map
        map = [[None for j in range(BROKEN_BLOCKS_PER_ROW)] for i in range(BROKEN_ROWS + 2)]
        map[0] = [Block(start_pos=(0, BOSS_SIZE[1] + boss.health_bar_height), size=(RIGHT_BORDER, BLOCK_HEIGHT), color="red")]
        y_inc = BOSS_SIZE[1] + boss.health_bar_height + BLOCK_HEIGHT
        for i in range(1, BROKEN_ROWS + 2):
            if i % 2 == 1:
                x_inc = ((RIGHT_BORDER - BROKEN_BLOCK_WIDTH - BROKEN_BLOCKS_PER_ROW) / (BROKEN_BLOCKS_PER_ROW - 1)) / 2
            else:
                x_inc = 0
            for j in range(BROKEN_BLOCKS_PER_ROW):
                map[i][j] = Block(start_pos=(x_inc, y_inc), size=(BROKEN_BLOCK_WIDTH, BLOCK_HEIGHT), color="blue")
                x_inc += (RIGHT_BORDER - BROKEN_BLOCK_WIDTH - BROKEN_BLOCKS_PER_ROW) / (BROKEN_BLOCKS_PER_ROW - 1)
            y_inc += (BOTTOM_BORDER - SPACE_FOR_LIVES - boss.height - boss.health_bar_height - BLOCK_HEIGHT*BROKEN_ROWS) / (BROKEN_ROWS - 1)
        map.remove(map[1])

        clock = pygame.time.Clock()
        fps = 60
        explosion_sound = pygame.mixer.Sound('explosion_sound.wav')
        pygame.mixer.set_num_channels(10)

        # Main game loop
        running = True
        while running:
            clock.tick(fps)

            # Quit if the user wants to
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Send and receive entity info
            entities = network.send(entities)
            player = entities["Player 1"]
            player2 = entities["Player 2"]
            boss = entities["Boss"]

            # Display menu screen when appropriate
            while not player2.connected:
                entities = network.send(entities)
                player = entities["Player 1"]
                player2 = entities["Player 2"]
                boss = entities["Boss"]
                menu_screen(win)

            # Handle sounds
            if player.num == 0:
                for key in player2.sounds_playing:
                    player.play_sound(key)
                player.sounds_playing.clear()
                # Player 1 passes down dutchman sounds to player 2
                if random.randint(1, 500) == 1:
                    player.play_sound("Dutchman")
                    player.sounds_playing.append("Dutchman")

                if random.randint(1, 500) == 1:
                    player.play_sound("Ship")
                    player.sounds_playing.append("Ship")

                if player.has_shot:
                    player.play_sound("Spongebob")
                    player.sounds_playing.append("Spongebob")
                    player.has_shot = False
            if player.num == 1:
                for key in player2.sounds_playing:
                    player.play_sound(key)
                player.sounds_playing.clear()
                if player.has_shot:
                    player.play_sound("Patrick")
                    player.sounds_playing.append("Patrick")
                    player.has_shot = False

            # The player is out when they run out of lives
            if player.lives == 0:
                player.still_alive = False
                player.health = 0

            # The boss is out if its health is gone
            if boss.health <= 0:
                boss.still_alive = False

            # Handle player movement
            if player.still_alive:
                player.handle_movement()

            # Handle gravity, landing, hitting head on blocks, and horizontal collisions
            if not player.game_over:
                player.apply_gravity(fps)
                for row_idx in range(len(map)):
                    for block in map[row_idx]:
                        if player.is_colliding_with(block) and player.y_vel > 0 and block.y + block.height / 2 < player.y < block.y + block.height:
                            player.handle_hitting_head(block)
                        elif player.is_colliding_with(block) and player.y_vel < 0 and block.y < player.y + player.height < block.y + block.height / 2:
                            player.handle_landing(block)
                        elif player.will_collide_horizontally(block, player.x_vel):
                            player.x -= player.x_vel
                        elif player.will_collide_horizontally(block, -player.x_vel):
                            player.x += player.x_vel

            # When a player falls off the bottom border, they lose a life and their health resets
            if player.y + player.height >= BOTTOM_BORDER:
                player.lives -= 1
                if player.num == 0:
                    player.x = 0
                    player.y = BOTTOM_BORDER - SPACE_FOR_LIVES - BLOCK_HEIGHT - player.height
                    player.health = player.total_health
                elif player.num == 1:
                    player.x = RIGHT_BORDER - player.width
                    player.y = BOTTOM_BORDER - SPACE_FOR_LIVES - BLOCK_HEIGHT - player.height
                    player.health = player.total_health

            # Handle explosion sounds
            if entities["Player 1"].explosion:
                pygame.mixer.Channel(9).play(explosion_sound)
                entities["Player 1"].explosion = False

            # Determine if the game is over
            if (not player.still_alive and not player2.still_alive) or not boss.still_alive:
                player.game_over = True

            entities = {"Player 1": player, "Player 2": player2, "Boss": boss}
            redraw_window(win, map, entities, player.active_missiles, player2.active_missiles, boss.active_weapons, player.lives, player.game_over)

        pygame.quit()
main()