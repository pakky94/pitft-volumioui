import pygame, os, logging
from ui import PlayerUI
from logging.handlers import TimedRotatingFileHandler

print("safd")
dir_path = os.path.dirname(os.path.realpath(__file__))
# if not os.path.isdir (os.path.join(dir_path, 'log')):
# 	os.mkdir(os.path.join(dir_path, 'log'))
logger = logging.getLogger("Test-PiTFT-Playerui logger")
handler = TimedRotatingFileHandler(os.path.join(dir_path, 'test-pitft-playerui.log') ,when="midnight",interval=1,backupCount=14)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
logger.info("pitft-VolumioUI log")

print("2")

sm = PlayerUI(logger)
