
import sys, os, logging, cv2

from playsound import playsound
import pandas as pd 
from datetime import datetime
from github import Github
from PyQt5 import QtWidgets, QtCore, QtGui, uic

basedir = os.path.dirname(__file__)


#logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')
loggingFile = "application.log"
def touch(path):
    with open(path, 'a'):
        os.utime(path, None)
touch(loggingFile)
logging.basicConfig(filename=loggingFile, encoding='utf-8', level=logging.ERROR)
#logging.getLogger().setLevel(logging.INFO)



class UpdaterWindow(QtWidgets.QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Window22222")

class Worker(QtCore.QObject):
    
    statusBarMsg = QtCore.pyqtSignal(str)
    registerationCompletedSig = QtCore.pyqtSignal(bool)
    studentRegisteredSig = QtCore.pyqtSignal(str)
    changePixmap = QtCore.pyqtSignal(QtGui.QImage)
    errorSig = QtCore.pyqtSignal(str)
    qrCodeDetector = cv2.QRCodeDetector()


    def start_registeration(self):

        self.start = True
        

        name = ""

        cap = cv2.VideoCapture(0)
        while(self.start):
            #Capture the video frame by frame
            ret, frame = cap.read()
            
            if ret:

                try:
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QtGui.QImage(rgbImage.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)
                except Exception as e:
                    logging.error(f'worker thread got {e}.')
                    self.errorSig.emit(str(e))
            if cv2.waitKey(30) & 0xff == ord('q'):
                break
                
            try:
                
                #barcodes = decode(frame)
                decodedText, points, _ = self.qrCodeDetector.detectAndDecode(frame)
                if decodedText == "":# not decodedText:
                    continue#print("List is empty")
                    logging.info(f'worker thread: no Qr code detected')
                else:
                    string = decodedText
                    result = string #.decode('unicode-escape').encode('latin1').decode('utf-8')
                    if name != result:
                        print(result)
                        self.studentRegisteredSig.emit(result)
                        name = result
        
            except Exception as e:
                logging.error(f'worker thread got {e}.')
                self.errorSig.emit(str(e))
            

    def stop(self):
        self.start = False
        


class Main(QtWidgets.QMainWindow):
    start_registeration_requestedSig = QtCore.pyqtSignal(bool)
    xlsx_file_dir = None
    studentLst = None
    today_date = str(datetime.today().strftime('%Y-%m-%d'))
    
    df = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.w = None
        # intialize the user interfeace
        uic.loadUi('src/pyqt/MainMenuGUI.ui', self)
        self.setWindowTitle("برنامج تسجيل الحضور")
        exitAct = QtWidgets.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)
        
        aboutAct = QtWidgets.QAction(QtGui.QIcon('exit24.png'), 'About', self)
        aboutAct.setShortcut('Ctrl+A')
        aboutAct.setStatusTip('About')
        aboutAct.triggered.connect(self.aboutPopUp)  

        check4updateAct = QtWidgets.QAction(QtGui.QIcon('exit24.png'), 'check for updates', self)
        #aboutAct.setShortcut('Ctrl+A')
        check4updateAct.setStatusTip('check for updates')
        check4updateAct.triggered.connect(self.check_for_updates)       

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        helpMenu = menubar.addMenu('&Help')

        fileMenu.addAction(exitAct)
        helpMenu.addAction(aboutAct)
        helpMenu.addAction(check4updateAct)


        # set buttons icons
        self.startRegisterationButton.setIcon(QtGui.QIcon('src\icons\start.png')) 
        self.CloseProgramButton.setIcon(QtGui.QIcon('src\icons\exit.png')) 
        self.CloseProgramButton.setIconSize(QtCore.QSize(30, 30))
        
        # set logo
        #input_image = cv2.imread("src/logo/Sadiq200x200.png", cv2.IMREAD_UNCHANGED)
        input_image = cv2.imread("src/logo/Alrafifain200x200.png", cv2.IMREAD_UNCHANGED)

        height, width, channels = input_image.shape
        bytesPerLine = channels * width
        qImg = QtGui.QImage(input_image.data, width, height, bytesPerLine, QtGui.QImage.Format_ARGB32)
        pixmap01 = QtGui.QPixmap.fromImage(qImg)
        pixmap_image = QtGui.QPixmap(pixmap01)
        label_imageDisplay = QtWidgets.QLabel()
        self.label_2.setPixmap(pixmap_image)
        
        app.aboutToQuit.connect(self.closeEvent)

        
        # connect buttons to functions
        self.CloseProgramButton.clicked.connect(self.close)
        self.startRegisterationButton.clicked.connect(self.onPress_start_registeration)
        

        self.worker = Worker()
        self.worker_thread = QtCore.QThread()

        # connect signals
        self.start_registeration_requestedSig.connect(self.worker.start_registeration)
        self.worker.studentRegisteredSig.connect(self.start_student_registeration_in_excell_file)

        self.worker.registerationCompletedSig.connect(self.worker.stop)


        self.worker.statusBarMsg.connect(self.handleStatusBarMsgs)
        self.worker.changePixmap.connect(self.setImage)

        self.worker.errorSig.connect(self.logErrors)

        # move worker to the worker thread
        self.worker.moveToThread(self.worker_thread)

        # start the thread
        self.worker_thread.start()
        
        self.show()

    def close_program(self):
        self.registeration_completed()
        if self.worker_thread.isRunning() == False:
            print("should be closed")

            self.close
            print("but it didn't")

    def closeEvent(self, event):
        close = QtWidgets.QMessageBox()
        close.setText("هل تريد أغلاق البرنامج؟")
        close.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        close = close.exec()

        if close == QtWidgets.QMessageBox.Yes:
            self.close_program()

            event.accept()
        else:
            event.ignore()
        #sys.exit(0)

    def onPress_start_registeration(self):
        if self.check_camera_availability() == True:
            if self.check_registeration_file_availability() == True:
                # self.startRegisterationButton.setEnabled(False)
                self.get_students_data()
            else:
                self.statusBar().showMessage("يرجى اختيار ملف تسجيل الحظور")
                self.openFileNamesDialog()
        else:
            self.statusBar().showMessage("الكاميرا لا تعمل")


    def start_student_registeration_in_excell_file(self,value):
        student_indx = None
        student_indx = self.df[self.df.name == str(value)].index
        print(student_indx)
        print(len(student_indx))
        if len(student_indx) != 1:
            playsound('src/sounds/wrong-answer.mp3')
            self.statusBar().showMessage("الطالب: "+str(value)+" غير موجود")
        else:
            self.df[self.today_date].iloc[student_indx] = 1
            try:
                self.df.to_excel(self.xlsx_file_dir, index=False)
            except:
                print("failed to write to excell")
            playsound('src/sounds/notification.mp3')
            self.statusBar().showMessage("تم تسجيل الطالب: " + value)
            #student_indx = None


    def registeration_completed(self):
        self.worker.registerationCompletedSig.emit(False)
        self.worker_thread.quit()
        print(self.worker_thread.isRunning())

        self.startRegisterationButton.setEnabled(True)


    def handleStatusBarMsgs(self, value):
        self.statusBar().showMessage(value)


    def check_camera_availability(self):
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            
            return True
        
        else:
            return False

    def check_registeration_file_availability(self):
        if self.xlsx_file_dir == None:
            return False
        else:
            return True

    def openFileNamesDialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(None,"اختيار ملف تسجيل الحضور", "","Excell Files (*.xlsx)", options=options)
        if files:
            self.xlsx_file_dir = files[0]
            print(self.xlsx_file_dir)
            self.get_students_data()

    def get_students_data(self):
        
            self.statusBar().showMessage("")
            self.df = pd.read_excel(self.xlsx_file_dir)
            try: #if the column of today is available
                today_column = list(self.df[self.today_date])
            except:
                self.df[self.today_date] = ""
            # today_date_pd = to_datetime(datetime.today(), format="%d/%m/%Y").date
            try:
                self.studentLst = list(self.df['name'])
            except:
                print("file is not in the correct format")
            if self.studentLst == None:
                self.xlsx_file_dir = None
                self.statusBar().showMessage("يرجى أختيار ملف بالترتيب الصحيح")

            else:
                self.startRegisterationButton.setEnabled(False)
                self.statusBar().showMessage("عملية تسجيل الحضور قيد العمل")
                self.start_registeration_requestedSig.emit(True)


            
    def aboutPopUp(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("عن البرنامج")
        msg.setText("تطوير:<br>\
        م.د. ذو الفقار حسين منديل - جامعة الامام الصادق (ع) \المثنى<br> \
        م.د. نور الدين عباس خالد - كلية بلاد الرافدين الجامعة \ديالى<br><br>"
         "االأيقونات من:\
                                        <br>icon king1 on freeicons.io\
                                        <br>Raj Dev on freeicons.io\
                                        <br>Manthana Chaiwong on freeicons.io \
                                        <br>Pixel perfect - Flaticon\
                                        <br><br>الملفات الصوتية من:<br>\
                                        SergeQuadrado from Pixabay \
                                ")
        msg.setIcon(QtWidgets.QMessageBox.Information)

        x = msg.exec_()  # this will show our messagebox

    def internet_on():
        try:
            urllib2.urlopen('http://github.com', timeout=1)
            return True
        except urllib2.URLError as err: 
            return False

    def check_for_updates(self):

        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            g = Github("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")
            repo = g.get_user().get_repo("TasjeelUpdate")
            latestVersion = repo.get_contents("version.txt")
            latestVersion = float(latestVersion.decoded_content.decode())
            print(latestVersion)
            with open('src/version/version.txt') as f:
                currentVersion = float(f.readlines()[0])

            updatedMsg = QtWidgets.QMessageBox()
            updatedMsg.setWindowTitle("check for updates")
            updatedMsg.setText("the App is up to date!")
            updatedMsg.setIcon(QtWidgets.QMessageBox.Information)

            updateAvailableMsg = QtWidgets.QMessageBox()
            updateAvailableMsg.setWindowTitle("check for updates")
            updateAvailableMsg.setText("App is not up to date! App is on version " + str(currentVersion) + " but could be on version " + str(latestVersion) + "!"\
            "<br>press ok to start updating")
            updateAvailableMsg.setIcon(QtWidgets.QMessageBox.Information)
            updateAvailableMsg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            QtWidgets.QApplication.restoreOverrideCursor()
            if (currentVersion  >= latestVersion):
                print("App is up to date!")
                x = updatedMsg.exec_() 
            else:
                print("App is not up to date! App is on version " + str(currentVersion) + " but could be on version " + str(latestVersion) + "!")
                x = updateAvailableMsg.exec_()
                if x == QtWidgets.QMessageBox.Ok:
                    try:
                        self.show_update_window()
                    except Exception as e:
                        print(str(e))

                    print('updating...')
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            NoInterenetConnectionMsg = QtWidgets.QMessageBox()
            NoInterenetConnectionMsg.setWindowTitle("checking internet connection")
            NoInterenetConnectionMsg.setText(str(e))
            NoInterenetConnectionMsg.setIcon(QtWidgets.QMessageBox.Information)
            x = NoInterenetConnectionMsg.exec_() 


    def show_update_window(self):
        self.w = UpdaterWindow()
        self.w.show()

    def checkAndMakeDIRs (self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    @QtCore.pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        self.CameraLabel.setPixmap(QtGui.QPixmap.fromImage(image))



    def showErrors(self, errormsg):
        errorMsgBox = QtWidgets.QMessageBox()
        errorMsgBox.setWindowTitle("There was an error")
        errorMsgBox.setText(errormsg)
        errorMsgBox.setIcon(QtWidgets.QMessageBox.Information)
        x = errorMsgBox.exec_()

    def logErrors(self, errormsg):
        #logging.debug('damn, a bug')
        #logging.info('something to remember')
        #logging.warning('that\'s not right')
        logging.error(errormsg)



app = QtWidgets.QApplication(sys.argv)
dir_ = QtCore.QDir("Cairo")
_id = QtGui.QFontDatabase.addApplicationFont("src/font/Cairo-Medium.ttf")
app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, 'src/icons/tasjeel.ico')))
app.setApplicationName("Tasjeel")

window = Main()

sys.exit(app.exec_())
