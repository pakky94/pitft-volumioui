import pygame
import os
import sys
import time
from threading import Thread

import config
from coverart import coverCacheServer

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

class ScrollingText():

    def __init__(self, text, pos, font, maxWidth=0, color=(255,255,255),  scrollSpeed=20, scroolFrequency=4, scrollStartWait=30, scrollEndWait=20):
        self.maxWidth = maxWidth
        self.updateText = True
        
        self.pos = pos
        self.text = text
        self.lastText = ""
        self.color = color        
        self.textImage = None
        self.font = font

        self.scrollSpeed = scrollSpeed
        self.scrollFrequency = scroolFrequency
        self.maxScroll = 0
        self.scrollStartWait = scrollStartWait
        self.scrollEndWait = scrollEndWait

        self.currentScroll = 0
        

    def setText(self, text=""):
        self.lastText = self.text
        self.text = text
        if not self.text == self.lastText:
            self.currentScroll = 0
            self.updateText = True

    def update(self):
        pass

    def render(self, surface):
        self.renderedText = self.text
        if self.updateText:
            self.textImage = self.font.render(self.text, True, self.color)
            self.maxScroll = int((self.textImage.get_width() - (self.maxWidth)) / self.scrollSpeed) + 1
            if self.maxScroll < 0:
                self.maxScroll = 0
            self.updateText = False

        if self.currentScroll <= 0:
            surface.blit(self.textImage, self.pos, 
                (self.scrollSpeed * int(max(self.currentScroll, 0) / self.scrollFrequency), 
                0, 
                min(self.textImage.get_width(), self.maxWidth), 
                self.textImage.get_height()))
        else:
            surface.blit(self.textImage, self.pos, 
                (self.scrollSpeed * (int(min(self.currentScroll, self.maxScroll * self.scrollFrequency) / self.scrollFrequency)), 
                0, 
                min(self.textImage.get_width(), self.maxWidth), 
                self.textImage.get_height()))
         
        self.currentScroll = self.currentScroll + 1
        if self.currentScroll > self.maxScroll * self.scrollFrequency + self.scrollEndWait:
            self.currentScroll = 0 - self.scrollStartWait

class PlayerUI():
    
    def __init__(self, logger, controller=None):
        self.logger = logger
        self.controller = controller
        self.coverCacheServer = coverCacheServer(logger)

        self.currentlyPlaying = False

        self.currentStatus = {}

        self.currentSongID = -1
        self.currentSongTitle = ""
        self.currentSongTitleLast = ""

        self.currentSongArtist = ""
        self.currentSongArtistLast = ""

        self.currentAlbum = ""
        self.currentAlbumLast = ""
        self.currentAlbumArtist = ""
        self.currentAlbumArtistLast = ""
        self.fetchingCover = False
        self.coverFetchThread = None

        # VOLUME CONTROL
        # self.currentVolume = -10
        # self.currentVolumeLast = 50
        # self.currentVolumeRender = None
        # self.volumePreMute = -10
        # self.volumeUpCounter = 0
        # self.volumeDownCounter = 0

        self.coverImage = None
        self.fetchingCoverTimer = 0

    def load(self):
        self.logger.debug("Initializing UI")
        self.path = os.path.dirname(os.path.realpath(__file__)) + "/"

        self.myFont = pygame.font.Font("data/ipaexg.ttf", config.font_size)
        self.myFontReduced = pygame.font.Font("data/ipaexg.ttf", config.font_size - 4)
        self.playBarFont = pygame.font.Font("data/OpenSans-Regular.ttf", 18)

        self.image = {}
        self.image["background"] = pygame.image.load(self.path + "data/background.png")
        self.image["button-play"] = pygame.image.load(self.path + "data/button-play.png")
        self.image["button-pause"] = pygame.image.load(self.path + "data/button-pause.png")
        self.image["button-previous"] = pygame.image.load(self.path + "data/button-previous.png")
        self.image["button-next"] = pygame.image.load(self.path + "data/button-next.png")
        self.image["no-cover"] = pygame.transform.scale(pygame.image.load(self.path + "data/no-cover.png"), (config.coverArtSize, config.coverArtSize))

        self.buttons = {}
        self.buttons["play-pause"] = ImgButton((100, 200), (64, 64), image=self.image["button-play"])
        self.buttons["play-previous"] = ImgButton((30, 200), (64, 64), image=self.image["button-previous"])
        self.buttons["play-next"] = ImgButton((170, 200), (64, 64), image=self.image["button-next"])
        
        self.titleTextBox = ScrollingText("", (20, 20), self.myFont, 440, color=config.title_text_color)
        self.albumTextBox = ScrollingText("", (20, 60), self.myFontReduced, 240, color=config.album_text_color)
        self.artistTextBox = ScrollingText("", (20, 90), self.myFontReduced, 240, color=config.artist_text_color)

        # VOLUME CONTROL
        # self.image["volume-up"] = pygame.image.load(self.path + "data/volume-up.png")
        # self.image["volume-down"] = pygame.image.load(self.path + "data/volume-down.png")
        # self.image["volume-mute"] = pygame.image.load(self.path + "data/volume-mute.png")
        # self.buttons["volume-up"] = ImgButton((395, 200), (64, 64), image=self.image["volume-up"])
        # self.buttons["volume-down"] = ImgButton((265, 200), (64, 64), image=self.image["volume-down"])
        # self.buttons["volume-mute"] = ImgButton((330, 200), (64, 64), image=None)

        # self.image["testbutton-image"] = pygame.image.load(self.path + "data/testbutton.png")
        # self.buttons["testbutton"] = ImgButton((300, 120), (64, 64), image=self.image["testbutton-image"])

    def update(self, mouse_event, currentTime=0):
        self.currentStatus = self.controller.playerStatus()
        currentsong = self.controller.currentSong()
        
        self.mouse_event(mouse_event, currentTime)

        # current song title
        if "title" in currentsong:
            self.currentSongTitle = currentsong["title"]
        else:
            self.currentSongTitle = ""

        # current song artist
        if "artist" in currentsong:
            self.currentSongArtist = currentsong["artist"]
        elif "name" in currentsong:
            self.currentSongArtist = currentsong["name"]
        else:
            self.currentSongArtist = ""
        
        # fetch album cover art
        if "album" in currentsong:
            self.currentAlbum = currentsong["album"]
        else:
            self.currentAlbum = ""
        if not self.currentAlbum == "" and (not self.currentAlbum == self.currentAlbumLast or not self.currentSongArtist == self.currentSongArtistLast):
            self.coverImage = None
        if not self.coverImage:
            if not self.fetchingCover:
                self.fetchingCover = True
                self.coverFetchThread = Thread(target=self.fetchCover)
                self.coverFetchThread.start()
                self.fetchingCoverTimer = 0
        if not self.fetchingCover:
            self.fetchingCoverTimer = self.fetchingCoverTimer + 1
            if self.fetchingCoverTimer > 30:
                self.fetchingCover = True
                self.coverFetchThread = Thread(target=self.fetchCover)
                self.coverFetchThread.start()
                self.fetchingCoverTimer = 0
        
        # VOLUME CONTROL
        # if "volume" in self.currentStatus:
        #     self.currentVolume = int(self.currentStatus["volume"])
        #     if self.currentVolume <= 2 and self.currentVolumeLast > 2:
        #         self.volumePreMute = self.currentVolumeLast
        #         self.buttons["volume-mute"].image = self.image["volume-mute"]
        #     elif self.currentVolume > 2:
        #         self.volumePreMute = -10
        #         self.buttons["volume-mute"].image = None
        # else:
        #     self.currentVolume = -10
        # if not self.currentVolume == self.currentVolumeLast or self.currentVolumeRender == None:
        #     self.currentVolumeRender = self.myFont.render(str(self.currentVolume), True, config.title_text_color)
        #     self.currentVolumeLast = self.currentVolume

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

        
        self.currentSongTitleLast = self.currentSongTitle
        self.currentSongArtistLast = self.currentSongArtist
        self.currentAlbumLast = self.currentAlbum
        self.titleTextBox.setText(self.currentSongTitle)
        self.albumTextBox.setText(self.currentAlbum)
        self.artistTextBox.setText(self.currentSongArtist)
    
    def render(self, surface):
        
        # surface.blit(self.image["background"], (0,0))
        surface.fill((0, 0, 0))

        self.titleTextBox.render(surface)
        self.albumTextBox.render(surface)
        self.artistTextBox.render(surface)

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
            if currentTime[1] == 0:
                surface.fill((0,0,128), rect=(playbarX+2, playbarY + 2 + textSurface.get_height(), int((playbarWidth - 4) / 2), playbarHeight - 4))
            else:
                surface.fill((0,0,128), rect=(playbarX+2, playbarY + 2 + textSurface.get_height(), int((playbarWidth - 4) * currentTime[0] / currentTime[1]), playbarHeight - 4))
        else:
            currentTime = [0, 0]
            textSurface = self.playBarFont.render(str(currentTime[0]), True, (255,255,255))
            surface.fill((255, 255, 255), rect=(playbarX, playbarY + textSurface.get_height(), playbarWidth, playbarHeight))
        
        if self.coverImage:
            surface.blit(self.coverImage, (266, 70))
        else:
            surface.blit(self.image["no-cover"], (266, 70))

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
        
        # VOLUME CONTROL
        # if self.buttons["volume-up"].is_clicked:
        #     if self.buttons["volume-up"].was_clicked:
        #         if self.buttons["volume-up"].time_clicked > 800 + self.volumeUpCounter * 300:
        #             if self.currentVolume > 2:
        #                 volHelp = self.currentVolume + 5
        #                 if volHelp > 100:
        #                     volHelp = 100
        #                 self.controller.setVolume(volHelp)
        #             else:
        #                 if self.volumePreMute > 2:
        #                     self.controller.setVolume(self.volumePreMute)
        #                 else:
        #                     self.controller.setVolume(5)
        #             self.volumeUpCounter = self.volumeUpCounter + 1
        #     else:
        #         if self.currentVolume > 2:
        #             volHelp = self.currentVolume + 5
        #             if volHelp > 100:
        #                 volHelp = 100
        #             self.controller.setVolume(volHelp)
        #         else:
        #             if self.volumePreMute > 2:
        #                 self.controller.setVolume(self.volumePreMute)
        #             else:
        #                 self.controller.setVolume(5)
        # else:
        #     self.volumeUpCounter = 0
        # if self.buttons["volume-down"].is_clicked:
        #     if self.buttons["volume-down"].was_clicked:
        #         if self.buttons["volume-down"].time_clicked > 800 + self.volumeDownCounter * 300:
        #             if self.currentVolume > 2:
        #                 volHelp = self.currentVolume - 5
        #                 if volHelp < 0:
        #                     volHelp = 0
        #                 self.controller.setVolume(volHelp)
        #             self.volumeDownCounter = self.volumeDownCounter + 1
        #     else:
        #         if self.currentVolume > 2:
        #             volHelp = self.currentVolume - 5
        #             if volHelp < 0:
        #                 volHelp = 0
        #             self.controller.setVolume(volHelp)
        # else:
        #     self.volumeDownCounter = 0
        # if self.buttons["volume-mute"].is_clicked and not self.buttons["volume-mute"].was_clicked:
        #     if self.volumePreMute < 2:
        #         # MUTE VOLUME
        #         self.controller.setVolume(0)
        #         self.volumePreMute = self.currentVolume
        #     else:
        #         # UNMUTE
        #         if self.volumePreMute > 2:
        #             self.controller.setVolume(self.volumePreMute)
        #         else:
        #             self.controller.setVolume(50)


        # if self.buttons["testbutton"].is_clicked and not self.buttons["testbutton"].was_clicked:
        #     print(self.currentStatus)
        #     print(self.controller.mpdclient.playlistinfo())
        #     currentsong = self.controller.currentSong()
            # if "album" in currentsong and "artist" in currentsong:
            #     self.coverImage = self.coverCacheServer.fetchCover(album=currentsong["album"], artist=currentsong["artist"])

    def fetchCover(self):
        if config.raspberry:
            try:
                (update, cover) = self.coverCacheServer.fetchCover()
                if update:
                    self.coverImage = cover
                self.fetchingCover = False
            except Exception as e:
                print(e)
                self.fetchingCover = False
        else:
            time.sleep(100)
            self.fetchingCover = False