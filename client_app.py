import sys
import client
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class MainWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.view_layout = QVBoxLayout()
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 512, 512)
        self.pixmap = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap)
        self.view.setScene(self.scene)
        self.view_layout.addWidget(self.view)

        self.button_layout = QVBoxLayout()

        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self.open)
        self.button_layout.addWidget(self.open_button)

        self.request_button = QPushButton("Request OCR")
        self.request_button.clicked.connect(self.request)
        self.button_layout.addWidget(self.request_button)

        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.view_layout)
        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)
        self.setWindowTitle("Attention OCR")

    def open(self):

        filename, _ = QFileDialog.getOpenFileName(self, "Open file", ".")
        self.pixmap.setPixmap(QPixmap(filename).scaled(self.scene.sceneRect().size().toSize()))

    def request(self):

        client.request("127.0.0.1", 1234, "image.jpg")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
