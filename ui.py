from PyQt5 import QtCore, Qt
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QComboBox, 
    QHBoxLayout, QVBoxLayout, QGridLayout, QAction, QFrame, QLCDNumber, QSpinBox)
from PyQt5.QtGui import QIcon, QColor 
from typing import List, Set
from itertools import cycle, islice, dropwhile

basicNotes: List[str] = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
notesCycle = cycle(basicNotes)
standardTuning: List[str] = ['E', 'A', 'D', 'G', 'B', 'E']

buttonWidth = 45
col0Width = 60

class FretButton(QPushButton):
    __parentLayout = None

    def setParentLayout(self, layout):
        self.__parentLayout = layout

    def getParentLayout(self):
        return self.__parentLayout

class Fret():
    def __init__(self, noteName: str):

        self.subscribers: List[String] = []
        self.noteName: str = noteName
        #self.parentString: String = parentString
        self.button = FretButton(self.noteName)
        self.button.setFixedWidth(buttonWidth)
        self.button.setCheckable(True)
        #self.button.setStyleSheet("QPushButton:checked { background-color: red;border:5px solid rgb(255, 170, 255); }")
        self.button.setStyleSheet("QPushButton:checked { background-color: #adaddf;} QPushButton { border-radius: 10px; }")
        self.button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button.clicked[bool].connect(self.notifyNoteToggle)

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)
    
    def notifyNoteToggle(self, checked: bool):
        for subscriber in self.subscribers:
           subscriber.notifyNoteToggle(self.noteName, checked)

class String():
    def __init__(self, index: int, noteName: str, numberFrets: int):
       self.subscribers: FretBoard = []
       self.stringIndex: int = index
       self.noteName: str = noteName
       self.noteSelector = self.newNoteSelector()
       self.frets: List[Fret] = []
       self.addFrets(numberFrets + 1)
       self.numberFrets: int = numberFrets

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def drawString(self, hbox1: QHBoxLayout):
        for i, fret in enumerate(self.frets):
            hbox1.addWidget(fret.button)
            fret.button.setParentLayout(hbox1)
            vLine = newVLine(i)
            hbox1.addWidget(vLine)
            #vLine.setLayout(hbox1)

    def newNoteSelector(self):
        comboBox = QComboBox()
        comboBox.addItems(basicNotes)
        index = comboBox.findText(self.noteName, QtCore.Qt.MatchFixedString)
        comboBox.setCurrentIndex(index)
        comboBox.setFixedWidth(col0Width)
        comboBox.currentIndexChanged.connect(self.changeBaseNoteByIndex)
        return comboBox

       
    def addFrets(self, numberFrets: int):
        startNote = dropwhile(lambda x: x != self.noteName, notesCycle)
        notesInString = islice(startNote, None, numberFrets)
        for note in notesInString:
            fret: Fret = Fret(note)
            for subscriber in self.subscribers:
                if fret.noteName in subscriber.markedNotes:
                    fret.button.setChecked(True)
            fret.subscribe(self)
            self.frets.append(fret)

    def changeBaseNote(self, noteName: str):
        index = self.noteSelector.findText(noteName, QtCore.Qt.MatchFixedString)
        self.noteSelector.setCurrentIndex(index)

    def changeBaseNoteByIndex(self, i: int):
        self.noteName = basicNotes[i]
        self.redrawString(self.stringIndex)
        

    def redrawString(self, stringIndex: int):
        layout = self.frets[0].button.getParentLayout()
        for i in reversed(range(1, layout.count())): 
            layout.itemAt(i).widget().setParent(None)
        self.frets.clear()
        self.addFrets(self.numberFrets + 1)
        self.drawString(layout)
        #for fret in reversed(self.frets): 
        #    fret.button.setParent(None)
        #for subscriber in self.subscribers:
        #    subscriber.redrawString(stringIndex)

    def notifyNoteToggle(self, noteName: str, checked: bool):
        for subscriber in self.subscribers:
            subscriber.toggleNoteGlobal(noteName, checked)

class FretBoard():
    def __init__(self, tuning: List[str], numberFrets: int):
        self.tuning: List[str] = tuning
        self.strings: List[String] = []
        self.numberFrets: int = numberFrets
        self.markedNotes: Set[str] = set()
        self.subscribers: List[QHBoxLayout] = []

        for i, noteName in enumerate(reversed(tuning)):
            string: String = String(i, noteName, numberFrets)
            string.subscribe(self)
            self.strings.append(string)

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def redrawString(self, stringIndex: int):
        for subscriber in self.subscribers:
           subscriber.redrawString(stringIndex)
    
    def toggleNoteGlobal(self, noteName: str, checked: bool):
        if checked:
            self.markedNotes.add(noteName)
        else:
            self.markedNotes.remove(noteName)

        for string in self.strings:
            for fret in string.frets:
                if fret.button.text() == noteName:
                    fret.button.setChecked(checked)  

    def clearAll(self):
        for string in self.strings:
            for fret in string.frets:
                fret.button.setChecked(False)  

    def setTuning(self, tuning: List[str]):
        self.tuning = tuning
        for string, noteName in zip(reversed(self.strings), self.tuning):
            string.changeBaseNote(noteName)

    def resetTuning(self):
        self.setTuning(standardTuning)
        

def newVLine(i: int):
    frameColor = QColor("#ff00ff")
    line = QFrame()
    #line.setFrameStyle(QFrame.VLine | QFrame.Plain)
    line.setFrameShape(QFrame.VLine)
    line.setLineWidth(3)
    line.setMidLineWidth(8)
    if i == 0:
       line.setMinimumSize(8,8)
    else:
       line.setMinimumSize(3,3)
    line.setStyleSheet("QWidget { background-color: %s; } " % frameColor.name())
    return line

def newFretLabel(i: int):
    number = str(i) if i > 0 else " "
    label1 = QLabel(number)
    label1.setFixedWidth(buttonWidth)
    label1.setAlignment(Qt.Qt.AlignCenter)
    label1.setStyleSheet("background-color: #ffffff;")
    return label1 

class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.stringsLayout = QVBoxLayout()
        self.initUI()

    def createFretboard(self, vbox1):
        numberFrets = 24
        self.fretBoard = FretBoard(standardTuning, numberFrets)
        self.fretBoard.subscribe(self)
    

        fretLabelsTop = QHBoxLayout()
        fretLabelsBottom = QHBoxLayout()

        col0Top = QLabel("")
        col0Top.setFixedWidth(col0Width)
        fretLabelsTop.addWidget(col0Top)
        col0Bottom = QLabel("")
        col0Bottom.setFixedWidth(col0Width)
        fretLabelsBottom.addWidget(col0Bottom)

        #it = fretLabelsTop.itemAt(0)
        for i in range(numberFrets + 1):
            fretLabelsTop.addWidget(newFretLabel(i))
            fretLabelsTop.addWidget(newVLine(i))

            fretLabelsBottom.addWidget(newFretLabel(i))
            fretLabelsBottom.addWidget(newVLine(i))

        vbox1.addLayout(fretLabelsTop)
        for string in self.fretBoard.strings:
            hbox1 = QHBoxLayout()

            hbox1.addWidget(string.noteSelector)
            
            string.drawString(hbox1)

            self.stringsLayout.addLayout(hbox1)
        vbox1.addLayout(self.stringsLayout)
        vbox1.addLayout(fretLabelsBottom)

    def redrawString(self, stringIndex: int):
        stringLayout = self.stringsLayout.itemAt(stringIndex).widget()
        for i in reversed(range(stringLayout.count())): 
            stringLayout.itemAt(i).widget().setParent(None)
        

        
    def initUI(self):
        
        self.col = QColor(0, 0, 0)

        container = QHBoxLayout()
        vbox1 = QVBoxLayout()

        hboxControls = QHBoxLayout()

        self.pbClearAll = QPushButton("Clear all")
        hboxControls.addWidget(self.pbClearAll)
        self.pbSetTuning = QPushButton("Reset tuning")
        hboxControls.addWidget(self.pbSetTuning)

        vbox1.addLayout(hboxControls)
        self.createFretboard(vbox1)
        self.pbClearAll.clicked.connect(self.fretBoard.clearAll)
        self.pbSetTuning.clicked.connect(self.fretBoard.resetTuning)

        self.setLayout(vbox1)    
        self.show()

