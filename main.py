import sys
import requests
import time
from PyQt5 import QtWidgets, QtCore
from PyQt5 import QtGui
from PyQt5.QtMultimedia import QSound
from PyQt5 import QtWidgets, QtCore, QtGui
import pygame

class CustomMessageBox(QtWidgets.QMessageBox):
    def __init__(self, location):
        super().__init__()
        self.setWindowTitle('התראה!')
        self.setText(f'התרעה ב{location}')
        self.setFont(QtGui.QFont('Arial', 35))
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.autoclose)
        self.timer.start(10000)  # 10 שניות

    def autoclose(self):
        self.accept()

class MissileAlertApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.sound_muted = False  # הוספתי משתנה לשמירת מצב ההשתקה
        pygame.init()
        pygame.mixer.init()
        self.movable = False  # האם החלון ניתן להזזה
        self.offset = None  # הזזה יחסית למיקום העכבר
        self.initUI()
        self.last_checked_time = None
        self.check_alerts()
        self.last_checked_time = None
        self.check_alerts()
        self.resize(350, 800)  # שינוי גודל החלון ל-600x350
        self.center()  # ממקם את החלון במרכז
        self.setWindowTitle('Missile Alert System')
        self.show()
        self.setStyleSheet("""
            QWidget {
                background-color: transparent; 
                color: white;
            }
            QTableWidget {
                border: none;  # הסרת הגבולות מהטבלה
            }
            QTableWidget QHeaderView::section {
                background-color: transparent;
                padding: 4px;
                border: none;  # הסרת הגבולות מהכותרת
                font-size: 14px;
            }
            QTableWidget::item {
                background-color: transparent;  # שינוי הרקע לשקוף
                color: white;
            }
            QLabel {
                background-color: transparent;  # שינוי הרקע לשקוף
                color: white;
            }
        """)

    def center_window(self, window):
        qr = window.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        window.move(qr.topLeft())


    def contextMenuEvent(self, event):
        context_menu = QtWidgets.QMenu(self)
        move_action = context_menu.addAction("הזז תוכנה")
        test_alert_action = context_menu.addAction("בדוק התראה")
        test_sound_action = context_menu.addAction("בדוק צליל")
        mute_sound_action = context_menu.addAction("השתק צליל" if not self.sound_muted else "בטל השתקת צליל")
        exit_action = context_menu.addAction("יציאה")  # הוספתי שורה זו
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action == move_action:
            self.movable = True  # מאפשר הזזה עם האירוע הבא של mouseMoveEvent
        elif action == test_alert_action:
            self.test_alert()
        elif action == test_sound_action:
            self.play_alert_sound()
        elif action == mute_sound_action:
            self.toggle_mute()
        elif action == exit_action:  # הוספתי שורה זו
            self.close()  # הוספתי שורה זו

    def toggle_mute(self):
        self.sound_muted = not self.sound_muted
        msg = QtWidgets.QMessageBox(self)  # הוספתי שורה זו
        if self.sound_muted:
            msg.setText("הצליל הושתק")
        else:
            msg.setText("ההשתקה בוטלה")
        self.center_window(msg)  # הוספתי שורה זו
        msg.exec_()
    
    def test_alert(self):
        location = "תל אביב"  # לדוגמה, תוכל לשנות לכל מיקום אחר
        msg_box = CustomMessageBox(location)
        msg_box.exec_()
    
    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(300, 300, 600, 350)
        self.center()

        self.title = QtWidgets.QLabel("צבע אדום", self)
        self.title.setFont(QtGui.QFont('Arial', 23))
        layout.addWidget(self.title)

        self.subtitle_new = QtWidgets.QLabel("התראות חדשות", self)
        self.subtitle_new.setFont(QtGui.QFont('Arial', 18, QtGui.QFont.Bold))
        layout.addWidget(self.subtitle_new)

        self.table_new = QtWidgets.QTableWidget(5, 2, self)
        self.table_new.setHorizontalHeaderLabels(["מיקום", "שעה"])
        self.table_new.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.table_new.setStyleSheet("""
            QTableWidget {
                background-color: black;
                color: white;
            }
            QHeaderView::section {
                background-color: black;
                color: white;
            }
            
        """)
        layout.addWidget(self.table_new)
        

        self.subtitle_old = QtWidgets.QLabel("התראות ישנות", self)
        self.subtitle_old.setFont(QtGui.QFont('Arial', 18, QtGui.QFont.Bold))
        layout.addWidget(self.subtitle_old)

        self.table_old = QtWidgets.QTableWidget(10, 2, self)
        self.table_old.setHorizontalHeaderLabels(["מיקום", "שעה"])
        self.table_old.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.table_old.setStyleSheet("""
            QTableWidget {
                background-color: black;
                color: white;
            }
            QHeaderView::section {
                background-color: black;
                color: white;
            }
        """)
        layout.addWidget(self.table_old)

        self.setLayout(layout)
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Missile Alert System')
        self.show()
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.movable:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.movable and self.offset is not None:
            new_position = self.mapToParent(event.pos() - self.offset)
            self.move(new_position)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.movable:
            self.movable = False
            self.offset = None
        else:
            super().mouseReleaseEvent(event)

    def play_alert_sound(self):
        if self.sound_muted:
            QtWidgets.QMessageBox.information(self, "השתקת צליל", "הצליל הושתק")
        else:
            alert_sound_path = 'C:/Users/cseli/Documents/Projects/Projects Python/GUI/12.mp3'
            pygame.mixer.music.load(alert_sound_path)
            pygame.mixer.music.play()

    def check_alerts(self):
        try:
            response = requests.get("https://www.oref.org.il/WarningMessages/History/AlertsHistory.json")
            alerts = response.json()

            # בדיקה אם זו הרצה ראשונה
            if not self.last_checked_time:
                # אם כן, עדכון הטבלאות והזמן האחרון ללא קפיצת הודעה
                self.update_tables(alerts)
                if alerts:
                    self.last_checked_time = alerts[0]['alertDate']
            else:
                # אם לא, בדיקה אם יש התראה חדשה
                new_alerts = [alert for alert in alerts if alert['alertDate'] > self.last_checked_time]
                if new_alerts:
                    # אם יש התראה חדשה, עדכון הטבלאות והזמן האחרון וקפיצת הודעה
                    self.last_checked_time = new_alerts[0]['alertDate']
                    self.update_tables(alerts)
                    location = new_alerts[0]['data']  # קיבלתי את המיקום מהנתונים החדשים ביותר
                    msg_box = CustomMessageBox(location)
                    msg_box.exec_()

        except Exception as e:
            print(f"An error occurred: {e}")

        # הגדרת הטיימר לבדיקה הבאה
        QtCore.QTimer.singleShot(5000, self.check_alerts)

    def update_tables(self, alerts):
        # Update new alerts table
        self.table_new.clearContents()
        for i, alert in enumerate(alerts[:5]):
            self.table_new.setItem(i, 0, QtWidgets.QTableWidgetItem(alert['data']))
            self.table_new.setItem(i, 1, QtWidgets.QTableWidgetItem(alert['alertDate']))

        # Adjust columns width to fit content for new alerts table
        self.table_new.resizeColumnsToContents()
        self.table_new.resizeRowsToContents()

        # Update old alerts table
        self.table_old.clearContents()
        for i, alert in enumerate(alerts[5:15]):
            self.table_old.setItem(i, 0, QtWidgets.QTableWidgetItem(alert['data']))
            self.table_old.setItem(i, 1, QtWidgets.QTableWidgetItem(alert['alertDate']))

        # Adjust columns width to fit content for old alerts table
        self.table_old.resizeColumnsToContents()
        self.table_old.resizeRowsToContents()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = MissileAlertApp()
    sys.exit(app.exec_())
    ex = MissileAlertApp()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
