# block.py stores all relevant information about each block the players stand on

# Imports
import pygame

class Block:
    def __init__(self, start_pos, size, color):
        self.x, self.y = start_pos
        self.width, self.height = size
        self.color = color
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)
