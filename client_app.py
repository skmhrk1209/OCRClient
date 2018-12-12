import numpy as np
import cv2
import sys
import re
import base64
import json
import client
from class_names import *
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

        self.image_view.setScene(self.image_scene)
        self.image_layout.addWidget(self.image_view)

        self.misc_layout = QVBoxLayout()

        self.setting_layout = QGridLayout()

        self.ip_address_label = QLabel("IP Address")
        self.setting_layout.addWidget(self.ip_address_label, 0, 0)

        self.ip_address_edit = QLineEdit("127.0.0.1")
        self.setting_layout.addWidget(self.ip_address_edit, 0, 1)

        self.port_number_label = QLabel("Port Number")
        self.setting_layout.addWidget(self.port_number_label, 1, 0)

        self.port_number_edit = QLineEdit("1234")
        self.setting_layout.addWidget(self.port_number_edit, 1, 1)

        self.misc_layout.addLayout(self.setting_layout)

        self.property_layout = QVBoxLayout()

        self.class_name_label = QLabel("Class Name")
        self.class_name_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        self.property_layout.addWidget(self.class_name_label)

        self.class_name_edit = QLineEdit()
        self.property_layout.addWidget(self.class_name_edit)

        self.class_id_slider = QSlider(Qt.Horizontal)
        self.class_id_slider.setRange(0, 999)
        self.class_id_slider.valueChanged.connect(
            lambda value: self.class_name_edit.setText(class_names[value])
        )
        self.property_layout.addWidget(self.class_id_slider)

        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self.open)
        self.property_layout.addWidget(self.open_button)

        self.misc_layout.addLayout(self.property_layout)

        self.request_layout = QVBoxLayout()

        self.request_classification_button = QPushButton("Request Classification")
        self.request_classification_button.clicked.connect(self.request_classification)
        self.request_layout.addWidget(self.request_classification_button)

        self.request_generation_button = QPushButton("Request Generation")
        self.request_generation_button.clicked.connect(self.request_generation)
        self.request_layout.addWidget(self.request_generation_button)

        self.misc_layout.addLayout(self.request_layout)

        self.main_layout = QHBoxLayout()

        self.main_layout.addLayout(self.image_layout)
        self.main_layout.addLayout(self.misc_layout)

        self.setLayout(self.main_layout)
        self.setWindowTitle("TensorFlow Hub Application")

        self.result = {}

    def open(self):

        filename, _ = QFileDialog.getOpenFileName(self, "Open file", ".")
        self.image = QImage(filename)
        self.image_pixmap.setPixmap(QPixmap.fromImage(self.image).scaled(512, 512))

    def request_classification(self):

        image = self.image.convertToFormat(QImage.Format_RGB888).scaled(224, 224)
        image = image.constBits().asstring(image.byteCount())
        image = np.fromstring(image, np.uint8).reshape(224, 224, 3)

        image = cv2.imencode(".png", image)[1]
        image = image.tostring()
        image = base64.b64encode(image)

        self.result.update(json.loads(client.request(
            self.ip_address_edit.text(),
            self.port_number_edit.text(),
            json.dumps(dict(process_type="classification", image=image))
        )))

        self.class_id_slider.setValue(self.result["class_id"])

    def request_generation(self):

        self.result.update(json.loads(client.request(
            self.ip_address_edit.text(),
            self.port_number_edit.text(),
            json.dumps(dict(process_type="generation", class_id=self.class_id_slider.value()))
        )))

        image = base64.b64decode(self.result["image"])
        image = np.fromstring(image, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        self.image = QImage(image.data, 512, 512, 512 * 3, QImage.Format_RGB888)
        self.image_pixmap.setPixmap(QPixmap.fromImage(self.image))


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
