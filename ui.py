from PyQt5 import QtCore, Qt
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QComboBox, 
    QHBoxLayout, QVBoxLayout, QGridLayout, QAction, QFrame, QLCDNumber, QSpinBox)
from PyQt5.QtGui import QIcon, QColor 
from typing import List, Set, Dict
from itertools import cycle, islice, dropwhile

basicNotes: List[str] = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
notesCycle = cycle(basicNotes)
standardTuning: List[str] = ['E', 'A', 'D', 'G', 'B', 'E']

intervalsDict: Dict[str, int] = { '1': 0,
                               'b2': 1,
                               '2': 2,
                               '#2': 3,
                               'b3': 3,
                               '3': 4,
                               '4': 5,
                               '#4': 6,
                               'b5': 6,
                               '5': 7,
                               '#5': 8,
                               '6': 9,
                               'b7': 10,
                               '7': 11,
                             }

scalesGlobal: Dict[str, List[str]] = {
        'Melodic Minor': ['1', '2', 'b3', '4', '5', '6', '7'],
}

melodicMinor: List[str] = ['1', '2', 'b3', '4', '5', '6', '7']

buttonWidth = 45
col0Width = 60

class Scale():
    def __init__(self, notes: int):
        self.notes = []
  

class FretButton(QPushButton):
    __parentLayout = None
    rightClicked = QtCore.pyqtSignal(bool)
    middleClicked = QtCore.pyqtSignal(bool)

    def __init__(self, QWidget):
        super().__init__(QWidget)
        self.individualMarked: bool = False

    def mousePressEvent (self, event):
        if event.button() == QtCore.Qt.RightButton :
            #self.rightClicked.emit(self.toggleMarked())
            self.rightClicked.emit(self.individualMarked)
        elif event.button() == QtCore.Qt.MiddleButton :
            self.middleClicked.emit(self.individualMarked)
        else:
            QPushButton.mousePressEvent(self, event)

    def setIndividualMarked(self, individualMarked):
        self.individualMarked = individualMarked
        self.setProperty('individualMarked', individualMarked)
        self.setStyle(self.style())
    
    def toggleIndividualMarked(self):
        self.setIndividualMarked(not self.individualMarked)
        return self.individualMarked
    
    def setParentLayout(self, layout):
        self.__parentLayout = layout

    def getParentLayout(self):
        return self.__parentLayout

class Fret():
    def __init__(self, fretIndex: int, noteName: str):

        self.subscribers: List[String] = []
        self.noteName: str = noteName
        self.fretIndex: int = fretIndex
        #self.parentString: String = parentString
        self.button = FretButton(self.noteName)
        self.button.setFixedWidth(buttonWidth)
        self.button.setCheckable(True)
        #self.button.setStyleSheet("QPushButton:checked { background-color: red;border:5px solid rgb(255, 170, 255); }")
        self.button.setStyleSheet("QPushButton[individualMarked=true] { border: 2px solid #000000;} QPushButton:checked { background-color: #adaddf;} QPushButton { border-radius: 10px; }")
        self.button.setFocusPolicy(QtCore.Qt.NoFocus)
        #self.button.clicked[bool].connect(self.notifyNoteToggle)
        #self.button.clicked[bool].connect(self.notifyNoteToggle)
        self.button.clicked[bool].connect(self.notifyNoteToggle)
        self.button.rightClicked[bool].connect(self.toggleIndividualMarked)
        self.button.middleClicked[bool].connect(self.addScale)

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def toggleIndividualMarked(self, individualMarked: bool):
        self.button.toggleIndividualMarked()
        pass
        #print(self.noteName, individualMarked)


 
    def notifyNoteToggle(self, checked: bool):
         
        for subscriber in self.subscribers:
            # notify String
            subscriber.notifyNoteToggle(self.noteName, checked)

    def addScale(self, individualMarked: bool):
        for subscriber in self.subscribers:
            # notify String
            subscriber.addScale(self.fretIndex, self.noteName, individualMarked)


class String():
    def __init__(self, index: int, noteName: str, numberFrets: int):
       self.subscribers: FretBoard = []
       self.stringIndex: int = index
       self.noteName: str = noteName
       self.noteSelector = self.newNoteSelector()
       self.frets: List[Fret] = []
       self.addFrets(numberFrets + 1)
       self.numberFrets: int = numberFrets

    def findNextNote(self, fretIndex: int, noteName: str) -> Fret:
        delta = 24
        for currentFretIndex, currentFret in enumerate(self.frets):
            if currentFret.noteName == noteName:
                currentDelta = abs(currentFretIndex - fretIndex)
                if currentDelta <= delta:
                    delta = currentDelta
                    fret = currentFret
        return fret

    def subscribe(self, subscriber):
        # subscribe String
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
        for fretIndex, note in enumerate(notesInString):
            fret: Fret = Fret(fretIndex, note)
            for subscriber in self.subscribers:
                print(type(subscriber))
                if fret.noteName in subscriber.markedNotesGlobal:
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
        startNote = dropwhile(lambda x: x != self.noteName, notesCycle)
        notesInString = islice(startNote, None, self.numberFrets + 1)
        for noteName, fret in zip(notesInString, self.frets):
            fret.button.setText(noteName)
            fret.noteName = noteName
            for subscriber in self.subscribers:
                fret.button.setChecked(fret.noteName in subscriber.markedNotesGlobal)

        for subscriber in self.subscribers:
            if fret.noteName in subscriber.markedNotesGlobal:
                fret.button.setChecked(True)

    def recreateString(self, stringIndex: int):
        layout = self.frets[0].button.getParentLayout()
        for i in reversed(range(1, layout.count())): 
            layout.itemAt(i).widget().setParent(None)
        self.frets.clear()
        self.addFrets(self.numberFrets + 1)
        self.drawString(layout)

    def notifyNoteToggle(self, noteName: str, checked: bool):
        for subscriber in self.subscribers:
            # notify FretBoard
            subscriber.toggleNoteGlobal(noteName, checked)

    def addScale(self, fretIndex: int, noteName: str, individualMarked: bool):
        for subscriber in self.subscribers:
            # notify FretBoard
            subscriber.addScale(self.stringIndex, fretIndex, noteName, individualMarked)


class FretBoard():
    def __init__(self, tuning: List[str], numberFrets: int):
        self.tuning: List[str] = tuning
        self.strings: List[String] = []
        self.numberFrets: int = numberFrets
        self.markedNotesGlobal: Set[str] = set()
        self.subscribers: List[QHBoxLayout] = []

        for i, noteName in enumerate(reversed(tuning)):
            string: String = String(i, noteName, numberFrets)
            string.subscribe(self)
            self.strings.append(string)

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def toggleNoteGlobal(self, noteName: str, checked: bool):
        if checked:
            self.markedNotesGlobal.add(noteName)
        else:
            self.markedNotesGlobal.remove(noteName)

        for string in self.strings:
            for fret in string.frets:
                if fret.button.text() == noteName:
                    fret.button.setChecked(checked)  
    def addScale(self, stringIndex: int, fretIndex: int, noteName: str, individualMarked: bool):

        startNote = dropwhile(lambda x: x != noteName, notesCycle)
        notesInString = cycle(startNote)
        #notesInString = [note for note in islice(startNote, None, 12)]
        scaleName = self.subscribers[0].comboBoxScales.currentText()
        scaleIntervals = [intervalsDict[interval] for interval in scalesGlobal[scaleName]]
        intervals = len(scaleIntervals)
        print(intervals)
        scaleIntervals_extended = list(islice(cycle(scaleIntervals), 0, len(scaleIntervals) + 1))
        print(len(scaleIntervals_extended))
        scaleIntervals_extended[intervals] += 12
        print("scaleIntervals_extended", scaleIntervals_extended)
        intervalDeltas: List[int] = []
        for i, interval in enumerate(scaleIntervals_extended[1:]):
            intervalDeltas.append(interval - scaleIntervals[i])

        mode = self.subscribers[0].comboBoxModes.currentIndex()
        modeDeltas = islice(cycle(intervalDeltas), mode, mode + intervals)


        note = next(notesInString)
        notesInMode: List = [note]
        for delta in modeDeltas:
            for j in range(delta):
                note = next(notesInString)
            notesInMode.append(note)

        notesInModeCycle = cycle(notesInMode[:intervals])
        for string in self.strings[stringIndex::-1]:
            for i in range(3):
                currentNoteName = next(notesInModeCycle)
                currentFret = string.findNextNote(fretIndex, currentNoteName)
                currentFret.button.setIndividualMarked(True)

    def clearAllGlobal(self):
        for string in self.strings:
            for fret in string.frets:
                fret.button.setChecked(False)  
        self.markedNotesGlobal.clear()

    def clearAllIndividual(self):
        for string in self.strings:
            for fret in string.frets:
                fret.button.setIndividualMarked(False)  
        #self.markedNotesGlobal.clear()


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

    def changeScaleByIndex(self, i: int):
        self.noteName = basicNotes[i]
        self.redrawString(self.stringIndex)
        
    def initUI(self):
        
        self.col = QColor(0, 0, 0)

        container = QHBoxLayout()
        vbox1 = QVBoxLayout()

        hboxControls = QHBoxLayout()

        self.pbClearAllGlobal = QPushButton("Clear all global")
        hboxControls.addWidget(self.pbClearAllGlobal)
        self.pbClearAllIndividual = QPushButton("Clear all individual")
        hboxControls.addWidget(self.pbClearAllIndividual)
        self.pbSetTuning = QPushButton("Reset tuning")
        hboxControls.addWidget(self.pbSetTuning)

        hboxScales = QHBoxLayout()

        lbScales = QLabel()
        lbScales.setText("Current Scale:")
        lbScales.setAlignment(QtCore.Qt.AlignRight)

        comboBoxScales = QComboBox()
        comboBoxScales.addItems(scalesGlobal.keys())
        comboBoxScales.currentIndexChanged.connect(self.changeScaleByIndex)

        lbModes = QLabel()
        lbModes.setText("Current Mode:")
        comboBoxModes = QComboBox()
        for i, interval in enumerate(scalesGlobal[comboBoxScales.currentText()]):
            comboBoxModes.addItem(str(i+1))
        hboxScales.addWidget(lbScales)
        hboxScales.addWidget(comboBoxScales)
        self.comboBoxScales = comboBoxScales
        hboxScales.addWidget(lbModes)
        hboxScales.addWidget(comboBoxModes)
        self.comboBoxModes = comboBoxModes

        vbox1.addLayout(hboxControls)
        self.createFretboard(vbox1)
        self.pbClearAllGlobal.clicked.connect(self.fretBoard.clearAllGlobal)
        self.pbClearAllIndividual.clicked.connect(self.fretBoard.clearAllIndividual)
        self.pbSetTuning.clicked.connect(self.fretBoard.resetTuning)
        vbox1.addLayout(hboxScales)

        self.setLayout(vbox1)    
        self.show()

