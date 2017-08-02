import pygame
from pygame.locals import *
import math
from decimal import *
import time

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
fps = 60
debugon = True
sfxkey=0
muteon=True

WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)
RED = pygame.Color(255, 0, 0)
YELLOW = pygame.Color(255, 255, 0)
GREEN = pygame.Color(0, 255, 0)
BLUE = pygame.Color(0, 0, 255)
PURPLE = pygame.Color(255, 0, 255)

pygame.mouse.set_visible(False)
font = pygame.font.SysFont('couriernew', 13)
fontComp = pygame.font.SysFont('couriernew', 26, True)
smallfont = pygame.font.SysFont('couriernew', 12)
massive = pygame.font.SysFont('couriernew', 200, True)

# sizes so nothing is hardcoded
size = (1024, 720)
standardSize = (16, 16)
bombSize = ((standardSize[0] / 2), (standardSize[1] / 2))

screen = pygame.display.set_mode(size)


clock = pygame.time.Clock()
pygame.display.set_caption("Explosive Platformer")

debugOverlay = pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()

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
sens1Img = getImg("Bricks/SensorMoving")
sens2Img = getImg("Bricks/SensorDest")
sens3Img = getImg("Bricks/SensorMulti")
exitImg = getImg("Bricks/Exit")
entranceImg = getImg("Bricks/Exit2")

switchImages= [getImg("Switch"),getImg("Switch2")]
switchImg = switchImages[0]
lockImg = getImg("bars")
keyImg = getImg("key")
crateImg = getImg("crate")
no_thing = getImg("no_thing")


#Anim
derek = getImg("Dereks/Derek")
left = [getImg("Dereks/anim1l"),getImg("Dereks/anim3l")]
right = [getImg("Dereks/anim1r"),getImg("Dereks/anim2r")]
'''left = [getImg("Dereks/anim1l"),getImg("Dereks/anim2l"),getImg("Dereks/anim3l")]
right = [getImg("Dereks/anim1r"),getImg("Dereks/Derek"),getImg("Dereks/anim2r")]'''

crouchImg = [getImg("Dereks/DerekCrouch"),getImg("Dereks/derekcrouchl")]

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
	
#takes single string, max width, font used, and color of text. returns list of dispObj
def wraptext(text, fullline, Font, render = False, color = (0,0,0)):  #need way to force indent in string
	Denting = True
	max = fullline
	size = Font.size(text)
	outtext = []
	while Denting:
		if Font.size(text)[0] > max:
			#Search for ammount of charachters that can fit in set fullline size
			thistext = ""
			for i in range(len(text)):
				if Font.size(thistext + text[i])[0] > max:
					count = len(thistext)
					break
				else:
					thistext += text[i]
			thistext = text[:count]
			#is it indentable
			if " " in thistext:
				for i in range(len(thistext)):
					#find first space from end
					if thistext[len(thistext)-(i+1)] == " ":
						#split text, add indent, update count
						outtext.append(thistext[:len(thistext)-(i+1)])
						text = text[len(thistext)-(i):]
						max = fullline
						break
			#unindentable, skip to next
			else:
				max += fullline
		else:
			#exit denting, add remaining to outtext, return
			Denting = False
			outtext.append(text)
			
	if render:
		text = []
		for i in range(len(outtext)):
			x = outtext[i]
			text.append(DispObj(Font.render(x, True, color),  (0, (i*size[1]))))
		outtext = text
	return outtext
	
TM1 = DispObj(wraptext("", 900, font, True), (10, 10), False, (900, 120)) #main room desc
TM2 = DispObj(wraptext("", 900, font, True), (10, 130), False, (900, 119)) #room responses


DB = DispObj(no_thing, (0, 0), True, size)

grateImg = getImg("Bricks/Grate")
Gplayer = getImg("Bricks/Gplayer")
Gbomb = getImg("Bricks/Gbomb")
Gmoving = getImg("Bricks/Gmoving")

#Bombs
bombImg = getImg("Bombs/Bomb")
platformImg = getImg("platform")



normalBombImgs = []
squareExplodeImgs = []
i = 0
while i < 6:
	squareExplodeImgs.append(getImg("Square Explosion/square_explosion_" + str(i)))
	i += 1
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


def toggle(bool):  # is used to make bomb and players stop when in contact with floor
	if bool:
		return False
	else:
		return True


def center(obj):  # finds center of object sent to function
	return (obj.coords[0] + (obj.size[0] / 2), obj.coords[1] + (obj.size[1] / 2))

def collide(p1, p2, p3, p4):
	# if right side is right of left side, and left side left of right side
	if p1[1] + p2[1] > p3[1] and p1[1] < p3[1] + p4[1]:
		# if bottom is below top and top is above bottom
		if p1[0] + p2[0] > p3[0] and p1[0] < p3[0] + p4[0]:
			return True


# object one coord par, size, object two coord pair and size
def hit(p1, p2, p3, p4):
	# if bottom is below top and top is above bottom
	# if right side is right of left side, and left side left of right side
	if p1[0] + p2[0] > p3[0] and p1[0] < p3[0] + p4[0]:
		if p1[1] + p2[1] > p3[1] and p1[1] < p3[1] + p4[1]:
			return True


# if point p3 is in p1 with size p2
def pointCollide(p1, p2, p3):
	if p1[0] + p2[0] > p3[0] and p1[0] < p3[0] and p1[1] + p2[1] > p3[1] and p1[1] < p3[1]:
		return True
		
def within(p1, p2, p3): #if value 1 is within p2 and p3
	if p2 > p3:
		if p1 < p2 and p1 > p3:
			return True
	else:
		if p1 > p2 and p1 < p3:
			return True
		
def DualLine(p1, p2, box):
	if p2[0]-p1[0] == 0: #Straight up line
		m = 2000
	else:
		m = (p2[1]-p1[1])/(p2[0]-p1[0])
	b = p1[1]-(m*p1[0])
	#having m and b:
	def f(x):
		return m*x+b
	if (box.coords[1] > f(box.coords[0]) and box.coords[1] > f(box.coords[0]+box.size[0])) or (box.coords[1]+box.size[1] < f(box.coords[0]) and box.coords[1]+box.size[1] < f(box.coords[0]+box.size[0])):
		return False
	else:
		return True
		
def getLower(p1, p2):
	if p1 > p2:
		return p2
	else:
		return p1

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
		self.collided = [0, 0] #x, y pushed

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
		if hit(i.coords, i.size, self.coords, self.size):  # UP

			p1 = center(self)
			if self.vel[1] > 0 and self.coords[1] <= i.coords[1]: #FLOOR
				self.coords[1] = i.coords[1] - self.size[1]
				if self.vel[1] > 0:
					self.vel[1] = 0
				self.floor = True
				pygame.draw.line(debugOverlay, BLUE, p1, center(self))
				if self.dualColliding and self.collided[1] == 1:
					print "Floor crush"
					self.Kill()
				else:
					self.collided[1] = -1
			if hit(self.coords, self.size, (i.coords[0], i.coords[1] + 3), (i.size[0], i.size[1] - 3)):  # LEFT / RIGHT
				p1 = center(self)
				if self.vel[0] > 0 and self.coords[0] <= i.coords[0]:
					self.coords[0] = i.coords[0] - self.size[0]
					self.vel[0] = 0
					pygame.draw.line(debugOverlay, YELLOW, p1, center(self))
					if self.dualColliding and self.collided[0] == 1:
						print "Left shark"
						self.Kill()
					else:
						self.collided[0] = -1
				if self.vel[0] < 0 and self.coords[0] + self.size[0] >= i.coords[0] + i.size[0]:
					self.coords[0] = i.coords[0] + i.size[0]
					self.vel[0] = 0
					pygame.draw.line(debugOverlay, RED, p1, center(self))
					if self.dualColliding and self.collided[0] == -1:
						print "Right wall"
						self.Kill()
					else:
						self.collided[0] = 1
			p1 = center(self)
			if self.vel[1] < 0 and self.coords[1] + self.size[1] >= i.coords[1] + i.size[1]: #CEILING
				self.coords[1] = i.coords[1] + i.size[1]
				self.vel[1] = 0
				pygame.draw.line(debugOverlay, GREEN, p1, center(self))
				if self.dualColliding and self.collided[1] == -1:
					print "Cieling crush"
					self.Kill()
				else:
					self.collided[1] = 1
			if type(i) == movingBlock:
				if i.vel[1] > 5 and center(player)[1] > center(i)[1]:
					self.Kill()
				self.dualColliding = True
		if hit(self.coords, (self.size[0], self.size[1] + 1), i.coords, i.size):
			self.floor = True

player = Person([50, 250], (standardSize),False)

#input object, output list of tuples: [top left, top right, bottom left, bottom right]
def getCorners(it):
	return [it.coords, (it.coords[0]+it.size[0], it.coords[1]), (it.coords[0], it.coords[1]+it.size[1]), (it.coords[0]+it.size[0], it.coords[1]+it.size[1])]

class movingBlock(object):
	def __init__(self, type, coords, size):
		self.hp = 1
		self.type = type
		self.coords = coords
		self.size = size
		self.floor = True
		self.vel = [0, 0]
		self.isExploding = False
		self.imgNum = 0
		
		self.mass = (size[0]*size[1])/256
		self.sixteens = (size[0]/16, size[1]/16)
		
		if self.sixteens != (0, 0):
			self.big = True
		else:
			self.big = False
		
		if type == 0: #Movable
			self.img = pygame.transform.scale(movingImg, size)

		if type == 1: #Destructable
			self.img = pygame.transform.scale(destructableImg, size)

		if type == 2: #Movable and Destructable
			self.img = pygame.transform.scale(multiImg, size)

	def incrementSprite(self, amount):
		newNum = self.imgNum+amount
		if newNum < 5:
			newImg = squareExplodeImgs[newNum]
			self.imgNum = newNum
			self.img = pygame.transform.scale(newImg, self.size)
		else:
			self.isExploding = False
			movingblocks.remove(self)


			
	def Collide(self, i):
		if hit(i.coords, i.size, self.coords, self.size):  # UP
			if self.big:
				p1 = center(self)
				p2 = center(i)
				if p1[0] > p2[0]: #To the right of center
					xdiff = (i.coords[0]+i.size[0])-self.coords[0]
					if p1[1] > p2[1]: #Below
						ydiff = (i.coords[1]+i.size[1])-self.coords[1]
						p1 = center(self) 
						if ydiff < xdiff:
							self.coords[1] = i.coords[1] + i.size[1] #CIELING
							self.vel[1] = 0
							p2 = center(self)
							pygame.draw.line(debugOverlay, GREEN, (p1[0]-1, p1[1]), (p2[0]-1, p2[1]))
						
						else:
							self.coords[0] = i.coords[0] + i.size[0] #RIGHT WALL
							self.vel[0] = 0
							p2 = center(self)
							pygame.draw.line(debugOverlay, RED, (p1[0], p1[1]-1), (p2[0], p2[1]-1))
							
						
					else: #Above
						ydiff = (self.coords[1]+self.size[1])-i.coords[1]
						p1 = center(self) 
						if ydiff < xdiff:
							self.coords[1] = i.coords[1] - self.size[1] #FLOOR
							if self.vel[1] > 0:
								self.vel[1] = 0
							self.floor = True
							pygame.draw.line(debugOverlay, BLUE, p1, center(self))
						
						else:
							self.coords[0] = i.coords[0] + i.size[0] #RIGHT WALL
							self.vel[0] = 0
							p2 = center(self)
							pygame.draw.line(debugOverlay, RED, (p1[0], p1[1]-1), (p2[0], p2[1]-1))
				
				else: #To the left of center
					xdiff = (self.coords[0]+self.size[0])-i.coords[0]
					if p1[1] > p2[1]: #Below
						ydiff = (i.coords[1]+i.size[1])-self.coords[1]
						p1 = center(self) 
						if ydiff < xdiff:
							self.coords[1] = i.coords[1] + i.size[1] #CIELING
							self.vel[1] = 0
							p2 = center(self)
							pygame.draw.line(debugOverlay, GREEN, (p1[0]-1, p1[1]), (p2[0]-1, p2[1]))
						
						else:
							self.coords[0] = i.coords[0] - self.size[0] #LEFT WALL
							self.vel[0] = 0
							pygame.draw.line(debugOverlay, YELLOW, p1, center(self))
						
					else: #Above
						ydiff = (self.coords[1]+self.size[1])-i.coords[1]
						p1 = center(self) 
						if ydiff < xdiff:
							self.coords[1] = i.coords[1] - self.size[1] #FLOOR
							if self.vel[1] > 0:
								self.vel[1] = 0
							self.floor = True
							pygame.draw.line(debugOverlay, BLUE, p1, center(self))
						
						else:
							self.coords[0] = i.coords[0] - self.size[0] #LEFT WALL
							self.vel[0] = 0
							pygame.draw.line(debugOverlay, YELLOW, p1, center(self))
					
			print xdiff, ydiff
			
			if not self.big:
				p1 = center(self)
				if self.vel[1] > 0 and self.coords[1] <= i.coords[1]: #FLOOR   and not self.floor
					self.coords[1] = i.coords[1] - self.size[1]
					if self.vel[1] > 0:
						self.vel[1] = 0
					self.floor = True
					pygame.draw.line(debugOverlay, BLUE, p1, center(self))
					
				if hit(self.coords, self.size, i.coords, i.size):  # LEFT / RIGHT
					p1 = center(self)
					if self.coords[0] <= i.coords[0]:
						self.coords[0] = i.coords[0] - self.size[0]
						self.vel[0] = 0
						pygame.draw.line(debugOverlay, YELLOW, p1, center(self))
						
					if self.coords[0] + self.size[0] >= i.coords[0] + i.size[0]:
						self.coords[0] = i.coords[0] + i.size[0]
						self.vel[0] = 0
						p2 = center(self)
						pygame.draw.line(debugOverlay, RED, (p1[0], p1[1]-1), (p2[0], p2[1]-1))
						
				#if hit(i.coords, i.size, self.coords, self.size):  # UP
					if self.vel[1] < 0 and self.coords[1] + 16 >= i.coords[1] + i.size[1]: #CEILING
						p1 = center(self)
						self.coords[1] = i.coords[1] + i.size[1]
						self.vel[1] = 0
						p2 = center(self)
						pygame.draw.line(debugOverlay, GREEN, (p1[0]-1, p1[1]), (p2[0]-1, p2[1]))

		if hit(self.coords, (self.size[0], self.size[1] + 1), i.coords, i.size):
			self.floor = True


class Brick(object):
	def __init__(self, type, coords, size, img):
		self.type = type
		self.coords = coords
		self.size = size
		rand = pygame.transform.scale(brickImg, size)
		self.img = rand

class Sensor(object):
	def __init__(self, type, coords, size):
		self.type = type
		self.coords = coords
		self.size = size
		self.trigger = None
		self.On = False
		self.actions = []
		
		if self.type == 0:
			self.img = pygame.transform.scale(sens1Img, size)
		if self.type == 2:
			self.img = pygame.transform.scale(sens3Img, size)
	
	def collide(self, i):
		if i.type == self.type and not self.On:
			if hit(i.coords, i.size, self.coords, self.size):
				self.On = True
				self.trigger.Trigger(self.actions)

sensors = []

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
		
	def Trigger(self, actions):
		self.open = actions
		
class Grate(object):
	def refresh(self):
		self.img.all = []
		if "guy" in self.blocked:
			self.img.all.append(self.overlays[0])
		if "bomb" in self.blocked:
			self.img.all.append(self.overlays[1])
		if "moving" in self.blocked:
			self.img.all.append(self.overlays[2])
		if "dest" in self.blocked:
			self.img.all.append(self.overlays[3])
		self.img.all.append(self.base)
		self.img.refresh()
			
	
	def __init__(self,coords,size, blocked):
		self.coords = coords
		self.size = size
		self.base = DispObj(pygame.transform.scale(grateImg, size), (0, 0), True, size)
		self.blocked = blocked #blocked is list of strings: ["guy", "bomb", "moving", "dest"]
		self.img = DispObj([self.base], self.coords, False, self.size)
		
		self.sixteens = (size[0]/16, size[1]/16)
		
		self.overlays = [DispObj(no_thing, (0, 0), True, size), DispObj(no_thing, (0, 0), True, size), DispObj(no_thing, (0, 0), True, size), DispObj(no_thing, (0, 0), True, size)]
		
		for x in range(self.sixteens[0]):
			for y in range(self.sixteens[1]):
				self.overlays[0].img.blit(Gplayer, (x*16, y*16))
				self.overlays[1].img.blit(Gbomb, (x*16, y*16))
				self.overlays[2].img.blit(Gmoving, (x*16, y*16))
				self.overlays[3].img.blit(Gmoving, (x*16, y*16))
		
		self.refresh()
		
	def Trigger(self, actions):
		for x in actions:
			if x in self.blocked:
				self.blocked.remove(x)
			else:
				self.blocked.append(x)
		self.refresh()
		
				
grates = []

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

exits = []



		
class Crate(object):
	def __init__(self,coords,size,img):
		self.coords = coords
		self.size = size
		self.img = img

class bomb(object):
	def __init__(self, type, coords, vel, size, pow, pow2, dmg, arm, img):
		self.type = type
		self.coords = coords
		self.size = size
		self.img = img
		self.pow = pow
		self.pow2 = pow2
		self.dmg = dmg
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
		if hit(i.coords, i.size, self.coords, self.size):
			p1 = center(self)
			if self.vel[0] > 0 and self.coords[0] <= i.coords[0]:
				self.coords[0] = i.coords[0] - self.size[0]
				self.vel[0] = 0
				self.stuck = True
				pygame.draw.line(debugOverlay, YELLOW, p1, center(self))
				if type(i) == movingBlock:
					self.stuckOn = i
					self.relative = (self.coords[0]-i.coords[0], self.coords[1]-i.coords[1])
			elif self.vel[0] < 0 and self.coords[0] + self.size[0] >= i.coords[0] + i.size[0]:
				self.coords[0] = i.coords[0] + i.size[0]
				self.vel[0] = 0
				self.stuck = True
				pygame.draw.line(debugOverlay, RED, p1, center(self))
				if type(i) == movingBlock:
					self.stuckOn = i
					self.relative = (self.coords[0]-i.coords[0], self.coords[1]-i.coords[1])
			elif self.vel[1] > 0 and self.coords[1] <= i.coords[1]: #FLOOR
				p1 = center(self)
				self.coords[1] = i.coords[1] - self.size[1]
				self.vel[1] = 0
				self.floor = True
				self.stuck = True
				pygame.draw.line(debugOverlay, BLUE, p1, center(self))
				if type(i) == movingBlock:
					self.stuckOn = i
					self.relative = (self.coords[0]-i.coords[0], self.coords[1]-i.coords[1])
			elif self.vel[1] < 0 and self.coords[1] + self.size[1] >= i.coords[1] + i.size[1]: #CEILING
				p1 = center(self)
				self.coords[1] = i.coords[1] + i.size[1]
				self.vel[1] = 0
				self.stuck = True
				pygame.draw.line(debugOverlay, GREEN, p1, center(self))
				if type(i) == movingBlock:
					self.stuckOn = i
					self.relative = (self.coords[0]-i.coords[0], self.coords[1]-i.coords[1])
				
				
		if hit(self.coords, (self.size[0], self.size[1] + 1), i.coords, i.size):
			self.floor = True

	def Detonate(self, mob):

		if type(mob) == Person:
			cm = center(mob)
			cs = center(self)

			xd = cm[0]-cs[0]
			yd = cm[1]-cs[1]

			td = math.hypot(xd, yd)

			pow = self.pow * ((self.detRange - td) / self.detRange)
			
			if pow > 0:
				if (td != 0):
					pygame.draw.line(debugOverlay, RED, cm, cs)
					sight = True
					square = (getLower(cm[0], cs[0]), getLower(cm[1], cs[1]), abs(xd), abs(yd))
					for x in bricks:
						if hit(x.coords, x.size, square[0:2], square[2:4]):
							if DualLine(cm, cs, x):
								sight = False
								pygame.draw.line(debugOverlay, PURPLE, cm, cs)
					if sight:
						mob.vel[0] += (xd / td) * pow
						mob.vel[1] += (yd / td) * pow
		
		elif type(mob) == movingBlock:
			cm = center(mob)
			cs = center(self)

			xd = cm[0]-cs[0]
			yd = cm[1]-cs[1]

			td = math.hypot(xd, yd)
			netforce = [0, 0]
			vel = ((xd / td), (yd / td))
			
			if hit(mob.coords, mob.size, (cs[0]-self.detRange, cs[1]-self.detRange), (2*self.detRange, 2*self.detRange)):
				pow = 0
				for x in xrange(mob.sixteens[0]):
					for y in xrange(mob.sixteens[1]):
						cm = (mob.coords[0]+(16*x)+8, mob.coords[1]+(16*y)+8)
						xd = cm[0]-cs[0]
						yd = cm[1]-cs[1]

						td = math.hypot(xd, yd)
						if td < self.detRange:
							pygame.draw.line(debugOverlay, RED, cm, cs)
							sight = True
							square = (getLower(cm[0], cs[0]), getLower(cm[1], cs[1]), abs(xd), abs(yd))
							for c in bricks:
								if hit(c.coords, c.size, square[0:2], square[2:4]):
									if DualLine(cm, cs, c):
										sight = False
										pygame.draw.line(debugOverlay, PURPLE, cm, cs)
							if sight or mob == self.stuckOn:
								pow = ((self.detRange - td) / self.detRange)
								netforce[0] += (xd / td) * pow
								netforce[1] += (yd / td) * pow
				if netforce[0] != 0 and netforce[1] != 0:
					print "\n", netforce
					if mob.type in [0, 2]:
						mob.vel[0] += (netforce[0] * self.pow2) / mob.mass
						mob.vel[1] += (netforce[1] * self.pow2) / mob.mass
						print mob.vel
					if mob.type in [1, 2]:
						dmg = math.floor(abs(netforce[0] * self.dmg) + abs(netforce[1] * self.dmg))
						print "Damage: ", dmg
						mob.hp -= dmg
						if mob.hp <= 0:
							mob.img = squareExplodeImgs[0]
							mob.isExploding = True
				
		else:
			print "Bomb pushing something unusual!"
			


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
		return bomb(self.type, [coords[0]+4, coords[1]+4], vel, (8, 8), self.kbP, self.kbB, self.dmg, self.arm, self.bomb)

DetGod = detonator(0, 16, 16, 5, 0, 99999, getImg("UI/DetGod"), bombImg)
<<<<<<< HEAD
=======
DetNorm = detonator(1, 2, 8, 3, 30, 4, getImg("UI/DetDefault"), bombImg)
>>>>>>> 9b3be4b642862f7ecf4308a81e67570bd02c054b
DetKB = detonator(2, 16, 30, 1, 20, 2, getImg("UI/DetJumper"), getImg("Bombs/tosser"))
DetMulti = detonator(3, 1, 10, 2, 80, 10, getImg("UI/DetMulti"), getImg("Bombs/Multi"))
DetDest = detonator(4, 1, 1, 20, 30, 4, getImg("UI/DetDestructive"), getImg("Bombs/Dest"))
DetCurrent = DetGod

bombs = []

bricks = []



def spawnChar(entrance):
	player.coords = [100,250]
	player.coords = entrance.coords

	'''
	if currLvl == 0:
		player.coords = [50, 250]
	elif currLvl == 1:
		player.coords = [50, 500]
	elif currLvl == 2:
		player.coords = [112, 544]
	else:
		player.coords = [50, 250]
	'''
	print currLvl
	player.vel[1] = 0
	player.vel[0] = 0

def createFloor(coordx, coordy, ry, rx, type=0):
	bricks.append(Brick(type, [coordx, coordy], (rx * 16, ry * 16), brickImg))

def wipeFloor():
	global bricks
	global bombs
	global movingblocks
	global switches
	global gates
	global platforms
	global crates
	global keys
	keys = []
	crates = []
	global grates
	global sensors
	sensors = []
	grates = []

	bricks = []
	bombs = []
	movingblocks = []
	switches = []
	gates = []
	platforms = []


def createExit(type, coords, size, img):
	exits.append(Exit(type, coords, size, img))

def createWall(coordx, coordy, rx, ry, dir):
	if dir == "down":
		bricks.append(Brick("type", [coordx, coordy], (ry * 16, rx * 16), brickImg))
	if dir == "up":
		bricks.append(Brick("type", [coordx, coordy], (ry * 16, rx * 16), brickImg))

def createMovingBlock(coordx, coordy, rx, ry, type, hp = 1):
	rand = movingBlock(type, [coordx, coordy], [rx*16, ry*16])
	rand.hp = hp
	movingblocks.append(rand)
	
def createSensor(coordx, coordy, rx, ry, type, actions, link = None):
	rand = Sensor(type, (coordx, coordy), (ry * 16, rx * 16))
	rand.actions = actions
	rand.trigger = link
	sensors.append(rand)
	
def createGrate(coordx, coordy, rx, ry, blocked):
	grates.append(Grate((coordx, coordy), (rx*16, ry*16), blocked))


def borderedLevel():
	createFloor(0, 0, 2, 64)
	createFloor(0, 688, 2, 64)
	createFloor(0, 32, 41, 2)
	createFloor(992, 32, 41, 2)
# creates floors and walls based on coor and size

switches = []
keys = []
gates = []
crates = []
platforms = []


def openReadFile(filePath):
	entrances = [Entrance(0, [700, 250], [1, 1], entranceImg)]
	exits = [Exit(0, [250, 250], [1, 1], exitImg)]
	file = open(filePath, "r")
	cont = file.readlines()
	print "----"
	for i in cont:
		symbol, type, x, y, xs, ys = i.split("*")
		if symbol == "$":
			if type == "-1":
				print "Floor"
				createFloor(int(x), int(y), int(int(ys) / 16), int(int(xs) / 16))
			elif type == "4":
				print "Enterances"
				entrances = [Entrance(4, [int(x), int(y)], [int(xs), int(ys)], entranceImg)]
				screen.blit(entrances[0].img, entrances[0].coords)
			elif type == "5":
				print "Exits"
				exits = [Exit(5, [int(x), int(y)], [int(xs), int(ys)], exitImg)]
				screen.blit(exits[0].img, exits[0].coords)
			else:
				print "moveBlock"
				createMovingBlock(int(x), int(y), int(int(xs) / 16), int(int(ys) / 16), int(type))
	spawnChar(entrances[0])

currLvl = 0
totalLvls = 101	#CHANGE THIS WHEN ADDING LVLS

def createLevel(lvl):	#Almost all refrences of this should be written createLevel(currLvl). Only use an int for bugtesting.
	entrances = [Entrance(0, [700, 250], [1, 1], entranceImg)]
	global DetCurrent
	wipeFloor()
	if (lvl == -1):
		pass
	elif (lvl == 0):
		borderedLevel()
		openReadFile("saves/Level0.txt")

		#platforms.append(Platform((896, 626), (64, 64), platformImg))
		switches.append(Switch("Switch", (256, 288), (32, 32), switchImg, False))
		crates.append(Crate((432, 160), (16, 16), crateImg))
		keys.append(Key((432, 160), (8, 8), keyImg))
		gates.append(Gate((896, 626), (64, 64), lockImg, False))

	elif (lvl == 1):
		createFloor(0, 0, 45, 2)
		createFloor(992, 0, 45, 2)
		createFloor(32, 688, 2, 60)
		createFloor(32, 0, 2, 60)
		createFloor(32, 304, 1, 18)
		createFloor(368, 288, 1, 12)
		createFloor(464, 272, 1, 3)
		createFloor(192, 224, 1, 13)
		createFloor(320, 240, 1, 2)
		createFloor(560, 224, 1, 15)
		createFloor(496, 192, 1, 17)
		createMovingBlock(656, 208, 2, 1, 1)
		createMovingBlock(240, 192, 3, 2, 0)
		createFloor(160, 416, 4, 12)
		createFloor(544, 528, 1, 16)
		createExit(4, [int(768), int(672)], [int(16), int(16)], exitImg)
		entrances = [Entrance(4, [int(48), int(256)], [int(16), int(16)], entranceImg)]
		grates.append(Grate([int(896), int(624)], [int(64), int(64)], []))
		
		DetCurrent = DetGod

		
	elif lvl == 2: #5
		createFloor(0, 0, 45, 5)
		createFloor(80, 608, 7, 59)
		createFloor(80, 448, 3, 21)
		createFloor(416, 544, 1, 1)
		createFloor(464, 544, 1, 1)
		createFloor(80, 0, 8, 45)
		createFloor(800, 0, 31, 14)
		createFloor(480, 336, 10, 20)
		createFloor(192, 272, 4, 34)
		entrances = [Entrance(4, [int(128), int(576)], [int(16), int(16)], entranceImg)]
		createMovingBlock(416, 480, 4, 4, 0)
		rand = Grate([int(736), int(496)], [int(64), int(112)], ["guy", "moving"])
		createSensor(736, 272, 4, 4, 0, ["guy"], rand)
		grates.append(rand)
		
		DetCurrent = DetMulti
		
	elif lvl == 3:
		createFloor(0, 0, 45, 2)
		createFloor(992, 0, 45, 2)
		createFloor(32, 0, 2, 60)
		createFloor(32, 576, 1, 60)
		createFloor(96, 512, 4, 1)
		createFloor(144, 496, 5, 1)
		createFloor(192, 480, 6, 1)
		createFloor(240, 464, 7, 1)
		createFloor(288, 448, 8, 1)
		createFloor(336, 432, 9, 1)
		createFloor(384, 416, 10, 1)
		createFloor(432, 400, 11, 1)
		createFloor(480, 384, 12, 1)
		createFloor(528, 368, 13, 1)
		createFloor(576, 352, 14, 1)
		createFloor(624, 336, 15, 1)
		createFloor(672, 320, 16, 1)
		createFloor(720, 304, 17, 1)
		createFloor(768, 288, 18, 1)
		createFloor(816, 272, 19, 1)
		createFloor(864, 256, 20, 1)
		createFloor(912, 240, 21, 1)
		createFloor(960, 224, 22, 1)
		entrances = [Entrance(4, [int(40), int(560)], [int(16), int(16)], entranceImg)]
		exits = [Exit(4, [int(944), int(576)], [int(16), int(16)], exitImg)]

		
	elif lvl == 4: #4
		createFloor(0, 448, 17, 64)
		createFloor(0, 0, 12, 20)
		createFloor(0, 384, 4, 7)
		createMovingBlock(320, 288, 4, 4, 1)
		createMovingBlock(320, 368, 4, 5, 0)
		createFloor(160, 336, 3, 10)
		createFloor(384, 240, 9, 11)
		createFloor(384, 0, 13, 11)
		createFloor(624, 0, 24, 25)
		createMovingBlock(560, 368, 4, 5, 0)
		createMovingBlock(560, 288, 4, 4, 1)
		entrances = [Entrance(4, [int(192), int(416)], [int(16), int(16)], entranceImg)]
		DetCurrent = DetKB
		
	#elif lvl == 5:

	elif lvl == 6: #3
		createFloor(0, 0, 9, 64)
		createFloor(960, 144, 36, 4)
		rand1 = Grate([int(80), int(480)], [int(304), int(32)], ["guy"])
		rand2 = Grate([int(352), int(384)], [int(32), int(96)], ["guy"])
		createSensor(384, 304, 3, 4, 0, ["guy"], rand1)
		createSensor(384, 304, 3, 4, 0, ["guy"], rand2)
		grates.append(rand1)
		grates.append(rand2)
		
		grates.append(Grate([int(224), int(448)], [int(32), int(32)], ["bomb"]))
		grates.append(Grate([int(0), int(144)], [int(80), int(576)], ["guy"]))
		
		createFloor(288, 352, 2, 21)
		createFloor(544, 656, 4, 26)
		createFloor(592, 144, 13, 2)
		createMovingBlock(288, 304, 6, 3, 0)
		grates.append(Grate([int(256), int(144)], [int(32), int(240)], ["guy", "moving"]))
		entrances = [Entrance(4, [int(112), int(448)], [int(16), int(16)], entranceImg)]
		exits = [Exit(4, [int(864), int(624)], [int(16), int(16)], exitImg)]
		
		DetCurrent = DetKB

	elif lvl == 7: #2
		createFloor(0, 560, 10, 64)
		createFloor(0, 0, 12, 64)
		createFloor(624, 192, 18, 12)
		rand = Grate([int(640), int(480)], [int(160), int(80)], ["guy"])
		createSensor(160, 512, 3, 4, 0, ["guy"], rand)
		grates.append(rand)
		createFloor(0, 192, 23, 4)
		createFloor(960, 192, 23, 4)
		createFloor(480, 400, 3, 7)
		createFloor(480, 384, 1, 2)
		grates.append(Grate([int(432), int(192)], [int(48), int(256)], ["guy", "bomb"]))
		createMovingBlock(560, 352, 4, 3, 0)
		grates.append(Grate([int(592), int(400)], [int(32), int(48)], ["guy"]))
		entrances = [Entrance(4, [int(110), int(540)], [int(16), int(16)], entranceImg)]
		createExit(4, [int(864), int(544)], [int(16), int(16)], exitImg)
		DetCurrent = DetKB
	
	#elif lvl == 8:

	
	#SEPERATION
	
	
	
	else:
		createFloor(0, 688, 2, 64)
		
	if lvl == 100:
		openReadFile("saves/LevelCutscene1.txt")
		#switches.append(Switch("Switch",(256,)))
		
	print "Loaded level: ", lvl
	DB.refresh()
	for i in bricks:
		DB.img.blit(i.img, i.coords)
	spawnChar(entrances[0])

def soundEffect(sfxkey):
	if not muteon:
		if sfxkey == 1:
			effect = pygame.mixer.Sound("assets/Sounds/Jump3.wav")
			effect.play()
		if sfxkey == 2:
			effect = pygame.mixer.Sound("assets/Sounds/Win.wav")
			effect.play()
		if sfxkey == 3:
			effect = pygame.mixer.Sound("assets/Sounds/Open.wav")
			effect.play()
		if sfxkey == 4:
			effect = pygame.mixer.Sound("assets/Sounds/Explosion.wav")
			effect.play()
		if sfxkey == 5:
			effect = pygame.mixer.Sound("assets/Sounds/throw.wav")
			effect.play()


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
movingbA = 10
createLevel(currLvl)
isCutsecne = True
if isCutsecne == True:
	createLevel(100)
def changeSwitch():
	for s in switches:
		s.img = switchImages[0]
timer = 10
while Running:
	mousepos = pygame.mouse.get_pos()
	if debugon:
		debugOverlay = pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()
	if bombWaitTime > 0:  # sets off bomb
		bombWaitTime -= 1
	bombsExplode = False
	player.dualColliding = False
	player.collided = [0, 0]
	bombType = 1
	screen.fill(WHITE)
	startTimer = False

	# user input
	for event in pygame.event.get():

		if event.type == pygame.KEYDOWN:
		#Switches and Interactable Objects
			if(len(switches) > 0):
				if (isNear(center(switches[0]), center(player))):
						if event.key in [K_e]:


								for s in switches:
									if len(movingblocks) <= s.blockamount and s.on == False:

										s.on = True
										movingblocks.append(movingBlock(0, [64, 64], (16, 16)))
										s.img = switchImages[1]

			# movement
			if event.key in [K_RIGHT, K_d]:  # move ->
				player.motion[0] += 2.0
				gR = 0
				personimg = right[player.index]
				movingRight = True
				movingLeft = False
			if event.key in [K_LEFT, K_a]:  # move <-
				player.motion[0] -= 2.0
				gL =0
				time.sleep(.02)
				personimg = left[player.index]
				movingLeft = True
				movingRight = False
			if event.key in [K_RIGHT and K_a, K_LEFT and K_d]:  # move ->
				movingRight = False
				movingLeft = False
			if event.key in [K_DOWN, K_s]:  # v
				player.motion[1] += 0.5
				player.Crouch()
			if event.key in [K_UP, K_w] and player.floor:  # ^
				player.vel[1] = -8
				sfxkey = 1
				soundEffect(sfxkey)
				player.floor = False
			if event.key in [K_LALT, K_e]:
				bombs = []
				
			if event.key == K_r:  # slow down
				fps = 1
			if event.key == K_f:  # speed up
				fps = 60
			if event.key == K_c:
				if debugon:
					debugon = False
				else:
					debugon = True
			if event.key == K_m:
				if muteon:
					muteon = False
				else:
					muteon = True
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

			if event.key == K_1 and debugon:
				bombs = []
				DetCurrent = DetGod
			if event.key == K_2 and debugon:
				bombs = []
				DetCurrent = DetNorm
			if event.key == K_3 and debugon:
				bombs = []
				DetCurrent = DetKB
			if event.key == K_4 and debugon:
				bombs = []
				DetCurrent = DetMulti
			if event.key == K_5 and debugon:
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


	p1 = center(player)
	player.coords[0] += player.vel[0]
	player.coords[1] += player.vel[1]
	if debugon:
		pygame.draw.line(debugOverlay, PURPLE, p1, center(player))
		pygame.draw.rect(debugOverlay, PURPLE, (player.coords[0], player.coords[1], player.size[0], player.size[1]), 1)

	if not hit(player.coords, player.size, (0, 0), size):
		player.Kill()


	player.floor = False

	for k in keys:
		screen.blit(k.img,k.coords)
		if isNear(player.coords, k.coords):
			player.hasKey = True
			sfxkey = 2
			soundEffect(sfxkey)

			keys.remove(k)
	for g in gates:
		if isNear(g.coords, player.coords):
			if player.hasKey == True:
				sfxkey = 3
				soundEffect(sfxkey)

	if len(movingblocks) > 0:
		for i in bricks:
			player.Collide(i)



	for i in platforms:
		player.Collide(i)
	for i in crates:
		player.Collide(i)
	for g in gates:
		player.Collide(g)
	for i in exits:
		if collide([player.coords[0]-8, player.coords[1]-8], [16,16], [i.coords[0]-8, i.coords[1]-8], [16,16]):
			currLvl += 1
			createLevel(currLvl)

	for i in movingblocks: #Moving blocks hit with each other
		for p in movingblocks:
			if not (p == i) and p.type != 1:
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

			personimg = derek
		if player.motion[0] < 0:
			counter += 1
			if counter == 10:
				player.index += 1
				counter = 0
			if player.index >= len(left):
				player.index = 0
			personimg = left[player.index]
		if player.motion[0] > 0:
			if not isCrouching :
				counter += 1
				if counter == 10:
					player.index += 1
					counter = 0
				if player.index >= len(right):
					player.index = 0

			personimg = right[player.index]

	# Moving Blocks
	for i in movingblocks: #Player hit with moving blocks
		if i.isExploding:
			i.incrementSprite(1)
		player.Collide(i)
		if i.type in [0, 2]:
			if i.vel[1] < maxFallSpeed and not i.floor:  # Gravity
				i.vel[1] += gravity

			i.floor = False
			if i.vel[0] <= -16:
				i.vel[0] = -16

			if i.vel[1] <= -16:
				i.vel[1] = -16

			if i.vel[0] >= 16:
				i.vel[0] = 16

			if i.vel[1] >= 16:
				i.vel[1] = 16

			p1 = center(i)
			i.coords[0] += i.vel[0]
			i.coords[1] += i.vel[1]
			if debugon:
				pygame.draw.line(debugOverlay, PURPLE, p1, center(i))
				pygame.draw.rect(debugOverlay, PURPLE, (i.coords[0], i.coords[1], i.size[0], i.size[1]), 1)

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

	for i in sensors:
		if i.trigger != None:
			for p in movingblocks:
				i.collide(p)
			
	for p in platforms:
		player.Collide(p)
	'''for mb in movingblocks:
		if isOnTop(p, mb) and isNear(center(p), center(mb)):
			print "you won!"
		mb.Collide(p)'''
	for i in bricks:
		#screen.blit(i.img, i.coords)
		player.Collide(i)
	for i in grates:
		if "guy" in i.blocked:
			player.Collide(i)
		if "bomb" in i.blocked:
			for p in bombs:
				p.Collide(i)
		if "moving" in i.blocked:
			for p in movingblocks:
				if (p.type == 0) or ("dest" in i.blocked and p.type == 2):
					p.Collide(i)

	for i in bombs:
		if i.isExploding:
			i.explodeTime -= 1
			i.incrementSprite(1, i.explodeTime)
			sfxkey = 4
			soundEffect(sfxkey)
			if i.explodeTime > 10:

				pygame.draw.circle(screen, BLACK, (int(center(i)[0]), int(center(i)[1])), detRange-player.size[0], 1)


		if i.explodeTime <= 0:
			bombs.remove(i)

		if not i.stuck:
			if i.vel[1] < 8:
				i.vel[1] += gravity*.75

			if i.vel[0] <= -8:
				i.vel[0] = -8

			if i.vel[1] <= -8:
				i.vel[1] = -8

			if i.vel[0] >= 8:
				i.vel[0] = 8

			if i.vel[1] >= 8:
				i.vel[1] = 8
				
			p1 = center(i)
			i.coords[0] += i.vel[0]
			i.coords[1] += i.vel[1]
			if debugon:
				pygame.draw.line(debugOverlay, PURPLE, p1, center(i))
				pygame.draw.rect(debugOverlay, PURPLE, (i.coords[0], i.coords[1], i.size[0], i.size[1]), 1)

		if not i.armed:
			i.time += 1
			if i.time >= i.arm:
				i.armed = True
				sfxkey = 5
				soundEffect(sfxkey)

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


	if bombsExplode:
		for i in bombs:
			if i.armed:
				if (i.type != 3) or (isNear(center(i), mousepos, 32)) or (isNear(center(i), center(player), 20)):
					i.isExploding = True
					i.img = normalBombImgs[0]
					i.Detonate(player)
					for p in movingblocks:
						i.Detonate(p)
					i.stuck = True
					i.stuckOn = None
					i.vel = [0, 0]


	if player.floor:
		player.vel[0] = Zero(player.vel[0], friction)

	screen.blit(DB.img, (0, 0))
	
	for i in sensors:
		screen.blit(i.img, i.coords)
	for i in bombs:
		screen.blit(i.img, i.coords)
	for s in switches:
		if s.on == True:
			s.time -= 1

		if s.time <= 0:
			s.on = False

		if s.on == False:
			s.img = switchImages[0]
			s.time = 500
		screen.blit(s.img, s.coords)
	for k in keys:
		screen.blit(k.img, k.coords)
	for g in gates:
		screen.blit(g.img, g.coords)
	for i in grates:
		screen.blit(i.img.img, i.coords)
	for c in crates:
		screen.blit(c.img, c.coords)
	#UI display
	
	screen.blit(personimg, player.coords)
	if DetCurrent.type == 3:
		pygame.draw.circle(screen, RED, mousepos, 32, 1)
		pygame.draw.rect(screen, WHITE, (0, 0, 123, 38))
	pygame.draw.rect(screen, WHITE, (0, 0, 100, 38))
	screen.blit(fontComp.render(str(len(bombs))+"/"+str(DetCurrent.max), False, BLACK), (41, 3))
	screen.blit(DetCurrent.img, (4, 4))
	for i in exits:
		screen.blit(i.img, i.coords)

	screen.blit(mouseImg, (mousepos[0]-3, mousepos[1]-3))
	if debugon:
		screen.blit(debugOverlay, (0, 0))
	pygame.display.update()
	clock.tick(fps)
