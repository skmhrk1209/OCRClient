import numpy as np
import cv2
import sys
import re
import base64
import json
import client
from algorithms import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class MainWindow(QWidget):

    def __init__(self):

        super(MainWindow, self).__init__()

        self.image_layout = QVBoxLayout()

        self.image_view = QGraphicsView()
        self.image_scene = QGraphicsScene()
        self.image_scene.setSceneRect(0, 0, 512, 512)

        self.image_pixmap = QGraphicsPixmapItem()
        self.image_scene.addItem(self.image_pixmap)

        self.bounding_box = QGraphicsRectItem()
        self.bounding_box.setPen(QPen(Qt.red, 2))
        self.image_scene.addItem(self.bounding_box)

        self.image_view.setScene(self.image_scene)
        self.image_layout.addWidget(self.image_view)

        self.property_layout = QVBoxLayout()

        self.setting_layout = QGridLayout()

        self.ip_address_label = QLabel("IP Address")
        self.setting_layout.addWidget(self.ip_address_label, 0, 0)

        self.ip_address_edit = QLineEdit("192.168.1.4")
        self.setting_layout.addWidget(self.ip_address_edit, 0, 1)

        self.port_number_label = QLabel("Port Number")
        self.setting_layout.addWidget(self.port_number_label, 1, 0)

        self.port_number_edit = QLineEdit("1234")
        self.setting_layout.addWidget(self.port_number_edit, 1, 1)

        self.property_layout.addLayout(self.setting_layout)

        self.operation_layout = QVBoxLayout()

        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self.open)
        self.operation_layout.addWidget(self.open_button)

        self.request_button = QPushButton("Request OCR")
        self.request_button.clicked.connect(self.request)
        self.operation_layout.addWidget(self.request_button)

        self.property_layout.addLayout(self.operation_layout)

        self.result_layout = QVBoxLayout()

        self.prediction_label = QLabel("Predictions")
        self.prediction_label.setAlignment(Qt.AlignCenter)
        self.result_layout.addWidget(self.prediction_label)

        self.prediction_edits = [QLineEdit() for _ in range(4)]
        for prediction_edit in self.prediction_edits:
            self.result_layout.addWidget(prediction_edit)

        self.attentionn_label = QLabel("Attentions")
        self.attentionn_label.setAlignment(Qt.AlignCenter)
        self.result_layout.addWidget(self.attentionn_label)

        self.attention_slider = QSlider(Qt.Horizontal)
        self.attention_slider.valueChanged.connect(self.pay_attention)
        self.result_layout.addWidget(self.attention_slider)

        self.property_layout.addLayout(self.result_layout)

        self.main_layout = QHBoxLayout()

        self.main_layout.addLayout(self.image_layout)
        self.main_layout.addLayout(self.property_layout)

        self.setLayout(self.main_layout)
        self.setWindowTitle("Attention OCR")

    def open(self):

        filename, _ = QFileDialog.getOpenFileName(self, "Open file", ".")
        self.image = QImage(filename)
        self.image_pixmap.setPixmap(QPixmap.fromImage(self.image).scaled(512, 512))

    def request(self):

        image = self.image.scaled(256, 256)
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")
        base64_encoded = byte_array.toBase64().data()

        result = json.loads(client.request(self.ip_address_edit.text(), self.port_number_edit.text(), base64_encoded))
        self.predictions = result["predictions"]
        self.bounding_boxes = result["bounding_boxes"]
        self.bounding_boxes = map_innermost_list(lambda point: list(map(lambda x: x * 16, point))[::-1], self.bounding_boxes)
        self.bounding_boxes = map_innermost_list(lambda point: QPointF(*point), self.bounding_boxes)
        self.bounding_boxes = map_innermost_list(lambda rect: QRectF(*rect), self.bounding_boxes)
        self.bounding_boxes = flatten_innermost_element(self.bounding_boxes)

        for prediction_edit, prediction in zip(self.prediction_edits, self.predictions):
            prediction_edit.setText(prediction)

    def pay_attention(self, value):

        self.bounding_box.setRect(self.bounding_boxes[int(len(self.bounding_boxes) * value / 100.0)])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
