import tkinter as tk
from PIL import Image, ImageTk
from time import time
import numpy as np

root = tk.Tk()
root.geometry('100x100')

canvas = tk.Canvas(root, width=100, height=100, bg="black")
canvas.place(x=0, y=0, anchor='nw')

root.bind('u', lambda e: switch_use_img())
def switch_use_img():
    global use_image
    use_image = not use_image

use_image = False

clr = "#"+("%06x"%int(np.random.default_rng(42).random()*16777215))
img = Image.new('RGBA', (28, 42), (*bytes.fromhex(clr[1:]), 255))
image = ImageTk.PhotoImage(img)


def update():
    canvas.delete('all')
    t = time()
    if use_image:
        for _ in range(5000):
            canvas.create_image(50, 50, anchor='c', image=image)
    else:
        for _ in range(5000):
            canvas.create_rectangle(50-14, 50-21, 50+14, 50+21, fill=clr, width=0)
    
    print(f"{'image' if use_image else 'rectangle'}:", (time()-t))
    
    dt = 1000//20 - int((time() - t)*10**3) # 20 : FPS
    print(dt)
    root.after(max(dt, 1), update)

update()
root.mainloop()
