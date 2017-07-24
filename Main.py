import pygame
from pygame.locals import *
import math
from decimal import *

pygame.init()
fps = 60

font = pygame.font.SysFont('couriernew', 13)
fontComp = pygame.font.SysFont('couriernew', 16, True)
smallfont = pygame.font.SysFont('couriernew', 12)
massive = pygame.font.SysFont('couriernew', 200, True)

size = (995, 259)
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()
pygame.display.set_caption("Explosive Platformer")
pygame.mouse.set_visible(False)


def center(obj):
	return (obj.coords[0]+(obj.size[0]/2), obj.coords[1]+(obj.size[1]/2))

#object one coord pair, size, object two coord pair and size
def collide(p1, p2, p3, p4):
	#if right side is right of left side, and left side left of right side
	if p1[1] + p2[1] > p3[1] and p1[1] < p3[1] + p4[1]:
		#if bottom is below top and top is above bottom
		if p1[0] + p2[0] > p3[0] and p1[0] < p3[0] + p4[0]:
			return True

class Person(object):
	def __init__(self, coords, size):
		self.coords = coords
		self.size = size
		self.vel = vel


#Current main screen, basic level.
Running = True
while Running:
	
	
	

	pygame.display.update()
	clock.tick(fps)