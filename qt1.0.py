import sys
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
import numpy as np


# import hihi
# import azorus

class MainWindow(QMainWindow):  # The main object

    def __init__(self):
        super(MainWindow, self).__init__()
        self.title = "Data Picker"
        self.setWindowTitle(self.title)
        label = QLabel(self)  # the label used to display the image
        # replace line 23 with proper code to obtain array from the camera
        # eg:
        # client = hihi.HTCClient()
        # tem = client.attach('TEM')
        # nav = client.attach('Navigator')
        # AMTCamera = client.attach('NanoSprint5')
        # array = AMTCamera.acquireImage(n_frames=1, tx=0.2)
        array = np.load('data/AMTImage.npy')
        # set the image(pixmap) of the label
        array = np.uint8((array - array.min()) / array.ptp() * 255.0)
        qi = QImage(array.data, array.shape[1], array.shape[0], array.shape[1], QImage.Format_Indexed8)
        qp = QPixmap.fromImage(qi)
        label.setPixmap(qp)
        #self.central = QWidget()
        #self.centralLayout = QVBoxLayout()
        self.label = label
        self.pixmaps = [qp]  # pixmaps store all the pixmaps; the pixmaps in it are resizable
        self.pixmaps_copy = self.pixmaps[:]  # pixmaps_copy is a copy of pixmaps but non-resizable
        self.cur_index = 0  # cur_index tracks the current pixmap the label is using. It's crucial for undo/redo
        self.w = qp.width()  # the original width of the image
        self.h = qp.height()  # the original height of the image
        self.locations = []  # stores the locations of the labels
        self.setCentralWidget(self.label)
        self.setMinimumSize(100, 100*self.h/self.w+30)
        self.scale = 1000/self.w
        self.resize(1000, 1000*self.h/self.w+30)
        self.init_menu()  # setup the menu
        print("original image: ", self.w, "x", self.h)
        print("current size: ", self.width(), "x", self.height()-30)

    def init_menu(self):
        # the shortcut keys would be helpful
        saveAction = QAction("&Save", self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.save)
        loadAction = QAction("&Load", self)
        loadAction.setShortcut('Ctrl+L')
        loadAction.triggered.connect(self.importLabels)
        clearAction = QAction("&Clear All", self)
        clearAction.setShortcut('Ctrl+D')
        clearAction.triggered.connect(self.clearLabels)
        undoAction = QAction("&Undo", self)
        undoAction.setShortcut('Ctrl+Z')
        undoAction.triggered.connect(self.undo)
        redoAction = QAction("&Redo", self)
        redoAction.setShortcut('Ctrl+Y')
        redoAction.triggered.connect(self.redo)
        updateAction = QAction("&Update Labels", self)
        updateAction.setShortcut('Ctrl+U')
        updateAction.triggered.connect(self.updateLabels)
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(saveAction)
        fileMenu.addAction(loadAction)
        fileMenu.addAction(clearAction)
        fileMenu.addAction(undoAction)
        fileMenu.addAction(redoAction)
        fileMenu.addAction(updateAction)
        fileMenu.addAction(exitAction)

    def save(self):
        filename = QFileDialog.getSaveFileName(self, 'Save as csv', '', '*.csv')
        if filename[0]:
            np.savetxt(filename[0], self.locations, delimiter=',')

    def resizeEvent(self, QResizeEvent):

        w = QResizeEvent.size().width()
        h = QResizeEvent.size().height()
        self.pixmaps[0] = self.pixmaps_copy[0].scaled(w, h - 30, Qt.KeepAspectRatio)
        self.updateLabels()
        if self.width() != self.pixmaps[0].width() or self.height()-30 != self.pixmaps[0].height():
            self.resize(self.pixmaps[0].width(), self.pixmaps[0].height()+30)
        self.scale = self.width()/self.w

    def mousePressEvent(self, QMouseEvent):
        x = QMouseEvent.x()
        y = QMouseEvent.y()
        new_pix = self.pixmaps[self.cur_index].copy()
        new_copy = self.pixmaps_copy[self.cur_index].copy()

        if self.cur_index < len(self.locations):
            self.locations = self.locations[:self.cur_index]
            self.pixmaps = self.pixmaps[:self.cur_index + 1]
            self.pixmaps_copy = self.pixmaps_copy[:self.cur_index + 1]
        self.drawLabel(new_pix, x, y, self.cur_index + 1)
        self.drawLabel(new_copy, x/self.scale, y/self.scale, self.cur_index + 1)
        self.locations.append([x/self.scale, (y - 30)/self.scale])
        self.pixmaps.append(new_pix)
        self.pixmaps_copy.append(new_copy)
        self.label.setPixmap(new_pix)
        self.cur_index += 1
        print("Pressed location:", int(self.locations[-1][0]), int(self.locations[-1][1]))

    def drawLabel(self, pixmap, x, y, num):
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.red, 3))
        painter.setFont(QFont('Decorative', 10))
        painter.drawLine(x, y - 5 - 30, x, y + 5 - 30)
        painter.drawLine(x - 5, y - 30, x + 5, y - 30)
        painter.setPen(QPen(Qt.black))
        painter.drawText(x + 5, y - 45, 20, 20, Qt.AlignCenter, str(num))
        painter.end()

    def updateLabels(self):
        pixmap = self.pixmaps[0]
        pixmap_copy = self.pixmaps_copy[0]
        xscale = pixmap.width() / self.w
        yscale = pixmap.height() / self.h
        i = 1
        self.pixmaps = [pixmap]
        self.pixmaps_copy = [pixmap_copy]
        for item in self.locations:
            cur1 = self.pixmaps[len(self.pixmaps) - 1].copy()
            cur2 = self.pixmaps_copy[len(self.pixmaps_copy) - 1].copy()
            self.drawLabel(cur1, item[0] * xscale, item[1] * yscale + 30, i)
            self.drawLabel(cur2, item[0], item[1] + 30, i)
            self.pixmaps.append(cur1)
            self.pixmaps_copy.append(cur2)
            i += 1

        self.label.setPixmap(self.pixmaps[self.cur_index])

    def clearLabels(self):
        self.cur_index = 0
        self.label.setPixmap(self.pixmaps[0])

    def undo(self):
        if self.cur_index > 0:
            self.cur_index -= 1
            self.label.setPixmap(self.pixmaps[self.cur_index])

    def redo(self):
        if self.cur_index < len(self.locations):
            self.cur_index += 1
            self.label.setPixmap(self.pixmaps[self.cur_index])

    def importLabels(self):
        filename = QFileDialog.getOpenFileName(self, 'Open csv file', '', '*.csv')
        if filename[0]:
            w = self.pixmaps[self.cur_index].width()
            h = self.pixmaps[self.cur_index].height()
            self.locations = []
            # self.pixmaps = []
            lst = list(np.loadtxt(open(filename[0], "rb"), delimiter=","))
            if len(lst) > 0:
                for item in lst:
                    self.locations.append(list(item))
                self.pixmaps_copy = [self.pixmaps_copy[0]]
                self.pixmaps = [self.pixmaps_copy[0].scaled(w, h, Qt.IgnoreAspectRatio)]
                self.cur_index = len(self.locations)
            self.updateLabels()


app = QApplication(sys.argv)
# need to change the path
path = r"C:\Users\songg\Anaconda3\Lib\site-packages\PySide2\plugins"
app.addLibraryPath(path)
w = MainWindow()
w.show()
sys.exit(app.exec_())

