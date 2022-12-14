# from projectile import *
from playerStates import *



class Entity:
    def __init__(self) -> None:
        self.pos = [950, 800]
        self.rect = pygame.Rect(self.pos[0], self.pos[1], 64, 120)

    def render(self, screen):
        pass
        
    def update(self):
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

    def handleBarrierCollision(self, barrierMap, entityRect: pygame.Rect=None):
        if entityRect == None:
            entityRect = self.rect
        for i in range(len(barrierMap)):
            # for j in range(len(barrierMap[i])):
            #     if barrierMap[i][j] != 0:
                    # rect = barrierMap[i][j].rect
                    rect = barrierMap[i].rect
                    if entityRect.colliderect(rect):
                        return rect
        return None

class Player(Entity):
    def __init__(self, pos) -> None:
        super().__init__()
        self.pos = [pos[0]*Tile.tileSize, pos[1]*Tile.tileSize]
        self.lives = 3
        self.speed = 500
        self.lastDirectionFaced = "front"
        self.rect = pygame.Rect(0, 0, Tile.tileSize*.9, Tile.tileSize*2*.9)
        self.health = 5 #lives
        self.weapons = {
            "mace" : True,
            "staff" : True,
            "gun" : True
        }
        self.weapon = "mace"
        self.currentState = StateGenerator.setState("idle", self)
        self.cameraShaking = False
        self.randomOffsetX = 0
        self.randomOffsetY = 0
        self.shakeIntensity = 3

    def shakeCamera(self, intensity):
        self.cameraShaking = True
        pygame.time.set_timer(pygame.USEREVENT+3, 350)
        self.shakeIntensity = intensity

    def setWeapon(self, weapon):
        if self.weapons[weapon] == True:
            self.weapon = weapon
    
    def getState(self):
        if type(self.currentState) == MoveState:
            return "moving"
        elif type(self.currentState) == IdleState:
            return "idle"
        elif type(self.currentState) == AttackState:
            return "attacking"

    def render(self, screen):
        super().render(screen)
        # self.currentState.render(screen, self.rect.move(-camera.xOffset + WIDTH/2, -camera.yOffest + HEIGHT/2))
        self.currentState.render(screen, camera.project(self.rect))

    def update(self, barrierMap):
        super().update()
        # camera.lerp_to(self.rect.centerx, self.rect.centery, 0.05)
        if self.getState() != "moving":
            self.currentState.update()
        else:
            self.currentState.update(barrierMap)
        if self.cameraShaking:
            self.randomOffsetX = randint(-self.shakeIntensity, self.shakeIntensity)
            self.randomOffsetY = randint(-self.shakeIntensity, self.shakeIntensity)
            camera.xOffset += self.randomOffsetX
            camera.yOffset += self.randomOffsetX
            print(self.randomOffsetX, self.randomOffsetY)

    
    def takeDamage(self, amt):
        if self.getState() != "attacking":
            self.health -= amt
            self.shakeCamera(5)

    def handleInput(self, events): # BUG need to put in new parameter
        self.currentState.handleInput(events)
        for event in events:
            if event.type == pygame.USEREVENT+3:
                self.cameraShaking = False
                self.randomOffsetX = 0
                self.randomOffsetY = 0
class FixedEnemy(Entity):
    size = Tile.tileSize*2
    def __init__(self, pos, bulletFrq=3000) -> None:
        super().__init__()
        # pos is given in the form of a position in the grid
        self.pos = [pos[0]*Tile.tileSize, pos[1]*Tile.tileSize]
        self.rect = pygame.Rect(self.pos[0], self.pos[1], FixedEnemy.size, FixedEnemy.size)
        self.bullets = []
        self.bulletFrq = bulletFrq
        pygame.time.set_timer(pygame.USEREVENT + 1, self.bulletFrq)
        self.readyToLaunch = False
        self.surface = pygame.transform.scale(pygame.image.load("assets/enemies/nut_devil_1.png"), self.rect.size)

    def update(self):
        super().update()
        for bullet in self.bullets:
            bullet.update()
            if bullet.checkState("exploding"):
                if bullet.checkExplosionDone():
                    self.bullets.remove(bullet)
                    Bullet.bullets.remove(bullet)

    def render(self, screen):
        for bullet in self.bullets:
            bullet.render(screen)
        r = self.rect.move(-camera.xOffset + WIDTH/2, -camera.yOffset + HEIGHT/2)
        screen.blit(self.surface, (r.x, r.y))
        super().render(screen)
    
    def handleInput(self, events):
        for event in events:
            if event.type == pygame.USEREVENT + 1:
                self.readyToLaunch = True
    
    def launchBullet(self, pos):
        self.bullets.append(Bullet(self.rect.center, pos))
        self.readyToLaunch = False
        pygame.time.set_timer(pygame.USEREVENT + 1, self.bulletFrq)


class MobileEnemy(Entity):
    def __init__(self) -> None:
        super().__init__()
    