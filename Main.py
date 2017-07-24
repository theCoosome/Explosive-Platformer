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

#SET GET IMAGES HERE
brickImg = getImg("Brick")
personimg = getImg("Human")
movingImg = getImg("BrickMoving")

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
		self.motion = [0.0, 0.0] #attempted motion, xy direction
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
		
player = Person([50, 250], (16, 16))

class movingBlock(object):
	def __init__(self, type, coords, size, img):
		self.type = type
		self.coords = coords
		self.size = size
		self.img = img
		self.floor = False
		self.vel = [0,-15]
class Brick(object):
	def __init__(self,type,coords,size,img):
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
testBomb = bomb(1, [300, 250], (8, 8), getImg("Bomb"))

bombs = [testBomb]

bricks = []

def createFloor(coordx,coordy,rx,ry):
	for i in range(rx,ry):
		bricks.append(Brick("type",[coordx + (16 * i),coordy],(16 * rx,16),brickImg))

def createWall(coordx,coordy,rx,ry,dir):
	for i in range(rx,ry):
		if dir == "down":
			bricks.append(Brick("type", [coordx, coordy - (16 * i)], (16, 16), brickImg))
		if dir == "up":
			bricks.append(Brick("type", [coordx, coordy + (16 * i)], (16, 16), brickImg))

def createMovingBlock(coordx,coordy,rx,ry):
	for i in range(rx,ry):
		movingblocks.append(movingBlock("type", [coordx + (16 * i), coordy], (16 * rx, 16), movingImg))

createFloor(0, 300, 0, 17)
createWall(0,300,0,4,"down")

createFloor(200, 200, 0, 8)
createWall(264,216,0,2,"up")
createMovingBlock(32,200,0,1)
#createFloor(300,332,0,20,)
#createWall(264,332,0,20,"up")

#Current main screen, basic level.
Running = True
bombWaitTime = 0
normalBombWait = 60
while Running:
	if bombWaitTime > 0:
		bombWaitTime -= 1
	bombsExplode = False
	bombType = 1
	screen.fill(WHITE)

		#user input
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			#movement
			if event.key in [K_LEFT, K_a]:
				player.motion[0] -= 2.0
			if event.key in [K_RIGHT, K_d]:
				player.motion[0] += 2.0
			if event.key in [K_DOWN, K_s]:
				player.motion[1] += 0.5
				player.Crouch()
			if event.key == K_r:
				fps = 10
			if event.key == K_f:
				fps = 60
				
			if event.key in [K_UP, K_w] and player.floor:
				player.vel[1] = -10
				player.floor = False
			if event.key == K_g:
				for i in bombs:
					i.floor = toggle(player.floor)
					i.vel[1] = 0
				player.floor = toggle(player.floor)
				player.vel[1] = 0



			if event.key == pygame.K_q:

				Running = False
			if event.key == pygame.K_SPACE:
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
				newBomb = bomb(bombType, [player.coords[0] - 5,player.coords[1]], (8, 8), getImg("Bomb"))
				x, y = pygame.mouse.get_pos()
				xChng = x - player.coords[1]
				yChng = y - player.coords[0]
				sOverall = 14
				tot = xChng + yChng
				if tot != 0:
					newBomb.vel[0] = (xChng/tot)*14
					newBomb.vel[1] = -(yChng/tot)*14
				else:
					newBomb.vel[0] = -14
				bombs.append(newBomb)
				bombWaitTime = normalBombWait



	#Player
	if not player.floor:
		if player.vel[1] < 16: #Gravity
			player.vel[1] += 0.5
	
	if (not player.floor):
		if player.vel[0] < .5 and player.motion[0] > 0:
			player.vel[0] += player.motion[0]/4
		if player.vel[0] > -.5 and player.motion[0] < 0:
			player.vel[0] += player.motion[0]/4
		
	else:
		if player.crouch:
			if player.vel[0] > player.motion[0]/4:
				player.vel[0] -= 0.5
			if player.vel[0] < player.motion[0]/4:
				player.vel[0] += 0.5
		else:
			if player.vel[0] > player.motion[0]:
				player.vel[0] -= 0.5
			if player.vel[0] < player.motion[0]:
				player.vel[0] += 0.5
	
	player.coords[0] += player.vel[0]
	player.coords[1] += player.vel[1]
	if not collide(player.coords, player.size, (0, 0), size):
		player.coords = [50, 250]
	
	player.floor = False
	for i in bricks:
<<<<<<< HEAD

		for f in movingblocks:
			f.floor =False
			if collide(i.coords, i.size, f.coords, f.size):
				if f.vel[1] > 0:
					f.floor = True
					f.coords[1] = i.coords[1] - f.size[1]
				if f.vel[1] < 0:
					f.coords[1] = i.coords[1] + i.size[1]
				f.vel[1] = 0
			screen.blit(f.img, f.coords)

			if collide(i.coords,i.size,player.coords,player.size):

				if player.vel[1] > 0:
					player.floor = True
					player.coords[1] = i.coords[1]-player.size[1]
				if player.vel[1] < 0:
					player.coords[1] = i.coords[1]+i.size[1]
				player.vel[1] = 0
=======
		if collide(i.coords, i.size, player.coords, player.size): #COLLISIONS
			if player.vel[1] < 0: #Up-ing
				player.coords[1] = i.coords[1]+i.size[1]
				player.vel[1] = 0
			if collide(player.coords, player.size, (i.coords[0], i.coords[1]+3), (i.size[0], i.size[1]-3)):
				if player.vel[0] > 0:
					player.coords[0] = i.coords[0] - player.size[0]
				if player.vel[0] < 0:
					player.coords[0] = i.coords[0] + i.size[0]
				player.vel[0] = 0

			if player.vel[1] > 0: #Falling
				player.coords[1] = i.coords[1]-player.size[1]
				player.vel[1] = 0
			
		if collide(player.coords, (16, 17), i.coords, i.size):
			player.floor = True
>>>>>>> origin/master

		screen.blit(i.img,i.coords)
	
	screen.blit(player.images[player.img], player.coords)
	#Bombs
	for i in bombs:
		if not i.floor:
			if i.vel[1] < 16:
				i.vel[1] += 0.5
		i.coords[0] += i.vel[0]
		i.coords[1] += i.vel[1]
		screen.blit(i.img, i.coords)

	if bombsExplode:
		for i in bombs:

			i.img = personimg


	#Moving Blocks
	for i in movingblocks:
		i.floor = False
		if not i.floor:
			if i.vel[1] < 16:  # Gravity
				i.vel[1] += 0.5
		i.coords[0] += i.vel[0]
		i.coords[1] += i.vel[1]
	pygame.display.update()
	clock.tick(fps)