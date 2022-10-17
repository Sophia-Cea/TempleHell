from world import *

world = World()

class Entity:
    def __init__(self) -> None:
        self.pos = [500, 350]
        self.rect = pygame.Rect(self.pos[0], self.pos[1], 50,50)
        self.surface = pygame.Surface(self.rect.size)
        self.surface.fill((255,0,255))

    def render(self, screen):
        r = self.rect.move(-camera.xOffset + WIDTH/2, -camera.yOffest + HEIGHT/2)
        screen.blit(self.surface, (r.x, r.y))
        
    def update(self):
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        camera.lerp_to(self.rect.centerx, self.rect.centery, 0.05)

    def handleBarrierCollision(self, entityRect: pygame.Rect=None):
        if entityRect == None:
            entityRect = self.rect
        for i in range(len(world.foregroundMap)):
            for j in range(len(world.foregroundMap[i])):
                if world.foregroundMap[i][j] != 0:
                    rect = (world.foregroundMap[i][j].rect)
                    if entityRect.colliderect(rect):
                        return rect
        return None

    def findClosestRectLeft(self, rects: list[pygame.Rect]):
        closestRect: pygame.Rect = rects[0]
        for rect in rects:
            if (self.pos[0] - rect.right) < (self.pos[0] - closestRect.right):
                closestRect = rect
        return closestRect

                

class Player(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.lives = 3
        self.speed = 3
        self.surface = pygame.Surface(self.rect.size)
        self.surface.fill((255,0,0))

    def render(self, screen):
        super().render(screen)
        pygame.draw.rect(screen, (255,0,0), self.rect.move(-camera.xOffset + WIDTH/2, -camera.yOffest + HEIGHT/2), 2)
        # screen.blit(self.surface, (-camera.xOffset + WIDTH/2, -camera.yOffest + HEIGHT/2), special_flags=pygame.BLEND_RGB_ADD)

    def update(self):
        super().update()

    def handleInput(self, events):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            rect = self.handleBarrierCollision(pygame.Rect(self.rect.x - self.speed*delta, self.rect.y, self.rect.width, self.rect.height))
            if rect == None:
                self.pos[0] -= self.speed * delta
            else: 
                self.pos[0] -= (self.pos[0] - rect.right) * delta

        if keys[pygame.K_RIGHT]:
            rect = self.handleBarrierCollision(pygame.Rect(self.rect.x + self.speed*delta, self.rect.y, self.rect.width, self.rect.height))
            if rect == None:
                self.pos[0] += self.speed * delta
            else:
                self.pos[0] += (rect.left - self.rect.right) * delta

        if keys[pygame.K_UP]:
            rect = self.handleBarrierCollision(pygame.Rect(self.rect.x, self.rect.y - self.speed*delta, self.rect.width, self.rect.height))
            if rect == None:
                self.pos[1] -= self.speed * delta
            else:
                self.pos[1] -= (self.rect.top - rect.bottom) * delta

        if keys[pygame.K_DOWN]:
            rect = self.handleBarrierCollision(pygame.Rect(self.rect.x, self.rect.y + self.speed * delta, self.rect.width, self.rect.height))
            if rect == None:
                self.pos[1] += self.speed * delta
            else:
                self.pos[1] += (rect.top - self.rect.bottom) * delta
        
        if keys[pygame.K_RETURN]:
            print("Self.pos = ", self.pos)
            print(f"Camera = [{camera.xOffset}, {camera.yOffest}]")
        print(delta)


class Enemy(Entity):
    def __init__(self) -> None:
        super().__init__()
    