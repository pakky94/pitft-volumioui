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

        self.currentVolume = -10
        self.currentVolumeLast = -10
        self.currentVolumeRender = None
        self.volumePreMute = -10

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
        self.image["button-previous"] = pygame.image.load(self.path + "data/" + "button-previous.png")
        self.image["button-next"] = pygame.image.load(self.path + "data/" + "button-next.png")
        self.image["volume-up"] = pygame.image.load(self.path + "data/" + "volume-up.png")
        self.image["volume-down"] = pygame.image.load(self.path + "data/" + "volume-down.png")

        self.buttons = {}
        self.buttons["play-pause"] = ImgButton((220, 250), (48, 48), image=self.image["button-play"])
        self.buttons["play-previous"] = ImgButton((165, 250), (48, 48), image=self.image["button-previous"])
        self.buttons["play-next"] = ImgButton((275, 250), (48, 48), image=self.image["button-next"])
        self.buttons["volume-up"] = ImgButton((410, 250), (48, 48), image=self.image["volume-up"])
        self.buttons["volume-down"] = ImgButton((360, 250), (48, 48), image=self.image["volume-down"])


    def update(self):
        self.currentstatus = self.controller.playerstatus()
        currentsong = self.controller.currentsong()
        
        # render current song title
        if "title" in currentsong:
            self.currentSongTitle = currentsong["title"]
        else:
            self.currentSongTitle = ""
        if not self.currentSongTitle == self.currentSongTitleLast:
            self.currentSongTitleRender = self.myFont.render(self.currentSongTitle, True, config.main_text_color)
            self.currentSongTitleLast = self.currentSongTitle
        
        #
        if "volume" in self.currentstatus:
            self.currentVolume = int(self.currentstatus["volume"])
            # print(str(self.currentVolume) + " - " + str(self.currentstatus["volume"]))
        else:
            self.currentVolume = -10
        if not self.currentVolume == self.currentVolumeLast:
            self.currentVolumeRender = self.myFont.render(str(self.currentVolume), True, config.main_text_color)
            self.currentVolumeLast = self.currentVolume

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

                
        
        

    
    def render(self, surface):
        
        surface.blit(self.image["background"], (0,0))
        
        if self.currentSongTitleRender:
            surface.blit(self.currentSongTitleRender, (20, 20))
        if self.currentVolumeRender:
            surface.blit(self.currentVolumeRender, (390, 205))

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

        if self.buttons["play-previous"].is_clicked and not self.buttons["play-previous"].was_clicked:
            print("previous button pressed")
            self.controller.playPrevious()
        if self.buttons["play-next"].is_clicked and not self.buttons["play-next"].was_clicked:
            self.controller.playNext()
        

        if self.buttons["volume-up"].is_clicked and not self.buttons["volume-up"].was_clicked:
            if self.currentVolume >= 0:
                volHelp = self.currentVolume + 5
                if volHelp > 100:
                    volHelp = 100
                self.controller.setVolume(volHelp)
        if self.buttons["volume-down"].is_clicked and not self.buttons["volume-down"].was_clicked:
            if self.currentVolume >= 0:
                volHelp = self.currentVolume - 5
                if volHelp < 0:
                    volHelp = 0
                self.controller.setVolume(volHelp)
