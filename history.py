"""
Suorittaa vieritettävän ikkunan pelihistorian katsomista varten.
Malli koodiin: youtube.com/watch?v=7rZ_6LFcGX8 (Python GUI Tutorial - 33 - Scrollbar|Tkinter, by Tech-Gram Academy)
"""

from tkinter import *

def listbox():
    root = Tk()

    frame = Frame(root)

    scroll = Scrollbar(frame)
    scroll.pack(side=RIGHT, fill=BOTH)

    listbox = Listbox(frame, yscrollcommand= scroll.set, width=50)

    with open("stats.txt") as file:
        listings = file.read().split('\n')

    for i in range(len(listings)):
        listbox.insert(END, listings[i - 1])
    listbox.pack(side=LEFT)

    frame.pack()
    scroll.config(command=Listbox.yview)
    root.mainloop()
