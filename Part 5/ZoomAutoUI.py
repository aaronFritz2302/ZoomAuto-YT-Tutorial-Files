import sys
from PyQt5.QtWidgets import QApplication,QMainWindow,QSystemTrayIcon,QAction,QMenu,QPushButton,QLineEdit,QCheckBox,QDateTimeEdit,QHeaderView      
from MainWinUI import Ui_MainWindow
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon
from pandas import DataFrame
from StorageSystem import DataBase
from threading import Thread
from plyer import notification
from time import sleep
from datetime import datetime
from urllib.request import urlopen
from pywinauto.application import Application

class ZoomBotUI(QMainWindow):
    
    closeBtns = []
    curMeetingCount = 0
    meetingData = []
    cols = ['Text','Text','Text','DateTime','CheckBox','CheckBox']
    sql = DataBase()
    flag = None
    
    def __init__(self):
        super(ZoomBotUI,self).__init__()
        
        #Setting up the UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.restoreData()
        self.startThread()
        
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
        self.flag = False
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
        self.startThread()
        
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
                    
    def startThread(self):
        meetingList = self.sql.readData()
        self.flag = False
        self.timerThread = Thread(target=self.timer,args=(meetingList,))
        sleep(1)
        self.timerThread.start()
        
    def timer(self,meetings):
        self.flag = True
        while self.flag:
            curTime = str(datetime.now().strftime('%d-%b , %H:%M:%S'))
            for meetingTime in meetings['DateTime']:
                if curTime == (meetingTime+':00'):
                    self.checkNetwork()
                    self.startMeeting(meetingTime,meetings)
                    self.deleteMeeting(list(meetings['DateTime']).index(meetingTime))
                    self.saveTable()
            sleep(1)
    
    def checkNetwork(self):
        not_connected = True
        while not_connected:
            try:
                urlopen('http://google.com')
                not_connected = False
            except:
                not_connected = True
            sleep(1)
        return 
    
    def startMeeting(self,time,meeting):
        meetingDetails = meeting.set_index('DateTime')
        name = meetingDetails['Name'][time]
        Id = meetingDetails['ID'][time]
        passwd = meetingDetails['Password'][time]
        no_audio = meetingDetails['Audio'][time]
        no_video = meetingDetails['Video'][time]
        
        notification.notify("ZoomAuto","Meeting has started","ZoomAuto",'./ZoomAuto.ico')
        zoomWin = Application(backend='uia').start(r"C:\Users\never\AppData\Roaming\Zoom\bin\Zoom.exe").connect(title='Zoom',timeout=100)
        homeTab = zoomWin.Zoom.child_window(title="Home", control_type="TabItem").wrapper_object()
        homeTab.click_input()
        joinBtn = zoomWin.Zoom.child_window(title="Join", control_type="Button").wrapper_object()
        joinBtn.click_input()
        
        joinWin = Application(backend='uia').connect(title = "Join Meeting",timeout = 100)
        idBox = joinWin.JoinMeeting.child_window(title="Please enter your Meeting ID or Personal Link Name", control_type="Edit").wrapper_object()
        idBox.type_keys(Id,with_spaces=True)
        
        nameBox = joinWin.JoinMeeting.child_window(title="Please enter your name", control_type="Edit").wrapper_object()
        nameBox.click_input()
        nameBox.type_keys("^a{BACKSPACE}")
        nameBox.type_keys(name,with_spaces=True)
        
        audio = joinWin.JoinMeeting.child_window(title='Do not connect to audio', control_type = "CheckBox").wrapper_object()
        video = joinWin.JoinMeeting.child_window(title='Turn off my video', control_type = "CheckBox").wrapper_object()
        audio_ts = audio.get_toggle_state()
        video_ts = video.get_toggle_state()
        
        if no_audio == 0 and audio_ts == 1:
            audio.toggle()
        if no_audio == 2 and audio_ts == 0:
            audio.toggle()
        
        if no_video == 0 and video_ts == 1:
            video.toggle()
        if no_video == 2 and video_ts == 0:
            video.toggle()
        
        joinBtn = joinWin.JoinMeeting.child_window(title="Join", control_type="Button").wrapper_object()
        joinBtn.click_input()
        
        passwdWin = Application(backend='uia').connect(title = "Enter meeting passcode",timeout = 100)
        passwdBox = passwdWin.EnterMeetingPasscode.child_window(title='Please enter meeting passcode', control_type="Edit")
        passwdBox.type_keys(passwd,with_spaces=True)
        meetingJoinBtn = passwdWin.EnterMeetingPasscode.child_window(title='Join Meeting', control_type="Button")
        meetingJoinBtn.click_input()
        notification.notify("ZoomAuto","Meeting Joined","ZoomAuto",'./ZoomAuto.ico')
        
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = ZoomBotUI()
    sys.exit(app.exec_())