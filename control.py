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
            print(self.mpdclient.mpd_version)          # print the MPD version
            print(self.mpdclient.find("any", "house")) # print result of the command "find any house"
            self.logger.info("Connected to MPD server at " + str(ip) + ":" + str(port))
            self.mpdconnected = True
        except Exception as e:
            print(e)

    def currentsong(self):
        if self.mpdconnected:
            return self.mpdclient.currentsong()
        else:
            return {}
    def startPlay(self):
        if self.mpdconnected:
            self.mpdclient.play()
            
    def toggleplay(self):
        if self.mpdconnected:
            self.mpdclient.pause()

    def playerstatus(self):
        if self.mpdconnected:
            return self.mpdclient.status()
        else:
            return {}

    def mpddisconnect(self):
        self.mpdclient.close()                     # send the close command
        self.mpdclient.disconnect()                # disconnect from the server
        self.mpdconnected = False

    def quit(self):
        self.mpddisconnect()