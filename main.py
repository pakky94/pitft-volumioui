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

            #self.read_mouse()
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
        # mouse_event = {"x": 0, "y": 0, "touch": 0}
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
        # return(mouse_event)

    def read_mouse(self):
        if config.mouse_type == "pitft_touchscreen":
            while not self.touch.queue_empty():
                for e in self.touch.get_event():
                    


                    # if e["x"] < self.xmin:
                    #     self.xmin = e["x"]
                    # if e["y"] < self.ymin:
                    #     self.ymin = e["y"]
                    # if e["x"] > self.xmax:
                    #     self.xmax = e["x"]
                    # if e["y"] > self.ymax:
                    #     self.ymax = e["y"]
                    
                    """
                    2018-10-23 21:35:24,612 INFO x min: 345
                    2018-10-23 21:35:24,612 INFO x max: 3715
                    2018-10-23 21:35:24,612 INFO y min: 184
                    2018-10-23 21:35:24,613 INFO y max: 3853

                    helpvar = int(e["x"] / 3840 * config.screen_height)
                    e["x"] = config.screen_width - int(e["y"] / 3840 * config.screen_width)
                    e["y"] = helpvar

                    touch_xmin = 345
                    touch_xmax = 3715
                    touch_ymin = 184
                    touch_ymax = 3853
                    """


                    helpvar = int((e["x"] - config.touch_xmin) / (config.touch_xmax - config.touch_xmin) * config.screen_height)
                    e["x"] = config.screen_width - int((e["y"] - config.touch_ymin) / (config.touch_ymax - config.touch_ymin) * config.screen_width)
                    e["y"] = helpvar
                    self.sm.mouse_event(e)
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


        # print("x min: " + str(self.xmin))
        # print("x max: " + str(self.xmax))
        # print("y min: " + str(self.ymin))
        # print("y max: " + str(self.ymax))


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
