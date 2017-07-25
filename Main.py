import pygame
from pygame.locals import *
import math
from decimal import *

pygame.init()
fps = 60

WHITE = pygame.Color(255, 255, 255)

font = pygame.font.SysFont('couriernew', 13)
fontComp = pygame.font.SysFont('couriernew', 16, True)
smallfont = pygame.font.SysFont('couriernew', 12)
massive = pygame.font.SysFont('couriernew', 200, True)

# sizes so nothing is hardcoded
size = (1024, 720)
standardSize = (16, 16)
bombSize = ((standardSize[0] / 2), (standardSize[1] / 2))

screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()
pygame.display.set_caption("Explosive Platformer")


# pygame.mouse.set_visible(False)

def getImg(name):  # gets images and prints their retrieval
	full = "assets/" + name + ".png"
	print "Loading: " + full
	try:
		return pygame.image.load(full)
	except pygame.error:  # if image isnt found, substitutes with writing in progress icon
		print "--File not found. Substituting"
		return pygame.image.load("assets/wip.png")


# SET GET IMAGES HERE
brickImg = getImg("Brick")
personimg = getImg("Derek")
movingImg = getImg("BrickMoving")


def toggle(bool):  # is used to make bomb and players stop when in contact with floor
	if bool:
		return False
	else:
		return True


def center(obj):  # finds center of object sent to function
	return (obj.coords[0] + (obj.size[0] / 2), obj.coords[1] + (obj.size[1] / 2))


# object one coord pair, size, object two coord pair and size
def collide(p1, p2, p3, p4):
	# if right side is right of left side, and left side left of right side
	if p1[1] + p2[1] > p3[1] and p1[1] < p3[1] + p4[1]:
		# if bottom is below top and top is above bottom
		if p1[0] + p2[0] > p3[0] and p1[0] < p3[0] + p4[0]:
			return True


# if point p3 is in p1 with size p2
def pointCollide(p1, p2, p3):
	if p1[0] + p2[0] > p3[0] and p1[0] < p3[0] and p1[1] + p2[1] > p3[1] and p1[1] < p3[1]:
		return True


class Person(object):
	def __init__(self, coords, size):
		self.coords = coords
		self.size = size
		self.vel = [0, -15]  # starts going up
		self.motion = [0.0, 0.0]  # attempted motion, xy direction
		self.floor = False  # is on ground
		self.crouch = False
		self.images = [getImg("Derek"), getImg("DerekCrouch")]
		self.img = 0

	def Crouch(self):
		self.crouch = True
		self.img = 1

	def unCrouch(self):
		self.crouch = False
		self.img = 0

	def Collide(self, i):
		if collide(i.coords, i.size, self.coords, self.size):  # DOWN
			# if self.vel[1] > 0: #Falling
			if center(self)[1] < center(i):
				self.coords[1] = i.coords[1] - self.size[1]
				self.vel[1] = 0
				self.floor = True
		if collide(self.coords, self.size, (i.coords[0], i.coords[1] + 3), (i.size[0], i.size[1] - 3)):  # LEFT / RIGHT
			if self.vel[0] > 0 and self.coords[0] <= i.coords[0]:
				self.coords[0] = i.coords[0] - self.size[0]
				self.vel[0] = 0
			if self.vel[0] < 0 and self.coords[0] + self.size[0] >= i.coords[0] + i.size[0]:
				self.coords[0] = i.coords[0] + i.size[0]
				self.vel[0] = 0
		if collide(i.coords, i.size, self.coords, self.size):  # UP
			if self.vel[1] < 0:  # Up-ing
				self.coords[1] = i.coords[1] + i.size[1]
				self.vel[1] = 0

		if collide(player.coords, (16, 17), i.coords, i.size):
			player.floor = True


player = Person([50, 250], (standardSize))


class movingBlock(object):
	def __init__(self, type, coords, size, img):
		self.type = type
		self.coords = coords
		self.size = size
		self.img = pygame.transform.scale(img, size)
		self.floor = False
		self.vel = [0, -15]


class Brick(object):
	def __init__(self, type, coords, size, img):
		self.type = type
		self.coords = coords
		self.size = size
		self.img = pygame.transform.scale(img, size)


movingblocks = []


class bomb(object):
	def __init__(self, type, coords, size, img):
		self.explodeTime = 10
		self.isExploding = False
		self.floor = False
		self.type = type
		self.coords = coords
		self.size = size
		self.img = img
		self.vel = [0, -15]

	def Collide(self, i):
		if collide(i.coords, i.size, self.coords, self.size):  # DOWN
			# if self.vel[1] > 0: #Falling
			if center(self)[1] < center(i):
				self.coords[1] = i.coords[1] - self.size[1]
				self.vel[1] = 0
				self.floor = True
		if collide(self.coords, self.size, (i.coords[0], i.coords[1] + 3), (i.size[0], i.size[1] - 3)):  # LEFT / RIGHT
			if self.vel[0] > 0 and self.coords[0] <= i.coords[0]:
				self.coords[0] = i.coords[0] - self.size[0]
				self.vel[0] = 0
			if self.vel[0] < 0 and self.coords[0] + self.size[0] >= i.coords[0] + i.size[0]:
				self.coords[0] = i.coords[0] + i.size[0]
				self.vel[0] = 0
		if collide(i.coords, i.size, self.coords, self.size):  # UP
			if self.vel[1] < 0:  # Up-ing
				self.coords[1] = i.coords[1] + i.size[1]
				self.vel[1] = 0

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


testBomb = bomb(1, [300, 250], (bombSize), getImg("Bomb"))

bombs = [testBomb]

bricks = []


def createFloor(coordx, coordy, ry, rx, type=0):
	bricks.append(Brick(type, [coordx, coordy], (rx * 16, ry * 16), brickImg))


def createWall(coordx, coordy, rx, ry, dir):
	if dir == "down":
		bricks.append(Brick("type", [coordx, coordy], (ry * 16, rx * 16), brickImg))
	if dir == "up":
		bricks.append(Brick("type", [coordx, coordy], (ry * 16, rx * 16), brickImg))


createFloor(0, 300, 1, 17)


def createMovingBlock(coordx, coordy, rx, ry):
	for i in range(rx, ry):
		movingblocks.append(movingBlock("type", [coordx + (16 * i), coordy], (16 * rx, 16), movingImg))


def createMovingBlock(coordx, coordy, rx, ry):
	for i in range(rx, ry):
		movingblocks.append(movingBlock("type", [coordx + (16 * i), coordy], (16 * rx, 16), movingImg))


# creates floors and walls based on coor and size
createFloor(0, 300, 1, 17)
createFloor(0, 300, 1, 4)

createFloor(200, 200, 1, 8)
createFloor(264, 216, 1, 2)
createMovingBlock(32, 200, 1, 1)
createFloor(200, 400, 3, 10)
createFloor(0, 704, 1, 34)
createFloor(600, 500, 1, 14)
createFloor(500, 300, 1, 1)
createFloor(300, 170, 1, 15)
createFloor(378, 245, 1, 3)
createFloor(220, 190, 1, 1)
createFloor(300, 256, 1, 10)
# createFloor(300,332,0,20,)
# createWall(264,332,0,20,"up")

# Current main screen, basic level.
Running = True

bombWaitTime = 0
normalBombWait = 1
detRange = 72
standardPower = 16

throwPower = 10

# maxFallSpeed != gravity!!
maxFallSpeed = 16
gravity = 0.5

affectedByBombs = [player]

while Running:
	if bombWaitTime > 0:  # sets off bomb
		bombWaitTime -= 1
	bombsExplode = False
	bombType = 1
	screen.fill(WHITE)

	# user input
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			# movement
			if event.key in [K_LEFT, K_a]:  # move <-
				player.motion[0] -= 2.0
			if event.key in [K_RIGHT, K_d]:  # move ->
				player.motion[0] += 2.0
			if event.key in [K_DOWN, K_s]:  # v
				player.motion[1] += 0.5
				player.Crouch()
			if event.key in [K_UP, K_w] and player.floor:  # ^
				player.vel[1] = -10
				player.floor = False
			if event.key == K_r:  # slow down
				fps = 10
			if event.key == K_f:  # speed up
				fps = 60
			if event.key == K_g:  # defunct?gravty on and off
				for i in bombs:
					i.floor = toggle(player.floor)
					i.vel[1] = 0
				player.floor = toggle(player.floor)
				player.vel[1] = 0
			if event.key == pygame.K_q:  # quiting
				Running = False
			if event.key == pygame.K_SPACE:  # exploding
				bombsExplode = True

		if event.type == pygame.KEYUP:
			if event.key in [K_LEFT, K_a]:
				player.motion[0] += 2.0
			if event.key in [K_RIGHT, K_d]:
				player.motion[0] -= 2.0
			if event.key in [K_DOWN, K_s]:
				player.motion[1] -= 0.5
				player.unCrouch()

		if event.type == pygame.MOUSEBUTTONDOWN:
			if bombWaitTime == 0:
				newBomb = bomb(bombType, [player.coords[0], player.coords[1]], (8, 8), getImg("Bomb"))
				x, y = pygame.mouse.get_pos()

				xChng = x - player.coords[0]
				yChng = y - player.coords[1]

				hy = math.hypot(xChng, yChng)

				if (hy != 0):
					newBomb.vel[0] = (xChng / hy) * throwPower
					newBomb.vel[1] = (yChng / hy) * throwPower

				bombs.append(newBomb)
				bombWaitTime = normalBombWait

	# Player
	# if not player.floor:
	if player.vel[1] < maxFallSpeed:  # maxFallSpeed
		player.vel[1] += gravity

	if (not player.floor):
		if player.vel[0] < .5 and player.motion[0] > 0:
			player.vel[0] += player.motion[0] / 4
		elif player.vel[0] > -.5 and player.motion[0] < 0:
			player.vel[0] += player.motion[0] / 4

	else:
		if player.crouch:
			if player.vel[0] > player.motion[0] / 4:
				player.vel[0] -= 0.5
			elif player.vel[0] < player.motion[0] / 4:
				player.vel[0] += 0.5
		else:
			if player.vel[0] > player.motion[0]:
				player.vel[0] -= 0.5
			elif player.vel[0] < player.motion[0]:
				player.vel[0] += 0.5

	player.coords[0] += player.vel[0]
	player.coords[1] += player.vel[1]
	if not collide(player.coords, player.size, (0, 0), size):
		player.coords = [50, 250]

	player.floor = False
	plamid = center(player)
	for i in bricks:
		player.Collide(i)
		for p in bombs:
			p.Collide(i)
		screen.blit(i.img, i.coords)

	screen.blit(player.images[player.img], player.coords)
	# Bombs
	for i in bombs:
		if not i.floor:
			if i.vel[1] < maxFallSpeed:
				i.vel[1] += gravity
		i.coords[0] += i.vel[0]
		i.coords[1] += i.vel[1]
		screen.blit(i.img, i.coords)

	if bombsExplode:
		for i in bombs:
			i.isExploding = True
			i.img = personimg
			for p in affectedByBombs:
				if i.type == 1:
					i.detonatorStandard(detRange, p, standardPower)

	for i in bombs:
		if i.isExploding:
			i.explodeTime -= 1
		if i.explodeTime <= 0:
			bombs.remove(i)

	# Moving Blocks
	for i in movingblocks:
		i.floor = False
		if not i.floor:
			if i.vel[1] < maxFallSpeed:  # Gravity
				i.vel[1] += gravity
		i.coords[0] += i.vel[0]
		i.coords[1] += i.vel[1]
	pygame.display.update()
	clock.tick(fps)