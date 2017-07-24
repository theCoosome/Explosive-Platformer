import pygame
from pygame.locals import *
import math
from decimal import *

pygame.init()
fps = 60

WHITE = pygame.Color(255,255,255)

font = pygame.font.SysFont('couriernew', 13)
fontComp = pygame.font.SysFont('couriernew', 16, True)
smallfont = pygame.font.SysFont('couriernew', 12)
massive = pygame.font.SysFont('couriernew', 200, True)

size = (1024, 720)
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()
pygame.display.set_caption("Explosive Platformer")
#pygame.mouse.set_visible(False)

def getImg(name):
	full = "assets/"+name+".png"
	print "Loading: "+full
	try:
		return pygame.image.load(full)
	except pygame.error:
		print "--File not found. Substituting"
		return pygame.image.load("assets/wip.png")

def toggle(bool):
	if bool:
		return False
	else:
		return True
		
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
		self.vel = [0, -15]
		self.motion = [0, 0] #attempted motion, xy direction
		self.floor = False #is on ground
		self.crouch = False
		self.images = [getImg("Human"), getImg("HumanCrouch")]
		self.img = 0
	def Crouch(self):
		self.crouch = True
		self.img += 1
	def unCrouch(self):
		self.crouch = False
		self.img -= 1
		
player = Person([250, 250], (16, 16))

class movingBlock(object):
	def __init__(self, type, coords, size, img):
		self.type = type
		self.coords = coords
		self.size = size
		self.img = img
		
movingblocks = []
		
class bomb(object):
	def __init__(self, type, coords, size, img):
		self.floor = False
		self.type = type
		self.coords = coords
		self.size = size
		self.img = img
		self.vel = [0, -15]
testBomb = bomb(1, [300, 250], (16, 16), getImg("Bomb"))

bombs = [testBomb]

#Current main screen, basic level
Running = True
while Running:
	screen.fill(WHITE)
	
	#user input
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			#movement
			if event.key in [K_LEFT, K_a]:
				player.motion[0] -= 2
			if event.key in [K_RIGHT, K_d]:
				player.motion[0] += 2
			if event.key in [K_DOWN, K_s]:
				player.motion[1] += 0.5
				player.Crouch()
			if event.key in [K_UP, K_w] and player.floor:
				player.vel[1] = -10
				player.floor = False
			if event.key == K_g:
				player.floor = toggle(player.floor)
				player.vel[1] = 0
			if event.type == pygame.QUIT:
				Running = False
			
		if event.type == pygame.KEYUP:
			if event.key in [K_LEFT, K_a]:
				player.motion[0] += 2
			if event.key in [K_RIGHT, K_d]:
				player.motion[0] -= 2
			if event.key in [K_DOWN, K_s]:
				player.motion[1] -= 0.5
				player.unCrouch()
				
				
	#Player
	if not player.floor:
		if player.vel[1] < 20: #Gravity
			player.vel[1] += 0.5
	
	if not player.floor or player.crouch:
		if player.vel[0] < player.motion[0]/2:
			player.vel[0] += 0.5
		if player.vel[0] > player.motion[0]/2:
			player.vel[0] -= 0.5
		
	else:
		if player.vel[0] > player.motion[0]:
			player.vel[0] -= 0.5
		if player.vel[0] < player.motion[0]:
			player.vel[0] += 0.5
		#if player.vel[1] > player.motion[1]:
		#	player.vel[1] -= 0.5
	
	player.coords[0] += player.vel[0]
	player.coords[1] += player.vel[1]
	
	screen.blit(player.images[player.img], player.coords)
	#Bombs
	for i in bombs:
		if not i.floor:
			if i.vel[1] < 20:
				i.vel[1] += 0.5
		i.coords[0] += i.vel[0]
		i.coords[1] += i.vel[1]
		screen.blit(i.img, i.coords)

	#Moving Blocks
	for i in movingblocks:
		screen.blit(i.img, i.coords)
	
	pygame.display.update()
	clock.tick(fps)