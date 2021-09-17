# Name: Gamesetup
# Author: G.G.Otto
# Date: 1/25/2021
# Version 1.7.3
#
# Used with the pygame module
#
# This module is to make setting up your game easier.
# It also in a variety of different functions, objects,
# and methods to make coding your game easier in general.
#
# WARNING: codes uses older versions may not be
# completely combatible with new versions

import pygame, time, math, random

class GameSetupError(Exception):
    '''error for the gamesetup module'''

class Clock:
    '''represents a stopwatch that keeps track of time in seconds
   the clock starts out paused, so don't forget to play it!'''

    def __init__(self, maxTime=None, **game):
        '''Clock() -> Clock
        Clock(float) -> Clock
        Clock(game=Game) -> Clock
        
        constructs a clock.
        the clock starts with 0 seconds.
        don't forget to start it!

        if game is given, returns a registered clock'''
        self.startTime = None
        self.saved = 0
        self.maxTime = maxTime
        if "game" in game: game["game"].register_clock(self)
        else: self.game = None

    def get_max(self):
        '''Clock.get_max() -> float/int
        returns the max time of the clock'''
        return self.maxTime

    def set_max(self, maxTime):
        '''Clock.set_max(maxTime) -> None
        sets the max time of the clock'''
        self.maxTime = maxTime

    def get_time(self):
        '''Clock.get_time() -> float
        returns the current time on the stopwatch'''
        if self.startTime == None: return self.saved
        currentTime = time.time()-self.startTime+self.saved
        if self.maxTime != None and currentTime > self.maxTime:
            return self.maxTime
        return currentTime

    def set_time(self, newTime):
        '''Clock.set_time(newTime) -> None
        sets the current time on the stopwatch
        pauses the clock in the process'''
        self.saved = newTime
        self.startTime = None

    def reset(self):
        '''Clock.reset() -> None
        resets the clock back to 0
        pauses the clock in the process'''
        self.set_time(0)

    def stop(self):
        '''Clock.stop() -> None
        pauses the stopwatch.
        stopwatch may be resumed using Clock.start()'''
        self.saved = self.get_time()
        self.startTime = None

    def start(self):
        '''Clock.start() -> None
        starts the stopwatch.
        stopwatch may be stopped using Clock.stop()'''
        self.startTime = time.time()

class Camera(pygame.Surface):
    '''Camera inherits from Surface
    creates a surface with moveable view'''

    def __init__(self, *args, **kwargs):
        '''Camera(*args, **kawrgs) -> Camera
        constructs the camera with normal surface attributes'''
        pygame.Surface.__init__(self, *args, **kwargs)
        self.view = (0,0)

    def point(self, point):
        '''Camera.point((x,y)) -> (x,y)
        returns the point (relative to screen) on camera'''
        return point[0]-self.view[0], point[1]-self.view[1]

    def move_by(self, x=0, y=0):
        '''Camera.move_by(int, int) -> None
        moves the camera's view by x and y'''
        self.view = self.view[0] + x, self.view[1] + y
    
    def get_view(self):
        '''Camera.get_view() -> (x,y)
        returns the view (top-left corner) of teh camera'''
        return self.view

    def set_view(self, point):
        '''Camera.set_view((x,y)) -> None
        sets the view (top-left corner) of the camera'''
        self.view = point

    def get_at(self, point):
        '''Camera.get_at((x,y)) -> color
        returns the color at point'''
        return pygame.Surface.get_at(self, self.point(point))

    def set_at(self, point, color):
        '''Camera.set_at((x,y), color) -> None
        sets the color of point'''
        pygame.Surface.set_at(self, self.point(point), color)

    def center_at(self, pos):
        '''Camera.center_at((x,y)) -> None
        centers the screen at pos'''
        self.set_view((pos[0] - self.get_width()/2, pos[1] - self.get_height()/2))

    def blit(self, source, dest, area=None, special_flags=0):
        '''Camera.blit(*args) -> Rect
        draws one image onto another'''
        return pygame.Surface.blit(self, source, self.point(dest), area, special_flags)

    ### METHODS TO DRAW SHAPES WITH ###

    def line(self, color, start_pos, end_pos, width=1):
        '''Camera.draw_line(Color, (x,y), (x,y), int) -> Rect
        draws a line from pygame.draw'''
        return pygame.draw.line(self, color, self.point(start_pos), self.point(end_pos), width)

    def rect(self, color, rect, *args, **kwargs):
        '''Camera.rect(color, rect, *args, **kwargs) -> Rect
        draws a rectangle from pygame.draw'''
        pos = self.point(rect)
        return pygame.draw.rect(self, color, (pos[0], pos[1], rect[2], rect[3]), *args, **kwargs)

    def circle(self, color, center, radius, *args, **kwargs):
        '''Camera.circle(color, (x,y), int, *args, **kwargs) -> Rect
        draws a circle from pygame.circle'''
        return pygame.draw.circle(self, color, center, radius, *args, **kwargs)
        
class Sprite(pygame.sprite.Sprite):
    '''sprite object to inherit from'''

    def __init__(self, game, surface, onsurface=None, *groups):
        '''Sprite(game, surface, onsurface, *groups) -> Sprite
        constructs an object'''
        pygame.sprite.Sprite.__init__(self, *groups)
        self.untiltedImg = surface
        self.tiltedImg = surface
        self.image = surface
        self.position = (0,0)
        self.head = 0
        self.game = game
        self.slideClock = Clock()
        self.slideDistance = 0
        self.sliding = False
        self.rect = self.image.get_rect()
        self.imageTurning = True
        self.onsurface = onsurface

    def get_rect(self):
        '''Sprite.get_rect() -> pygame.Rect
        returns the rect object for sprite'''
        return self.rect

    def set_image_turning(self, boolean=None):
        '''Sprite.set_image_turning(bool) -> None
        disables image turning. if boolean not given, toggles image turning'''
        if isinstance(boolean, bool):
            self.imageTurning = boolean
        else:
            self.imageTurning = not self.imageTurning

    def surface(self, surface=None):
        '''Sprite.surface(surface) -> Surface
        sets the new image of the sprite and heading is set to 0
        if surface not given, returns image'''
        if surface == None:
            return self.image
        
        self.heading(0)
        self.untiltedImg = surface
        self.tiltedImg = surface
        self.image = surface

    def heading(self, heading=None):
        '''Sprite.get_heading(heading) -> int
        returns the heading of the object if heading not given
        otherwise sets heading'''
        if heading == None:
            return math.degrees(self.head)
        if self.imageTurning:
            self.image = pygame.transform.rotozoom(self.tiltedImg, heading, 1)
        self.head = math.radians(heading)
        self.rect = self.image.get_rect()
        self.pos(self.pos())
        self.stop_time()

    def tilt(self, heading):
        '''Sprite.tilt(heading) -> None
        tilts the image so that heading for image is 0 for sprite'''
        self.tiltedImg = pygame.transform.rotozoom(self.untiltedImg, heading, 1)
        self.heading(self.heading())

    def towards(self, pos):
        '''Sprite.towards(pos) -> float
        returns the heading towards pos'''
        if pos == self.pos(): return self.heading()
        x, y = pos[0]-self.pos()[0], self.pos()[1]-pos[1]

        # cases
        if x == 0:
            if y >= 0: return 90
            else: return 270
                
        elif y == 0:
            if x >= 0: return 0
            else: return 180

        heading = math.degrees(math.atan(y/x))
        if (x < 0 and y > 0) or (x < 0 and y < 0):
            heading += 180
        return heading

    def distance(self, pos):
        '''Sprite.distance((x,y)) -> float
        returns the distance from pos to sprite'''
        return math.sqrt((self.xcor() - pos[0])**2 + (self.ycor() - pos[1])**2)

    def in_dir(self, heading, distance, rel=True):
        '''Sprite.in_dir(int, int, bool) -> (x,y)
        returns the point in distance from direction (heading)
        if rel, heading is relative to the sprite's heading'''
        if rel: heading = self.heading() + heading
        return self.xcor() + distance*math.cos(math.radians(heading)), \
            self.ycor() - distance*math.sin(math.radians(heading))

    def line(self):
        '''Sprite.slope() -> (slope, yintercept)
        returns line from pos going out with heading
        if slope is undefined, it is treated as None'''
        if self.heading() == 90 or self.heading() == 270:
            return

        # calculate slope
        point = self.in_front()
        x,y = point[0]-self.pos()[0], self.pos()[1]-point[1]

        if x == 0:
            return None
        
        slope = y/x
        yinter = -self.pos()[0]*slope

        return slope, yinter
    
    def pos(self, pos=None):
        '''Sprite.pos(pos) -> int
        returns the position of the object if pos not given
        otherwise sets pos'''
        if pos == None:
            return round(self.position[0]), round(self.position[1])

        self.rect = pygame.Rect(pos[0]-self.rect.width/2, pos[1]-self.rect.height/2,
            self.rect.width, self.rect.height)
        self.rect.normalize()
        self.position = pos
        self.stop_time()

    def xcor(self, xcor=None):
        '''Sprite.xcor(xcor) -> int
        returns the xcoord of object if xcor not given
        otherwises sets xcoord'''
        if xcor == None:
            return self.pos()[0]
        self.pos((xcor, self.ycor()))

    def ycor(self, ycor=None):
        '''Sprite.ycor(ycor) -> int
        returns the ycoord of object if ycor not given
        otherwises sets ycoord'''
        if ycor == None:
            return self.pos()[1]
        self.pos((self.xcor(), ycor))

    def in_front(self, distance=1):
        '''Sprite.in_front(distance=1) -> None
        returns the point in front of sprite by distance'''
        return self.pos()[0]+distance*math.cos(self.head), \
            self.pos()[1]-distance*math.sin(self.head)

    def forward(self, distance):
        '''Sprite.forward(distance) -> None
        moves the object forward by distance'''
        self.pos((self.position[0]+distance*math.cos(self.head), self.position[1]-distance*math.sin(self.head)))

    def forward_time(self, distance, time):
        '''Sprite.forward_time(distance, time) -> None
        moves the object forward distance in time (seconds)
        movement will stop on change of position or heading'''
        if time <= 0:
            raise GameSetupError("Time for sprite movement must be positive.")
        
        self.sliding = True
        self.slideStart = self.pos()
        self.slideDistance = distance
        self.slideClock.reset()
        self.slideClock.set_max(time)
        self.slideClock.start()

    def update(self):
        '''Sprite.update() -> None
        keeps updating the sprite'''
        # update if moving with time
        if self.sliding:
            distance = self.slideDistance*self.slideClock.get_time()/self.slideClock.get_max()
            self.position = (self.slideStart[0]+distance*math.cos(math.radians(self.heading())),
                self.slideStart[1]-distance*math.sin(math.radians(self.heading())))
            
        self.game.blit(self.image, self.position, True, True, self.onsurface)

    def stop_time(self):
        '''Sprite.stop_time() -> None
        stops sprite's movement with time'''
        self.sliding = False
        
class Widget(dict):
    '''represents a widget for in-module objects'''

    def __init__(self, game, rect=(0,0,0,0), defaults={}, **attributes):
        '''Widget(game, rect, defaults, **attributes) -> Widget
        constructs the widget
        rect is pygame.Rect, defaults is dict'''
        dict.__init__(self, defaults)
        for arg in attributes:
            if arg not in defaults:
                raise GameSetupError(arg+" not in widget attributes. Must be in\n"+str(defaults))
            self[arg] = attributes[arg]

        self.id = len(game.get_widgets())
        self.rect = rect
        game.add_widget(self, self.id)
        self.game = game
        self.events = {}

    def __eq__(self, other):
        '''Widget == other -> bool
        returns if self is other'''
        return isinstance(other, Widget) and other.id == self.id

    def __str__(self):
        '''str(Widget) -> str
        converts widget to str'''
        return f"<Widget -ID: {self.id} -Rect: {self.rect} -Events: {self.events}>"

    def get_clear_ID(self):
        '''Widget.ID() -> str
        returns a clear event ID'''
        i = 0
        while True:
            ID = f"generated_event_id_{i}"
            if ID not in self.events:
                return ID
            i += 1
            
    def is_over(self, pos):
        '''Widget.is_over(pos) -> bool
        returns if pos is over widget'''
        return self.rect[0] < pos[0] < self.rect[0]+self.rect[2] and \
            self.rect[1] < pos[1] < self.rect[1]+self.rect[3]

    def is_event(self, eventId):
        '''Widget.is_event(eventId) -> bool
        returns whether eventId is attached to an event'''
        return eventId in self.events

    def get_rect(self):
        '''Widget.get_rect() -> tuple
        returns the rectangle of the widget'''
        return self.rect

    def set_rect(self, newRect):
        '''Widget.set_rect(newRect) -> None
        setter for rect attribute'''
        self.rect = newRect

    def get_id(self):
        '''Widget.get_id() -> float
        returns the widgets ID'''
        return self.id

    def configure(self, key, value):
        '''Widget.configure(key, value) -> None
        changes attribute key to value'''
        if key in self:
            self[key] = value

    def move(self, pos, center=True):
        '''Widget.move(pos, center=True) -> None
        moves the widget to pos (centered if center is True)'''
        if center: pos = pos[0]-self.rect[2]/2, pos[1]-self.rect[3]/2
        self.rect = pos[0], pos[1], self.rect[2], self.rect[3]

    def set_focus_var(self, boolean):
        '''Widget.set_focus_var(boolean) -> None
        simple setter for self.focus attribute'''
        self.focus = boolean

    def focus(self, focus=None):
        '''Widget.focus(focus) -> None/bool
        if focus specified, sets focus. otherwise returns focus'''
        if focus == None:
            return self.game.focus() == self
        if focus == False:
            self.game.focus(False)
        else:
            self.game.focus(self)

    def event(self, event):
        '''Widget.event(event) -> None
        filler for method to checks an event'''
        pass

    def process_event(self, event):
        '''Widget.process_event(event) -> None
        processes an event for bindings'''
        perform = []
        for eventID in self.events:
            eventInfo = self.events[eventID]
            
            # on click and on release
            if ((eventInfo[0] == "onclick" and event.type == pygame.MOUSEBUTTONDOWN and event.button == eventInfo[2]) or \
               (eventInfo[0] == "onrelease" and event.type == pygame.MOUSEBUTTONUP and event.button == eventInfo[2])) and \
               self.is_over(event.pos):
                perform.append(eventInfo[1])

            # on key and on key release
            elif (eventInfo[0] == "onkey" and event.type == pygame.KEYDOWN and event.key == eventInfo[2]) or \
                (eventInfo[0] == "onkeyrelease" and event.type == pygame.KEYUP and event.key == eventInfo[2]):
                perform.append(eventInfo[1])

            # on key press
            elif eventInfo[0] == "onkeypress" and pygame.key.get_pressed()[eventInfo[2]] == 1:
                perform.append(eventInfo[1])

        for method in perform:
            try:
                method(event)
            except TypeError:
                method()

        self.event(event)

    def onclick(self, eventId, command=None, num=1):
        '''Widget.onclick(eventId, command=None, num=None) -> None
        sets up an event using eventId. If command=None, removes exisiting event
        eventId is any str or int, num is the mouse button number (1,2, or 3)
        auto generates ID if eventId is None
        ---
        onclick will call command when the mouse button is clicked'''
        if command == None:
            self.remove_event(eventId)
        if eventId== None:
            eventId = self.get_clear_ID()
        self.events[eventId] = ("onclick", command, num)

    def onrelease(self, eventId, command=None, num=1):
        '''Widget.onrelease(eventId, command=None, num=1) -> ID
        sets up an event using eventId. If command=None, removes exsiting event
        eventId is any str or int, num is the mouse button number (1,2, or 3)
        auto generates ID if eventId is None
        ---
        onrelease will call command when the mouse button is released'''
        if command == None:
            self.remove_event(eventId)
        if eventId == None:
            eventId = self.get_clear_ID()
        self.events[eventId] = ("onrelease", command, num)
        return eventId

    def onkey(self, eventId, command=None, key=None):
        '''Widget.onkey(eventId, command=None, key=None) -> None
        sets up an event with eventId. If command=None, removes exsisting event
        key is the key number, eventId is any str or int
        auto generates ID if eventId is None
        ---
        onkey will call command everytime key is pressed down'''
        if command == None:
            self.remove_event(eventId)
        if eventId == None:
            eventId = self.get_clear_ID()
        self.events[eventId] = ("onkey", command, key)
        return eventId

    def onkeyrelease(self, eventId, command=None, key=None):
        '''Widget.onkeyrelease(eventId, command=None, key=None) -> None
        sets up an event with eventId. If command=None, removes exsisting event
        key is the key number, eventId is any str or int
        auto generates ID if eventId is None
        ---
        onkeyrelease will call command everytime key is released'''
        if command == None:
            self.remove_event(eventId)
        if eventId == None:
            eventId = self.get_clear_ID()
        self.events[eventId] = ("onkeyrelease", command, key)
        return eventId

    def onkeypress(self, eventId, command=None, key=None):
        '''Widget.onkeypress(eventId, command=None, key=None) -> None
        sets up an event with eventId. If command=None, removes exsisting event
        key is the key number, eventId is any str or int
        auto generates ID if eventId is None
        ---
        onkeypress will call command every 50 milliseconds if key is pressed'''
        if command == None:
            self.remove_event(eventId)
        if eventId == None:
            eventId = self.get_clear_ID()
        self.events[eventId] = ("onkeypress", command, key)
        return eventId

    def remove_event(self, eventId):
        '''Widget.remove_event(eventId) -> None
        deactivates the event connected to eventId'''
        if eventId in self.events:
            self.events.pop(eventId)        

class TabBar(Widget):
    '''represents the tab bar for switching pages'''

    def __init__(self, game, **attributes):
        '''TabBar(game, attribtues) -> TabBar
        sets up a tabbar for game

        attributes are:
         left=0: the number of pixels to the left of the tabbar to edge
         top=0: the number of pixels on top of the tabbar to edge
         leftPage=0: the number of pixels to the left of the pages to edge
         topPage=1: the number of pixels on the top of the pages to tabbar
         tab=(200,200,200): color of tab image for buttons
         current=(150,150,150): color for current tab
         disable=(170,170,170): image for disabled tabs
         font=("Arial", 12): font for the tab text
         color=(0,0,0): color of text
         marginsize=5: margin on the side of the text
         margintop=2: margin on the top and bottom of the text
         gap=1: gap between tabs

        Note: changing font is not yet supported

        to add a tab use TabBar.add_tab(text, surface, disabled)
        if will create a tab on the end of all other tabs
        that will open surface when clicked
        alternatively, you can do TabBar + (text, surface, disabled)

        to access tab use TabBar.get(index)
        index starts from 0 and progresses from left to right
        will return (text, surface, disabled, Button)
        final element is the button object for tab

        to edit a tab use Tabar.set(index, text=None, surface=None, disabled=False)
        this will change tab at index. if parameter is None,
        that parameter is not changed doesn't change for button

        to display tabs, you must do TabBar.update() in your game's update method'''
        defaults = {
            "left":0, "top":0, "leftPage":0, "topPage":1,
            "tab":(220,220,220), "current":(150,150,150), "disable":(120,120,120),
            "font":("Arial",20), "color":(0,0,0), "marginside":5, "margintop":2, "gap":1}

        Widget.__init__(self, game, (0,0,0), defaults, **attributes)
        self.game = game
        self.tabs = []
        self.current = None
        self.numTabs = 0
        self["font"] = pygame.font.SysFont(*self["font"])

    def __len__(self):
        '''len(TabBar) -> int
        returns the number of tabs in tabbar'''
        return self.numTabs

    def __add__(self, tab):
        '''TabBar+(text, surface, disabled=False) -> Button
        adds a tab to the tabbar
        text is text displayed, surface is surface opened onclick'''
        self.add_tab(*tuple(tab))
        return self

    def is_open(self, index):
        '''TabBar.is_open(index) -> bool
        returns if index is the tab open'''
        return index == self.current[0]
    
    def get(self, index):
        '''TabBar.get(index) -> [text, surface, disabled, Button]
        gets the tab at index. indexes start at 0 and progress from left to right'''
        return self.tabs[index]

    def set(self, index, text=None, surface=None, disabled=None):
        '''TabBar.set(index, text=None, surface=None, disabled=None) -> None
        configures the parameters of tab at index. if parameter is None, it stays as it was'''
        self.tabs[index][-1].set(text, disabled)
            
        # update lists
        if text != None:
            last = self.tabs[0][-1]
            for i in range(1,len(self)):
                self.tabs[i][-1].set_pos(last.get_next_pos())
                last = self.tabs[i][-1]
            self.get(index)[0] = text
                
        if surface != None:
            self.get(index)[1] = surface
            if self.is_open(index):
                self.current[1] = surface
            
        if disabled != None:
            self.get(index)[2] = disabled

    def switch(self, index):
        '''TabBar.switch(index) -> Surface
        switches to surface at index and returns it'''
        last = self.current
        new = self.get(index)
        self.current = [index, self.tabs[index][1]]

        # update button shapes
        if last != None:
            self.get(last[0])[-1].set(self.get(last[0])[0])
        new[-1].set(new[0])

    def add_tab(self, text, surface, disabled=False):
        '''TabBar.add_tab(text, surface, disabled=False) -> Button
        sets up tab for tabbar
        text is text displayed, surface is surface opened onclick'''
        # create tab button
        nextPos = (self["left"], self["top"])
        if len(self) >= 1:
            nextPos = self.tabs[-1][-1].get_next_pos()
        self.tabs.append([text, surface, disabled, _Tab(self.game, text, nextPos, self)])
        self.numTabs += 1

    def update(self):
        '''TabBar.update() -> None
        updates the tabbar'''
        if len(self.tabs) == 0: return
        for tab in self.tabs: tab[-1].update()
        if self.current == None: return

        # update current page
        pos = self["leftPage"], self["top"] + self["topPage"] + self.tabs[0][-1].get_rect()[3]
        self.game.blit(self.current[1], pos)
    
class Button(Widget):
    '''represents a button to click
   inherits from Widget'''

    def __init__(self, game, img, **attributes):
        '''Button(game, img, **attribtues) -> Button
        constructs a button using for game using attributes

        if img not a surface, img should be (width, height)

        attributes to use:
         pos: sets the position of the button
         command: the function/method called on click
         hover: surface of button on hover
         click: surface of button on click
         disable: surface of button when disabled
         disabled: boolean if disabled
         center: boolean if button is centered at pos'''
        defaults = {
          "pos":(0,0), "command":None, "hover":None,
          "click":None, "disable":None, "disabled":False,
          "center":True }

        if isinstance(img, pygame.Surface):
            rect = img.get_rect()
        else:
            rect = (0,0,img[0],img[1])
            
        Widget.__init__(self, game, rect, defaults, **attributes)
        self.move(self["pos"], self["center"])
        self.img = img
        
        # bindings
        self.clicked = False
        self.onclick(None, self.perform)
        self.onrelease(None, self.perform)

    def set_disabled(self, boolean):
        '''Button.set_disabled(boolean) -> None
        sets whether the button is disabled'''
        self["disabled"] = boolean

    def set_img(self, newImg):
        '''Button.get_img(newImg) -> None
        setter for main button image'''
        self.img = newImg
        self.set_pos(self["pos"])

    def set_pos(self, pos):
        '''Button.set_pos(pos) -> None
        sets the position of the button'''
        if isinstance(self.img, pygame.Surface):
            self.set_rect(self.img.get_rect())
            self.move(pos, self["center"])
        else:
            self.set_rect((pos[0], pos[1], self.img[0], self.img[1]))
        self["pos"] = pos
        
    def perform(self, event):
        '''Button.perform(event) -> None
        performs the command'''
        if event.type == pygame.MOUSEBUTTONUP:
            if self["command"] != None and not self["disabled"] and self.clicked:
                self["command"]()
            self.clicked = False
        elif not self.clicked:
            self.clicked = True
        
    def update(self):
        '''Button.update() -> None
        updates the button'''
        img = None
        
        # disabled img
        if self["disabled"]:
            if self["disable"] != None:
                img = self["disable"]
                
        # click img
        elif self.clicked and self["click"] != None:
            if not self.is_over(pygame.mouse.get_pos()):
                self.clicked = False
            else:
                img = self["click"]
                
        # hover img
        elif self.is_over(pygame.mouse.get_pos()) and self["hover"] != None:
            img = self["hover"]

        if img == None:
            img = self.img

        if isinstance(img, pygame.Surface):
            self.set_rect(img.get_rect())
            self.move(self["pos"], self["center"])
            self.game.blit(img, self["pos"], self["center"], self["center"])
        else:
            self.set_rect((self["pos"][0], self["pos"][1], self.img[0], self.img[1]))

class _Tab(Button):
    '''represents a tab button'''

    def __init__(self, game, text, pos, tabbar):
        '''_Tab(game, tabbar) -> _Tab
        constructs a tab for tabbar'''
        self.tabbar = tabbar
        self.game = game
        self.btnImg = self.btn_surface(text, tabbar["tab"])
        self.currentImg = self.btn_surface(text, tabbar["current"])
        self.disableImg = self.btn_surface(text, tabbar["disable"])

        self.index = len(tabbar)
        Button.__init__(self, game, self.btnImg, disable=self.disableImg,
            command=lambda: tabbar.switch(self.index), center=False, pos=pos)\

    def __str__(self):
        '''str(_Tab) -> str
        converts tab to str'''
        return str(self.index)

    def get_next_pos(self):
        '''_Tab.get_next_pos() -> (x,y)
        returns the position of the next tab'''
        return self["pos"][0]+self.get_rect()[2]+self.tabbar["gap"], self["pos"][1]
        
    def btn_surface(self, text, color):
        '''_Tab.btn_surface(text, color) -> pygame.Surface
        returns the surface for button with text'''
        text = self.tabbar["font"].render(text, True, self.tabbar["color"])

        # width and height of surface
        width = text.get_rect().width+self.tabbar["marginside"]*2
        height = text.get_rect().height+self.tabbar["margintop"]*2
        if isinstance(color, pygame.Surface):
            if width < color.get_rect().width:
                width = color.get_rect().width
            if height < color.get_rect().height:
                height = color.get_rect().height
            
        # create surface
        surface = pygame.Surface((width, height))
        if isinstance(color, pygame.Surface):
            self.game.blit(color, (width/2, height/2), True, True, surface)
        else:
            surface.fill(color)
        self.game.blit(text, (width/2, height/2), True, True, surface)
        
        return surface

    def set(self, text=None, disabled=None):
        '''_Tab.set(text=None, disabled=None) -> None
        sets button to text'''
        if text != None:
            self.btnImg = self.btn_surface(text, self.tabbar["tab"])
            self.currentImg = self.btn_surface(text, self.tabbar["current"])
            self.disableImg = self.btn_surface(text, self.tabbar["disable"])

            # set button img to correct surface
            if self.tabbar.is_open(self.index):
                self.set_img(self.currentImg)
            else:
                self.set_img(self.btnImg)
            self["disable"] = self.disableImg
            
        if disabled != None:
            self.set_disabled(disabled)

class Popup(Widget):
    '''represents a popup widget'''

    def __init__(self, game, img):
        '''Popup(game, img) -> Popup
        sets up a popup for game

        call Popup.add_button(rect, command) to set up buttons
        call Popup.update() to update the popup on the screen'''
        Widget.__init__(self, game, img.get_rect())
        self.game = game
        self.img = img
        self.buttons = []
        self.isopen = False
        self.width, self.height = pygame.display.get_window_size()

    def is_open(self):
        '''Popup.is_open() -> bool
        returns if the popup is open or not'''
        return self.isopen

    def get_buttons(self):
        '''Popup.get_buttons() -> list
        returns a list of all buttons'''
        return self.buttons
        
    def add_button(self, rect, command):
        '''Popup.add_button(rect, command) -> Button
        creates and returns the button at rect
        treat the top-left corner of the popup as (0,0)'''
        button = Button(self.game, (rect[2], rect[3]), pos=(rect[0]+self.width/2-self.img.get_rect()[2]/2,
            rect[1]+self.height/2-self.img.get_rect()[3]/2), command=lambda: self.command(command))
        self.buttons.append(button)
        return button

    def command(self, command):
        '''Popup.command(command) -> Button
        performs command if popup is open'''
        if self.isopen: command()

    def open(self):
        '''Popup.open() -> None
        opens the popup'''
        self.isopen = True

    def close(self):
        '''Popup.close() -> None
        closes the popup'''
        self.isopen = False

    def toggle(self):
        '''Popup.toggle() -> None
        if popup is open, closes popup, else opens popup'''
        self.isopen = not self.isopen

    def update(self):
        '''Popup.update() -> None
        updates the popup on the screen'''
        if not self.isopen: return
        self.game.blit(self.img, (self.width/2, self.height/2), True, True)

        for button in self.buttons:
            button.update()

class _AfterEvent:
    '''private class for after events'''

    def __init__(self, game, eventList, ms, command):
        '''_AfterEvent(Game, eventList, ms, command) -> _AfterEvent
        constructs the event object for after'''
        self.ms = ms
        self.command = command
        self.clock = Clock(game=game)
        self.clock.start()
        self.eventList = eventList
        self.eventList.append(self)
        self.completed = False

    def check(self):
        '''_AfterEvent.check() -> None
        checks if the event is ready'''
        if self.clock.get_time() > self.ms/1000 and not self.completed:
            self.command()
            self.eventList.remove(self)
            self.completed = True

class Sound(pygame.mixer.Sound):
    '''represents a sound object to be played, muted, unmuted'''

    def __init__(self, game, file):
        '''Sound(game, file) -> Sound
        constructs the sound'''
        pygame.mixer.Sound.__init__(self, file)
        self.game = game
        self.unmute()
        if game.is_muted(): self.mute()

    def set_volume(self, newVolume):
        '''Sound.set_volume(newVolume) -> None
        sets the background volume'''
        self.originVolume = newVolume
        if not self.game.is_muted(): self.unmute()

    def mute(self):
        '''Sound.mute() -> None
        mutes the sound'''
        pygame.mixer.Sound.set_volume(self, 0)

    def unmute(self):
        '''Sound.unmute() -> None
        unmutes the sound'''
        pygame.mixer.Sound.set_volume(self, self.originVolume)
        
class Game:
    '''represents the game object
    intended to be inherited from. includes methods like after
    you must include an update method and your display
    you must call Game.mainloop() to start your game
    your Game.update() method will be called every iteration of mainloop'''

    def __init__(self):
        '''Game() -> Game
        constructs the game'''
        self.restarting = False
        self.isGameRunning = True
        self._AfterEvents = []
        self.soundsList = []
        self.isGameMuted = False
        self.screen = None
        self.widgets = {}
        self.gameFocusedWidget = None
        self.bindings = {}
        self.gameClocks = []

    def focus(self, focus=None):
        '''Game.focus(focus=None) -> type
        if focus is specified, sets widget supplied to focus
        Otherwise returns the current widget in focus
        if focus is False, removes all focus'''
        if focus == None:
            return self.gameFocusedWidget
        elif not focus:
            self.gameFocusedWidget = None
        elif not isinstance(focus, Widget):
            raise GameSetupError("Cannot set focus to a non-widget.")

        self.gameFocusedWidget = focus

    def get_screen(self):
        '''Game.get_screen() -> type
        returns the game screen'''
        return self.screen

    def is_muted(self):
        '''Game.is_muted() -> bool
        returns whether the game is muted or not'''
        return self.isGameMuted

    def get_widgets(self):
        '''Game.get_widgets() -> dict
        returns all widgets'''
        return self.widgets

    def get_widget(self, widgetID):
        '''Game.get_widget(widgetID) -> Widget
        returns the widget connected to ID'
        returns None if not found'''
        if widgetID in self.widgets:
            return self.widgets[widgetID]

    def add_widget(self, widget, widgetID):
        '''Game.add_widget() -> None
        adds widget to game'''
        self.widgets[widgetID] = widget

    def after(self, ms, command):
        '''Game.after(ms, command) -> time
        performs command after ms milliseconds'''
        self._AfterEvents.append(_AfterEvent(self, self._AfterEvents, ms, command))

    def sound(self, file, volume=1):
        '''Game.sound(file, volume=1) -> Sound
        sets up and then returns a sound object'''
        newSound = Sound(self, file)
        newSound.set_volume(volume)
        self.soundsList.append(newSound)
        return newSound

    def mute(self):
        '''Game.mute() -> None
        mutes all sounds'''
        for sound in self.soundsList:
            sound.mute()
        self.isGameMuted = True

    def unmute(self):
        '''Game.unmute() -> None
        unmutes all sounds'''
        for sound in self.soundsList:
            sound.unmute()
        self.isGameMuted = False
    
    def register_clock(self, clock):
        '''Game.register_clock(Clock) -> None
        registers a clock for the main pause'''
        self.gameClocks.append(clock)

    def pause_all_clocks(self):
        '''Game.pause_all_clocks() -> None
        pauses all registered clocks'''
        for clock in self.gameClocks: clock.stop()

    def play_all_clocks(self):
        '''Game.play_all_clocks() -> None
        plays all registered clocks'''
        for clock in self.gameClocks: clock.start()
        
    def restart(self):
        '''Game.restart() -> None
        completely restarts the game
        restarts pygame as well'''
        self.isGameRunning = False
        self.restarting = True

    def close(self):
        '''Game.close() -> None
        closes the game window'''
        self.isGameRunning = False

    def update(self):
        '''Game.update() -> None
        place holder. This method is meant to be overridden
        don't forget to update your display!'''
        pass

    def event(self, event):
        '''Game.event(event) -> None
        checks up an event. This method is meant to be overridden'''
        pass

    def blit(self, surface, pos, centerx=False, centery=False, onsurface=None):
        '''Game.blit(surface, pos, centerx=False, centery=False, onsurface=None) -> None
        blits surface on onsurface at pos'''
        if onsurface == None:
            onsurface = self.screen
            
        if centerx:
            pos = pos[0]-surface.get_rect().width/2, pos[1]
        if centery:
            pos = pos[0], pos[1]-surface.get_rect().height/2
            
        onsurface.blit(surface, pos)

    def bind(self, eventType, command, ID=None):
        '''Game.bind(ID, eventType, command) -> None
        binds eventType to command and returns ID
        if ID not given, ID will be automatically a non-used ID'''
        if ID == None:
            ID = self.get_clear_id()
        self.bindings[ID] = (eventType, command)
        return ID

    def unbind(self, ID=None):
        '''Game.unbind(eventType) -> None
        unbinds event from ID
        if ID not given, unbinds all'''
        if eventType == None:
            self.bindings.clear()
        if eventType in self.bindings:
            self.bindings.pop(ID)

    def get_clear_id(self):
        '''Game.get_clear_id() -> str
        returns an id that is not bound'''
        i = 0
        while True:
            ID = f"generated_event_id_{i}"
            if ID not in self.bindings:
                return ID
            i += 1
            
    def mainloop(self):
        '''Game.mainloop() -> None
        starts the mainloop for the game'''
        while self.isGameRunning:
            # check all after events
            for event in self._AfterEvents[:]:
                event.check()

            # other events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()

                # process event in widgets
                for widget in self.widgets:
                    self.widgets[widget].process_event(event)

                # process event for bindings
                for binding in self.bindings:
                    if event.type == self.bindings[binding][0]:
                        try:
                            self.bindings[binding][1](event)
                        except TypeError:
                            self.bindings[binding][1]()
                    
                self.event(event)

            self.update()

        # quit or restart
        pygame.quit()
        if self.restarting:
            pygame.init()
            self.__init__()

def distance(p1, p2):
    '''distance((x,y), (x,y)) -> float
    returns the distance between p1 and p2'''
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def remove_bg(surface):
    '''remove_bg(pygame.Surface) -> pygame.Surface
    removes the background from surface and returns it'''
    if isinstance(surface, str): surface = pygame.image.load(surface)
    surface = surface.convert_alpha()
    color = surface.get_at((0,0))
    rect = surface.get_rect()
    for x in range(rect[2]):
        for y in range(rect[3]):
            if surface.get_at((x,y)) == color:
                surface.set_at((x,y), (0,0,0,0))
    return surface

def change_colors(surface, *colors):
    '''change_colors(pygame.Surface, old_color, new_color, old_color, ect) -> pygame.Surface
    changes the colors in surface and returns the result'''
    if isinstance(surface, str): surface = pygame.image.load(surface)
    surface = surface.convert_alpha()
    rect = surface.get_rect()
    for x in range(rect[2]):
        for y in range(rect[3]):
            color = surface.get_at((x,y))
            if color in colors and colors.index(color) % 2 == 0:
                surface.set_at((x,y), colors[colors.index(color) + 1])
    return surface

def set_alpha(surface, alpha):
    '''set_alpha(pygame.Surface, int) -> pygame.Surface
    sets the alpha value of the color and returns the surface'''
    if isinstance(surface, str): surface = pygame.image.load(surface)
    surface = surface.convert_alpha()
    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            color = list(surface.get_at((x,y)))
            if color[3] != 0: surface.set_at((x,y), color[:3] + [alpha])
    return surface

def towards(p1, p2):
    '''towards((x,y), (x,y)) -> float
    returns the angle from p1 to p2'''
    if p1 == p2: return 0
    x,y = p2[0]-p1[0], p1[1]-p2[1]

    # special cases
    if x == 0:
        if y >= 0: return 90
        else: return 270
                
    elif y == 0:
        if x >= 0: return 0
        else: return 180

    heading = math.degrees(math.atan(y/x))
    if (x < 0 and y > 0) or (x < 0 and y < 0):
        heading += 180
    return heading

def in_dir(p1, heading, distance):
    '''in_dir((x,y), float, float) -> (x,y)
    returns the point that is distance in front of given point in heading'''
    return p1[0] + distance*math.cos(math.radians(heading)), p1[1] - distance*math.sin(math.radians(heading))

def blit(onsurface, surface, pos, center_x=False, center_y=False):
    '''blit(onsurface, surface, (x,y), bool, bool) -> Rect
    draws surface on onsurface at pos'''
    if centerx:
        pos = pos[0]-surface.get_rect().width/2, pos[1]
    if centery:
        pos = pos[0], pos[1]-surface.get_rect().height/2   
    onsurface.blit(surface, pos)

def rotate_point(angle, origin, point):
    '''rotate_point(angle, origin, point) -> (x,y)
    rotate_point(int, (x,y), (x,y)) -> (x,y)
    rotates point around origin by angle'''
    # store data
    x,y = point[0] - origin[0], point[1] - origin[1]
    matrix = (math.cos(math.radians(angle)), -math.sin(math.radians(angle))), \
        (math.sin(math.radians(angle)), math.cos(math.radians(angle)))

    # return output
    output = apply_matrix(matrix, (x,y))
    return output[0] + origin[0], output[1] + origin[1]

def rotate_points(angle, origin, *points):
    '''rotate_points(angle, origin, point, point, ...) -> ((x,y), (x,y), ...)
    rotate_points(int, (x,y), (x,y), (x,y), ...) -> ((x,y), (x,y), ...)
    rotates a set of points around origin by angle'''
    output = []
    for point in points:
        output.append(rotate_point(angle, origin, point))
    return tuple(output)

def dot(v1, v2):
    '''dot((int, int), (int, int)) -> (int, int)
    returns the dot product of the two vectors'''
    return v1[0]*v2[0] + v1[1]*v2[1]

def apply_matrix(matrix, vector):
    '''apply_matrix((int, int), ((int, int), (int, int))) -> (int, int)
    applies matrix to vector'''
    return dot(matrix[0], vector), dot(matrix[1], vector)

if __name__ == "__main__":
    print(rotate_points(-towards((0,0), (0,1)), (0,0), (0,0), (0,1)))
