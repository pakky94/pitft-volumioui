#!/usr/bin/python3
# -*- coding: utf-8 -*-
import datetime
import logging
import os
import sys
import time
from logging.handlers import TimedRotatingFileHandler
import pygame

import config
import daemon
from control import Controller
from pitft_touchscreen import pitft_touchscreen
from ui import PlayerUI


# OS enviroment variables for pitft
if config.raspberry:
    os.environ["SDL_FBDEV"] = config.display_device

dir_path = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger("PiTFT-Playerui logger")
handler = TimedRotatingFileHandler(os.path.join(dir_path, 'pitft-playerui.log') ,when="midnight",interval=1,backupCount=14)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

try: 
	if config.loglevel == "DEBUG":
		loglevel = logging.DEBUG
		logger.setLevel(loglevel)
	else:
		logger.setLevel(logging.INFO)
except:
	logger.setLevel(logging.INFO)

logger.info("pitft-VolumioUI log")

class PitftDaemon(daemon.Daemon):

    def setup(self):
        
        logger.info("Starting setup")

        if config.mouse_type == "pitft_touchscreen":
            self.touch = pitft_touchscreen()
            self.touch.start()

        self.controller = Controller(logger)
        
        pygame_init_done = False
        while not pygame_init_done:
            try:
                pygame.init()
                if config.raspberry:
                    pygame.mouse.set_visible(False)
                pygame_init_done = True
            except:
                logger.debug("Pygame init failed")
                pygame_init_done = False
                time.sleep(5)
        
        size = config.screen_width, config.screen_height
        if config.screen_fullscreen:
            logger.debug("Pygame init Fullscreen")
            self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        else:
            logger.debug("Pygame init Windowed")
            self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption('pitft-volumioui')
        

        self.sm = PlayerUI(logger, controller=self.controller)


        self.mouse_event = {"x": 0, "y": 0, "touch": 0}


        # self.xmin = 5000
        # self.ymin = 5000
        # self.xmax = -1000
        # self.ymax = -1000

    def run(self):
        self.setup()
        self.sm.load()
        self.running = True
        
        mpdreconnecttimer = 0
        try:
            self.controller.mpdconnect(config.mpdip, config.mpdport)
        except Exception as e:
            print(e)


        logger.debug("Initialization complete")
        clock = pygame.time.Clock()
        while self.running:
            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:
            #         crashed = True

                # print(event)
            if self.controller.mpdconnected:
                pass
            else:
                mpdreconnecttimer = mpdreconnecttimer + 1
                if mpdreconnecttimer > 300:
                    logger.info("Retry connection to MPD server...")
                    mpdreconnecttimer = 0
                    self.controller.mpdconnect(config.mpdip, config.mpdport)

            currentTime = pygame.time.get_ticks()
            self.update_mouse()
            self.sm.update(self.mouse_event, currentTime)
            self.sm.render(self.screen)

            pygame.display.update()
            clock.tick(15)
        # while True:
        #     time.sleep(1)
        #     pass

    def update_mouse(self):
        if config.mouse_type == "pitft_touchscreen":
            self.mouse_event["touch"] = 0
            while not self.touch.queue_empty():
                for e in self.touch.get_event():
                    self.mouse_event["x"] = config.screen_width - int((e["y"] - config.touch_ymin) / (config.touch_ymax - config.touch_ymin) * config.screen_width)
                    self.mouse_event["y"] = int((e["x"] - config.touch_xmin) / (config.touch_xmax - config.touch_xmin) * config.screen_height)
                    self.mouse_event["touch"] = 1
        elif config.mouse_type == "pygame":
            for e in pygame.event.get():
                if e.type == pygame.MOUSEMOTION:
                    self.mouse_event["x"] = e.pos[0]
                    self.mouse_event["y"] = e.pos[1]
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_event["x"] = e.pos[0]
                    self.mouse_event["y"] = e.pos[1]
                    self.mouse_event["touch"] = 1
                elif e.type == pygame.MOUSEBUTTONUP:
                    self.mouse_event["x"] = e.pos[0]
                    self.mouse_event["y"] = e.pos[1]
                    self.mouse_event["touch"] = 0

    def quit(self):
        logger.info("Quitting...")
        if config.mouse_type == "pitft_touchscreen":
            self.touch.stop()
        logger.info("Quit")        
        time.sleep(0.2)
        running = False
        pygame.quit()


def main():
    mydaemon = PitftDaemon(logger=logger)

    if len(sys.argv) > 1:
        if 'start' == sys.argv[1]:
            mydaemon.start()
        elif 'stop' == sys.argv[1]:
            mydaemon.stop()
        elif 'restart' == sys.argv[1]:
            mydaemon.restart()
        elif ('control' == sys.argv[1] or 'c' ==sys.argv[1]) and len(sys.argv) == 3:
            #mydaemon.control(sys.argv[2])
            pass
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart|control <command>" % sys.argv[0])
        sys.exit(2)

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())
    
    def flush(self):
        pass

if __name__ == "__main__":
    if config.loglevel == "DEBUG":
        try:
            main()
        except Exception as e:
            logger.info(e)
            raise
    else:
        main()
