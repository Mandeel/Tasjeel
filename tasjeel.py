
AppVersion = '0.5'
import sys, os, logging, cv2, atexit
import time


from playsound import playsound
import pandas as pd 
from datetime import datetime
from github import Github, GithubException
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from urllib.request import urlopen, URLError
import subprocess
import qtawesome as qta
#from qt_material import apply_stylesheet
import qtmodern.styles
import qtmodern.windows

basedir = os.path.dirname(__file__)


#logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')
loggingFile = "application.log"
def touch(path):
    with open(path, 'a'):
        os.utime(path, None)
touch(loggingFile)
logging.basicConfig(filename=loggingFile, encoding='utf-8', level=logging.ERROR)
#logging.getLogger().setLevel(logging.INFO)

class aboutWindow(QtWidgets.QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("عن البرنامج")
        uic.loadUi('src/pyqt/AboutMenuGUI.ui', self)
        # set logo
        input_image1 = cv2.imread("src/logo/Sadiq150x150.png", cv2.IMREAD_UNCHANGED)
        input_image2 = cv2.imread("src/logo/Alrafifain150x150.png", cv2.IMREAD_UNCHANGED)

        height, width, channels = input_image1.shape
        bytesPerLine = channels * width
        qImg1 = QtGui.QImage(input_image1.data, width, height, bytesPerLine, QtGui.QImage.Format_ARGB32)
        pixmap01 = QtGui.QPixmap.fromImage(qImg1)
        pixmap_image1 = QtGui.QPixmap(pixmap01)
        self.uni1_lbl.setPixmap(pixmap_image1)
        self.about_lbl.setOpenExternalLinks(True)


        qImg2 = QtGui.QImage(input_image2.data, width, height, bytesPerLine, QtGui.QImage.Format_ARGB32)
        pixmap02 = QtGui.QPixmap.fromImage(qImg2)
        pixmap_image2 = QtGui.QPixmap(pixmap02)
        self.uni2_lbl.setPixmap(pixmap_image2)
        self.closeButton.clicked.connect(self.close)
        
class activationWindow(QtWidgets.QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تفعيل البرنامج")
        uic.loadUi('src/pyqt/ActivationMenuGUI.ui', self)
        # set logo
        self.closeButton.clicked.connect(self.close)
       

class Downloader(QtCore.QThread):

    # Signal for the window to establish the maximum value
    # of the progress bar.
    setTotalProgress = QtCore.pyqtSignal(int)
    # Signal to increase the progress.
    setCurrentProgress = QtCore.pyqtSignal(int)
    # Signal to be emitted when the file has been downloaded successfully.
    succeeded = QtCore.pyqtSignal()
    setCurrentSpeed = QtCore.pyqtSignal(float)

    def __init__(self, url, filename):
        super().__init__()
        self._url = url
        self._filename = filename

    def run(self):
        url = "https://github.com/Mandeel/Tasjeel/releases/latest/download/Tasjeel.setup.exe"
        #url = "https://github.com/pbatard/rufus/releases/download/v3.21/rufus-3.21.exe"
        filename = "setup.exe"
        readBytes = 0
        chunkSize = 1024
        # Open the URL address.
        try:
            os.remove("setup.exe")
        except OSError:
            pass
        start_time = time.time()

        with urlopen(url) as r:
            # Tell the window the amount of bytes to be downloaded.
            self.setTotalProgress.emit(int(r.info()["Content-Length"]))
            with open(filename, "ab") as f:
                while True:
                    # Read a piece of the file we are downloading.
                    chunk = r.read(chunkSize)
                    # If the result is `None`, that means data is not
                    # downloaded yet. Just keep waiting.
                    if chunk is None:
                        continue
                    # If the result is an empty `bytes` instance, then
                    # the file is complete.
                    elif chunk == b"":
                        break
                    # Write into the local file the downloaded chunk.
                    f.write(chunk)
                    readBytes += chunkSize
                    # Tell the window how many bytes we have received.
                    self.setCurrentProgress.emit(readBytes)
                    elapsed_time = time.time() - start_time
                    current_speed = readBytes / elapsed_time
                    # Update the label with the current speed.
                    self.setCurrentSpeed.emit(current_speed)
        # If this line is reached then no exception has ocurred in
        # the previous lines.
        self.succeeded.emit()

class UpdaterWindow(QtWidgets.QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self):
        super().__init__()
        uic.loadUi('src/pyqt/updateWindow.ui', self)
        
        font_id = QtGui.QFontDatabase.addApplicationFont("src/font/Cairo-Medium.ttf")
        font_family = QtGui.QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QtGui.QFont(font_family)
        font.setPointSize(8)
        font2 = font
        font2.setPointSize(10)

        # set font
        self.setFont(font)
        self.label.setFont(font2)
        self.button.setFont(font2)
        self.progressBar.setFont(font2)
        self.button.pressed.connect(self.initDownload)

    def initDownload(self):
        self.label.setText("جاري عملية التنزيل...")
        # Disable the button while the file is downloading.
        self.button.setEnabled(False)
        # Run the download in a new thread.
        self.downloader = Downloader(
            "https://github.com/Mandeel/Tasjeel/releases/latest/download/Tasjeel.setup.exe",
            #"https://github.com/pbatard/rufus/releases/download/v3.21/rufus-3.21.exe",
            "setup.exe"
        )
        # Connect the signals which send information about the download
        # progress with the proper methods of the progress bar.
        self.downloader.setTotalProgress.connect(self.progressBar.setMaximum)
        self.downloader.setCurrentProgress.connect(self.progressBar.setValue)
        self.downloader.setCurrentSpeed.connect(self.updateSpeedLabel)

        # Qt will invoke the `succeeded()` method when the file has been
        # downloaded successfully and `downloadFinished()` when the
        # child thread finishes.
        self.downloader.succeeded.connect(self.downloadSucceeded)
        self.downloader.finished.connect(self.downloadFinished)
        self.downloader.start()

    def updateSpeedLabel(self, speed):
        self.label.setText(f"جاري عملية التنزيل... ({round(speed / 1024):.0f}KB/s)")

    def downloadSucceeded(self):
        # Set the progress at 100%.
        self.progressBar.setValue(self.progressBar.maximum())
        self.label.setText("تم تنزيل الملف بنجاح!")
        #atexit.register(os.execl, "setup.exe", "setup.exe")
        #self.close
        subprocess.Popen("setup.exe")
        sys.exit(app.exec_())

    def downloadFinished(self):
        # Restore the button.
        self.button.setEnabled(True)
        # Delete the thread when no longer needed.
        del self.downloader


class Worker(QtCore.QObject):
    
    statusBarMsg = QtCore.pyqtSignal(str)
    registerationCompletedSig = QtCore.pyqtSignal(bool)
    studentRegisteredSig = QtCore.pyqtSignal(str)
    changePixmap = QtCore.pyqtSignal(QtGui.QImage)
    errorSig = QtCore.pyqtSignal(str)
    delaySig = QtCore.pyqtSignal(int)
    # Signal to be emitted when the registration has been halted.
    haltingIndicatorSig = QtCore.pyqtSignal(bool)
    qrCodeDetector = cv2.QRCodeDetector()

    delay_Amount = 5
    def start_registeration(self):

        self.start = True
        name = ""

        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda: self.haltingIndicatorSig.emit(False))

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
                        #self.haltingIndicatorSig.emit(True)
                        #time.sleep(self.delay_Amount)
                        #self.haltingIndicatorSig.emit(False)
                        self.haltingIndicatorSig.emit(True)
                        self.timer.start(self.delay_Amount * 1000)

                        
        
            except Exception as e:
                logging.error(f'worker thread got {e}.')
                self.errorSig.emit(str(e))
            

    def stop(self):
        self.start = False
        
    def change_delay_amount(self, amount):
        self.delay_Amount = amount


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
        exitAct = QtWidgets.QAction(QtGui.QIcon('exit24.png'), 'أغلاق', self)
        exitAct.setStatusTip('أغلاق البرنامج')
        exitAct.triggered.connect(self.close)
        
        aboutAct = QtWidgets.QAction(QtGui.QIcon('exit24.png'), 'عن', self)
        #aboutAct.setShortcut('Ctrl+A')
        aboutAct.setStatusTip('حول')
        aboutAct.triggered.connect(self.aboutPopUp)  
        
        activationAct = QtWidgets.QAction(QtGui.QIcon('exit24.png'), 'تفعيل', self)
        #aboutAct.setShortcut('Ctrl+A')
        activationAct.setStatusTip('تفعيل البرنامج')
        activationAct.triggered.connect(self.activationPopUp)  

        check4updateAct = QtWidgets.QAction(QtGui.QIcon('exit24.png'), 'فحص التحديثات', self)

        #aboutAct.setShortcut('Ctrl+A')
        check4updateAct.setStatusTip('فحص التحديثات')
        check4updateAct.triggered.connect(self.check_for_updates)       

        # Set the font size to 14 points
        font_id = QtGui.QFontDatabase.addApplicationFont("src/font/Cairo-Medium.ttf")
        font_family = QtGui.QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QtGui.QFont(font_family)
        font.setPointSize(10)

        self.radioButton.setFont(font)
        self.radioButton_2.setFont(font)
        self.radioButton_3.setFont(font)
        self.radioButton_4.setFont(font)
        self.radioButton_5.setFont(font)
        self.radio_button_1.setFont(font)
        self.radio_button_2.setFont(font)

        

        menubar = self.menuBar()
        menubar.setFont(font)
        #fileMenu = menubar.addMenu('&ملف')
        fileMenu = menubar.addMenu('ملف')
        fileMenu.setFont(font)

        helpMenu = menubar.addMenu('مساعدة')
        helpMenu.setFont(font)
        
        fileMenu.addAction(exitAct)
        helpMenu.addAction(aboutAct)
        helpMenu.addAction(activationAct)
        helpMenu.addAction(check4updateAct)



        # set buttons icons
        start_icon = qta.icon('fa.play',
                        active='fa.play',
                        color='green',
                        color_active='green')
        self.startRegisterationButton.setIcon(start_icon) 
        
        close_icon = qta.icon('fa.times',
                        active='fa.times',
                        color='red',
                        color_active='red')
                        
                        
        self.fnshBtn.setIcon(close_icon)
        self.fnshBtn.setEnabled(False)
        
        # status bar
        #self.statusbar.setStyleSheet('font-size: 12pt;')
        self.statusbar.setFont(font)
        # indicator
        movie = QtGui.QMovie('src/images/blinking_green_button.gif')
        self.indicator_label.setMovie(movie)
        self.indicator_label.hide()
        movie.start()

        app.aboutToQuit.connect(self.closeEvent)

        
        # connect buttons to functions
        self.startRegisterationButton.clicked.connect(self.onPress_start_registeration)
        self.fnshBtn.clicked.connect(self.registeration_completed)


        self.radio_button_1.toggled.connect(self.themeSelector)
        #self.radio_button_1.setChecked(True)


        self.worker = Worker()
        self.worker_thread = QtCore.QThread()
        
        

        # connect signals
        self.start_registeration_requestedSig.connect(self.worker.start_registeration)
        self.worker.studentRegisteredSig.connect(self.start_student_registeration_in_excell_file)

        self.worker.registerationCompletedSig.connect(self.worker.stop)
        self.worker.haltingIndicatorSig.connect(self.haltingIndicatorFunc)

        self.worker.statusBarMsg.connect(self.handleStatusBarMsgs)
        self.worker.changePixmap.connect(self.setImage)

        self.worker.errorSig.connect(self.logErrors)
        self.worker.delaySig.connect(self.worker.change_delay_amount)

        # move worker to the worker thread
        self.worker.moveToThread(self.worker_thread)

        # start the thread
        self.worker_thread.start()
        
        #connect radio buttons
        self.radioButton.clicked.connect(self.changeDelayinGui)
        self.radioButton_2.clicked.connect(self.changeDelayinGui)
        self.radioButton_3.clicked.connect(self.changeDelayinGui)
        self.radioButton_4.clicked.connect(self.changeDelayinGui)
        self.radioButton_5.clicked.connect(self.changeDelayinGui)


        #App settings
        self.settings = QtCore.QSettings('Mandeel', 'Tasjeel')
        self.restore_settings()
        self.changeDelayinGui()

    def restore_settings(self):
        # Get the saved radio button selection from the QSettings object

        # Set the appropriate radio button as checked
        if self.settings.contains("theme_selection"):
            # there is the key in QSettings
            print('Checking for theme preference in config')
            theme_selection = self.settings.value('theme_selection')
            print('Found theme_selection in config:' + theme_selection)
            if theme_selection == "light":
                qtmodern.styles.light(QtWidgets.QApplication.instance())
                self.radio_button_1.setChecked(True)
                #self.radio_button_2.setChecked(False)


            else:
                qtmodern.styles.dark(QtWidgets.QApplication.instance())
                self.radio_button_2.setChecked(True)
                #self.radio_button_1.setChecked(False)

        if self.settings.contains("delay_selection"):
            # there is the key in QSettings
            print('Checking for theme preference in config')
            delay_selection = self.settings.value('delay_selection')
            print('Found delay_selection in config:' + str(delay_selection))
            if delay_selection == 0:
                self.radioButton.setChecked(True)
            elif delay_selection == 3:
                self.radioButton_2.setChecked(True)
            elif delay_selection == 5:
                self.radioButton_3.setChecked(True)
            elif delay_selection == 7:
                self.radioButton_4.setChecked(True)
            elif delay_selection == 10:
                self.radioButton_5.setChecked(True)
            self.changeDelayinGui()


        self.show()

    def close_program(self):
        self.registeration_completed()
        if self.worker_thread.isRunning() == False:
            self.close

    def closeEvent(self, event):
        
        font_id = QtGui.QFontDatabase.addApplicationFont("src/font/Cairo-Medium.ttf")
        font_family = QtGui.QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QtGui.QFont(font_family)
        font.setPointSize(8)
        font2 = font
        font2.setPointSize(10)

        close = QtWidgets.QMessageBox()
        close.setFont(font2)
        close.setIcon(QtWidgets.QMessageBox.Question)
        close.setText(u"هل تريد الخروج؟")
        close.setWindowTitle(u"تأكيد الخروج")
        close.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        buttonY = close.button(QtWidgets.QMessageBox.Yes)
        buttonY.setText(u'نعم')
        buttonY.setFont(font)
        buttonN = close.button(QtWidgets.QMessageBox.Cancel)
        buttonN.setText('الغاء')   
        buttonN.setFont(font)    
        close = close.exec()


        if close == QtWidgets.QMessageBox.Yes:

            event.accept()
            self.close_program()

        else:
            event.ignore()
        #sys.exit(0)


     #   box.setWindowTitle('Kaydet!')
       # box.setText('Kaydetmek İstediğinize Emin Misiniz?')

    def onPress_start_registeration(self):
        if self.check_camera_availability() == True:
            if self.check_registeration_file_availability() == True:
                # self.startRegisterationButton.setEnabled(False)
                self.get_students_data()
            else:
                self.statusBar().showMessage("يرجى اختيار ملف تسجيل الحضور")
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
        self.xlsx_file_dir = None

        self.startRegisterationButton.setEnabled(True)
        self.fnshBtn.setEnabled(False)
        self.CameraLabel.hide()
        self.groupBox_2.show()
        self.groupBox_3.show()
        self.indicator_label.hide()
        self.statusBar().showMessage("تم إنهاء عملية تسجيل الحضور")

        

    def changeDelayinGui(self):
        if self.radioButton.isChecked():
            self.settings.setValue('delay_selection', 0)
            self.worker.delaySig.emit(0)
        elif self.radioButton_2.isChecked():
            self.settings.setValue('delay_selection', 3)
            self.worker.delaySig.emit(3)
        elif self.radioButton_3.isChecked():
            self.settings.setValue('delay_selection', 5)
            self.worker.delaySig.emit(5)
        elif self.radioButton_4.isChecked():
            self.settings.setValue('delay_selection', 7)
            self.worker.delaySig.emit(7)          
        elif self.radioButton_5.isChecked():
            self.settings.setValue('delay_selection', 10)
            self.worker.delaySig.emit(10)  
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
        file_dialog = QtWidgets.QFileDialog()

        # Set the initial directory to the desktop folder
        desktop_path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
        file_dialog.setDirectory(desktop_path)

        #files, _ = QtWidgets.QFileDialog.getOpenFileNames(None,"اختيار ملف تسجيل الحضور", "","Excell Files (*.xlsx)", options=options)
        files, _ = file_dialog.getOpenFileNames(None,"اختيار ملف تسجيل الحضور", "","Excell Files (*.xlsx)", options=options)
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
                self.fnshBtn.setEnabled(True)
                self.CameraLabel.show()
                self.groupBox_2.hide()
                self.groupBox_3.hide()
                self.indicator_label.show()

                self.statusBar().showMessage("عملية تسجيل الحضور قيد العمل")
                self.start_registeration_requestedSig.emit(True)


    def haltingIndicatorFunc(self, value):
        #change image of the indicator label
        print("halting ... " + str(value))
        if value == True:
            halt_image = cv2.imread("src/images/halt.png", cv2.IMREAD_UNCHANGED)
            height, width, channels = halt_image.shape
            bytesPerLine = channels * width
            qImg1 = QtGui.QImage(halt_image.data, width, height, bytesPerLine, QtGui.QImage.Format_ARGB32)
            pixmap01 = QtGui.QPixmap.fromImage(qImg1)
            pixmap_image1 = QtGui.QPixmap(pixmap01)
            self.indicator_label.setPixmap(pixmap_image1)
        else:
            movie = QtGui.QMovie('src/images/blinking_green_button.gif')
            self.indicator_label.setMovie(movie)
            self.indicator_label.show()
            movie.start()

    def aboutPopUp(self):
        self.w = aboutWindow()
        self.w.show()

    def activationPopUp(self):
        self.w = activationWindow()
        self.w.show()


    def check_for_updates(self):

        font_id = QtGui.QFontDatabase.addApplicationFont("src/font/Cairo-Medium.ttf")
        font_family = QtGui.QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QtGui.QFont(font_family)
        font.setPointSize(8)
        font2 = font
        font2.setPointSize(10)
        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            g = Github()
            repo = g.get_repo("Mandeel/Tasjeel")
            latestVersion = repo.get_contents("src/version/version.txt")
            latestVersion = float(latestVersion.decoded_content.decode())
            print(latestVersion)
            with open(r'C:\Program Files (x86)\Tasjeel\src\version\version.txt') as f:
                currentVersion = float(f.readlines()[0])

            updatedMsg = QtWidgets.QMessageBox()
            updatedMsg.setFont(font2)
            updatedMsg.setIcon(QtWidgets.QMessageBox.Information)
            updatedMsg.setWindowTitle("فحص التحديثات")
            updatedMsg.setText("البرنامج محدث! أصدار النسخة الحالية هو " + str(currentVersion) + " وهو أحدث نسخة متوفرة")
            updatedMsg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            okButton = updatedMsg.button(QtWidgets.QMessageBox.Ok)
            okButton.setText(u"حسنا")
            #okButton.setFont(font)


            updateAvailableMsg = QtWidgets.QMessageBox()
            updateAvailableMsg.setFont(font2)
            updateAvailableMsg.setIcon(QtWidgets.QMessageBox.Information)
            updateAvailableMsg.setWindowTitle("فحص التحديثات")
            updateAvailableMsg.setText("البرنامج ليس محدثا! أصدار النسخة الحالية هو " + str(currentVersion) + " لكن يمكن تحديث البرنامج للنسخة " + str(latestVersion) + "!"\
            "<br>أضغط على موافق لبدأ عملية التحديث")
            updateAvailableMsg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            okButton = updateAvailableMsg.button(QtWidgets.QMessageBox.Ok)
            okButton.setText(u"موافق")
            okButton.setFont(font)
            cancelButton = updateAvailableMsg.button(QtWidgets.QMessageBox.Cancel)
            cancelButton.setText(u"إلغاء")
            cancelButton.setFont(font)

            QtWidgets.QApplication.restoreOverrideCursor()
            if (currentVersion  >= latestVersion):
                print("نسخة البرنامج الحالية هي أخر نسخة!")
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
            NoInterenetConnectionMsg.setWindowTitle("فشل الاتصال")
            #NoInterenetConnectionMsg.setText(str(e))
            NoInterenetConnectionMsg.setText("تأكد من اتصالك بالأنترنيت")
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
        errorMsgBox.setWindowTitle("حدث خطأ!")
        errorMsgBox.setText(errormsg)
        errorMsgBox.setIcon(QtWidgets.QMessageBox.Information)
        x = errorMsgBox.exec_()

    def logErrors(self, errormsg):
        #logging.debug('damn, a bug')
        #logging.info('something to remember')
        #logging.warning('that\'s not right')
        logging.error(errormsg)

    def themeSelector(self, light):
        if light:
            qtmodern.styles.light(QtWidgets.QApplication.instance())
            self.settings.setValue('theme_selection', 'light')

        else:
            qtmodern.styles.dark(QtWidgets.QApplication.instance())
            self.settings.setValue('theme_selection', 'dark')

            
app = QtWidgets.QApplication(sys.argv)
dir_ = QtCore.QDir("Cairo")
_id = QtGui.QFontDatabase.addApplicationFont("src/font/Cairo-Medium.ttf")
app.setWindowIcon(QtGui.QIcon("src/icons/tasjeel.png"))#(QtGui.QIcon(qta.icon('fa5s.user-check')))
app.setApplicationName("برنامج تسجيل الحضور")
app.setApplicationVersion(AppVersion)
qtmodern.styles.light(app)



#qtmodern.styles.light(app)

window = Main()
window.setLayoutDirection(QtCore.Qt.RightToLeft)
window.setFixedSize(800, 620)
window.statusBar().setSizeGripEnabled(False) 

#mw = qtmodern.windows.ModernWindow(window)
#mw.show()

sys.exit(app.exec_())
