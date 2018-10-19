import logging
import os
import sys
import time

import pygame

import config
import daemon

os.environ["SDL_FBDEV"] = config.display_device

class PitftDaemon(daemon.Daemon):

    def setup(self):

        pygame_init_done = False
        while not pygame_init_done:
            try:
                pygame.init()
                pygame_init_done = True
            except:
                # logger.debug("Pygame init failed")
                pygame_init_done = False
                time.sleep(5)
        
        size = config.screen_width, config.screen_height
        if config.scree_fullscreen:
            self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption('pitft-volumioui')
        
        pass

    def run(self):
        self.setup()
        self.running = True
        
        clock = pygame.time.Clock()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    crashed = True

                # print(event)
            self.screen.fill((255,255,0))

            pygame.display.update()
            clock.tick(60)
        # while True:
        #     time.sleep(1)
        #     pass

    def quit(self):
        running = False
        pygame.quit()
        time.sleep(0.2)
        pass



def main():
    daemon = PitftDaemon()

    if len(sys.argv) > 1:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif ('control' == sys.argv[1] or 'c' ==sys.argv[1]) and len(sys.argv) == 3:
            #daemon.control(sys.argv[2])
            pass
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart|control <command>" % sys.argv[0])
        sys.exit(2)

if __name__ == "__main__":
    main()
