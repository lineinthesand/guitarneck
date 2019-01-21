import sys
import ui
from PyQt5.QtWidgets import (QApplication)

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = ui.MainWindow()
    sys.exit(app.exec_())

