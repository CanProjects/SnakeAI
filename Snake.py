from numpy.lib.utils import info
import pygame
import numpy as np
import random
import time
import collections
from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
import random
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.optimizers import Adam
from gym import Env
from gym.spaces import Discrete, Box
import stable_baselines3
from stable_baselines3 import A2C
from stable_baselines3.common.env_util import make_vec_env
from gym import spaces
from stable_baselines3 import A2C
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.env_util import make_vec_env
from typing import Callable
from stable_baselines3.common.env_checker import check_env


class Snake(Env):


    def __init__(self):
        # Generate board
        self.boardXSize = 10
        self.boardYSize = 10
        self.moveCounter = 0
        self.reset()

        # AI PART
        self.action_space = Discrete(4)
        self.observation_space = Box(0, 3, shape = (self.boardXSize-5,self.boardYSize-5), dtype = np.int32)
        #AI PART

        # Empty is 0, snake head is 1, Food is 2, tail is 3.

        # HUMAN CONTROL STUFF
                # # Make moves
                # x = 0
                # while x < 1000:
                #     # GameSpeed Control
                #     time.sleep(0.1)
                #     # Picking an action and doing it
                #     # action = random.randint(0, 3)
                #     letter = str(input('move? '))
                #     # YOU MESSED UP ALL THE COORDINATES AND YET IT STILL WORKS, X and Y AND EVERYTHING MAKES NO SENSE YET IT WORKS?
                #     # whatever i guess lmao so long as it works.
                #     if letter == 'd':
                #         action = 0
                #     elif letter == 'a':
                #         action = 1
                #     elif letter == 'w':
                #         action = 2
                #     elif letter == 's':
                #         action = 3
                #     self.step(action)
                #     print(self.state)
                #     x += 1

    def foodSpawn(self):
        # Array to store indexes of empty spots
        potentialLocs = []
        # Finds the indexes of all the empty spots
        for i in range(0, len(np.where(self.state == 0)[0])):
            # Put them into array as tuples
            potentialLocs.append((np.where(self.state == 0)[0][i],np.where(self.state == 0)[1][i]))
        # Randomly chose from these indexes
        if len(potentialLocs) == 0:
            pass
        else:
        # Spawn food (food is denoted in array as 2)
            locChoice = random.choice(potentialLocs)
            self.state[locChoice[0]][locChoice[1]] = 2

    def makeMove(self, action):
        # Down
        if action == 0:
            self.snakeCoordx += 1
        # Up
        elif action == 1:
            self.snakeCoordx -= 1
        # Left
        elif action == 2:
            self.snakeCoordy -= 1
        # Right
        elif action == 3:
            self.snakeCoordy += 1

    def step(self, action):

        # time.sleep(0.3)



        # Check for death and reset game
        if self.deathWall(action) or self.moveCounter > 120:
            self.reset()
            reward = -50
            done = True
        elif self.deathTail(action):
            self.reset()
            reward = -50
            done = True  
        else:
            # Adding to our tailLog the last coordinate of the snake.
            self.tailLogic(self.snakeCoordy, self.snakeCoordx)
            
            self.moveCounter +=1
            # Checking if your action would grab you food. First it checks if your action will kill you. Cant spawn food till later because we dont want it to spawn where the snake will spawn later.
            if not self.deathWall(action):
                if self.foodCapture(action):
                    foodCap = True
                else:
                    foodCap = False
                    reward = 0
                    # reward = -1

            if foodCap:
                self.foodSpawn()
                reward = 40
                self.tailLength += 1
                self.moveCounter = 0

            # Placing our tail (also clears board)
            self.placeTail()

            self.makeMove(action)

            # Putting in new snake location (snake is 1)
            self.state[self.snakeCoordy][self.snakeCoordx] = 1
            done = False

        NParrayData = np.array(self.state).reshape(self.boardXSize,self.boardYSize)
        NParrayData = np.pad(NParrayData, pad_width=5, mode='constant', constant_values='4')
        x = (np.argwhere(NParrayData == 1))[0,0]
        y = (np.argwhere(NParrayData == 1))[0,1]
        
        newState = np.array(NParrayData[x-2:x+3, y-2:y+3])
        # self.state = newState

        info = {}
        self.render()

        #Return step into
        return newState,reward,done,info


    def deathWall(self, action):
        # Checking if your action will kill you
        if action == 0:
            if self.snakeCoordx + 1 > self.boardYSize - 1:
                return True
        elif action == 1:
            if self.snakeCoordx - 1 < 0:
                return True
        elif action == 2:
            if self.snakeCoordy - 1 < 0:
                return True
        elif action == 3:
            if self.snakeCoordy + 1 > self.boardXSize - 1:
                return True
        else:
            return False

    def deathTail(self, action):
        if action == 0:
            if self.state[self.snakeCoordy][self.snakeCoordx+1] == 3:
                return True
        elif action == 1:
            if self.state[self.snakeCoordy][self.snakeCoordx-1] == 3:
                return True
        elif action == 2:
            if self.state[self.snakeCoordy-1][self.snakeCoordx] == 3:
                return True
        elif action == 3:
            if self.state[self.snakeCoordy+1][self.snakeCoordx] == 3:
                return True
        else:
            return False

    def foodCapture(self, action):
        # Checking if your action got you food.
        if (
            action == 0
            and self.state[self.snakeCoordy][self.snakeCoordx + 1] == 2
            or action == 1
            and self.state[self.snakeCoordy][self.snakeCoordx - 1] == 2
            or action == 2
            and self.state[self.snakeCoordy - 1][self.snakeCoordx] == 2
            or action == 3
            and self.state[self.snakeCoordy + 1][self.snakeCoordx] == 2
        ):
            return True
        else:
            return False

    def tailLogic(self, x, y):
        # Creating a log for the tail locations, removing from it if it gets too long to avoid clutter.
        if len(self.tailLog) < self.boardXSize * self.boardYSize:
            self.tailLog.appendleft((x, y))
        else:
            self.tailLog.appendleft((x, y))
            self.tailLog.pop

    def placeTail(self):
        # Erases old tail and head
        for i in range(self.boardXSize):
            for z in range(self.boardYSize):
                if self.state[i][z] == 3 or self.state[i][z] == 1:
                    self.state[i][z] = 0

        # Puts in new tail
        for i in range(0, self.tailLength):
            self.state[self.tailLog[i][0]][self.tailLog[i][1]] = 3

    def render(self,mode='human'):
        pygame.init()

        # Game window size
        size = self.width, self.height = 600, 600
        # Game color bank
        self.black = 0, 0, 0
        self.blue = 0, 0, 255
        self.red = 255, 0, 0
        self.green = 0, 255, 0
        self.white = 255, 255, 255
        # Setting screen
        self.screen = pygame.display.set_mode(size)
        # Start your engines
        run = True
        def drawGrid():
            blockSize = int(self.width/self.boardXSize)
            for x in range(0, self.width, blockSize):
                for y in range(0, self.height, blockSize):
                    rect = pygame.Rect(x, y, blockSize, blockSize)
                    pygame.draw.rect(self.screen, self.black, rect, 1)
        # Creating our exit condition

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        self.screen.fill(self.white)

        drawGrid()
        blockSize = self.width/10
        for i in range (0,10):
            for z in range(0,10):
                x = i*blockSize
                y = z*blockSize
                rect = pygame.Rect(x, y, blockSize, blockSize)
                if self.state[i][z] == 0:
                    pygame.draw.rect(self.screen,self.black,rect,0)       
                if self.state[i][z] == 1:
                    pygame.draw.rect(self.screen,self.red,rect,0) 
                if self.state[i][z] == 2:
                    pygame.draw.rect(self.screen,self.blue,rect,0)  
                if self.state[i][z] == 3:
                    pygame.draw.rect(self.screen,self.green,rect,0)  
        pygame.display.update()
        time.sleep(0.04)




                # for i in self.state:
                #     for z in i:
                #         print(int(z),' ' , end='')
                #     print('')
                # time.sleep(0.3)

    def reset(self):
        self.state = np.zeros((self.boardXSize, self.boardYSize))
        self.tailLength = 0
        self.snakeCoordy, self.snakeCoordx = random.randint(1, self.boardXSize - 2), random.randint(1, self.boardYSize - 2)
        self.state[self.snakeCoordy][self.snakeCoordx] = 1
        self.tailLog = collections.deque()
        self.foodSpawn()
        self.moveCounter = 0
        NParrayData = np.array(self.state).reshape(self.boardXSize,self.boardYSize)
        NParrayData = np.pad(NParrayData, pad_width=5, mode='constant', constant_values='4')
        x = (np.argwhere(NParrayData == 1))[0,0]
        y = (np.argwhere(NParrayData == 1))[0,1]
        
        newState = np.array(NParrayData[x-2:x+3, y-2:y+3])
        return newState
    
