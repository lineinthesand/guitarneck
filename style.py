class FretStyle(object):
    def __init__(self, radius: float = 20, fretMarginX: float = 10):
        self._radius: float = radius
        self._fretMarginX: float = fretMarginX
        self._fretMarginY: float = 5
        self._circleX: float = 0
        self._fontSize: float = 0
        self._fretWidth: float = 0
        self._fretHeight: float = 0
        self._calcPrivateVars()
        self.circleStrokeColor: str = '#000000'
        self.circleFillColor: str = '#ffffff'

    @property
    def radius(self): return self._radius

    @radius.setter
    def radius(self, radius: int):
        self._radius = radius
        self._calcPrivateVars()

    @property
    def fretMarginX(self): return self._fretMarginX
    @fretMarginX.setter
    def fretMarginX(self, fretMarginX: int):
        self._fretMarginX = fretMarginX
        self._calcPrivateVars()

    @property
    def fretHeight(self):
        return self._fretHeight

    @property
    def fretWidth(self):
        return self._fretWidth

    @property
    def fontSize(self):
        return self._fontSize

    @property
    def circleX(self): return self._circleX

    def _calcPrivateVars(self):
        self._calcFontSize()
        self._calcFretDimensions()
        self._calcCircleX()

    def _calcFontSize(self):
        self._fontSize = self._radius * 1.1

    def _calcFretDimensions(self):
        self._fretWidth = 2 * self._radius + 2 * self._fretMarginX
        self._fretHeight = 2 * self._radius + 2 * self._fretMarginY

    def _calcCircleX(self):
        self._circleX = self._fretWidth / 2


