import pygame
from pygame.locals import *
import math
from decimal import *
#from plyer import notification


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
LGRAY = pygame.Color(214, 214, 194)

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


sensorMovingImg = getImg("Bricks/SensorMoving")
sensorMultiImg = getImg("Bricks/SensorMulti")
sensorDestImg = getImg("Bricks/SensorDest")
brickImg = getImg("Bricks/Brick")
grateImg = getImg("Bricks/Grate")
personimg = getImg("Dereks/Derek")
movingImg = getImg("Bricks/BrickMoving")
destructableImg = getImg("Bricks/BrickDestructable")
exitImg = getImg("Bricks/Exit")
entranceImg = getImg("Bricks/Entrance")
multiImg = getImg("Bricks/BrickMulti")
bombImg = getImg("Bomb")
no_thing = getImg("no_thing")
switchImages= [getImg("Switch"),getImg("Switch2")]
switchImg = switchImages[0]

bricks = []
switches = []

#Mouse Images
AimImg = getImg("Mouse/Aim")
BrickPlaceImg = getImg("Mouse/Brick")
GratePlaceImg = getImg("Mouse/Grate")
DPlaceImg = getImg("Mouse/Destructable")
MovablePlaceImg = getImg("Mouse/Movable")
MultiPlaceImg = getImg("Mouse/Multi")
ExitPlaceImg = getImg("Mouse/Exit")
EntrancePlaceImg = getImg("Mouse/Entrance")
RemoveImg = getImg("Mouse/Remove")
mouseImgs = [AimImg, BrickPlaceImg, GratePlaceImg, DPlaceImg, MovablePlaceImg, MultiPlaceImg, ExitPlaceImg, EntrancePlaceImg, RemoveImg, switchImg, sensorMovingImg, sensorDestImg, sensorMultiImg]
mouseImg = mouseImgs[0]


def center(obj):  # finds center of object sent to function
	return (obj.coords[0] + (obj.size[0] / 2), obj.coords[1] + (obj.size[1] / 2))

def pointCollide(p1, p2, p3):
	if p1[0] + p2[0] > p3[0] and p1[0] < p3[0] and p1[1] + p2[1] > p3[1] and p1[1] < p3[1]:
		return True

def collide(p1, p2, p3, p4):
	# if right side is right of left side, and left side left of right side
	if p1[1] + p2[1] > p3[1] and p1[1] < p3[1] + p4[1]:
		# if bottom is below top and top is above bottom
		if p1[0] + p2[0] > p3[0] and p1[0] < p3[0] + p4[0]:
			return True

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

CBRICK = -1
CMOVABLE = 0
CDESTRUCTABLE = 1
CMULTI = 2
CGRATE = 3
CENTRANCE = 4
CEXIT = 5
CSWITCH = 6
CSENSORMOVING = 7
CSENSORDEST = 8
CSENSORMULTI = 9


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

class DispObj(object):
	def refresh(self):
		if not self.simple:
			final = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()
			for i in self.all:
				final.blit(i.img, i.coords)
			self.img = final
		else:
			self.img = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()
			self.img.blit(self.all, (0, 0))
	#coords, img is blitable object or list of DispObj. simple is wether or not is list. size is needed if not simple.
	def __init__(self, img, coords = (0, 0), simple = True, size = (0, 0)):
		self.coords = coords
		self.img = img #Final image, use this to blit to screen
		self.all = img #List of display objects, used if not simple
		self.simple = simple
		self.size = size
		self.refresh()

drawOverlay = pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()

class Brick(object):
	def __init__(self, type, coords, size, img):
		self.type = type
		self.coords = coords
		self.size = size
		self.img = pygame.transform.scale(img, size)

class Switch(object):
	def __init__(self,type,coords,size,img,on):
		self.type = type
		self.coords = coords
		self.size = size
		self.img = img
		self.on = on
		self.trigger = None
		self.time = 500
		self.blockamount = 10

class Exit():
	def __init__(self, type, coords, size, img):
		self.type = type
		self.coords = coords
		self.size = size
		self.img = pygame.transform.scale(img, size)

class Entrance():
	def __init__(self, type, coords, size, img):
		self.type = type
		self.coords = coords
		self.size = size
		self.img = pygame.transform.scale(img, size)

class Grate(object):
	def __init__(self, type, coords, size, img):
		self.type = type
		self.coords = coords
		self.size = size
		self.img = pygame.transform.scale(img, size)

def drawMeasurement(rect, axis):
	#If our axis is horizontal
	cenx, ceny = rect.center
	w2 = (math.fabs(rect.width / 2))
	h2 = (math.fabs(rect.height / 2))
	if axis == 0:

		startx, starty = cenx - w2, ceny - h2
		endx, endy = cenx + w2, ceny - h2
		if starty - 8 > 0:
			starty -= 8
			endy -= 8
		else:
			startx, starty = cenx - w2, ceny + h2
			endx, endy = cenx + w2, ceny + h2
			starty += 8
			endy += 8
		start = startx, starty
		end = endx, endy

		pygame.draw.line(drawOverlay, RED, start, ((startx + (endx - startx) / 2) - 8, starty))
		pygame.draw.line(drawOverlay, RED, ((startx + (endx - startx) / 2) + 8, starty), end)

		hText = smallfont.render(str(int(math.fabs(rect.width/16))), False, BLACK)
		drawOverlay.blit(hText, (startx + ((endx - startx) / 2) - 8, starty - 8))

		pygame.draw.line(drawOverlay, RED, (startx, starty - 4), (startx, starty + 4))
		pygame.draw.line(drawOverlay, RED, (endx, endy - 4), (endx, endy + 4))
	if axis == 1:
		startx, starty = cenx - w2, ceny - h2
		endx, endy = cenx - w2, ceny + h2
		if startx -8 > 0:
			startx -= 8
			endx -= 8
		else:
			startx, starty = cenx + w2, ceny - h2
			endx, endy = cenx + w2, ceny + h2
			startx += 8
			endx += 8
		start = startx, starty
		end = endx, endy

		pygame.draw.line(drawOverlay, RED, start, (startx,  (starty + (endy - starty) / 2) - 8))
		pygame.draw.line(drawOverlay, RED, (startx, (starty + (endy - starty) / 2) + 8), end)

		wText = smallfont.render(str(int(math.fabs(rect.height/16))), False, BLACK)

		drawOverlay.blit(wText, (startx - 8, starty + ((endy-starty)/2) - 8))

		pygame.draw.line(drawOverlay, RED, (startx - 4, starty), (startx + 4, starty))
		pygame.draw.line(drawOverlay, RED, (endx - 4, endy), (endx + 4, endy))

def drawBricks():
	for i in bricks:
		screen.blit(i.img, i.coords)

def drawAll():
	drawBricks()
	for i in switches:
		screen.blit(i.img, i.coords)
	for i in sensors:
		screen.blit(i.img, i.coords)

def deleteAll():
	delList = []
	for i in range(len(bricks)):
		coords = (min(rectX, brx), min(rectY, bry))
		pSize = (int(math.fabs(brx - rectX)), int(math.fabs(bry - rectY)))
		if collide(coords, pSize, bricks[i].coords, bricks[i].size):
			print "Touching"
			delList.append(bricks[i])
	for i in delList:
		del bricks[bricks.index(i)]
	delList = []
	for i in range(len(switches)):
		coords = (min(rectX, brx), min(rectY, bry))
		pSize = (int(math.fabs(brx - rectX)), int(math.fabs(bry - rectY)))
		if collide(coords, pSize, switches[i].coords, switches[i].size):
			print "Touching"
			delList.append(switches[i])
	for i in delList:
		del switches[switches.index(i)]
	delList = []
	for i in range(len(sensors)):
		coords = (min(rectX, brx), min(rectY, bry))
		pSize = (int(math.fabs(brx - rectX)), int(math.fabs(bry - rectY)))
		if collide(coords, pSize, sensors[i].coords, sensors[i].size):
			print "Touching"
			delList.append(sensors[i])
	for i in delList:
		del sensors[sensors.index(i)]


def createFloor(coordx, coordy, ry, rx, type):
	if type == -1:
		bricks.append(Brick(type, [coordx, coordy], (rx * 16, ry * 16), brickImg))
	elif type == 3:
		bricks.append(Grate(type, [coordx, coordy], (rx*16, ry*16), grateImg))
	elif type == 4:
		remList = []
		for i in bricks:
			if i.type == 4:
				remList.append(i)
		for i in remList:
			del bricks[bricks.index(i)]

		bricks.append(Entrance(type, [coordx, coordy], (rx*16, ry*16), entranceImg))
	elif type == 5:
		remList = []
		for i in bricks:
			if i.type == 5:
				remList.append(i)
		for i in remList:
			del bricks[bricks.index(i)]

		bricks.append(Exit(type, [coordx, coordy], (rx * 16, ry * 16), exitImg))
	elif type == 6:
		switches.append(Switch(0, [coordx, coordy], (16,16), switchImg, True))
	elif type == 7:
		sensors.append(Sensor(0, [coordx, coordy], (rx * 16, ry * 16)))
	elif type == 8:
		sensors.append(Sensor(1, [coordx, coordy], (rx * 16, ry * 16)))
	elif type == 9:
		sensors.append(Sensor(2, [coordx, coordy], (rx * 16, ry * 16)))
	else:
		bricks.append(movingBlock(type, [coordx, coordy], (rx * 16, ry * 16)))


placeMode = "brick"

movingblocks = []
sensors = []

class Sensor(object):
	def __init__(self, type, coords, size):
		self.type = type
		self.coords = coords
		self.size = size
		self.trigger = None
		self.On = False
		self.actions = []

		if self.type == 0:
			self.img = pygame.transform.scale(sensorMovingImg, size)
		if self.type == 1:
			self.img = pygame.transform.scale(sensorDestImg, size)
		if self.type == 2:
			self.img = pygame.transform.scale(sensorMultiImg, size)

	def collide(self, i):
		if i.type == self.type:
			if hit(i.coords, i.size, self.coords, self.size):
				self.On = True
				self.trigger.Trigger(self.actions)

class bomb(object):
	def __init__(self, coords, size, type, img):
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

def round_int_down(x):
    return x - (x%16)
def round_int_up(x):
    return x - (x%16) +16

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
pressedLMB = False

all = []

def saveFile():

	file = open("saves/Level Editor Save.txt", "w")
	file.truncate
	writeList = []
	for i in bricks:
		x,y = i.coords
		xs, ys = i.size
		out = ""
		if i.type == -1:
			out = "createFloor("+str(x)+", "+str(y)+", "+str(int(ys / 16))+", "+str(int(xs / 16))+")"
		
		elif i.type in [0, 1, 2]:
			out = "createMovingBlock("+str(x)+", "+str(y)+", "+str(int(xs / 16))+", "+str(int(ys / 16))+", "+str(i.type)+")"
		
		elif i.type == 3:
			out = "grates.append(Grate([int("+str(x)+"), int("+str(y)+")], [int("+str(xs)+"), int("+str(ys)+")], []))"
		
		elif i.type == 4:
			print "Enterances"
			out = "entrances = [Entrance(4, [int("+str(x)+"), int("+str(y)+")], [int("+str(xs)+"), int("+str(ys)+")], entranceImg)]"
		
		elif i.type == 5:
			print "Exits"
			out = "createExit(4, [int("+str(x)+"), int("+str(y)+")], [int("+str(xs)+"), int("+str(ys)+")], exitImg)"
		else:
			print "invalid type:", i.type
			out = "#something odd"


		out += "\n"
		writeList.append(out)
	for i in sensors:
		x, y = i.coords
		xs, ys = i.size
		out = ""
		print "Sensors"
		out = "createSensor(" + str(x) + ", " + str(y) + ", " + str(int(xs / 16)) + ", " + str(
			int(ys / 16)) + ", " + str(i.type) + ", [])"
		out += "\n"
		writeList.append(out)
	for i in switches:
		x, y = i.coords
		xs, ys = i.size
		out = ""
		print "Switches"
		out = "switches.append(Switch('Switch', [int(" + str(x) + "), int(" + str(y) + ")], [int(" + str(
			xs) + "), int(" + str(ys) + ")], switchImg, False))"
		out += "\n"
		writeList.append(out)
			
	print writeList
	file.writelines(writeList)
	file.close()

oldImg = mouseImgs[0]

while Running:
	drawOverlay = pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()
	delList = []
	for i in bricks:
		if i.size[0] == 0 or i.size[1] == 0:
			delList.append(i)
	for i in delList:
		del bricks[bricks.index(i)]
	delList = []

	mousepos = pygame.mouse.get_pos()
	screen.fill(WHITE)
	currImgNum = mouseImgs.index(mouseImg)

	placeRect = Rect(0,0,0,0)

	w, h = size

	for i in range(0, (w/16)):
		startPos = (i*16, 0)
		endPos = (i*16, h)
		pygame.draw.line(screen, LGRAY, startPos, endPos)
	for i in range(0, (h/16)):
		startPos = (0, i*16)
		endPos = (w, i*16)
		pygame.draw.line(screen, LGRAY, startPos, endPos)
	if pressedLMB:
		mouseX, mouseY = mousepos
		startX, startY = startLoc
		if mouseX >= startX:
			mouseX = round_int_up(mouseX)
		else:
			startX += 16
			mouseX = round_int_up(mouseX-16)
		if mouseY >= startY:
			mouseY = round_int_up(mouseY)
		else:
			startY += 16
			mouseY = round_int_up(mouseY - 16)

		startX = round_int_down(startX)
		startY = round_int_down(startY)
		placeRect = Rect(startX, startY, mouseX - startX, mouseY - startY)
		pygame.draw.rect(drawOverlay, BLUE, placeRect, 2)
		drawMeasurement(placeRect, 0)
		drawMeasurement(placeRect, 1)

	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q:  # quiting
				Running = False
			if event.key == pygame.K_s:
				# notification.notify(
				# 	title='Saved',
				# 	message='Your level has been saved',
				# 	app_name='Here is the application name',
				# 	app_icon='path/to/the/icon.png'
				# )

				print "SAVED!"
				saveFile()
			if event.key == pygame.K_1:
				mouseImg = mouseImgs[0]
			if event.key == pygame.K_2:
				mouseImg = mouseImgs[1]
			if event.key == pygame.K_3:
				mouseImg = mouseImgs[2]
			if event.key == pygame.K_4:
				mouseImg = mouseImgs[3]
			if event.key == pygame.K_5:
				mouseImg = mouseImgs[4]
			if event.key == pygame.K_6:
				mouseImg = mouseImgs[5]
			if event.key == pygame.K_7:
				mouseImg = mouseImgs[6]
			if event.key == pygame.K_8:
				mouseImg = mouseImgs[7]
			if event.key == pygame.K_9:
				mouseImg = mouseImgs[8]
			if event.key == pygame.K_0:
				mouseImg = mouseImgs[9]

		if event.type == pygame.MOUSEBUTTONDOWN:
			print event.button
			if event.button == 1:
				pressedLMB = True
				startLoc = mousepos
			if event.button == 3:
				pressedLMB = True
				startLoc = mousepos
			if event.button == 4:
				newImgNum = mouseImgs.index(mouseImg) + 1
				print "up 1 ", newImgNum
				if newImgNum >= len(mouseImgs):
					newImgNum = 0
				mouseImg = mouseImgs[newImgNum]
			if event.button == 5:
				newImgNum = mouseImgs.index(mouseImg) - 1
				print "down 1 ", newImgNum
				if newImgNum < 0:
					newImgNum = len(mouseImgs)-1
				mouseImg = mouseImgs[newImgNum]
		#Associations: [AimImg, BrickPlaceImg, DPlaceImg, MovablePlaceImg, MultiPlaceImg, ExitPlaceImg, RemoveImg]
		if event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1:
				pressedLMB = False
				rectX, rectY = placeRect.topleft
				brx, bry = placeRect.bottomright
				if(currImgNum == 1):
					createFloor(min(rectX, brx), min(rectY, bry), int(math.fabs((bry-rectY)/16)), int(math.fabs((brx-rectX)/16)), CBRICK)
				elif (currImgNum == 2):
					createFloor(min(rectX, brx), min(rectY, bry), int(math.fabs((bry - rectY) / 16)),
								int(math.fabs((brx - rectX) / 16)), CGRATE)
				elif (currImgNum == 3):
					createFloor(min(rectX, brx), min(rectY, bry), int(math.fabs((bry - rectY) / 16)),
								int(math.fabs((brx - rectX) / 16)), CDESTRUCTABLE)
				elif(currImgNum == 4):
					createFloor(min(rectX, brx), min(rectY, bry), int(math.fabs((bry - rectY) / 16)),
								int(math.fabs((brx - rectX) / 16)), CMOVABLE)
				elif (currImgNum == 5):
					createFloor(min(rectX, brx), min(rectY, bry), int(math.fabs((bry - rectY) / 16)),
							int(math.fabs((brx - rectX) / 16)), CMULTI)
				elif (currImgNum == 6):
					createFloor(min(rectX, brx), min(rectY, bry), 1, 1, CEXIT)
				elif (currImgNum == 7):
					createFloor(min(rectX, brx), min(rectY, bry), 1, 1, CENTRANCE)
				elif(currImgNum == 8):
					delList = []
					deleteAll()
				elif(currImgNum == 9):
					createFloor(min(rectX, brx), min(rectY, bry), 1, 1, CSWITCH)
				elif(currImgNum == 10):
					createFloor(min(rectX, brx), min(rectY, bry), int(math.fabs((bry - rectY) / 16)),
								int(math.fabs((brx - rectX) / 16)), CSENSORMOVING)
				elif (currImgNum == 11):
					createFloor(min(rectX, brx), min(rectY, bry), int(math.fabs((bry - rectY) / 16)),
								int(math.fabs((brx - rectX) / 16)), CSENSORDEST)
				elif (currImgNum == 12):
					createFloor(min(rectX, brx), min(rectY, bry), int(math.fabs((bry - rectY) / 16)),
								int(math.fabs((brx - rectX) / 16)), CSENSORMULTI)
			if event.button == 3:
				pressedLMB = False
				rectX, rectY = placeRect.topleft
				brx, bry = placeRect.bottomright
				delList = []
				deleteAll()


	drawAll()
	screen.blit(drawOverlay, (0,0))
	screen.blit(mouseImg, (mousepos[0] - 3, mousepos[1] - 3))
	pygame.display.update()
	clock.tick(60)
