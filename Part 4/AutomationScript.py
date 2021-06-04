from pywinauto.application import Application
from win10toast            import ToastNotifier
from threading             import Thread
from DataStorage           import StorageSystem
from datetime              import datetime
from time                  import sleep
from requests              import urlopen
from ZoomBotUI             import ZoomBotUI

class MeetingAutomation():
    
    sql = StorageSystem()
    creteNotification = ToastNotifier()
    ui = ZoomBotUI()
    
    def __init__(self):
        self.data = self.sql.readData()
        
    def processData(self):
        data = self.data['DateTime']
        timings = []
        year = str(datetime.now().year)
        for x in data:
            timings.append(f"{year}-{x}:00")
        return timings
        
    def timer(self,timeList):
        timings = self.processData()
        while True:
            curTime = str(datetime.now().strftime('%y-%d-%b , %H:%m:%S'))
            for meetingTime in timings:
                if curTime == meetingTime:
                    self.startMeeting(self.data['DateTime'][timings.index(meetingTime)])
                    self.ui.deleteMeeting(timings.index(meetingTime))
                    timings.remove(meetingTime)
            sleep(1)
    
    def checkNetwork(self):
        connected = True
        while connected:
            try:
                urlopen('http://google.com')
                connected = False
            except:
                connected = True
            sleep(1)    
        return connected
        
    def startMeeting(self,time):
        self.checkNetwork()
            
        meetingDetails = self.data.set_index('DateTime')
        name = meetingDetails['Name'][time]
        ID = meetingDetails['ID'][time]
        passwd = meetingDetails['Password'][time]
        audio = meetingDetails['Audio'][time]
        video = meetingDetails['Video'][time]
        
        self.creteNotification.show_toast('ZoomBot','Meeting is starting')
        zoomWin = Application(backend='uia').start(r"C:\Users\never\AppData\Roaming\Zoom\bin\Zoom.exe").connect(title='Zoom',timeout=100)
        homeTab = zoomWin.Zoom.child_window(title="Home", control_type="TabItem").wrapper_object()
        homeTab.click_input()
        joinBtn = zoomWin.Zoom.child_window(title="Join", control_type="Button").wrapper_object()
        joinBtn.click_input()
        
        joinWin = Application(backend='uia').connect(title = "Join Meeting",timeout = 100)
        idBox = joinWin.JoinMeeting.child_window(title="Please enter your Meeting ID or Personal Link Name", control_type="Edit").wrapper_object()
        idBox.type_keys(ID,with_spaces=True)
        nameBox = joinWin.JoinMeeting.child_window(title="Please enter your name", control_type="Edit").wrapper_object()
        nameBox.click_input()
        nameBox.type_keys("^a{BACKSPACE}")
        nameBox.type_keys(name,with_spaces=True)
        joinBtn = joinWin.JoinMeeting.child_window(title="Join", control_type="Button").wrapper_object()
        joinBtn.click_input()
        
        passwdWin = Application(backend='uia').connect(title = "Enter meeting passcode",timeout = 100)
        passwdBox = passwdWin.EnterMeetingPasscode.child_window(title='Please enter meeting passcode', control_type="Edit")
        passwdBox.type_keys(passwd,with_spaces=True)
        meetingJoinBtn = passwdWin.EnterMeetingPasscode.child_window(title='Join Meeting', control_type="Button")
        meetingJoinBtn.click_input()
        self.creteNotification.show_toast('ZoomBot','Meeting Joined')
        
        return
        
