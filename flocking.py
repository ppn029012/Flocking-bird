
#import modules
from random import *
import math
import pygame
from pygame.locals import *
from pygame.sprite import Sprite


'''
Name: robot(Sprite)
Attributes:screen: the surface used to store this robot
           image_file: the image used to present this robot
           x,y: the position of this robot in screen
           speed: the speed it moves
           direction: the direction it moves to, use a float to represent
           visDistance: the distance a robot can see
           visAngle: the angle a robot can see
MethodS:trun(desAngle): smoothly turn to the destination direction
        randomDIr(): choose a random direction
        moveForward(): move a step to the choosed direction
        blitme(): show the robot in the screen
        update(): rotate the image according to the direction
'''
class robot(Sprite):
  def __init__(self,screen, image_file, x, y ,speed, direction, deltadir,visDistance, visAngle):
    Sprite.__init__(self)
    self.speed = speed 
    self.direction = direction
    self.isSpeedingUp = False
    self.status = 1
    self.deltadir = deltadir
    self.x = x
    self.y = y
    self.canSeeBird = []
    self.visDistance = visDistance
    self.image_file = image_file
    self.screen = screen
    self.visAngle = visAngle
    self.base_image = pygame.image.load(image_file).convert_alpha()
    self.base_image = pygame.transform.rotate(self.base_image, -90)
    self.image = self.base_image
    self.image_w, self.image_h = self.image.get_size()

  def turn(self,desAngle):
    if self.direction < desAngle:
      self.direction += self.deltadir
    else:
      self.direction -= self.deltadir    
     
  def randomDir(self):
    # produce a random direction around current direction
    randomDirection = (random()/4)-0.125
    newdirection = self.direction + randomDirection
    self.turn(newdirection)
  
  def moveForward(self):
    self.x += self.speed * math.sin(self.direction*2*3.14)
    self.y += self.speed * math.cos(self.direction*2*3.14)
    self.canSeeBird = []
    
  def blitme(self):
    draw_pos = self.image.get_rect().move(
            self.x - self.image_w / 2, 
            self.y - self.image_h / 2)
    self.screen.blit(self.image, draw_pos)

  def update(self):
    self.image = pygame.transform.rotate(self.base_image, self.direction*360)


  def calibrateDirection(self,direction):
    if direction >1:
      return direction -1
    elif direction < 0 :
      return direction + 1
    else:
      return direction


# get distance between two points
def getDistance(a,b):  
        d = (b[1]-a[1])**2+(b[0]-a[0])**2
        d = math.sqrt(d)
        return d

# change a position vector to dirction float
def vector2dir (vector):
  if vector[0]>0 and vector[1]>0:
    direction = math.atan(vector[0]/vector[1])
    direction = direction/6.28
  if vector[0]>0 and vector[1]<0:
    direction = math.atan(-vector[1]/vector[0])
    direction = direction/6.28
    direction = direction + 0.25
  if vector[0]<0 and vector[1]<0:
    direction = math.atan(vector[1]/vector[0])
    direction = direction/6.28
    direction = direction + 0.5
  if vector[0]<0 and vector[1]>0:
    direction = math.atan(vector[1]/-vector[0])
    direction = direction/6.28
    direction = direction +0.75
  return direction



def main():

  # Game parameters
  SCREEN_WIDTH, SCREEN_HEIGHT = 900, 800 # the main window size
  BG_COLOR = 150, 150, 80  #background colour
  NUM = 9  #number of robot
  robot_normal = 'normal.jpg'   # the wondering state picture
  robot_avoid = 'avoid.jpg' # the avoid state picture
  robot_flock = 'flock.jpg' # the flocking state picture
  robot_catchup = 'catchup.jpg' # the catch up state picture

  # initialize pygame
  pygame.init()
  screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
  clock = pygame.time.Clock()

  
  # initialize parameters
  dMin=30   # the avoid distance
  dFlocking=120  # the distance begin to flock
  birdList = []

  for i in range(NUM):	#creat birds
    instance = robot(screen, robot_normal, randint(10,SCREEN_WIDTH-10), randint(10,SCREEN_HEIGHT-10) ,10, random() , 0.01, 150, 1)
    birdList.append(instance)

  # the main loop
  while True:
    #when press x button, exit()
    for event in pygame.event.get():
      if event.type == QUIT:
          exit()

    screen.fill(BG_COLOR) #set background colour
    time_passed = clock.tick(7) #set clock
    

    # at this stage, each bird will scan their around to find other birds
    # and then the will analyze those birds to determine their direction
    
    for bird in birdList:
      # initialize each bird
      bird.deltadir = 0.01
      bird.speed = 10
      bird.canSeeBird = []
      bird.base_image = pygame.image.load(robot_normal).convert_alpha()
      for otherBird in birdList:
        if bird == otherBird:   # do not analyse itself
          continue
        d = getDistance([bird.x,bird.y],[otherBird.x,otherBird.y]) #get distance between birds
        if d <= bird.visDistance: # the distance is smaller than the distance a bird can see
          # get direction between these two bird
          direction = vector2dir([otherBird.x-bird.x, otherBird.y-bird.y])  
          direction = direction - bird.direction 
          if -0.3 < direction < 0.3:  # the angle is fit for the bird to see another bird
            bird.canSeeBird.append(otherBird)


    for bird in birdList:
      # no birds have seen
      if len(bird.canSeeBird) == 0:
        continue
      # caculate the average direction of other bird
      otherX=0
      otherY=0
      otherDirection=0
      # caculate the average position of other bird
      for otherBird in bird.canSeeBird:
        otherX += otherBird.x
        otherY += otherBird.y
      otherX = otherX/len(bird.canSeeBird)
      otherY = otherY/len(bird.canSeeBird)

      otherAveragePosition = [otherX, otherY] #other birds average position
      distance = getDistance(otherAveragePosition,[bird.x,bird.y])
      
      if distance < dMin:  # distance is too small, so need avoidance
        bird.base_image = pygame.image.load(robot_avoid).convert_alpha() # change image
        #change to the oppsite direction
        vector=[]
        for otherBird in bird.canSeeBird:
          vector += [-otherBird.x+bird.x,-otherBird.y+bird.y] 
        direction = vector2dir(vector)
        bird.direction = direction


        

      # distance between the bird is bigger than avoid edge and small than FLOCKing edge
      if dMin < distance < dFlocking:   # Flocking
        bird.deltadir = 0.1
        bird.base_image = pygame.image.load(robot_flock).convert_alpha()
        otherDirection=0
        #turn to right direction
        for otherBird in bird.canSeeBird:
          otherDirection += otherBird.direction
        otherDirection = otherDirection/len(bird.canSeeBird)
        bird.turn(otherDirection)      # keep same direction with the average direction of the birds it can see


      if  distance > dFlocking :  # distance is bigger than flocking edge , do it need to catch up
        bird.base_image = pygame.image.load(robot_catchup).convert_alpha() #change image
        bird.deltadir = 0.08 # increase turn rate
        #turn to the right direction
        vector = [otherAveragePosition[0]-bird.x,otherAveragePosition[1]-bird.y]  
        direction = vector2dir(vector)
        bird.turn(direction)
        bird.speed = 16  #speed up
      
    # avoiding the birds cross the boundary
    for bird in birdList:
      if len(bird.canSeeBird)==0: 
        bird.randomDir()
      if bird.y <50:
        bird.direction = 1
      if bird.x <50:
        bird.direction =0.25 
      if bird.y >620:
        bird.direction =0.5
      if bird.x >620:
        bird.direction =0.75
      if  bird.x >= 620 and bird.y >=400:
        bird.direction = 0.625
      if bird.x <=50 and bird.y <=50:
        bird.direction =0.125
      if bird.y <=20 and bird.x >= 620:
        bird.direction =0.875
      if bird.y >=400 and bird.x <=50:
        bird.direction =0.375
      
      
      #show the change to the screen
      bird.moveForward()
      bird.update()
      bird.blitme()

    pygame.display.flip()



if __name__== '__main__': main()

