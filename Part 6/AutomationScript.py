from pywinauto.application import Application

zoomWin = Application(backend='uia').start(r"C:\Users\never\AppData\Roaming\Zoom\bin\Zoom.exe").connect(title='Zoom',timeout=100)
homeTab = zoomWin.Zoom.child_window(title="Home", control_type="TabItem").wrapper_object()
homeTab.click_input()
joinBtn = zoomWin.Zoom.child_window(title="Join", control_type="Button").wrapper_object()
joinBtn.click_input()

joinWin = Application(backend='uia').connect(title = "Join Meeting",timeout = 100)
idBox = joinWin.JoinMeeting.child_window(title="Please enter your Meeting ID or Personal Link Name", control_type="Edit").wrapper_object()
idBox.type_keys('ID',with_spaces=True)
nameBox = joinWin.JoinMeeting.child_window(title="Please enter your name", control_type="Edit").wrapper_object()
nameBox.click_input()
nameBox.type_keys("^a{BACKSPACE}")
nameBox.type_keys('name',with_spaces=True)
joinBtn = joinWin.JoinMeeting.child_window(title="Join", control_type="Button").wrapper_object()
joinBtn.click_input()

passwdWin = Application(backend='uia').connect(title = "Enter meeting passcode",timeout = 100)
passwdBox = passwdWin.EnterMeetingPasscode.child_window(title='Please enter meeting passcode', control_type="Edit")
passwdBox.type_keys('passwd',with_spaces=True)
meetingJoinBtn = passwdWin.EnterMeetingPasscode.child_window(title='Join Meeting', control_type="Button")
meetingJoinBtn.click_input()
