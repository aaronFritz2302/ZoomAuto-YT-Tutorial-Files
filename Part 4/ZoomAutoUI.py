import sys
from PyQt5.QtWidgets import QApplication,QMainWindow,QSystemTrayIcon,QAction,QMenu,QPushButton,QLineEdit,QCheckBox,QDateTimeEdit,QHeaderView      
from MainWinUI import Ui_MainWindow
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon
from pandas import DataFrame
from StorageSystem import DataBase

class ZoomBotUI(QMainWindow):
    
    closeBtns = []
    curMeetingCount = 0
    meetingData = []
    cols = ['Text','Text','Text','DateTime','CheckBox','CheckBox']
    sql = DataBase()
    
    def __init__(self):
        super(ZoomBotUI,self).__init__()
        
        #Setting up the UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.restoreData()
        
        #Adding Functions to Buttons
        self.ui.closeBtn.clicked.connect(self.hide)
        self.ui.minBtn.clicked.connect(self.showMinimized)
        self.ui.closeBtn.setToolTip("Close")
        self.ui.minBtn.setToolTip("Minimize")
        self.ui.addBtn.clicked.connect(self.addMeeting)
        self.ui.saveBtn.clicked.connect(self.saveTable)
        
        # Changing Headers of the Table
        stylesheet = "::section{background-color:rgb(204,204,204);border-radius:14px}"
        self.ui.tableWidget.horizontalHeader().setStyleSheet(stylesheet)
        self.ui.tableWidget.verticalHeader().setStyleSheet(stylesheet)
        
        #Setting Up the Tray Menu
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("./ZoomAuto.png"))
        show_action = QAction("Show",self)
        hide_action = QAction("Hide",self)
        quit_action = QAction("Quit",self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(self.closeEvent)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        #Display the UI on Screen
        self.show()
        
    def closeEvent(self,event):
        self.saveTable()
        self.tray_icon.hide()
        self.close()
        
    def mousePressEvent(self,event):
        self.dragPos = event.globalPos()
        
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos()+event.globalPos()-self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()
            
    def addMeeting(self):
        name = QLineEdit(self)
        Id = QLineEdit(self)
        passwd = QLineEdit(self)
        datetime = QDateTimeEdit(self)
        audio = QCheckBox(self)
        video = QCheckBox(self)
        close = QPushButton(self)
        
        datetime.setDisplayFormat('dd-MMM , hh:mm')
        datetime.setDateTime(QDateTime().currentDateTime())
        
        close.setIcon(QIcon('./close-button.png'))
        close.setFlat(True)
        
        self.ui.tableWidget.insertRow(self.curMeetingCount)
        close.setObjectName(str(self.curMeetingCount))
        close.released.connect(lambda: self.deleteMeeting(close.objectName()))
        self.closeBtns.append(close)
        self.elements = [name,Id,passwd,datetime,audio,video,close]
        col = 0
        for element in self.elements:
            self.ui.tableWidget.setCellWidget(self.curMeetingCount, col, element)
            col+=1
        
        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(6,QHeaderView.ResizeToContents)
        
        self.elements.remove(close)
        row = []
        for element,name in zip(self.elements,self.cols):
            element.setObjectName(name)
            row.append(element)
        self.meetingData.append(row)
        self.curMeetingCount += 1
        
    def deleteMeeting(self,button_id):
        self.ui.tableWidget.removeRow(int(button_id))
        self.curMeetingCount -= 1
        self.closeBtns.remove(self.closeBtns[int(button_id)])
        for i in range(self.curMeetingCount):
            self.closeBtns[i].setObjectName(str(i))
        self.meetingData.remove(self.meetingData[int(button_id)])
    
    def saveTable(self):
        data = []
        rows = []
        for x in range(len(self.meetingData)):
            for i in range(6):
                if self.meetingData[x][i].objectName() == "Text":
                    data.append(self.meetingData[x][i].text())
                elif self.meetingData[x][i].objectName() == "DateTime":
                    data.append(self.meetingData[x][i].text())
                elif self.meetingData[x][i].objectName() == "CheckBox":
                    data.append(self.meetingData[x][i].checkState())
            rows.append(data)
            data = []
        meeting = DataFrame(rows,columns=('Name','ID','Password','DateTime','Audio','Video')) 
        self.sql.enterData(meeting)
        
    def restoreData(self):
        data = self.sql.readData()
        for x in range(len(data)):
            self.addMeeting()
            for y in range(len(data.columns)):
                if self.meetingData[x][y].objectName() == "Text":
                    self.meetingData[x][y].setText(data.loc[x][y])
                if self.meetingData[x][y].objectName() == "DateTime":
                    dateTime = QDateTime().fromString(data.loc[x][y],'dd-MMM , hh:mm')
                    self.meetingData[x][y].setDateTime(dateTime)
                if self.meetingData[x][y].objectName() == "CheckBox":
                    self.meetingData[x][y].setCheckState(int(data.loc[x][y]))
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = ZoomBotUI()
    sys.exit(app.exec_())