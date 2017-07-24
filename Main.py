import pygame
from pygame.locals import *
import math

pygame.init()

font = pygame.font.SysFont('couriernew', 13)
fontComp = pygame.font.SysFont('couriernew', 16, True)
smallfont = pygame.font.SysFont('couriernew', 12)
massive = pygame.font.SysFont('couriernew', 200, True)

size = (995, 259)
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()
pygame.display.set_caption("Explosive Platformer")
pygame.mouse.set_visible(False)



Running = True
while Running:
	
	
	
	screen.update()
	clock.tick(60)