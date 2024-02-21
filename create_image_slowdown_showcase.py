import tkinter as tk
from PIL import Image, ImageTk

# from time import _time
import numpy as np

from time import time_ns as _time

####            FROM OTHER AREAS START          ####

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Timers(metaclass = Singleton):
    MAX_SIZE = 1000
    TIMERS = ("FPS",)

    def __init__(self):
        self.timers = {}
        self.timestamps = {}
        self.iterators = {}

        for name in Timers.TIMERS:
            self._add_timer( name )

    ###
    #  Private methods
    ###
    def _store(self, timer, time):
        if len( self.timers[timer] ) < Timers.MAX_SIZE:
            self.timers[timer].append( time )
        else:
            self.timers[timer][ self.iterators[timer] ] = time
        self.iterators[timer] = ( self.iterators[timer] + 1 ) % Timers.MAX_SIZE

    def _get_range(self, timer, a, b):
        # get range [a, b) == timer[a:b]
        if a < 0: # wraps around end of list
            return self.timers[timer][a:] + self.timers[timer][:b]
        else:
            return self.timers[timer][a:b]
    
    def _add_timer(self, timer):
        self.timers[timer]     = []
        self.timestamps[timer] = None
        self.iterators[timer]  = 0

    ###
    #  Public methods
    ###
    def is_valid(self, timer):
        return timer in self.timers and len(self.timers[timer]) > 0

    def get_count(self, timer):
        if self.is_valid(timer):
            return len(self.timers[timer])
        return 0

    def get_last(self, timer):
        if self.is_valid(timer):
            return self.timers[timer][ self.iterators[timer]-1 ]
        return 0.0

    def get_mean(self, timer, n=None):
        if self.is_valid(timer):
            length = len(self.timers[timer])
            if n is None or n >= length:
                return sum(self.timers[timer]) / length
            else: # if n < length
                stop = self.iterators[timer]
                start = stop - n
                vals = self._get_range(timer, start, stop)
                return sum( vals ) / n
        return 0.0

    def update(self, timer):
        if timer in Timers.TIMERS:
            t = _time()
            if self.timestamps[timer] is not None:
                dt = t - self.timestamps[ timer ]
                self._store( timer, dt * 10**-6 ) # save as ms
            self.timestamps[ timer ] = t

    def start(self, timer):
        if timer in Timers.TIMERS:
            self.timestamps[timer] = None # invalidate last timestamp so self.update() does not store deltaTime
            self.update(timer)

    def stop(self, timer):
        self.update(timer)






class Constants():
    X_DIM = 28      # CONFIGURABLE (default: 28)
    Y_DIM = 42      # CONFIGURABLE (default: 42)

    X_TILES = 35    # CONFIGURABLE (default: 35)
    Y_TILES = 17    # CONFIGURABLE (default: 17)
    Z_TILES = 1     # CONFIGURABLE (default: 1)

    X_PIXELS = X_DIM * X_TILES
    Y_PIXELS = Y_DIM * Y_TILES

    FPS = 20        # CONFIGURABLE (default: 20)
    USE_IMAGE = True

    @staticmethod
    def switch_use_image():
        Constants.USE_IMAGE = not Constants.USE_IMAGE
        print(f"Switched to {Constants.USE_IMAGE}")

def calculate_coords(x, y):
    return x, y, x + Constants.X_DIM, y + Constants.Y_DIM

####            FROM OTHER AREAS END    ####


####            MAIN PART START         ####
rng = np.random.default_rng(42)

class Tile():
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.clr = "#"+("%06x"%int(rng.random()*16777215))

        img = Image.new('RGBA', (Constants.X_DIM, Constants.Y_DIM), (*bytes.fromhex(self.clr[1:]), 255))
        self.image = ImageTk.PhotoImage(img)

    def paint(self, canvas):
        if Constants.USE_IMAGE:
            canvas.create_image(self.x, self.y, anchor='nw', image=self.image)
        else:
            canvas.create_rectangle(*calculate_coords(self.x, self.y), fill=self.clr, width=0)

class Main():
    def __init__(self, parent):
        self.parent = parent

        self.tiles = np.zeros((Constants.X_TILES, Constants.Y_TILES, Constants.Z_TILES), dtype='object')
        self.init_tiles()

        self.createGUI()

    def init_tiles(self):
        for x in range(Constants.X_TILES):
            for y in range(Constants.Y_TILES):
                for z in range(Constants.Z_TILES):
                    self.tiles[x, y, z] = Tile(x*Constants.X_DIM, y*Constants.Y_DIM)
        

    def createGUI(self):
        self.parent.title('Showcase')
        self.parent.geometry("1430x800")

        self.canvas = tk.Canvas(self.parent, width=Constants.X_PIXELS, height=Constants.Y_PIXELS, bg='black', highlightthickness=1)
        self.canvas.place(x=15, y=15, anchor='nw')

        self.canvas.bind('u', lambda e: Constants.switch_use_image())
        self.canvas.focus_set()

        self.parent.after(1, self.update)

    def update(self):
        t = _time()

        self.paint()

        print(f"Update time: {(_time()-t) * 10**-6:.5f} ms")

        t = int((_time() - t) * 10**-6)
        dt = 1000//Constants.FPS - t
        # print(f"after delay: {max(dt, 1)}")
        self.parent.after(max(dt, 1), self.update)

    def paint(self):
        Timers().update('FPS')
        fps_count = Timers().get_count('FPS')
        if fps_count > 0 and ( fps_count % Constants.FPS ) == 0:
            fps = 1000. / Timers().get_mean('FPS', n = Constants.FPS)
            print('FPS: %.1f' % (fps))

        try:
            self.canvas.delete('!keep')
        except tk._tkinter.TclError as e: # this means you exited the game
            # raise e
            quit()

        for x in range(Constants.X_TILES):
            for y in range(Constants.Y_TILES):
                for z in range(Constants.Z_TILES):
                    self.tiles[x, y, z].paint(self.canvas)
    
    def start(self):
        self.parent.mainloop()


####            MAIN PART END               ####

main = Main(tk.Tk())
main.start()