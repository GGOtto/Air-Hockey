# Name: Air Hockey
# Author: G.G.Otto
# Date: 7/27/21
# Version: 1.0

import pygame, random, math
from pygame.locals import *
import gamesetup as gs

class Putter(gs.Sprite):
    '''manipulates a hockey putter'''

    def __init__(self, game, color, top):
        '''Putter(Game, (r,g,b), bool) -> Putter
        constructs a hockey putter
        top is True for top section, False for bottom'''
        gs.Sprite.__init__(self, game, pygame.transform.rotozoom(gs.change_colors("hockey.png",
            (0, 0, 0, 255), (0, 0, 0, 0), (127, 127, 127, 255), color), 0, 0.7))
        self.top = top
        self.size = self.surface().get_size()
        game.get_putters().append(self)
        self.set_image_turning(False)

        # position putter
        if top:
            self.pos((300,100))
        else:
            self.pos((300,600))

    def process_coords(self, pos):
        '''Putteer.process_coords((x,y)) -> x,y
        returns the coordinates processed for putter's side of the field'''
        output = list(pos)
        
        # process center barrier
        if self.top and pos[1] > 350 - self.size[1]/2 + 3:
            output[1] = 350 - self.size[1]/2 + 3
        elif not self.top and pos[1] < 350 + self.size[1]/2 - 3:
            output[1] = 350 + self.size[1]/2 - 3

        # process top and bottom
        if output[1] < 0:
            output[1] = 0
        elif output[1] > 700:
            output[1] = 700

        # process sides
        if output[0] < 0:
            output[0] = 1
        elif output[0] > 600:
            output[0] = 599
            
        return output
        
    def pos(self, pos=None):
        '''Putter.pos(pos=None) -> None
        control for the putter's position'''
        if pos == None:
            return gs.Sprite.pos(self)

        # if too close to putt
        pos = self.process_coords(pos)
        if self.game.get_putt().distance(pos) < self.size[0]/2 - 10 + \
           self.game.get_putt().surface().get_width()/2:
            self.stop_time()
        else:
            gs.Sprite.pos(self, pos)            

class RobotPutter(Putter):
    '''moves around the robot putter'''

    def __init__(self, game, difficulty):
        '''Robot_Putter(Game, int) -> RobotPutter
        constructs the robot putter
        difficulty is 1, 2, or 3'''
        Putter.__init__(self, game, (0,0,255), True)
        self.last = (self.pos(), -1)
        self.difficulty = difficulty
        self.heading(270)
        self.clock = gs.Clock()
        self.clock.set_time(20)

    def decide(self):
        '''RobotPutter.decide() -> None
        makes the decisions for the putter'''
        if self.clock.get_time() <= 0.5 or 180 < self.game.get_putt().heading() < 360 \
            or self.game.get_putt().is_stopped():
            return
        
        # make choice
        putt = self.game.get_putt()
        choiceCoords = putt.in_front(2*putt.distance((300,0))/3)
        heading = gs.towards(choiceCoords, (random.randint(210, 390), 700))
        choice = self.process_coords(gs.in_dir(choiceCoords, heading+180, self.size[0]/2-1))

        # use choice
        self.heading(self.towards(choice))
        self.forward_time(self.distance(choice), 0.5)
        self.clock.reset()
        self.clock.start()

    def update(self):
        '''RobotPutter.update() -> None
        updates the robot putter'''
        self.decide()
        Putter.update(self)

class Putt(gs.Sprite):
    '''manipulates the hockey putt'''

    def __init__(self, game):
        '''Putt(game) -> Putt
        constructs the hockey putt'''
        gs.Sprite.__init__(self, game, pygame.transform.rotozoom(gs.remove_bg("putt.png"), 0, 0.6))
        self.pos((300,350))
        self.set_image_turning(False)
        self.heading(random.choice((90, 270)))
        self.size = self.surface().get_size()
        self.inTop = False
        self.inSide = False
        self.norm = 0.4
        self.normAdd = 0.3
        self.speed = self.norm
        self.bounceOff = []
        self.stopped = True

    def set_stopped(self, boolean, move=False):
        '''Putt.set_stopped(boolean) -> None
        sets the stopped attribute'''
        self.stopped = boolean
        if move: pygame.mouse.set_pos((300, 600))

    def is_stopped(self):
        '''Putt.is_stopped() -> bool
        returns if the putt is stopped'''
        return self.stopped

    def reset(self, scorer):
        '''Putt.reset(scorer) -> None
        resets the putt'''
        self.stopped = True
        self.pos((300, 350))

        # heading
        if scorer == 0:
            self.heading(270)
        else:
            self.heading(90)

    def update(self):
        '''Putt.update() -> None
        updates the hockey putt'''
        if self.stopped:
            gs.Sprite.update(self)
            return

        # if win game
        if self.game.is_win():
            self.stopped = True
        
        # bounce off wall
        x,y = self.in_front(3)
        if not self.size[0]/2 - 3 < x < 600 - self.size[0]/2 + 3:
            if not self.inSide:
                if not -30 < x < 630:
                    self.heading(self.towards((300, 350)))
                    self.inTop = True
                else:
                    self.heading(180 - self.heading())
        else:
            self.inSide = False

        # bounce off ceiling
        if not self.size[1]/2 - 3 < y < 700 - self.size[1]/2 + 3:# and not 200 < x < 400:
            if not self.inTop:
                if not -30 < y < 730:
                    self.heading(self.towards((300, 350)))
                    self.inTop = True
                else:
                    self.heading(-self.heading())
            else:
                self.inTop = False
                
        # bounce off putter
        for putter in self.game.get_putters():
            if gs.distance((x,y), putter.pos()) < self.size[0]/2 + putter.surface().get_width()/2:
                if putter not in self.bounceOff:
                    self.heading(180+self.towards(putter.pos()))
                    self.speed = self.norm + self.normAdd
                    self.bounceOff.append(putter)
            elif putter in self.bounceOff:
                self.bounceOff.remove(putter)

        self.forward(self.speed)
        gs.Sprite.update(self)

        # reduce speed
        if self.speed > self.norm:
            self.speed -= 0.001

class Game(gs.Game):
    '''manipulates the main game'''

    def __init__(self):
        '''Game() -> Game
        constructs the main game'''
        gs.Game.__init__(self)

        # screen setup
        self.screen = pygame.display.set_mode((600, 700))
        pygame.display.set_caption("Air Hockey")
        pygame.display.set_icon(gs.remove_bg("logo.png"))

        # attributes
        self.background = pygame.image.load("field.png")
        self.putt = Putt(self)
        self.putters = []
        self.player = Putter(self, (255, 0, 0), False)
        self.enemy = RobotPutter(self, 3)
        self.scores = [0,0]
        self.scoreDisplay = None
        self.colors = "blue", "red"
        self.winner = None

        # fonts
        self.scoreFont = pygame.font.SysFont("Arial", 34, True)
        self.scoreDisplayFont = pygame.font.SysFont("Arial", 200, True)
        self.winFont = pygame.font.SysFont("Arial", 120, True)
        self.timeFont = pygame.font.SysFont("Arial", 100, True)

        # initial timer
        self.initTime = gs.Clock()
        self.initTime.start()
        self.after(3100, lambda: self.putt.set_stopped(False, True))

    def set_score_display(self, setting):
        '''Game.set_score_display(setting) -> None
        setter for scoreDisplay'''
        self.scoreDisplay = setting

    def get_putters(self):
        '''Game.get_putters() -> list
        returns a list of all putters'''
        return self.putters

    def get_putt(self):
        '''Game.get_putt() -> Putt
        returns the game putt'''
        return self.putt

    def is_win(self):
        '''Game.is_win() -> bool
        returns if the game is won or not'''
        return self.winner != None

    def check_score(self):
        '''Game.check_score() -> None
        deals with a scoring'''
        x,y = self.putt.pos()

        scorer = None
        if 180 < x < 420 and -30 < y < 30:
            scorer = 1
        elif 180 < x < 420 and 670 < y < 730:
            scorer = 0

        if scorer != None:
            self.putt.reset(scorer)
            self.scores[scorer] += 1

            # check game win or not
            if self.scores[scorer] == 7:
                self.winner = self.colors[scorer]
            else:
                self.scoreDisplay = scorer
                self.after(3000, lambda: self.putt.set_stopped(False, True))
                self.after(2000, lambda: self.set_score_display(None))

            # reset putters
            self.player.pos((300, 600))
            self.enemy.pos((300, 100))
            pygame.mouse.set_pos((300, 600))

    def event(self, event):
        '''Game.event(event) -> None
        deals with game event'''
        if event.type == MOUSEMOTION:
            if not self.putt.is_stopped():
                pos = self.player.process_coords(event.pos)
                self.player.heading(self.player.towards(pos))
                self.player.forward_time(self.player.distance(pos), 0.05)
        elif event.type == KEYDOWN and self.is_win():
                self.__init__()
                

    def update(self):
        '''Game.update() -> None
        updates a single game frame'''
        self.screen.blit(self.background, (0,0))

        # deal with scores
        self.blit(self.scoreFont.render(str(self.scores[0]), True,
            "blue"), (566, 35), True, True)
        self.blit(self.scoreFont.render(str(self.scores[1]), True,
            "red"), (34, 665), True, True)

        # update game objects
        self.putt.update()
        self.player.update()
        self.enemy.update()
        self.check_score()

        # display for "Score!"
        if self.scoreDisplay != None:
            self.blit(self.scoreDisplayFont.render("Score!", True,
                self.colors[self.scoreDisplay]), (300, 350), True, True)

        # display for winner
        if self.is_win():
            self.blit(self.winFont.render(f"{self.winner.capitalize()} wins!",
                True, self.winner), (300, 350), True, True)

        # initial timer
        if self.initTime.get_time() < 3:
            self.blit(self.timeFont.render(str(int(3 - self.initTime.get_time()) + 1), True,
                "white"), (300, 265), True, True)
        
        pygame.display.update()

pygame.init()
Game().mainloop()
