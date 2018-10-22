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
os.environ["SDL_FBDEV"] = config.display_device

dir_path = os.path.dirname(os.path.realpath(__file__))
# if not os.path.isdir (os.path.join(dir_path, 'log')):
# 	os.mkdir(os.path.join(dir_path, 'log'))
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

        try:
            self.controller.mpdconnect()
        except Exception as e:
            print(e)
        
        pygame_init_done = False
        while not pygame_init_done:
            try:
                pygame.init()
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

    def run(self):
        self.setup()
        self.sm.load()
        self.running = True
        
        mpdreconnecttimer = 0
        self.controller.mpdconnect(config.mpdip, config.mpdport)


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

            self.read_mouse()
            self.sm.update()
            self.sm.render(self.screen)

            pygame.display.update()
            clock.tick(30)
        # while True:
        #     time.sleep(1)
        #     pass

    def read_mouse(self):
        if config.mouse_type == "pitft_touchscreen":
            while not self.touch.queue_empty():
                for e in self.touch.get_event():
                    e["x"] = int(e["x"] / 10)
                    e["y"] = int(e["y"] / 10)
                    self.sm.mouse_event(e)
                    print(e)
        elif config.mouse_type == "pygame":
            for event in pygame.event.get():
                if event.type == pygame.MOUSEMOTION:
                    self.sm.mouse_event({"x": event.pos[0], 
                                        "y": event.pos[1],
                                        "touch": 0
                                        }) 
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.sm.mouse_event({"x": event.pos[0], 
                                        "y": event.pos[1],
                                        "touch": 1
                                        })
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.sm.mouse_event({"x": event.pos[0], 
                                        "y": event.pos[1],
                                        "touch": 0
                                        })

    def quit(self):
        logger.info("Quitting...")
        if config.mouse_type == "pitft_touchscreen":
            self.touch.stop()
        logger.info("Quit")        
        time.sleep(0.2)
        running = False
        pygame.quit()



def main():
    # # stdout_logger = logging.getLogger('STDOUT')
    # # stdo = StreamToLogger(stdout_logger, logging.INFO)
    # stdo = StreamToLogger(logger, logging.INFO)
    # # stderr_logger = logging.getLogger('STDERR')
    # # sdte = StreamToLogger(stderr_logger, logging.ERROR)
    # stde = StreamToLogger(logger, logging.DEBUG)

    # mydaemon = PitftDaemon(stdout=os.path.join(dir_path, 'stdout.log'), stderr=os.path.join(dir_path, 'stderr.log'))
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

if __name__ == "__main__":
    if config.loglevel == "DEBUG":
        try:
            main()
        except Exception as e:
            logger.info(e)
            raise
    else:
        main()
