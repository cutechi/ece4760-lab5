import sys, logging, signal
from gi.repository import Gtk, Gdk, GLib

from pylib.ildaparser import IldaParser
from pylib.laserviz import LaserViz
from pylib.serialcomm import SerialComm
from pylib.log import init_logging, with_logging

from threading import Thread, Event
from time import sleep


p = IldaParser(sys.argv[1])
if len(sys.argv) > 2:
    port = sys.argv[2]
else:
    port = None

class FramePlayer(Thread):
    def __init__(self, lv, p, ser):
        Thread.__init__(self)
        self.lv = lv
        self.p = p
        self.kill = Event()
        self.FPS = 15
        self.ser = ser
        self.start()

    def stop(self):
        self.kill.set()

    def run(self):
        while True:
            for f in self.p.get_frames():
                self.lv.set_frame(f)
                if self.ser is not None:
                    self.ser.set_frame(f)
                self.kill.wait(1.0/self.FPS)
                if (self.kill.is_set()):
                    return

@with_logging
class MainGUI:

    def window_destroy(self, event):
        Gtk.main_quit()
        self.player.stop()
        if self.serial is not None:
            self.serial.stop()
        self.log.info("Bye!")

    def __init__(self):
        self.gladefile = "pylib/gui.glade"

        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(self)

        self.laserviz = LaserViz(self)

        self.window = self.builder.get_object("mainWindow")
        self.window.show()


        #self.laserviz.set_frame(p.frames[0])
        
        if port is not None:
            self.serial = SerialComm(port)
            self.serial.set_frame(p.frames[0])
            self.serial.start()
        else:
            self.serial = None

        self.player = FramePlayer(self.laserviz, p, self.serial)

        #Ctrl+C handling
        def handler(signum, frame):
            self.log.warning("INTERRUPT; shutting down...")
            self.window_destroy(None)
        signal.signal(signal.SIGTERM, handler)
        signal.signal(signal.SIGINT, handler)

        #This fairly pointless function is necessary to periodically wake up
        #the gtk main thread to detect system interrupts even when not focused
        #I believe this is due to a Gtk bug
        GLib.timeout_add(500, lambda : True)
        
        Gdk.threads_init()
        GLib.threads_init()

        self.log.info("ECE 4760 Laser Projector Controller")
        self.log.info("Starting...")

        Gdk.threads_enter()
        Gtk.main()
        Gdk.threads_leave()


if __name__ == "__main__":
    init_logging(log_level = logging.DEBUG)
    main = MainGUI()
