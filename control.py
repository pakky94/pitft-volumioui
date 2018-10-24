from mpd import MPDClient

class Controller():
    
    def __init__(self, logger):
        self.logger = logger
        self.mpdclient = MPDClient()
        self.mpdclient.timeout = 10
        self.mpdclient.idletimeout = None # timeout for fetching the result of the idle command is handled seperately, default: None

        self.mpdconnected = False
    
    def mpdconnect(self, ip, port):
        try:
            self.mpdclient.connect(ip, port)  # connect to localhost:6600
            self.logger.info("Connected to MPD server at " + str(ip) + ":" + str(port))
            self.mpdconnected = True
        except Exception as e:
            print(e)

    def currentSong(self):
        if self.mpdconnected:
            return self.mpdclient.currentsong()
        else:
            return {}

    def startPlay(self):
        if self.mpdconnected:
            self.mpdclient.play()

    def playPrevious(self):
        if self.mpdconnected:
            try:
                status = self.mpdclient.status()
                if int(status["time"].split(':')[0]) < 3:
                    self.mpdclient.previous()
                else:
                    self.mpdclient.seekcur(0)
            except Exception as e:
                self.logger.error(e)
    
    def playNext(self):
        if self.mpdconnected:
            try:
                self.mpdclient.next()
            except Exception as e:
                self.logger.error(e)
            
    def toggleplay(self):
        if self.mpdconnected:
            self.mpdclient.pause()

    def playerStatus(self):
        if self.mpdconnected:
            return self.mpdclient.status()
        else:
            return {}
    
    def setVolume(self, volume):
        if self.mpdconnected:
            try:
                self.mpdclient.setvol(volume)
            except Exception as e:
                self.logger.error(e)

    def mpdDisconnect(self):
        self.mpdclient.close()                     # send the close command
        self.mpdclient.disconnect()                # disconnect from the server
        self.mpdconnected = False

    def quit(self):
        self.mpdDisconnect()