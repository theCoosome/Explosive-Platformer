import pygame
from pygame.locals import *
import math
from decimal import *
import time

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
fps = 60
debugon = True

WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
BLUE = pygame.Color(0, 0, 255)

pygame.mouse.set_visible(False)
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
brickImg = getImg("Bricks/Brick")
personimg = getImg("Dereks/Derek")
movingImg = getImg("Bricks/BrickMoving")
destructableImg = getImg("Bricks/BrickDestructable")
multiImg = getImg("Bricks/BrickMulti")

switches= [getImg("Switch"),getImg("Switch2")]
switchImg = switches[0]
lockImg = getImg("bars")
keyImg = getImg("key")
crateImg = getImg("crate")




#Bombs
bombImg = getImg("Bomb")
platformImg = getImg("platform")



normalBombImgs = []
i = 0
while i < 10:
	normalBombImgs.append(getImg("Explosion_Normal/sprite_0" + str(i)))
	i+=1
while i < 17:
	normalBombImgs.append(getImg("Explosion_Normal/sprite_" + str(i)))
	i+=1
normalExplode = [getImg("")]

#Mice
AimImg = getImg("Mouse/Aim")
mouseImg = AimImg

#Anim
derek = getImg("Dereks/Derek")
left = [getImg("Dereks/anim1l"),getImg("Dereks/anim2l"),getImg("Dereks/anim3l")]
right = [getImg("Dereks/anim1r"),getImg("Dereks/Derek"),getImg("Dereks/anim2r")]
crouchImg = [getImg("Dereks/DerekCrouch"),getImg("Dereks/derekcrouchl")]

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


def isNear(p1, p2, dist = 32):

	xChng = p1[0] - p2[0]
	yChng = p1[1] - p2[1]

	hy = math.hypot(xChng, yChng)
	#print distance
	if hy <= dist:
		return True
	else:
		return False
def isOnTop(p1,p2):
	distance = abs(p1.coords[1] - p2.coords[1])
	if distance <= 32:
		return True
	else:
		return False

class Platform(object):
	def __init__(self,coords,size,img):
		self.coords = coords
		self.size = size
		self.img = pygame.transform.scale(img, size)
		self.stuck = False

class Person(object):
	def __init__(self, coords, size, hasKey):
		self.coords = coords
		self.size = size
		self.vel = [0, -15]  # starts going up
		self.motion = [0.0, 0.0]  # attempted motion, xy direction
		self.floor = False  # is on ground
		self.crouch = False
		self.index = 0
		self.img = 0
		self.hasKey = hasKey

		self.dualColliding = False

	def Crouch(self):
		self.crouch = True
		self.img = 1

	def unCrouch(self):
		self.crouch = False
		self.img = 0

	def Kill(self):
		print "Ded"
		createLevel(currLvl)
	def Collide(self, i):
		if collide(i.coords, i.size, self.coords, self.size):  # UP

			if self.dualColliding:
				self.Kill()
			if type(i) == movingBlock:
				if i.vel[1] > 5 and center(player)[1] > center(i)[1]:
					self.Kill()
				self.dualColliding = True

			p1 = center(self)
			#if center(self)[1] < center(i)[1]: #FLOOR
			if self.vel[1] > 0 and self.coords[1] <= i.coords[1]:
				self.coords[1] = i.coords[1] - self.size[1]
				if self.vel[1] > 0:
					self.vel[1] = 0
				self.floor = True
				pygame.draw.line(screen, BLUE, p1, center(self))
			if collide(self.coords, self.size, (i.coords[0], i.coords[1] + 3), (i.size[0], i.size[1] - 3)):  # LEFT / RIGHT
				p1 = center(self)
				if self.coords[0] <= i.coords[0]:
					self.coords[0] = i.coords[0] - self.size[0]
					self.vel[0] = 0
					pygame.draw.line(screen, RED, p1, center(self))
				if self.coords[0] + self.size[0] >= i.coords[0] + i.size[0]:
					self.coords[0] = i.coords[0] + i.size[0]
					self.vel[0] = 0
					pygame.draw.line(screen, RED, p1, center(self))
					
			if self.vel[1] < 0 and self.coords[1] + self.size[1] >= i.coords[1] + i.size[1]:
				self.coords[1] = i.coords[1] + i.size[1]
				self.vel[1] = 0
				pygame.draw.line(screen, GREEN, p1, center(self))
		if collide(self.coords, (self.size[0], self.size[1] + 1), i.coords, i.size):
			self.floor = True
		
	def floorCol(self, i):
		if collide(i.coords, i.size, self.coords, self.size):  # UP
			if self.vel[1] > 0 and self.coords[1] <= i.coords[1]:
				self.coords[1] = i.coords[1] - self.size[1]
				if self.vel[1] > 0:
					self.vel[1] = 0
				self.floor = True


player = Person([50, 250], (standardSize),False)


class movingBlock(object):
	def __init__(self, type, coords, size):
		self.hp = 1
		self.type = type
		self.coords = coords
		self.size = size
		self.floor = False
		self.vel = [0, 0]
		if type == 0: #Movable
			self.img = pygame.transform.scale(movingImg, size)

		if type == 1: #Destructable
			self.img = pygame.transform.scale(destructableImg, size)

		if type == 2: #Movable and Destructable
			self.img = pygame.transform.scale(multiImg, size)

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

class Switch(object):
	def __init__(self,type,coords,size,img,toggle):
		self.type = type
		self.coords = coords
		self.size = size
		self.img = img
		self.toggle = toggle
movingblocks = []


class Key(object):
	def __init__(self,coords,size,img):
		self.coords = coords
		self.size = size
		self.img = pygame.transform.scale(img, size)
class Gate(object):
	def __init__(self,coords,size,img,open):
		self.coords = coords
		self.size = size
		self.img = pygame.transform.scale(img, size)
		self.open = open
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
class Crate(object):
	def __init__(self,coords,size,img):
		self.coords = coords
		self.size = size
		self.img = img

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

class bomb(object):
	def __init__(self, type, coords, vel, size, pow, arm, img):
		self.type = type
		self.coords = coords
		self.size = size
		self.img = img
		self.pow = pow
		self.time = 0
		self.arm = arm
		self.armed = False
		self.explodeTime = 16
		self.isExploding = False
		self.floor = False
		self.stuck = False

		self.stuckOn = None
		self.relative = (0, 0)

		self.vel = vel
		self.detRange = 72

	def incrementSprite(self, number, curr):
		curr = 16 - curr
		self.img = normalBombImgs[curr]

	def Collide(self, i):
		if collide(self.coords, self.size, i.coords, i.size):  # LEFT / RIGHT
			if self.vel[0] > 0 and self.coords[0] <= i.coords[0]:
				self.coords[0] = i.coords[0] - self.size[0]
				self.vel[0] = 0
				self.stuck = True
				if type(i) == movingBlock:
					self.stuckOn = i
					self.relative = (self.coords[0]-i.coords[0], self.coords[1]-i.coords[1])
			if self.vel[0] < 0 and self.coords[0] + self.size[0] >= i.coords[0] + i.size[0]:
				self.coords[0] = i.coords[0] + i.size[0]
				self.vel[0] = 0
				self.stuck = True
				if type(i) == movingBlock:
					self.stuckOn = i
					self.relative = (self.coords[0]-i.coords[0], self.coords[1]-i.coords[1])
		if collide(i.coords, i.size, self.coords, self.size):  # DOWN
			if center(self)[1] < center(i)[1]:
				self.coords[1] = i.coords[1] - self.size[1]
				self.vel[1] = 0
				self.floor = True
				self.stuck = True
				if type(i) == movingBlock:
					self.stuckOn = i
					self.relative = (self.coords[0]-i.coords[0], self.coords[1]-i.coords[1])
			if center(self)[1] > center(i)[1]:  # Up-ing
				self.coords[1] = i.coords[1] + i.size[1]
				self.vel[1] = 0
				self.stuck = True
				if type(i) == movingBlock:
					self.stuckOn = i
					self.relative = (self.coords[0]-i.coords[0], self.coords[1]-i.coords[1])

		if collide(self.coords, (self.size[0], self.size[1] + 1), i.coords, i.size):
			self.floor = True

	def Detonate(self, mob):

		px, py = mob.coords
		bx, by = self.coords

		xd = px - bx
		yd = py - by

		td = math.hypot(xd, yd)

		pow = self.pow * ((self.detRange - td) / self.detRange)

		if pow < 0:
			pow = 0

		if (td != 0):
			mob.vel[0] += (xd / td) * pow
			mob.vel[1] += (yd / td) * pow


class detonator(object):
	def __init__(self, type, kbP, kbB, dmg, arm, max, img, img2):
		self.type = type
		self.kbP = kbP #player knockback
		self.kbB = kbB #block knockback
		self.dmg = dmg
		self.arm = arm #arm time
		self.max = max #Max quantity out
		self.img = img #Detonator image
		self.bomb = img2 #Bomb image
	def newBomb(self, coords, vel):
		return bomb(self.type, coords, vel, (8, 8), self.kbP, self.arm, self.bomb)

DetGod = detonator(0, 16, 16, 5, 0, 99999, getImg("UI/DetDefault"), bombImg)
DetNorm = detonator(1, 2, 8, 5, 30, 4, getImg("UI/DetDefault"), bombImg)
DetKB = detonator(2, 16, 16, 1, 20, 2, getImg("UI/DetJumper"), getImg("tosser"))
DetMulti = detonator(3, 4, 6, 5, 80, 10, getImg("UI/DetMulti"), getImg("Multi"))
DetDest = detonator(4, 1, 1, 20, 30, 4, getImg("UI/DetDestructive"), getImg("Dest"))
DetCurrent = DetGod

bombs = []

bricks = []



def spawnChar():
	if currLvl == 0:
		player.coords = [50, 250]
	elif currLvl == 1:
		player.coords = [50, 500]
	else:
		player.coords = [50, 250]
	print currLvl
	player.vel[1] = 0
	player.vel[0] = 0

def createFloor(coordx, coordy, ry, rx, type=0):
	bricks.append(Brick(type, [coordx, coordy], (rx * 16, ry * 16), brickImg))

def wipeFloor():
	del bricks[:]
	del bombs[:]
	del movingblocks[:]
	del switchs[:]
	del gates[:]
	del platforms[:]

def createWall(coordx, coordy, rx, ry, dir):
	if dir == "down":
		bricks.append(Brick("type", [coordx, coordy], (ry * 16, rx * 16), brickImg))
	if dir == "up":
		bricks.append(Brick("type", [coordx, coordy], (ry * 16, rx * 16), brickImg))



def createMovingBlock(coordx, coordy, rx, ry, type):
	movingblocks.append(movingBlock(type, [coordx, coordy], [rx*16, ry*16]))



def borderedLevel():
	createFloor(0, 0, 2, 64)
	createFloor(0, 688, 2, 64)
	createFloor(0, 32, 41, 2)
	createFloor(992, 32, 41, 2)
# creates floors and walls based on coor and size

switchs = []
keys = []
gates = []
crates = []
platforms = []


def openReadFile(filePath):
	file = open(filePath, "r")
	cont = file.readlines()
	for i in cont:
		symbol, type, x, y, xs, ys = i.split("*")
		if symbol == "$":

			if type == "-1":
				print "worked"
				createFloor(int(x), int(y), int(int(ys) / 16), int(int(xs) / 16))
			else:
				print "moveBlock"
				createMovingBlock(int(x), int(y), int(int(xs) / 16), int(int(ys) / 16), int(type))


currLvl = 0
totalLvls = 2	#CHANGE THIS WHEN ADDING LVLS

def createLevel(lvl):	#Almost all refrences of this should be written createLevel(currLvl). Only use an int for bugtesting.
	wipeFloor()
	spawnChar()
	if (lvl == -1):
		openReadFile("saves/Level Editor Save.txt")
	elif (lvl == 0):
		borderedLevel()
		createFloor(32, 300, 1, 15)
		createFloor(200, 200, 1, 8)
		createFloor(264, 216, 1, 2)
		createFloor(200, 400, 3, 10)
		createFloor(600, 500, 1, 14)
		createFloor(500, 300, 1, 1)
		createFloor(300, 170, 1, 15)
		createFloor(378, 245, 1, 3)
		createFloor(220, 190, 1, 1)
		createFloor(300, 256, 1, 10)

		#platforms.append(Platform((896, 626), (64, 64), platformImg))
		switchs.append(Switch("Switch", (256, 284), (32, 32), switchImg, False))
		crates.append(Crate((432, 160), (16, 16), crateImg))
		keys.append(Key((432, 160), (8, 8), keyImg))
		gates.append(Gate((896, 626), (64, 64), lockImg, False))
		#movingblocks.append(movingBlock(0,[64,64],(16,16)))
		movingblocks.append(movingBlock(0,[320,60],(48,32)))

	elif (lvl == 1):
		createFloor(0, 688, 2, 64)

# Current main screen, basic level.
Running = True


bombWaitTime = 0
normalBombWait = 1
detRange = 72
standardPower = 16

throwPower = 10

# maxFallSpeed != gravity!!
maxFallSpeed = 16
gravity = 0.5  # pixels per frame
friction = 0.25  # pixels per frame


def Zero(num, rate, goal = 0.0):
	if num > goal:
		num = num-rate
		if num <= goal:
			num = goal
	if num < goal:
		num = num+rate
		if num >= goal:
			num = goal
	return num


affectedByBombs = [player]

movingLeft = False
movingRight = False
gR = 0
gL = 0
isCrouching = False
counter = 0

createLevel(currLvl)

while Running:
	mousepos = pygame.mouse.get_pos()
	if bombWaitTime > 0:  # sets off bomb
		bombWaitTime -= 1
	bombsExplode = False
	player.dualColliding = False
	bombType = 1
	screen.fill(WHITE)

	# user input
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:

			#Switches and Interactable Objects
			if (isNear(center(switchs[0]), center(player))):
				if event.key in [K_e]:
					movingblocks.append(movingBlock(0, [64, 64], (16, 16)))

					switchs[0].img = switches[1]



			# movement
			if event.key in [K_RIGHT, K_d]:  # move ->
				player.motion[0] += 2.0
				gR = 0
				movingRight = True
				movingLeft = False
			if event.key in [K_LEFT, K_a]:  # move <-
				player.motion[0] -= 2.0
				gL =0
				time.sleep(.02)
				movingLeft = True
				movingRight = False
			if event.key in [K_RIGHT and K_a, K_LEFT and K_d]:  # move ->
				movingRight = False
				movingLeft = False
				playerimg=derek
			if event.key in [K_DOWN, K_s]:  # v
				player.motion[1] += 0.5
				player.Crouch()
			if event.key in [K_UP, K_w] and player.floor:  # ^
				player.vel[1] = -8
				effect = pygame.mixer.Sound("assets/Sounds/Jump3.wav")
				effect.play()
				player.floor = False
			if event.key == K_r:  # slow down
				fps /= 2
			if event.key == K_f:  # speed up
				fps = 60
			if event.key == K_x:
				createLevel(currLvl)
			if event.key == K_z:
				print "Coords: ", player.coords[0], player.coords[1]
				print "Velocity: ", player.vel[0], player.vel[1]
				print "Motion: ", player.motion[0], player.motion[1]
				print "Floored: ", player.floor
			if event.key == K_g:  # defunct?gravty on and off
				for i in bombs:
					i.floor = toggle(player.floor)
					i.vel[1] = 0
				player.floor = toggle(player.floor)
				player.vel[1] = 0
			if event.key == pygame.K_q:  # quitting
				Running = False
			if event.key == K_p:  # Increment level by 1
				currLvl += 1
				if currLvl >= totalLvls:
					currLvl = 0
				createLevel(currLvl)
			if event.key == K_o:
				currLvl -= 1
				if currLvl < 0:
					currLvl = totalLvls - 1
				createLevel(currLvl)
			if event.key == K_l:  # slow down
				currLvl = -1
				createLevel(-1)
			if event.key == pygame.K_SPACE:  # exploding
				bombsExplode = True
			if event.key == pygame.K_t:  # print cursor location, useful for putting stuff in the right spot
				x, y = pygame.mouse.get_pos()
				print "Absolute: ", x, y
				print "16 base:", x/16, y/16, "("+str((x/16)*16), str((y/16)*16)+")"

			if event.key == K_1:
				bombs = []
				DetCurrent = DetGod
			if event.key == K_2:
				bombs = []
				DetCurrent = DetNorm
			if event.key == K_3:
				bombs = []
				DetCurrent = DetKB
			if event.key == K_4:
				bombs = []
				DetCurrent = DetMulti
			if event.key == K_5:
				bombs = []
				DetCurrent = DetDest


		if event.type == pygame.KEYUP:
			if event.key in [K_LEFT, K_a]:
				player.motion[0] += 2.0
			if event.key in [K_RIGHT, K_d]:
				player.motion[0] -= 2.0
			if event.key in [K_DOWN, K_s]:
				player.motion[1] -= 0.5
				player.unCrouch()

		if event.type == pygame.MOUSEBUTTONDOWN:
			if bombWaitTime == 0 and len(bombs) < DetCurrent.max:
				x, y = pygame.mouse.get_pos()

				xChng = x - player.coords[0]
				yChng = y - player.coords[1]

				hy = math.hypot(xChng, yChng)

				if (hy != 0):
					bombs.append(DetCurrent.newBomb([player.coords[0], player.coords[1]], [((xChng / hy) * throwPower), ((yChng / hy) * throwPower)]))

				bombWaitTime = normalBombWait

	# Player
	# if not player.floor:
	if player.vel[1] < maxFallSpeed:  # maxFallSpeed
		player.vel[1] += gravity


	#PLAYER MOVEMENT INPUT
	if (not player.floor):
		if player.vel[0] < .5 and player.motion[0] > 0:
			player.vel[0] += player.motion[0] / 4
		elif player.vel[0] > -.5 and player.motion[0] < 0:
			player.vel[0] += player.motion[0] / 4

	else:
		if player.motion[0] != 0:
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

	if player.vel[0]  <=-16:
		player.vel[0] = -16

	if player.vel[1] <=-16:
		player.vel[1] = -16

	if player.vel[0] >= 16:
		player.vel[0] = 16

	if player.vel[1] >= 16:
		player.vel[1] = 16



	player.coords[0] += player.vel[0]
	player.coords[1] += player.vel[1]

	if not collide(player.coords, player.size, (0, 0), size):
		player.Kill()


	player.floor = False

	for k in keys:
		screen.blit(k.img,k.coords)
		if isNear(player.coords, k.coords):
			player.hasKey = True
			effect = pygame.mixer.Sound("assets/Sounds/Win.wav")
			effect.play()
			print("1")
			keys.remove(k)
	for g in gates:
		if isNear(g.coords, player.coords):
			if player.hasKey == True:
				effect = pygame.mixer.Sound("assets/Sounds/Open.wav")
				effect.play()
				print("2")
	
	if len(movingblocks) > 0:
		for i in bricks:
			player.Collide(i)
		
	for i in platforms:
		player.Collide(i)
	for i in crates:
		player.Collide(i)
		screen.blit(i.img,i.coords)
	for g in gates:
		player.Collide(g)
		screen.blit(g.img,g.coords)

	for i in movingblocks: #Moving blocks collide with each other
		for p in movingblocks:
			if not (p == i):
				p.Collide(i)
	if player.vel[0] == 0 and player.vel[1] == 0:
		movingLeft = False
		movingRight = False
	if player.crouch:
		if player.motion[0] < 0:
			personimg = crouchImg[1]
		else:
			personimg = crouchImg[0]
	else:
		if player.motion[0] == 0:
			personimg = right[1]
		elif player.motion[0] < 0:
			if movingLeft:
				counter += 1
				if counter == 10:
					player.index += 1
					counter = 0
				if player.index >= len(left):
					player.index = 0
			personimg = left[player.index]
		elif player.motion[0] > 0:
			if movingRight:
				if not isCrouching :
					counter += 1
					if counter == 10:
						player.index += 1
						counter = 0
					if player.index >= len(right):
						player.index = 0
			personimg = right[player.index]

	# Moving Blocks
	for i in movingblocks: #Player collide with moving blocks
		player.Collide(i)
		if i.type in [0, 2]:
			i.floor = False
			if i.vel[1] < maxFallSpeed:  # Gravity
				i.vel[1] += gravity

			if i.vel[0] <= -16:
				i.vel[0] = -16

			if i.vel[1] <= -16:
				i.vel[1] = -16

			if i.vel[0] >= 16:
				i.vel[0] = 16

			if i.vel[1] >= 16:
				i.vel[1] = 16

			i.coords[0] += i.vel[0]
			i.coords[1] += i.vel[1]

			for p in bricks:
				i.Collide(p)
			if i.floor:
				i.vel[0] = Zero(i.vel[0], friction)
		screen.blit(i.img,i.coords)
		
		for p in platforms:
			player.Collide(p)
			for mb in movingblocks:
				if isOnTop(p,mb) and isNear(center(p),center(mb)):
					print "you won!"
				mb.Collide(p)
			screen.blit(p.img,p.coords)

	for i in bricks:
		screen.blit(i.img, i.coords)
		player.Collide(i)

	for i in bombs:
		if i.isExploding:
			i.explodeTime -= 1
			i.incrementSprite(1, i.explodeTime)
			effect = pygame.mixer.Sound("assets/Sounds/Explosion.wav")
			effect.play()
			if i.explodeTime > 10:

				pygame.draw.circle(screen, BLACK, (int(center(i)[0]), int(center(i)[1])), detRange-player.size[0], 1)


		if i.explodeTime <= 0:
			bombs.remove(i)

		if not i.stuck:
			if i.vel[1] < maxFallSpeed:
				i.vel[1] += gravity
			i.coords[0] += i.vel[0]
			i.coords[1] += i.vel[1]

		if not i.armed:
			i.time += 1
			if i.time >= i.arm:
				i.armed = True
				effect = pygame.mixer.Sound("assets/Sounds/throw.wav")
				effect.play()

		if (i.stuckOn != None):
			if (i.stuckOn in movingblocks): #Follow what it is stuck to
				i.coords = [i.stuckOn.coords[0]+i.relative[0], i.stuckOn.coords[1]+i.relative[1]]
			elif (i.stuckOn in crates): #Follow what it is stuck to
				i.coords = [i.stuckOn.coords[0]+i.relative[0], i.stuckOn.coords[1]+i.relative[1]]
			else:
				i.stuck = False
				i.stuckOn = None

		if not i.stuck:
			for p in bricks:
				i.Collide(p)
			for p in movingblocks:
				i.Collide(p)
			for p in crates:
				i.Collide(p)
		screen.blit(i.img,i.coords)


	if bombsExplode:
		for i in bombs:
			if i.armed:
				if (i.type != 3) or (isNear(center(i), mousepos, 32)) or (isNear(center(i), center(player), 20)):
					i.isExploding = True
					i.img = normalBombImgs[0]
					i.Detonate(player)
					for p in movingblocks:
						if p.type in [0,2]:
							i.Detonate(p)
					i.stuck = True
					i.stuckOn = None
					i.vel = [0, 0]


	if player.floor:
		player.vel[0] = Zero(player.vel[0], friction)

	for s in switchs:
		screen.blit(s.img, s.coords)
	#UI display
	screen.blit(personimg, player.coords)
	screen.blit(DetCurrent.img, (4, 4))
	if DetCurrent.type == 3:
		pygame.draw.circle(screen, RED, mousepos, 32, 1)

	screen.blit(mouseImg, (mousepos[0]-3, mousepos[1]-3))
	pygame.display.update()
	clock.tick(fps)
















































































































