raspberry = True

display_device = "/dev/fb1"
mouse_device = "/dev/input/event0"
mouse_driver = "TSLIB"
if raspberry:
    mouse_type = "pitft_touchscreen"
    touch_xmin = 345
    touch_xmax = 3715
    touch_ymin = 184
    touch_ymax = 3853
else:
    mouse_type = "pygame"

if raspberry:
    screen_fullscreen = True
else:
    screen_fullscreen = False
screen_width = 480
screen_height = 320

loglevel = "DEBUG"

if raspberry:
    mpdip = "127.0.0.1"
    mpdport = 6600
else:
    mpdip = "192.168.1.201"
    mpdport = 6600


font = "Comic Sans MS"
font_size = 32
title_text_color = (255, 255, 255)
album_text_color = (255, 255, 255)
artist_text_color = (255, 255, 255)

coverArtSize = 196