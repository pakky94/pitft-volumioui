import pygame
import os

import config

class ImgButton():
    
    def __init__(self, position, size, image=None):
        self.position = position
        self.size = size
        (x1, y1) = position[0], position[1]
        (x2, y2) = (position[0] + size[0], position[1] + size[1])
        self.left = min(x1, x2)
        self.top = min(y1, y2)
        self.right = max(x1, x2)
        self.bottom = max(y1, y2)
        self.visible = True
        
        self.image = image

        self.is_clicked = False
        self.was_clicked = False

    def check_click(self, click_pos, mouse_down):
        self.was_clicked = self.is_clicked
        if self.visible:
            if not mouse_down == 0:
                self.is_clicked = (self.left <= click_pos[0] <= self.right and 
                    self.top <= click_pos[1] <= self.bottom)
            else:
                self.is_clicked = False
        else:
            self.was_clicked = False
            self.is_clicked = False

    def render(self, surface):
        if self.visible and self.image:
            surface.blit(self.image, self.position)
        else:
            pass
    
    def hide(self):
        self.visible = False
    
    def show(self):
        self.visible = True
    
class PlayerUI():
    
    def __init__(self, logger, controller=None):
        self.logger = logger
        self.controller = controller

        self.currentlyPlaying = False

        self.currentStatus = {}

        self.currentSongID = -1
        self.currentSongTitle = ""
        self.currentSongTitleLast = ""
        self.currentSongTitleRender = None

    def load(self):
        self.logger.debug("Initializing UI")
        self.path = os.path.dirname(os.path.realpath(__file__)) + "/"

        # pygame.font.init()
        self.myFont = pygame.font.SysFont(config.font, config.font_size)
        self.currentSongTitleRender = self.myFont.render("", False, (255, 255, 255))

        self.image = {}
        self.image["background"] = pygame.image.load(self.path + "data/" + "background.png")
        self.image["button-play"] = pygame.image.load(self.path + "data/" + "button-play.png")
        self.image["button-pause"] = pygame.image.load(self.path + "data/" + "button-pause.png")

        self.buttons = {}
        self.buttons["play-pause"] = ImgButton((220, 250), (48, 48), image=self.image["button-play"])


    def update(self):
        self.currentstatus = self.controller.playerstatus()
        currentsong = self.controller.currentsong()
        
        if "title" in currentsong:
            self.currentSongTitle = currentsong["title"]
        else:
            self.currentSongTitle = ""

        # change the play/pause button image based on the player status
        if "state" in self.currentstatus.keys():
            if self.currentstatus["state"] == "play":
                self.buttons["play-pause"].image = self.image["button-pause"]
                self.currentlyPlaying = True
            else:
                self.buttons["play-pause"].image = self.image["button-play"]
                self.currentlyPlaying = False
        else:
            self.buttons["play-pause"].image = self.image["button-play"]
            self.currentlyPlaying = False

                
        
        if not self.currentSongTitle == self.currentSongTitleLast:
            self.currentSongTitleRender = self.myFont.render(self.currentSongTitle, True, (0, 255, 0))
            self.currentSongTitleLast = self.currentSongTitle

    
    def render(self, surface):
        
        surface.blit(self.image["background"], (0,0))
        
        surface.blit(self.currentSongTitleRender, (20, 20))

        for n, b in self.buttons.items():
            b.render(surface)


    def mouse_event(self, e):
        for n, b in self.buttons.items():
            b.check_click((e["x"], e["y"]), e["touch"])
        
        if self.buttons["play-pause"].is_clicked and not self.buttons["play-pause"].was_clicked:
            if self.currentstatus["state"] == "stop":
                self.controller.startPlay()
            else:
                self.controller.toggleplay()
        
        # if self.buttons["play-pause"].was_clicked and not self.buttons["play-pause"].is_clicked:
        #     print("play button released")
    