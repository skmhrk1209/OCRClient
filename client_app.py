import numpy as np
import cv2
import sys
import base64
import client
from PyQt5.QtCore import *
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

        self.property_layout = QVBoxLayout()

        self.textbox_layout_1 = QGridLayout()

        self.ip_address_label = QLabel("IP Address")
        self.textbox_layout_1.addWidget(self.ip_address_label, 0, 0)

        self.ip_address_textbox = QLineEdit("192.168.1.4")
        self.textbox_layout_1.addWidget(self.ip_address_textbox, 0, 1)

        self.port_number_label = QLabel("Port Number")
        self.textbox_layout_1.addWidget(self.port_number_label, 1, 0)

        self.port_number_textbox = QLineEdit("1234")
        self.textbox_layout_1.addWidget(self.port_number_textbox, 1, 1)

        self.property_layout.addLayout(self.textbox_layout_1)

        self.button_layout = QVBoxLayout()

        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self.open)
        self.button_layout.addWidget(self.open_button)

        self.request_button = QPushButton("Request OCR")
        self.request_button.clicked.connect(self.request)
        self.button_layout.addWidget(self.request_button)

        self.property_layout.addLayout(self.button_layout)

        self.textbox_layout_2 = QVBoxLayout()

        self.annotation_textboxes = [QLineEdit() for _ in range(4)]
        for annotation_textbox in self.annotation_textboxes:
            self.textbox_layout_2.addWidget(annotation_textbox)

        self.property_layout.addLayout(self.textbox_layout_2)

        self.main_layout = QHBoxLayout()

        self.main_layout.addLayout(self.view_layout)
        self.main_layout.addLayout(self.property_layout)

        self.setLayout(self.main_layout)
        self.setWindowTitle("Attention OCR")

    def open(self):

        filename, _ = QFileDialog.getOpenFileName(self, "Open file", ".")
        self.image = QImage(filename)
        self.pixmap.setPixmap(QPixmap.fromImage(self.image).scaled(self.scene.sceneRect().size().toSize()))

    def request(self):

        image = self.image.scaled(256, 256)
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")
        base64_encoded = byte_array.toBase64().data()

        annotations = client.request(self.ip_address_textbox.text(), self.port_number_textbox.text(), base64_encoded)
        for annotation_textbox, annotation in zip(self.annotation_textboxes, annotations.split("_")):
            annotation_textbox.setText(annotation)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
