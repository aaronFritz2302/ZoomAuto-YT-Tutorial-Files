import sys
from PyQt5.QtWidgets import QApplication,QMainWindow
from MainWinUI import Ui_MainWindow
from PyQt5.QtCore import Qt

class ZoomBotUI(QMainWindow):
    
    def __init__(self):
        super(ZoomBotUI,self).__init__()
        
        #Setting up the UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        #Display the UI on Screen
        self.show()
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = ZoomBotUI()
    sys.exit(app.exec_())