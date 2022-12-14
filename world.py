# from utils import *
import json
from pygame import Rect
from entity import *

# camera = Camera()
file = "newMap.json"
player = Player((7.5,7))


class Door:
    directions = {
        "up" : 0,
        "right" : 1,
        "down" : 2,
        "left" : 3
    }
    def __init__(self, doorDict) -> None:
        self.pos = doorDict["pos"]
        self.id = doorDict["id"]
        self.isVertical = doorDict["vertical"] # BUG could be bug here if it doesnt convert true to True....
        self.rect = pygame.Rect(self.pos[1] * Tile.tileSize, self.pos[0] * Tile.tileSize, Tile.tileSize, Tile.tileSize)
        if self.isVertical:
            self.rect.height = Tile.tileSize*2
            self.doorImg = pygame.transform.scale(pygame.image.load("assets/tiles/door_vertical.png"), (self.rect.size))
        else:
            self.rect.width = Tile.tileSize*2
            self.doorImg = pygame.transform.scale(pygame.image.load("assets/tiles/door_horizontal.png"), (self.rect.size))
        # self.doorImg.fill((255,0,255)) # TODO refactor this so it draws the door as 2 tiles or smth
        self.playerInDoor = False
        self.needToChangeRoom = False
        self.inwardDirection = doorDict["inwardDirection"] # 0: top, 1: right, 2: down, 3: left

    def render(self, screen: pygame.Surface):
        screen.blit(self.doorImg, camera.projectPoint(self.rect.topleft))
    
    def update(self):
        if player.rect.colliderect(self.rect):
            if self.isVertical:
                if player.rect.centerx in range(self.rect.centerx-10, self.rect.centerx+10):
                    self.needToChangeRoom = True
            else:
                if player.rect.centery in range(self.rect.centery-10, self.rect.centery+10):
                    self.needToChangeRoom = True

class Room:
    def __init__(self, roomDict) -> None:
        self.dict = roomDict
        self.needToChangeRoom = False
        self.currentDoorId = 0
        self.backgroundMap: list[list[int]] = roomDict["background"]
        self.foregroundMap: list[list[int]] = roomDict["foreground"]
        self.enemyMap = roomDict["enemies"]
        self.decorMap = roomDict["decor"]
        self.doors = roomDict["doors"]
        self.centerOfRoom = [] #TODO this will be used for the doors to determine where the inside of the room is
        self.backgroundTiles: list[Tile] = []
        self.foregroundTiles: list[Tile] = []
        self.enemies = []
        self.decorations = []
        for i in range(len(self.doors)):
            self.doors[i] = Door(self.doors[i])
        for i in range(len(self.backgroundMap)):
            for j in range(len(self.backgroundMap[i])):
                if self.backgroundMap[i][j] != 0:
                    self.backgroundTiles.append(BackgroundTile(j, i, self.backgroundMap[i][j]))
                if self.foregroundMap[i][j] != 0:
                    self.foregroundTiles.append(ForegroundTile(j, i, self.foregroundMap[i][j]))
                if self.enemyMap[i][j] != 0: # TODO make this thing add enemy just by inputting the type.
                    self.enemies.append(FixedEnemy((j, i), randint(100, 5000)))
                if self.decorMap[i][j] != 0:
                    self.decorations.append(AnimatedTile(j, i, self.decorMap[i][j]))
                    
    def render(self, screen):
        for tile in self.backgroundTiles:
            tile.drawTile(screen)
        for tile in self.foregroundTiles:
            tile.drawTile(screen)
        for door in self.doors:
            door.render(screen)
        for decor in self.decorations:
            decor.drawTile(screen)
        for enemy in self.enemies:
            enemy.render(screen)

    def update(self):
        for door in self.doors:
            door.update()
            if door.needToChangeRoom:
                self.needToChangeRoom = True
                door.needToChangeRoom = False
                self.currentDoorId = door.id
        for decor in self.decorations:
            if type(decor) == AnimatedTile:
                decor.update()
        for enemy in self.enemies:
            enemy.update()
            if enemy.readyToLaunch:
                if measureDistance(enemy.pos, player.pos) <= 200:
                    enemy.launchBullet(player.rect.center)

    def handleInput(self, events):
        for enemy in self.enemies:
            enemy.handleInput(events)

    def getBounds(self) -> Rect:
        top_left = self.foregroundTiles[0].rect.topleft # in case top left isn't (0,0)
        top = 0
        left = 0
        bottom = (len(self.foregroundMap) * Tile.tileSize)
        right = (len(self.foregroundMap[0]) * Tile.tileSize)

        return Rect(0, 0, right, bottom)

class Chunk:
    def __init__(self, chunkDict) -> None:
        self.chunkDict = chunkDict
        self.currentRoom = 0
        self.nextDoorId = 0
        self.rooms = []
        self.doorConnections = chunkDict["doorConnections"]
        for room in chunkDict["rooms"]:
            self.rooms.append(Room(room))
        self.fadeThingy = pygame.Surface((WIDTH, HEIGHT))
        self.fadeThingy.fill((0,0,0))
        self.fadingIn = False
        self.fadingOut = False
        self.opacity = 225
        # self.transitioning = False
    
    def render(self, screen):
        self.getCurrentRoom().render(screen)
        if self.fadingIn or self.fadingOut:
            screen.blit(self.fadeThingy, (0,0))
    
    def getCurrentRoom(self) -> Room:
        return self.rooms[self.currentRoom]

    def update(self):
        if self.fadingIn or self.fadingOut:
            self.fadeThingy.set_alpha(self.opacity)
        self.getCurrentRoom().update()
        if self.getCurrentRoom().needToChangeRoom:
            self.fadingOut = True

        if self.fadingIn:
            if self.opacity > 0:
                self.opacity -= 15
            else:
                self.fadingIn = False
                self.opacity = 255
                self.fadeThingy.set_alpha(self.opacity)
        elif self.fadingOut:
            if self.opacity < 255:
                self.opacity += 15
            else:
                self.fadingOut = False
                self.fadingIn = True
                self.changeRooms()
        

    def handleInput(self, events):
        self.getCurrentRoom().handleInput(events)

    def changeRooms(self):
        for i in range(len(self.doorConnections)):
            if self.getCurrentRoom().currentDoorId in self.doorConnections[i]:
                if self.doorConnections[i][0] == self.getCurrentRoom().currentDoorId:
                    self.nextDoorId = self.doorConnections[i][1]
                else:
                    self.nextDoorId = self.doorConnections[i][0]
                break
        for room in enumerate(self.rooms):
            for door in room[1].doors:
                if door.id == self.nextDoorId:
                    self.currentRoom = room[0]
                    room[1].needToChangeRoom = False
                    break
        for room in self.rooms:
            for door in room.doors:
                if door.id == self.nextDoorId:
                    player.pos = [door.pos[1]*Tile.tileSize, door.pos[0]*Tile.tileSize]
                    if door.inwardDirection == Door.directions["up"]:
                        player.pos[1] -= player.rect.height
                    elif door.inwardDirection == Door.directions["down"]:
                        player.pos[1] += player.rect.height
                    elif door.inwardDirection == Door.directions["left"]:
                        player.pos[0] -= player.rect.width
                    elif door.inwardDirection == Door.directions["right"]:
                        player.pos[0] += player.rect.width
                    break
        self.nextDoorId = None

class World:
    def __init__(self) -> None:
        with open(file) as f:
            self.world = json.load(f)
        self.chunks = []
        for key in self.world:
            self.chunks.append(Chunk(self.world[key]))
        self.currentChunk = 0
        self.heartImg = pygame.transform.scale(pygame.image.load("assets/other/heart.png"), (30,30))
        self.fadeThingy = pygame.Surface((WIDTH, HEIGHT))
        self.fadeThingy.fill((0,0,0))
        self.fadingIn = False
        self.fadingOut = False
        self.opacity = 225
    
    def getCurrentChunk(self) -> Chunk:
        return self.chunks[self.currentChunk]
    
    def render(self, screen):
        self.getCurrentChunk().render(screen)
        for i in range(player.health):
            screen.blit(self.heartImg, (35+i*40, 30))
        if self.fadingIn or self.fadingOut:
            screen.blit(self.fadeThingy, (0,0))

    def update(self):
        if self.fadingIn or self.fadingOut:
            self.fadeThingy.set_alpha(self.opacity)
        camera.set_bounds(self.getCurrentChunk().getCurrentRoom().getBounds())
        camera.lerp_to(player.rect.centerx, player.rect.centery, 0.05)
        if self.currentChunk == 0:
            self.getCurrentChunk().getCurrentRoom().update()
            if self.getCurrentChunk().getCurrentRoom().needToChangeRoom:
                self.fadingOut = True
            
        if self.fadingIn:
            if self.opacity > 0:
                self.opacity -= 15
            else:
                self.fadingIn = False
                self.opacity = 255
                self.fadeThingy.set_alpha(self.opacity)
        elif self.fadingOut:
            if self.opacity < 255:
                self.opacity += 15
            else:
                self.fadingOut = False
                self.fadingIn = True
                
                # TODO make a door class that stores next intended position
                # Gahd damn this is so sloppy
                # You really want to have 4 lines and an if statement for every door in the game? that sounds like a mess
                # Also, consider making a setCurrentRoom(chunk, room) function. In that function, you can put 
                if self.getCurrentChunk().getCurrentRoom().currentDoorId == 1:
                    self.currentChunk = 1
                    player.pos = [12*Tile.tileSize, 2*Tile.tileSize]
                elif self.getCurrentChunk().getCurrentRoom().currentDoorId == 2:
                    self.currentChunk = 2
                    player.pos = [6*Tile.tileSize, 10*Tile.tileSize]
                    self.getCurrentChunk().currentRoom = 6

        else:
            self.getCurrentChunk().update()
        Bullet.checkAllBulletsCollision(self.getCurrentChunk().getCurrentRoom().foregroundTiles, player)
        
        
    def handleInput(self, events):
        self.getCurrentChunk().handleInput(events)