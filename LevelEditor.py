import pygame
from pygame.locals import *
import math
from decimal import *

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

size = (1024, 720)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Explosive Platformer Level Editor")

WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
BLUE = pygame.Color(0, 0, 255)

clock = pygame.time.Clock()

pygame.mouse.set_visible(False)
font = pygame.font.SysFont('couriernew', 13)
fontComp = pygame.font.SysFont('couriernew', 16, True)
smallfont = pygame.font.SysFont('couriernew', 12)
massive = pygame.font.SysFont('couriernew', 200, True)

def getImg(name):  # gets images and prints their retrieval
	full = "assets/" + name + ".png"
	print "Loading: " + full
	try:
		return pygame.image.load(full)
	except pygame.error:  # if image isnt found, substitutes with writing in progress icon
		print "--File not found. Substituting"
		return pygame.image.load("assets/wip.png")

brickImg = getImg("Brick")
personimg = getImg("Derek")
movingImg = getImg("BrickMoving")
destructableImg = getImg("BrickDestructable")
bombImg = getImg("Bomb")

#Mouse Images
AimImg = getImg("Mouse/Aim")
BrickPlaceImg = getImg("Mouse/Brick")
DPlaceImg = getImg("Mouse/Destructable")
MovablePlaceImg = getImg("Mouse/Movable")
MultiPlaceImg = getImg("Mouse/Multi")
ExitPlaceImg = getImg("Mouse/Exit")
RemoveImg = getImg("Mouse/Remove")
mouseImgs = [AimImg, BrickPlaceImg, DPlaceImg, MovablePlaceImg, MultiPlaceImg, ExitPlaceImg, RemoveImg]
mouseImg = mouseImgs[0]

def center(obj):  # finds center of object sent to function
	return (obj.coords[0] + (obj.size[0] / 2), obj.coords[1] + (obj.size[1] / 2))

class Person(object):
	def __init__(self, coords, size):
		self.coords = coords
		self.size = size
		self.vel = [0, -15]  # starts going up
		self.motion = [0.0, 0.0]  # attempted motion, xy direction
		self.floor = False  # is on ground
		self.crouch = False
		self.index = 0
		self.img = 0


	def Crouch(self):
		self.crouch = True
		self.img = 1


	def unCrouch(self):
		self.crouch = False
		self.img = 0

	def Collide(self, i):
		if collide(self.coords, self.size, (i.coords[0], i.coords[1] + 3), (i.size[0], i.size[1] - 3)):  # LEFT / RIGHT
			p1 = center(self)
			if self.vel[0] > 0 and self.coords[0] <= i.coords[0]:
				self.coords[0] = i.coords[0] - self.size[0]
				self.vel[0] = 0
				pygame.draw.line(screen, RED, p1, center(self))
			if self.vel[0] < 0 and self.coords[0] + self.size[0] >= i.coords[0] + i.size[0]:
				self.coords[0] = i.coords[0] + i.size[0]
				self.vel[0] = 0
				pygame.draw.line(screen, RED, p1, center(self))
		if collide(i.coords, i.size, self.coords, self.size):  # UP
			p1 = center(self)
			if center(self)[1] > center(i)[1]:
				self.coords[1] = i.coords[1] + i.size[1]
				self.vel[1] = 0
				pygame.draw.line(screen, GREEN, p1, center(self))
			if center(self)[1] < center(i)[1]: #DOWN
				self.coords[1] = i.coords[1] - self.size[1]
				self.vel[1] = 0
				self.floor = True
				pygame.draw.line(screen, BLUE, p1, center(self))
		if collide(self.coords, (self.size[0], self.size[1] + 1), i.coords, i.size):
			self.floor = True


class movingBlock(object):
	def __init__(self, type, coords, size):
		self.hp = 1
		self.type = type
		self.coords = coords
		self.size = size
		self.floor = False
		self.vel = [0, 0]
		if type == 0:  # Movable
			self.img = pygame.transform.scale(movingImg, size)

		if type == 1:  # Destructable
			self.img = pygame.transform.scale(destructableImg, size)

		if type == 2:  # Movable and Destructable
			self.img = pygame.transform.scale(destructableImg, size)

	def Collide(self, i):
		if collide(self.coords, self.size, i.coords, i.size):  # LEFT / RIGHT
			if self.vel[0] > 0 and self.coords[0] <= i.coords[0]:
				self.coords[0] = i.coords[0] - self.size[0]
				self.vel[0] = 0
			if self.vel[0] < 0 and self.coords[0] + self.size[0] >= i.coords[0] + i.size[0]:
				self.coords[0] = i.coords[0] + i.size[0]
				self.vel[0] = 0
		if collide(i.coords, i.size, self.coords, self.size):  # DOWN
			if center(self)[1] < center(i)[1]:
				self.coords[1] = i.coords[1] - self.size[1]
				self.vel[1] = 0
				self.floor = True
		if collide(i.coords, i.size, self.coords, self.size):  # UP
			if center(self)[1] > center(i)[1]:  # Up-ing
				self.coords[1] = i.coords[1] + i.size[1]
				self.vel[1] = 0

		if collide(self.coords, (self.size[0], self.size[1] + 1), i.coords, i.size):
			self.floor = True


class Brick(object):
	def __init__(self, type, coords, size, img):
		self.type = type
		self.coords = coords
		self.size = size
		self.img = pygame.transform.scale(img, size)





placeMode = "brick"

movingblocks = []


class bomb(object):
	def __init__(self, type, coords, size, img):
		self.explodeTime = 16
		self.isExploding = False
		self.floor = False
		self.stuck = False
		self.stuckOn = None
		self.type = type
		self.coords = coords
		self.size = size
		self.img = img
		self.vel = [0, -15]

	def incrementSprite(self, number, curr):
		curr = 16 - curr
		self.img = normalBombImgs[curr]

	def Collide(self, i):
		if collide(self.coords, self.size, i.coords, i.size):  # LEFT / RIGHT
			if self.vel[0] > 0 and self.coords[0] <= i.coords[0]:
				self.coords[0] = i.coords[0] - self.size[0]
				self.vel[0] = 0
				self.stuck = True
			if self.vel[0] < 0 and self.coords[0] + self.size[0] >= i.coords[0] + i.size[0]:
				self.coords[0] = i.coords[0] + i.size[0]
				self.vel[0] = 0
				self.stuck = True
		if collide(i.coords, i.size, self.coords, self.size):  # DOWN
			if center(self)[1] < center(i)[1]:
				self.coords[1] = i.coords[1] - self.size[1]
				self.vel[1] = 0
				self.floor = True
				self.stuck = True
		if collide(i.coords, i.size, self.coords, self.size):  # UP
			if center(self)[1] > center(i)[1]:  # Up-ing
				self.coords[1] = i.coords[1] + i.size[1]
				self.vel[1] = 0
				self.stuck = True

		if collide(self.coords, (self.size[0], self.size[1] + 1), i.coords, i.size):
			self.floor = True

	def detonatorStandard(self, detRange, mob, standardPower):

		px, py = mob.coords
		bx, by = self.coords

		xd = px - bx
		yd = py - by

		td = math.hypot(xd, yd)
		pow = standardPower * ((detRange - td) / detRange)

		if pow < 0:
			pow = 0

		if (td != 0):
			mob.vel[0] += (xd / td) * pow
			mob.vel[1] += (yd / td) * pow

def Zero(num, rate, goal=0):
	if num > goal:
		num -= rate
		if num < goal:
			num = goal
	if num < goal:
		num += rate
		if num > goal:
			num = goal
	return num

gR = 0
gL = 0

Running = True

while Running:
	mousepos = pygame.mouse.get_pos()
	screen.fill(WHITE)

	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q:  # quiting
				Running = False

		if event.type == pygame.MOUSEBUTTONDOWN:
			print event.button
			if event.button == 1:
				startPlace()
			if event.button == 4:
				newImgNum = mouseImgs.index(mouseImg) + 1
				if newImgNum >= len(mouseImgs):
					newImgNum = 0
				mouseImg = mouseImgs[newImgNum]
			if event.button == 5:
				newImgNum = mouseImgs.index(mouseImg) - 1
				if newImgNum < 0:
					newImgNum = len(mouseImgs)-1
				mouseImg = mouseImgs[newImgNum]

	screen.blit(mouseImg, (mousepos[0] - 3, mousepos[1] - 3))
	pygame.display.update()
	clock.tick(60)
