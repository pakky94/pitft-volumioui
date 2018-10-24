import pygame
import os
import sys

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
        self.time_since_click = 0
        self.time_clicked = 0
    
    def check_click(self, click_pos, mouse_down, currentTime=0):
        self.was_clicked = self.is_clicked
        if self.visible:
            if not mouse_down == 0:
                self.is_clicked = (self.left <= click_pos[0] <= self.right and 
                    self.top <= click_pos[1] <= self.bottom)
                if self.is_clicked and not self.was_clicked:
                    self.time_since_click = currentTime
                elif self.is_clicked and self.was_clicked:
                    self.time_clicked = currentTime - self.time_since_click
                else:
                    self.time_clicked = 0
            else:
                self.is_clicked = False
                self.time_clicked = 0
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

        self.currentSongArtist = ""
        self.currentSongArtistLast = ""
        self.currentSongArtistRender = None

        self.currentVolume = -10
        self.currentVolumeLast = 50
        self.currentVolumeRender = None
        self.volumePreMute = -10
        self.volumeUpCounter = 0
        self.volumeDownCounter = 0

    def load(self):
        self.logger.debug("Initializing UI")
        self.path = os.path.dirname(os.path.realpath(__file__)) + "/"

        # pygame.font.init()
        # self.myFont = pygame.font.SysFont(config.font, config.font_size)
        self.myFont = pygame.font.Font("data/ipaexg.ttf", config.font_size)
        self.playBarFont = pygame.font.Font("data/OpenSans-Regular.ttf", 18)
        self.currentSongTitleRender = self.myFont.render("", False, (255, 255, 255))
        self.currentSongArtistRender = self.myFont.render("", False, (255, 255, 255))

        self.image = {}
        self.image["background"] = pygame.image.load(self.path + "data/background.png")
        self.image["button-play"] = pygame.image.load(self.path + "data/button-play.png")
        self.image["button-pause"] = pygame.image.load(self.path + "data/button-pause.png")
        self.image["button-previous"] = pygame.image.load(self.path + "data/button-previous.png")
        self.image["button-next"] = pygame.image.load(self.path + "data/button-next.png")
        self.image["volume-up"] = pygame.image.load(self.path + "data/volume-up.png")
        self.image["volume-down"] = pygame.image.load(self.path + "data/volume-down.png")
        self.image["volume-mute"] = pygame.image.load(self.path + "data/volume-mute.png")

        self.buttons = {}
        self.buttons["play-pause"] = ImgButton((100, 200), (64, 64), image=self.image["button-play"])
        self.buttons["play-previous"] = ImgButton((30, 200), (64, 64), image=self.image["button-previous"])
        self.buttons["play-next"] = ImgButton((170, 200), (64, 64), image=self.image["button-next"])
        self.buttons["volume-up"] = ImgButton((395, 200), (64, 64), image=self.image["volume-up"])
        self.buttons["volume-down"] = ImgButton((265, 200), (64, 64), image=self.image["volume-down"])
        self.buttons["volume-mute"] = ImgButton((330, 200), (64, 64), image=None)



        # self.image["testbutton-image"] = pygame.image.load(self.path + "data/testbutton.png")
        # self.buttons["testbutton"] = ImgButton((300, 50), (64, 64), image=self.image["testbutton-image"])

    def update(self, mouse_event, currentTime=0):
        self.currentStatus = self.controller.playerStatus()
        currentsong = self.controller.currentSong()
        
        self.mouse_event(mouse_event, currentTime)

        # render current song title
        if "title" in currentsong:
            self.currentSongTitle = currentsong["title"]
        else:
            self.currentSongTitle = ""
        if not self.currentSongTitle == self.currentSongTitleLast:
            self.currentSongTitleRender = self.myFont.render(self.currentSongTitle.encode("utf-8").decode("utf-8"), True, config.main_text_color)
            self.currentSongTitleLast = self.currentSongTitle

        # render current song artist
        if "artist" in currentsong:
            self.currentSongArtist = currentsong["artist"]
        else:
            self.currentSongArtist = ""
        if not self.currentSongArtist == self.currentSongArtistLast:
            self.currentSongArtistRender = self.myFont.render(self.currentSongArtist, True, config.main_text_color)
            self.currentSongArtistLast = self.currentSongArtist
        
        #
        if "volume" in self.currentStatus:
            self.currentVolume = int(self.currentStatus["volume"])
            if self.currentVolume <= 2 and self.currentVolumeLast > 2:
                self.volumePreMute = self.currentVolumeLast
                self.buttons["volume-mute"].image = self.image["volume-mute"]
            elif self.currentVolume > 2:
                self.volumePreMute = -10
                self.buttons["volume-mute"].image = None
        else:
            self.currentVolume = -10
        if not self.currentVolume == self.currentVolumeLast or self.currentVolumeRender == None:
            self.currentVolumeRender = self.myFont.render(str(self.currentVolume), True, config.main_text_color)
            self.currentVolumeLast = self.currentVolume

        # change the play/pause button image based on the player status
        if "state" in self.currentStatus.keys():
            if self.currentStatus["state"] == "play":
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
        if self.currentSongArtistRender:
            surface.blit(self.currentSongArtistRender, (20, 60))
        if self.currentVolumeRender:
            surface.blit(self.currentVolumeRender, (self.buttons["volume-mute"].position[0] + 12, self.buttons["volume-mute"].position[1] + 13))

        
        playbarX = 20
        playbarY = 270
        playbarWidth = 440
        playbarHeight = 13
        if "time" in self.currentStatus:
            currentTime = self.currentStatus["time"].split(":")
            currentTime[0] = int(currentTime[0])
            currentTime[1] = int(currentTime[1])
            minutes = int(currentTime[0] / 60)
            seconds =  int(currentTime[0] % 60)
            textSurface = self.playBarFont.render(str(minutes) + ":" + '{0:02d}'.format(seconds), True, (255,255,255))
            surface.blit(textSurface, (playbarX + 5, playbarY))
            minutes = int(currentTime[1] / 60)
            seconds =  int(currentTime[1] % 60)
            textSurface = self.playBarFont.render(str(minutes) + ":" + '{0:02d}'.format(seconds), True, (255,255,255))
            surface.blit(textSurface, (playbarX  + playbarWidth - 5 - textSurface.get_width(), playbarY))
            surface.fill((255, 255, 255), rect=(playbarX, playbarY + textSurface.get_height(), playbarWidth, playbarHeight))
            surface.fill((0,0,128), rect=(playbarX+2, playbarY + 2 + textSurface.get_height(), int((playbarWidth - 4) * currentTime[0] / currentTime[1]), playbarHeight - 4))
        else:
            currentTime = [0, 0]
            textSurface = self.playBarFont.render(str(currentTime[0]), True, (255,255,255))
            surface.fill((255, 255, 255), rect=(playbarX, playbarY + textSurface.get_height(), playbarWidth, playbarHeight))
            # surface.fill((0,0,128), rect=(playbarX+2, playbarY + 2 + textSurface.get_height(), int((playbarWidth - 4) * currentTime[0] / currentTime[1]), playbarHeight - 4))


        for n, b in self.buttons.items():
            b.render(surface)
        
    def mouse_event(self, e, currentTime):
        for n, b in self.buttons.items():
            b.check_click((e["x"], e["y"]), e["touch"], currentTime)
        
        if self.buttons["play-pause"].is_clicked and not self.buttons["play-pause"].was_clicked:
            if self.currentStatus["state"] == "stop":
                self.controller.startPlay()
            else:
                self.controller.toggleplay()

        if self.buttons["play-previous"].is_clicked and not self.buttons["play-previous"].was_clicked:
            self.controller.playPrevious()
        if self.buttons["play-next"].is_clicked and not self.buttons["play-next"].was_clicked:
            self.controller.playNext()
        

        if self.buttons["volume-up"].is_clicked:
            if self.buttons["volume-up"].was_clicked:
                if self.buttons["volume-up"].time_clicked > 800 + self.volumeUpCounter * 300:
                    if self.currentVolume > 2:
                        volHelp = self.currentVolume + 5
                        if volHelp > 100:
                            volHelp = 100
                        self.controller.setVolume(volHelp)
                    else:
                        if self.volumePreMute > 2:
                            self.controller.setVolume(self.volumePreMute)
                        else:
                            self.controller.setVolume(5)
                    self.volumeUpCounter = self.volumeUpCounter + 1
            else:
                if self.currentVolume > 2:
                    volHelp = self.currentVolume + 5
                    if volHelp > 100:
                        volHelp = 100
                    self.controller.setVolume(volHelp)
                else:
                    if self.volumePreMute > 2:
                        self.controller.setVolume(self.volumePreMute)
                    else:
                        self.controller.setVolume(5)
        else:
            self.volumeUpCounter = 0
        if self.buttons["volume-down"].is_clicked:
            if self.buttons["volume-down"].was_clicked:
                if self.buttons["volume-down"].time_clicked > 800 + self.volumeDownCounter * 300:
                    if self.currentVolume > 2:
                        volHelp = self.currentVolume - 5
                        if volHelp < 0:
                            volHelp = 0
                        self.controller.setVolume(volHelp)
                    self.volumeDownCounter = self.volumeDownCounter + 1
            else:
                if self.currentVolume > 2:
                    volHelp = self.currentVolume - 5
                    if volHelp < 0:
                        volHelp = 0
                    self.controller.setVolume(volHelp)
        else:
            self.volumeDownCounter = 0
        if self.buttons["volume-mute"].is_clicked and not self.buttons["volume-mute"].was_clicked:
            if self.volumePreMute < 2:
                # MUTE VOLUME
                self.controller.setVolume(0)
                self.volumePreMute = self.currentVolume
            else:
                # UNMUTE
                if self.volumePreMute > 2:
                    self.controller.setVolume(self.volumePreMute)
                else:
                    self.controller.setVolume(50)


        # if self.buttons["testbutton"].is_clicked and not self.buttons["testbutton"].was_clicked:
        #     print(self.currentStatus)
        #     print(self.controller.mpdclient.playlistinfo())