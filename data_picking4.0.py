from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
import numpy as np
from PIL import Image, ImageTk
import csv
#import hihi
#import azorus


root = Tk()
root.title("Data Picking")
#root.geometry('400x400')
#client = hihi.HTCClient()
#tem = client.attach('TEM')
#nav = client.attach('Navigator')
#AMTCamera = client.attach('NanoSprint5')
#array = AMTCamera.acquireImage(n_frames=1, tx=0.2)

#array = np.array(Image.open('test2.jpg'))
array = np.load('data/AMTImage.npy')
array = np.uint8((array - array.min()) / array.ptp() * 255.0)

class MyCanvas(Canvas):
    def __init__(self, master):
        Canvas.__init__(self, master, bd=0,highlightthickness=0)
        self.image = Image.fromarray(array)
        self.img_copy = self.image.copy()
        self.background_image = ImageTk.PhotoImage(self.image)
        self.org_size = (self.background_image.width(), self.background_image.height())
        self.cur = self.create_image(0, 0, anchor=NW, image=self.background_image)
        self.xscale = 1
        self.yscale = 1
        self.bind('<Configure>', self._resize_image)
        self.bind('<Button>', self._mouse_click)
        self.locations = []
        self.labels = []
        self.arrows = []

    def _resize_image(self, event):
        new_width = event.width
        new_height = event.height
        self.xscale = new_width/self.org_size[0]
        self.yscale = new_height/self.org_size[1]

        self.image = self.img_copy.resize((new_width, new_height))
        self.background_image = ImageTk.PhotoImage(self.image)
        self.itemconfig(self.cur, image=self.background_image)

        for i in range(0, len(self.locations)):
            self.coords(self.arrows[i], (self.locations[i][0]*self.xscale+0.5, self.locations[i][1]*self.yscale-1))
            self.labels[i].place(x=self.locations[i][0]*self.xscale+6, y=self.locations[i][1]*self.yscale-16)
            #self.locations[i][0] = self.locations[i][0]*self.xscale
            #self.locations[i][1] = self.locations[i][1]*self.yscale
        self.height = new_height
        self.width = new_width
        print(self.locations)
    def _mouse_click(self, event):
        self.locations.append([event.x/self.xscale, event.y/self.yscale])
        arrow = self.create_text(event.x + 0.5, event.y - 1, text='+', fill='red', tags=str(len(self.locations)), anchor='center')
        self.arrows.append(arrow)
        label = Label(self, text=str(len(self.locations)))
        label.place(x=event.x + 6, y=event.y - 16)
        self.labels.append(label)
        print(self.locations)


def setupMenu(root):
    menubar = Menu(root)
    menu = Menu(menubar, tearoff=0)
    menu.add_command(label="Save as txt", command=saveLabels)
    menu.add_command(label="Save as csv", command=save_csv)
    menu.add_command(label="Import text file", command=importTxt)
    menu.add_command(label="Import csv file", command=importCsv)
    menu.add_separator()
    menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=menu)
    menubar.add_command(label="Undo", command=undo)
    menubar.add_command(label="Clear All", command=clearLabels)
    root.config(menu=menubar)


def saveLabels():
    filename = asksaveasfilename(defaultextension='.txt', filetypes=[("text files", '*.txt')], title="save file")
    if len(filename) > 0:
        f = open(filename, "w")
        f.write("width="+str(mycanvas.org_size[0])+"; height="+str(mycanvas.org_size[1])+"\n")
        f.write("x y\n")
        for item in mycanvas.locations:
            f.write(str(int(item[0])) + " " + str(int(item[1])) + "\n")
        f.close()
    print(mycanvas.locations)


def save_csv():
    filename = asksaveasfilename(defaultextension='.csv', filetypes=[("csv files", '*.csv')], title="save file")
    #print(filename)
    np.savetxt(filename, mycanvas.locations, delimiter=',')


def clearLabels():
    mycanvas.locations.clear()
    for item in mycanvas.labels:
        item.destroy()
    for item in mycanvas.arrows:
        mycanvas.delete(item)
    mycanvas.labels.clear()
    mycanvas.arrows.clear()


def undo():
    length = len(mycanvas.labels)
    if length > 0:
        mycanvas.locations.pop()
        mycanvas.labels[length-1].destroy()
        mycanvas.labels.pop()
        mycanvas.delete(mycanvas.arrows[length - 1])
        mycanvas.arrows.pop()


def importTxt():
    filename = askopenfilename(filetypes=[("text files", '*.txt')], title="Choose file")
    if len(filename) > 0:
        clearLabels()
        f = open(filename, "r")
        f.readline()
        f.readline()

        for line in f:
            loc = line.split(" ")
            x = float(loc[0])
            y = float(loc[1])
            mycanvas.locations.append([x, y])
            arrow = mycanvas.create_text(x * mycanvas.xscale + 0.5, y * mycanvas.yscale - 1, text='+',
                                         fill='red',
                                         anchor='center')
            mycanvas.arrows.append(arrow)
            label = Label(mycanvas, text=str(len(mycanvas.locations)))
            label.place(x=x * mycanvas.xscale + 6, y=y * mycanvas.yscale - 16)
            mycanvas.labels.append(label)

def importCsv():
    filename = askopenfilename(filetypes=[("csv", '*.csv')], title="Choose file")
    if len(filename) > 0:
        clearLabels()
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in reader:
                loc = row[0].split(",")
                x = float(loc[0])
                y = float(loc[1])
                mycanvas.locations.append([x, y])
                arrow = mycanvas.create_text(x * mycanvas.xscale + 0.5, y * mycanvas.yscale - 1, text='+',
                                             fill='red',
                                             anchor='center')
                mycanvas.arrows.append(arrow)
                label = Label(mycanvas, text=str(len(mycanvas.locations)))
                label.place(x=x * mycanvas.xscale+6, y=y * mycanvas.yscale-16)
                mycanvas.labels.append(label)
        print(mycanvas.locations)
"""
        for line in f:
            loc = line.split(" ")
            x = float(loc[0])
            y = float(loc[1])
            mycanvas.locations.append([x, y])
            arrow = mycanvas.create_text((x + 0.5) * mycanvas.xscale, (y - 1) * mycanvas.yscale, text='+', fill='red',
                                         anchor='center')
            mycanvas.arrows.append(arrow)
            label = Label(mycanvas, text=str(len(mycanvas.locations)))
            label.place(x=(x + 6) * mycanvas.xscale, y=(y - 16) * mycanvas.yscale)
            mycanvas.labels.append(label)"""

mycanvas = MyCanvas(root)
#print(mycanvas.width, mycanvas.height)
root.geometry(str(int(mycanvas.org_size[0]*0.5))+'x'+str(int(mycanvas.org_size[1]*0.5)))
#print(str(int(mycanvas.width*0.5)), str(int(mycanvas.height*0.5)))
mycanvas.pack(fill=BOTH, expand=YES)
setupMenu(root)
root.mainloop()