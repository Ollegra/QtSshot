import sys
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QRectF, QPointF
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QPainterPath, QPen, QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QMessageBox, QFileDialog,
                             QVBoxLayout, QHBoxLayout, QPushButton, QLabel)
from PIL import ImageGrab
import os

global screenshot


class SnippingWidget(QMainWindow):
    closed = pyqtSignal()
    def __init__(self, parent=None):
        super(SnippingWidget, self).__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background:transparent;")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        self.outsideSquareColor = "red"
        self.squareThickness = 2

        self.start_point = QPointF()
        self.end_point = QPointF()

    def mousePressEvent(self, event):
        self.start_point = event.pos().toPointF()
        self.end_point = event.pos().toPointF()
        self.update()


    def mouseMoveEvent(self, event):
        self.end_point = event.pos().toPointF()
        self.update()


    def mouseReleaseEvent(self, QMouseEvent):
        global screenshot
        r = QRectF(self.start_point, self.end_point).normalized()
        self.hide()
        bbox = r.getCoords()
        if bbox[0] == bbox[2] or bbox[1] == bbox[3]:
            self.show()
            msg = QMessageBox.information(
                None,
                'Внимание',
                'Не выбран прямоугольник для скриншота, попродуйте еще раз.')
            super().mouseReleaseEvent(QMouseEvent)
            return
#           img = ImageGrab.grab(bbox=r.getCoords())
        img = ImageGrab.grab(bbox=bbox)
        img.save("temp/testImage.png")                       # <---- установите свой путь
        screenshot = QPixmap("temp/testImage.png")
        QApplication.restoreOverrideCursor()
        self.closed.emit()
        self.start_point = QPointF()
        self.end_point = QPointF()


    def paintEvent(self, event):
        trans = QColor(22, 100, 233)
        r = QRectF(self.start_point, self.end_point).normalized()
        qp = QPainter(self)
        trans.setAlphaF(0.2)
        qp.setBrush(trans)
        outer = QPainterPath()
        outer.addRect(QRectF(self.rect()))
        inner = QPainterPath()
        inner.addRect(r)
        r_path = outer - inner
        qp.drawPath(r_path)
        qp.setPen(QPen(QColor(self.outsideSquareColor), self.squareThickness))
        trans.setAlphaF(0)
        qp.setBrush(trans)
        qp.drawRect(r)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Инструмент скриншотов')
        self.setGeometry(50, 50, 450, 250)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #1A9AC8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #47AFD5;
            }
        """)
        #self.screenshot = None
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        
        
        self.label = QLabel()
        layout = QVBoxLayout(self.centralWidget)
        layout.addWidget(self.label)

        button_layout = QHBoxLayout()
        self.button = QPushButton(' Cкриншот')
        self.button.setIcon(QIcon(os.path.join("icons", "screenshot.png")))
        self.button.setShortcut('Ctrl+7')
        self.button.clicked.connect(self.activateSnipping)

        self.copyBtn = QPushButton(' Копировать')
        self.copyBtn.setIcon(QIcon(os.path.join("icons", "copy.png")))
        self.copyBtn.clicked.connect(self.copyToClipboard)
        self.copyBtn.setEnabled(False)
        
        self.save_btn = QPushButton(' Сохранить')
        self.save_btn.setIcon(QIcon(os.path.join("icons", "save.png")))
        self.save_btn.clicked.connect(self.save_screenshot)
        self.save_btn.setEnabled(False)

        button_layout.addWidget(self.button)
        button_layout.addWidget(self.copyBtn)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)
        self.shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut.activated.connect(self.activateSnipping)

        if not os.path.exists("temp"):
            os.makedirs("temp")

        self.snipper = SnippingWidget()
        self.snipper.closed.connect(self.on_closed)


    def activateSnipping(self):
        self.snipper.showFullScreen()
        QApplication.setOverrideCursor(Qt.CursorShape.CrossCursor)
        self.hide()

    def on_closed(self):
        global screenshot
        self.label.setPixmap(screenshot) 
        self.show()
        self.adjustSize()
        self.copyBtn.setEnabled(True)
        self.save_btn.setEnabled(True)

    def copyToClipboard(self):
        global screenshot
        QApplication.clipboard().setPixmap(screenshot)
        QMessageBox.information(
            None, 
            'Внимание', 
            'Изображение скопировано в буфер обмена')
    
    def save_screenshot(self):
        global screenshot
        if screenshot:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить скриншот",
                os.path.expanduser("~/Pictures/screenshot.png"),
                "Images (*.png *.jpg *.bmp)"
            )
            if file_path:
                screenshot.save(file_path)

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join("icons", "pitivi.png")))
    w = MainWindow()
    #w.resize(400, 400)
    w.show()       
    sys.exit(app.exec())