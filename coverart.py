import pygame, io
from urllib.request import urlopen
import config


class coverCacheServer():

    def __init__(self, logger, cacheFolder="cache"):
        self.logger = logger

        self.lastCoverUrl = ""
        self.lastCover = None
        if config.raspberry:
            urlopen("http://" + config.mpdip)

    def fetchCover(self, force=False):
        cover=None
        coverUrl = ""
        try:
            with open("/var/local/www/currentsong.txt", 'r') as r:
                for l in r:
                    if l.startswith("coverurl="):
                        coverUrl = l.split("coverurl=")[1]
        except Exception as e:
            self.logger.error(e)
        
        if not coverUrl.startswith("/"):
            coverUrl = "/" + coverUrl
        try:
            if (not coverUrl == self.lastCover) or force:
                self.lastCoverUrl = coverUrl
                url = "http://" + config.mpdip + coverUrl

                image_str = urlopen(url).read()
                image_file = io.BytesIO(image_str)
                
                cover = pygame.image.load(image_file)
                cover = pygame.transform.scale(cover, (config.coverArtSize, config.coverArtSize))
                self.lastCover = cover

                return (True, cover)
        except Exception as e:
            self.logger.error("coverServer: download and conversion error: " + str(e))
            return (True, None)
            pass

        return (False, None)
        