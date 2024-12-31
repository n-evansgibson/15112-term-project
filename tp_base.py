from cmu_graphics import *
from PIL import Image
from types import SimpleNamespace
import math
import random
from tp_mapsFINAL import maps, mapInfo


# Line class: Each line represents a degree in the player's FOV. 
class Line:

    def __init__(self, height, x, soulVisible, color):
        self.height = height
        self.x = x
        self.soulful = soulVisible
        self.color = color
    
    def __repr__(self):
        return f'<Line of height {self.height} at position {self.x}>'
    
    def __eq__(self, other):
        return (isinstance(other, Line) and self.height == other.height
                and self.x == other.x)
    
    def flicker(self):
        self.color = 'black'
    
# Level class: Stores map, time alotted, start position, exit position, name for each level
# Logic: Every time that a new level is loaded, the current level increases by one. currLevel indexes into info and map

class Level:
    
    def __init__(self, name, number, timeAlotted, startX, startY, exitX, exitY):
        self.name = name
        self.number = number
        self.timeAlotted = timeAlotted
        self.startX, self.startY = startX, startY
        self.exitX, self.exitY = exitX, exitY

    def __repr__(self):
        return f'<Level {self.number}: {self.name}>'
    
    def __eq__(self, other):
        return (isinstance(other, Level) and self.name == other.name and self.number == other.number)
    

def onAppStart(app):
    initializeApp(app)

def initializeApp(app):
        # List of all map info
    app.allMaps = loadAllMaps(maps, mapInfo)

    # Time
    app.stepsPerSecond = 15

    # Controls
    app.startMode = True
    app.directionsMode = False
    app.gameMode = False
    app.death = False
    app.failed = False
    app.newLevel = True
    app.gameFinished = False

    app.paused = False
    app.strideTaken = False
    app.soulInView = False

    # Resets game
    resetGame(app)

    # Controls lives
    app.hearts = [CMUImage(Image.open('images/tp_oneheart.png')), CMUImage(Image.open('images/tp_twohearts.png')),
                  CMUImage(Image.open('images/tp_threehearts.png'))]
        # Source: https://pixabay.com/es/illustrations/pixel-coraz%C3%B3n-8bit-videojuego-5876981/
   
    # Starting screen
    app.startButtonColor = 'white'
    app.logo = CMUImage(Image.open('images/hindsight_logo.png'))
    app.eyes = [CMUImage(Image.open('images/tp.eye1.2.png')), CMUImage(Image.open('images/tp.eye2.2.png')),
                CMUImage(Image.open('images/tp.eye3.2.png'))]
    app.redEyes = [CMUImage(Image.open('images/tp.eyered1.2.png')), CMUImage(Image.open('images/tp.eyered2.2.png')),
                CMUImage(Image.open('images/tp.eyered3.2.png'))]
        # Source: I created these with Photoshop! And my camera! 

    app.currEyes = app.eyes
    app.eyeIndex = 0
    app.countingDir = +1

    # Sounds
    app.footstep = loadSound('sounds/footstep.mp3')
        # Source: https://pixabay.com/sound-effects/concrete-footsteps-2wav-14794/
    app.introMusic = loadSound('sounds/intro_music.mp3')
        # Source: https://pixabay.com/sound-effects/relaxing-guitar-loop-v5-245859/ 
    app.choirMusic = loadSound('sounds/choir_music.mp3')
        # Source: https://pixabay.com/sound-effects/creepy-female-choir-singing-amp-breathing-247697/
    app.bell = loadSound('sounds/tp_bell0.mp3')
        # Source: https://pixabay.com/sound-effects/copper-bell-ding-22-172687/
    app.frigginhurt = loadSound('sounds/tp_frigginhurt.mp3')
        # Source: https://pixabay.com/sound-effects/friggin-hurt-37029/
    app.clickNoise = loadSound('sounds/tp_click.mp3')
        # Source: https://pixabay.com/sound-effects/user-interface-click-234656/
    app.heartbeat = loadSound('sounds/tp_heartbeat.mp3')
        # Source: https://pixabay.com/sound-effects/heart-beat-137135/ 
    app.woosh = loadSound('sounds/tp_woosh.mp3')
        # Source: https://pixabay.com/sound-effects/short-woosh-109592/ 

     # Color palette
    app.wood = rgb(45, 8, 10)
    app.deep = rgb(19, 3, 3)
    app.tan = rgb(184, 150, 133)
    app.carmine =  rgb(153, 30, 32)

    # Other images
    app.playButton = CMUImage(Image.open('images/tp_playbutton.png'))
    app.pauseButton = CMUImage(Image.open('images/tp_pausebutton.png'))
        # Source: I created these with Photoshop!
    
    # Screens
    app.pauseScreen = CMUImage(Image.open('images/tp_pauseScreen.png'))
    app.failScreen = CMUImage(Image.open('images/tp_failscreen.png'))
        # Note: I used chatGPT to help me come up with the text for this screen!
    app.deathScreen = CMUImage(Image.open('images/tp_deathscreen.png'))
    app.deathScreenHeld = CMUImage(Image.open('images/tp_deathScreenHeld.png'))
    app.levelScreen = CMUImage(Image.open('images/tp_levelscreen.png'))
    app.levelScreenHeld = CMUImage(Image.open('images/tp_levelscreenHeld.png'))
    app.deathMessages = ["Well, that didn't work.", "Better luck next time.", "Snap out of it, thanks.",
                         "You are worthless.", "Do better.", "Ditto."]
    app.successScreen = CMUImage(Image.open('images/tp_successScreen.png'))
    app.creators1 = CMUImage(Image.open('images/tp_creatorsnote1.png'))
    app.creators2 = CMUImage(Image.open('images/tp_creatorsnote2.png'))
    app.directions1 = CMUImage(Image.open('images/tp_directions1.png'))
    app.directions2 = CMUImage(Image.open('images/tp_directions2.png'))

    # Screen sources: I modified these iamges within Photoshop to create my screens.
    # Arrow keys: https://www.nicepng.com/downpng/u2w7q8u2a9u2r5a9_l1-computer-arrows-keys-png/
    # Running man: https://purepng.com/photo/12829/people-running-man#google_vignette
    # Bell: https://pngimg.com/image/53581
    # Yellow orb: https://www.freeiconspng.com/images/orb-png 

    # More controls
    app.currPassScreen = app.levelScreen
    app.currDeathScreen = app.deathScreen
    app.currDirectionScreen = app.creators1

    # Spots 
    app.spots = []
    app.spotCount = 0
    app.spotImage = CMUImage(Image.open('images/tp_vloss1.png'))

# Turns each map and its info into a Level class
def loadAllMaps(maps, mapInfo):
    allMaps = []
    for index in range(len(maps)):
        name, number, timeAlotted, startX, startY, exitX, exitY = mapInfo[index]
        newLevel = Level(name, number, timeAlotted, startX, startY, exitX, exitY)
        allMaps.append(newLevel)
    return allMaps

def resetGame(app):
    # Map, position and movement for Level 1
    app.currentMap = 0
    app.rot = math.pi/4
    app.rotadjust = 0
    app.speed = 0.1

    # Controls lives
    app.lives = 3

    # Controls
    app.strideTaken = False
    app.death = False
    app.failed = False
    app.newLevel = True 
    app.paused = False
    
    #Load first map
    loadNewLevel(app, app.allMaps[app.currentMap])


def loadNewLevel(app, Level):

    # Sets new map, player position, and exit position
    app.map = maps[Level.number - 1]
    app.posx, app.posy = Level.startX, Level.startY
    app.exitX, app.exitY = Level.exitX, Level.exitY
    app.rot = math.pi/4

    # Resets time, counter, and spots
    app.time = Level.timeAlotted
    app.counter = 0
    app.paused = True
    app.spots = []

#Creates footstep sound effect
def onStep(app):
    # Locks screen dimensions
    if app.width != 400 or app.height != 400:
        app.width = app.height = 400
        app.frigginhurt.play()

    if app.startMode or (not app.paused and not app.failed): # Removed app.death and app.newLevel
        takeStep(app)

def takeStep(app):
    app.counter += 1

    if app.startMode: 
        # eye animation
        if app.counter % 5 == 0:
            app.eyeIndex += app.countingDir
            if app.eyeIndex == 0:
                app.countingDir = +1
            elif app.eyeIndex == 2:
                app.countingDir = -1

    if app.gameMode:
        # Game timer
        if app.counter % app.stepsPerSecond == 0:
            app.time -= 1
        
        #Checks for death
        if  not app.death and app.time < 0 and distance(app.posx, app.posy, app.exitX, app.exitY) > 1:
            # Subtract a life, show death message
            app.lives -= 1
            if app.lives == 0:
                app.failed = True
            else:
                # Show death screen
                app.death = True
                app.currMessage = random.randint(0, 6)
                app.paused = True
                app.heartbeat.pause()
    
                # Reload current level
                loadNewLevel(app, app.allMaps[app.currentMap])
            
        # Checks for completing level
        if distance(app.posx, app.posy, app.exitX, app.exitY) <= 1:
            # Load next level
            app.currentMap += 1
            app.paused = True
            app.heartbeat.pause()
            # Checks if all levels have been completed
            if app.currentMap > len(app.allMaps) - 1:
                app.gameFinished = True
            else:
                # Load and display next level screen
                app.newLevel = True
                app.woosh.play()
                loadNewLevel(app, app.allMaps[app.currentMap])


        # Footstep sound effect (needs to be fixed)
        if app.counter % 5 == 0 and app.strideTaken:
            app.footstep.play(restart = True)
            app.strideTaken = False

        # Sets volume of bell based on distance from exit
        originalX, originalY = app.allMaps[app.currentMap].startX, app.allMaps[app.currentMap].startY
        oldDistance = distance(originalX, originalY, app.exitX, app.exitY)
        newDistance = distance(app.posx, app.posy, app.exitY, app.exitY)
        volume = 1 - (newDistance/oldDistance)

        #Plays bell every six seconds
        if app.counter % 75 == 0 and volume > 0:
            app.bell.setVolume(volume)
            app.bell.play()

    
        #Draws spots
        if app.counter % 120 == 0 and len(app.spots) < 10:
            app.spotCount += 1
            randX = random.randint(0, 400)
            randY = random.randint(150, 400)
            newSpot = makeSpot(app, app.spotImage, randX, randY)
            app.spots.append(newSpot)
        # Makes spots grow
        if app.counter % 15 == 0:
            for spot in app.spots:
                spot.r += 5

def distance(x1, y1, x2, y2):
    return ((x2-x1)**2 + (y2-y1)**2)**0.5

# Spot growth

def loadSpots(app):
    app.spots = []
    app.spotCount = 0
    app.stepsPerSecond = 15
    app.steps = 0
    app.dotImage = CMUImage(Image.open('vlossimages/tp_vloss1.png'))

def makeSpot(app, image, x, y):
    spot = SimpleNamespace()
    spot.image = image
    spot.x = x
    spot.y = y
    spot.r = 15
    return spot


def findObject(app, angle, x, y):
    # Very important raycasting source: https://lodev.org/cgtutor/raycasting.html
    raySpeed = 0.05
    dx, dy = (raySpeed*math.cos(angle)), (raySpeed*math.sin(angle))
    distanceCounter = 0
    soulVisible = False

    while True: 
        x, y = (x + dx, y + dy)
        distanceCounter += 1

        # LINES 321-224: logic of finding height based on raycasting  video:
        # https://www.youtube.com/watch?v=5xyeWBxmqzc&list=PLlYT7ZZOcBNA1hVBjkKFMnW0YDDODdy40&index=2
        
        # If the exit can be seen before the wall, set boolean soulVisibile to true
        if app.map[int(x)][int(y)] == 3:
            soulVisible = True
        elif app.map[int(x)][int(y)] == 1:
            wallHeight = 1 
            height = wallHeight/(raySpeed * distanceCounter)
            break

    return height, soulVisible
        

def redrawAll(app):

    # Starting screen
    if app.startMode:
        drawRect(0, 0, app.width, app.height, fill = 'grey')
        drawImage(app.logo, 0, 0, width = app.width, height = app.height)
        drawImage(app.currEyes[app.eyeIndex], app.width/2, 3*app.height/4, width = 3*(app.width*1.5)/4, height = app.height*1.5, 
                  align = 'center')
        app.introMusic.play(loop = True)
    
    elif app.directionsMode:
        drawImage(app.currDirectionScreen, 0, 0, width = app.width, height = app.height)
    
    # Game screen: whenever the raycaster is being drawn. This includes when the raycaster is being paused, and between pass/fail screens
    elif app.gameMode:

        # Music
        app.choirMusic.play(loop = True)
        app.introMusic.pause()

        #Creates floor and ceiling
        drawRect(0, app.height/2, app.width, app.height/2, fill = 'grey')
        drawRect(0, 0, app.width, app.height/2, fill = 'black')

        # Creates a line representing distance from nearest way at each degree
        lineList = []
        soulInView = False

        for degree in range(70):
            angle = app.rot + math.radians(degree - 35)
            x, y = app.posx, app.posy
            height, soulVisible = findObject(app, angle, x, y)
            # Checks if soul is in front of wall at that specific line
            if soulVisible:
                soulInView = True
            # Adds line to list to be drawn
            newLine = Line(height, angle, soulVisible, app.wood)
            lineList.append(newLine)
        
        #Plays heartbeat based on distance if soul is visible
        if soulInView:
            app.heartbeat.play(loop = True)
            #Determines volume of heartbeat
            originalX, originalY = app.allMaps[app.currentMap].startX, app.allMaps[app.currentMap].startY
            oldDistance = distance(originalX, originalY, app.exitX, app.exitY)
            dist = distance(app.posx, app.posy, app.exitY, app.exitY)
            soulVolume = 1 - (dist/oldDistance)
            app.heartbeat.setVolume(soulVolume)
                
        # Scale taken from testing with Matplot
        scaleX = 350 
        scaleY = 130

        # Checks that x of last line is in bounds
        lastX = lineList[-1].x
        scaledLastX = float(lastX * scaleX) - 90
        shift = abs(scaledLastX - app.width)
        if scaledLastX > app.width: 
            shift *= -1

        #Plots each line in cmu graphics
        for line in lineList:
            # A lot of guesswork involved in scaling the lines :)
            scaledX = float(line.x * scaleX) - 90 + shift
            scaledY = float(line.height * scaleY)

            # Gives texture to walls
            if int(scaledX) % 5 == 0:
                line.color = app.deep
            
            # Draws lines, with top border
            drawLine(scaledX, app.height/2 + scaledY, scaledX, app.height/2 - scaledY,
                    lineWidth = 7, fill = line.color)
            drawLine(scaledX, app.height/2 - scaledY, scaledX, app.height/2 - scaledY - scaledY/10,
                     lineWidth = 7, fill = 'white')
        

        # Creates time and distance bars
        barHeight = app.height/32
        barWidth = app.width/3 - 10
        barX = 2*app.width/3
        # Finds ratio of current time to total time
        totalTime = app.allMaps[app.currentMap].timeAlotted
        timeWidth = (app.time/totalTime) * barWidth
        # Time bar
        if app.time > 0:
            drawRect(barX, app.height/32, timeWidth, barHeight, fill = app.carmine)
        drawRect(barX, app.height/32, barWidth, barHeight, fill = None, borderWidth = 2, border = 'white')
        # Distance bar
        originalX, originalY = app.allMaps[app.currentMap].startX, app.allMaps[app.currentMap].startY
        oldDistance = distance(originalX, originalY, app.exitX, app.exitY)
        newDistance = distance(app.posx, app.posy, app.exitX, app.exitY)
        proxWidth = barWidth - (newDistance/oldDistance) * barWidth
        if proxWidth > 0:
            drawRect(barX, 3*app.height/32, proxWidth, barHeight, fill = app.carmine)
        drawRect(barX, 3*app.height/32, barWidth, barHeight, fill = None, borderWidth = 2, border = 'white')
        # Labels time and distance bars
        drawLabel('time:', barX - 10, app.height/32, align = 'top-right', fill = app.carmine, size = 15, font = 'monospace',
                  bold = True)
        drawLabel('proximity:', barX - 10, 3*app.height/32, align = 'top-right', fill = app.carmine, size = 15, font = 'monospace',
                  bold = True)
        
        # Draws level label
        drawLabel(f'Level {app.currentMap + 1}', 10, barHeight, fill = app.carmine, font = 'monospace',
                  bold = True, size = 15, align = 'top-left')
        

        # Draws lives graphic
        heartIndex = app.lives - 1
        if heartIndex >= 0:
            drawImage(app.hearts[heartIndex], 45, 3*app.height/32 + 10, width = 150, height = 150, align = 'center')
        
        # Draws spots
        for spot in app.spots:
            drawImage(spot.image, spot.x, spot.y, width = spot.r, height = spot.r, align = 'center')

        # Draws play/pause button
        if app.paused:
            currButton = app.playButton
            drawImage(app.pauseScreen, 0, 0, width = 400, height = 400)
            
        else:
            currButton = app.pauseButton
        drawImage(currButton, app.width - 20, 5*app.height/32 + 20, width = 125, height = 125, align = 'center')

        # Pass and death screens

        if app.newLevel: 
            drawImage(app.currPassScreen, 0, 0, width = 400, height = 400)
            # Display info for the new level
            level = app.allMaps[app.currentMap]
            drawLabel(f'Level {level.number}', 200, 130, font = 'monospace', fill = 'white', size = 18, bold = True)
            drawLabel(level.name, 200, 180, font = 'monospace', fill = 'white', size = 14, bold = True)

        elif app.death:
            drawImage(app.currDeathScreen, 0, 0, width = 400, height = 400)
            # Display level and random death message
            level = app.allMaps[app.currentMap]
            drawLabel(f'Level {level.number}', 200, 130, font = 'monospace,', fill = 'white', size = 18, bold = True)
            drawLabel(app.deathMessages[app.currMessage], 200, 180, font = 'monospace', fill = 'white', size = 14, bold = True)

        if app.failed:
            # Display the failing screen, shame the user, then have a button to reset the entire game
            drawImage(app.failScreen, 0, 0, width = 400, height = 400)
        
        elif app.gameFinished:
            # Display the final message, then have a button to reset the entire game
            drawImage(app.successScreen, 0, 0, width = 400, height = 400)


# Hold up and down arrow keys to move forward and backwards
def onKeyHold(app, keys):
        if not app.paused and not app.failed:
            x, y = app.posx, app.posy

            # Changes walking speed
            if 'space' in keys:
                app.speed = 0.2
            else:
                app.speed = 0.1
            
            # Moving forward and backwards
            if 'up' in keys:
                #Lines 335 and 338: logic learned from raycaster tutorial video (see lines 218-219)
                x, y = (x + app.speed * math.cos(app.rot)), (y + app.speed * math.sin(app.rot))
                app.strideTaken = True
            elif 'down' in keys:
                x, y = (x - app.speed * math.cos(app.rot)), (y - app.speed * math.sin(app.rot))
                app.strideTaken = True
            else:
                app.strideTaken = False
            if app.map[int(x)][int(y)] == 0:
                app.posx, app.posy = x, y
            
            #Rotation
            if 'right' in keys:
                app.rot += math.pi/20
            elif 'left' in keys: 
                app.rot -= math.pi/20
        

def onMouseMove(app, mouseX, mouseY):
    # Highlights start button when mouse hovers over it
    if app.startMode:
        if mouseInEyeBox(app, mouseX, mouseY):
            app.currEyes = app.redEyes
        else:
            app.currEyes = app.eyes
    elif app.gameMode:
        # Highlights buttons of death and level screens when mouse hovers over
        if app.death:
            if mouseInPassBox(mouseX, mouseY):
                app.currDeathScreen = app.deathScreenHeld
            else:
                app.currDeathScreen = app.deathScreen
        elif app.newLevel:
            if mouseInPassBox(mouseX, mouseY):
                app.currPassScreen = app.levelScreenHeld
            else:
                app.currPassScreen = app.levelScreen

# Starts game
def onMousePress(app, mouseX, mouseY):
    app.clickNoise.play(restart = True)
    if app.startMode:
        if mouseInEyeBox(app, mouseX, mouseY):
            app.startMode = False
            app.directionsMode = True
    elif app.directionsMode:
        if app.currDirectionScreen  == app.creators1:
            app.currDirectionScreen = app.creators2
        elif app.currDirectionScreen == app.creators2:
            app.currDirectionScreen = app.directions1
        elif app.currDirectionScreen == app.directions1:
            app.currDirectionScreen = app.directions2
        elif app.currDirectionScreen == app.directions2:
            app.gameMode = True
            app.directionsMode = False
    
    elif app.gameMode:
        if mouseOverPauseButton(mouseX, mouseY) and (not app.failed and not app.newLevel and not app.death):
            app.paused = not app.paused
        elif app.death and mouseInPassBox(mouseX, mouseY):
            app.paused = False
            app.death = False                
        elif app.newLevel and mouseInPassBox(mouseX, mouseY):
            app.paused = False
            app.newLevel = False
        elif mouseOverRestartButton(app, mouseX, mouseY) and (app.failed or app.gameFinished) and not app.paused:
            # Stops music
            app.choirMusic.pause()
            initializeApp(app)
        
# Button definitions

def mouseInEyeBox(app, mouseX, mouseY):
    top = 3*app.height/4 - 80
    bottom = 3*app.height/4 + 40
    left = app.width/2 - 100
    right = app.width/2 + 100
    return (left <= mouseX <= right) and (top <= mouseY <= bottom)

def mouseOverPauseButton(mouseX, mouseY):
    top = 60
    bottom = top + 50
    left = 350
    right = left + 50
    return (left <= mouseX <= right) and (top <= mouseY <= bottom)

def mouseOverRestartButton(app, mouseX, mouseY):
    if app.failed:
        top = 220
        bottom = top + 60
        left = 140
        right = left + 125
    elif app.gameFinished: 
        top = 285
        bottom = top + 65
        left = 135
        right = left + 130
    return (left <= mouseX <= right) and (top <= mouseY <= bottom)

def mouseInPassBox(mouseX, mouseY):
    top = 250
    bottom = 290
    left = 80
    right = 315
    return (left <= mouseX <= right) and (top <= mouseY <= bottom)

# From loading images and sounds demo (Ed)

def loadSound(relativePath):
    return Sound(relativePath)

def main():
    runApp()


main()
