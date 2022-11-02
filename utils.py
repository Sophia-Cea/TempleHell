import pygame
import sys
import os
import math
from random import randint, choice


pygame.init()
WIDTH = 1000
HEIGHT = 700
class GameClock:
    def __init__(self) -> None:
        self.fps_cap = 60
        self.clock = pygame.time.Clock()
        self._delta: float = 1.0

    def tick(self):
        self._delta = self.clock.tick(self.fps_cap) / 1000

clock = GameClock()

# Call this function to get the current delta time value
def delta():
    return clock._delta


class Camera:
    def __init__(self):
        self.xOffset = WIDTH/2
        self.yOffest = HEIGHT/2
    
    def lerp_to(self, x, y, percent):
        self.xOffset += (x - self.xOffset) * percent
        self.yOffest += (y - self.yOffest) * percent

    def lerp_x(self, x, y, percent):
        self.xOffset += (x - self.xOffset) * percent
    
    def lerp_y(self, x, y, percent):
        self.yOffest += (y - self.yOffest) * percent

    def project(self, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(rect.x - self.xOffset + WIDTH/2, rect.y - self.yOffest + HEIGHT/2, rect.w, rect.h)

    def projectPoint(self, pos: tuple) -> tuple:
        return (pos[0] - self.xOffset + WIDTH/2, pos[1] - self.yOffest + HEIGHT/2)

    def projectVector(self, pos: pygame.Vector2) -> tuple:
        return (pos.x - self.xOffset + WIDTH/2, pos.y - self.yOffest + HEIGHT/2)

    def unprojectPoint(self, pos:tuple) -> tuple:
        x_temp = pos[0] - WIDTH/2
        y_temp = pos[1] - HEIGHT/2
        return (x_temp + self.xOffset, y_temp + self.yOffest)

    def unprojectVector(self, pos:pygame.Vector2) -> pygame.Vector2:
        x_temp = pos.x - WIDTH/2
        y_temp = pos.y - HEIGHT/2
        return (x_temp + self.xOffset, y_temp + self.yOffest)
    

camera = Camera()       

def gradient(col1, col2, surface, rect=None):
    if rect == None:
        rect = pygame.Rect(0,0, surface.get_width(), surface.get_height())

    if type(col1) != tuple:
        col1 = col1.copy()
    if type(col2) != tuple:
        col2 = col2.copy()
    inc1 = (col2[0] - col1[0])/rect.height
    inc2 = (col2[1] - col1[1])/rect.height
    inc3 = (col2[2] - col1[2])/rect.height
    color = [col1[0], col1[1], col1[2]]
    for i in range(rect.height):
        pygame.draw.line(surface, color, (rect.x, rect.y + i), (rect.width, rect.y + i), 2)
        color[0] += inc1
        color[1] += inc2
        color[2] += inc3

def resource_path(relative_path):
  if hasattr(sys, '_MEIPASS'):
      return os.path.join(sys._MEIPASS, relative_path)
  return os.path.join(os.path.abspath('.'), relative_path)

def clampColor(val):
    if val > 255:
        val = 255
    if val < 0:
        val = 0
    return int(val)

def convertRect(rectTuple):
    newRect = rectTuple
    return pygame.Rect(WIDTH/100*newRect[0], HEIGHT/100*newRect[1], WIDTH/100*newRect[2], HEIGHT/100*newRect[3])

def measureDistance(pt1, pt2):
    return math.sqrt((pt2[0] - pt1[0])**2 + (pt2[1] - pt1[1])**2)

def deg2rad(degrees):
    return degrees * math.pi / 180

def rad2deg(radians):
    return radians * 180 / math.pi

class Colors:
    col1 = [248, 248, 255]
    col2 = [237, 87, 82]
    col3 = [51, 51, 51]
    col4 = [214, 233, 252]
    col5 = [146, 170, 199]

    textCol = col3.copy()
    bgCol1 = col1.copy()
    bgCol2 = col1.copy()
    buttonCol1 = col4.copy()
    buttonCol2 = col5.copy()
    accentCol = col2.copy()

class Fonts:
    WIDTH = WIDTH
    HEIGHT = HEIGHT
    fonts = {
        "title": pygame.font.Font(resource_path("font.ttf"), int(WIDTH/14), bold=False, italic=False),
        "subtitle": pygame.font.Font(resource_path("font.ttf"), int(WIDTH/20), bold=False, italic=False),
        "paragraph": pygame.font.Font(resource_path("font.ttf"), int(WIDTH/26), bold=False, italic=False),
        "button": pygame.font.Font(resource_path("font.ttf"), int(WIDTH/28), bold=False, italic=False)
    }

    def resizeFonts(screen):
        Fonts.WIDTH = screen.get_width()
        Fonts.fonts = {
            "title": pygame.font.Font(resource_path("font.ttf"), int(Fonts.WIDTH/14), bold=False, italic=False),
            "subtitle": pygame.font.Font(resource_path("font.ttf"), int(Fonts.WIDTH/20), bold=False, italic=False),
            "paragraph": pygame.font.Font(resource_path("font.ttf"), int(Fonts.WIDTH/26), bold=False, italic=False),
            "button": pygame.font.Font(resource_path("font.ttf"), int(Fonts.WIDTH/28), bold=False, italic=False)
        }

class Text:
    texts = []
    def __init__(self, text, font, color, position, centered, underline = False) -> None:
        self.content = str(text)
        self.fontSize = font
        self.font = Fonts.fonts[font]
        self.color = color
        self.pos = position
        self.centered = centered
        self.text = self.font.render(self.content, True, self.color)
        self.rect = pygame.Rect(0,0,0,0)
        Text.texts.append(self)
        self.underline = underline

    def resize(self):
        self.font = Fonts.fonts[self.fontSize]
        self.text = self.font.render(self.content, True, self.color)

    def reset(self, color, content):
        self.color = color
        self.content = content
        self.font = Fonts.fonts[self.fontSize]
        self.text = self.font.render(self.content, True, self.color)

    def draw(self, surface):
        if self.centered:
            self.rect = pygame.Rect(surface.get_width()/100*self.pos[0]-self.text.get_width()/2, surface.get_height()/100*self.pos[1], self.text.get_width(), self.text.get_height())
            surface.blit(self.text, (surface.get_width()/100*self.pos[0]-self.text.get_width()/2, surface.get_height()/100*self.pos[1]))
            if self.underline:
                smallMargin = surface.get_width()/100*3
                xCoord1 = surface.get_width()/100*(self.pos[0])-self.text.get_width()/2 + smallMargin
                xCoord2 = xCoord1 + self.text.get_width() - 2*smallMargin
                yCoord = surface.get_height()/100 * (self.pos[1]) + self.text.get_height()
                pygame.draw.line(surface, Colors.accentCol, (xCoord1, yCoord), (xCoord2, yCoord), 5)
        else:
            self.rect = pygame.Rect(surface.get_width()/100*self.pos[0], surface.get_height()/100*self.pos[1], self.text.get_width(), self.text.get_height())
            surface.blit(self.text, (surface.get_width()/100*self.pos[0], surface.get_height()/100*self.pos[1]))
            if self.underline:
                smallMargin = surface.get_width()/100*3
                xCoord1 = surface.get_width()/100*(self.pos[0]) + smallMargin
                xCoord2 = xCoord1 + self.text.get_width() - 2*smallMargin
                yCoord = surface.get_height()/100 * (self.pos[1]+1) + self.text.get_height()
                pygame.draw.line(surface, Colors.accentCol, (xCoord1, yCoord), (xCoord2, yCoord), 5)

    def checkMouseOver(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            return True

    def resizeAll(surface):
        Fonts.resizeFonts(surface)
        for text in Text.texts:
            text.resize()

class Button:
    buttons = []
    def __init__(self, text, rect, cornerRadius, textColor=Colors.textCol, gradCol1=Colors.buttonCol1, gradCol2=Colors.buttonCol2, onclickFunc=None) -> None:
        self.rect: pygame.Rect = rect
        self.convertedRect = convertRect((self.rect.x, self.rect.y, self.rect.width, self.rect.height))
        self.surface = pygame.Surface((self.convertedRect.width, self.convertedRect.height), pygame.SRCALPHA)
        self.hoverSurface = pygame.Surface((self.convertedRect.width, self.convertedRect.height), pygame.SRCALPHA)
        self.textContent = text
        self.textColor = textColor
        self.cornerRadius = cornerRadius
        self.gradCol1 = gradCol1
        self.gradCol2 = gradCol2
        self.hovering = False
        self.onClickFunc = onclickFunc
        self.drawImage(self.gradCol1, self.gradCol2, self.textColor, self.surface)
        self.drawImage(self.darken(self.gradCol1, .9), self.darken(self.gradCol2, .9), self.darken(self.textColor, .9), self.hoverSurface)
        self.resizedSurface = pygame.transform.scale(self.surface, (self.convertedRect.width, self.convertedRect.height))
        self.resizedHoverSurface = pygame.transform.scale(self.hoverSurface, (self.convertedRect.width, self.convertedRect.height))

        Button.buttons.append(self)

    def drawImage(self, gradCol1, gradCol2, textCol, surface):
        color = gradCol1.copy()
        inc1 = (gradCol2[0] - gradCol1[0])/(self.convertedRect.height - self.cornerRadius)
        inc2 = (gradCol2[1] - gradCol1[1])/(self.convertedRect.height - self.cornerRadius)
        inc3 = (gradCol2[2] - gradCol1[2])/(self.convertedRect.height - self.cornerRadius)
        for i in range(self.convertedRect.height - self.cornerRadius):
            pygame.draw.rect(surface, color, pygame.Rect(0, i, self.convertedRect.width, self.cornerRadius), border_radius=self.cornerRadius)
            color[0] += inc1
            color[1] += inc2
            color[2] += inc3
        text = Fonts.fonts["button"].render(self.textContent, True, textCol)
        surface.blit(text, (surface.get_width()/2-text.get_width()/2, surface.get_height()/2-text.get_height()/2))

    def darken(self, color, val):
        newCol = color.copy()
        newCol = [clampColor(newCol[0] * val), clampColor(newCol[1] * val), clampColor(newCol[2] * val)]
        return newCol

    def draw(self, surface):
        if self.hovering == False:
            surface.blit(self.resizedSurface, (self.convertedRect.x, self.convertedRect.y))
        else:
            surface.blit(self.resizedHoverSurface, (self.convertedRect.x, self.convertedRect.y))

    def checkMouseOver(self, pos):
        if self.convertedRect.collidepoint(pos):
            return True

    def resize(self, surface):
        self.convertedRect = convertRect(surface, (self.rect.x, self.rect.y, self.rect.width, self.rect.height))
        self.resizedSurface = pygame.transform.scale(self.surface, (self.convertedRect.width, self.convertedRect.height))
        self.resizedHoverSurface = pygame.transform.scale(self.hoverSurface, (self.convertedRect.width, self.convertedRect.height))

