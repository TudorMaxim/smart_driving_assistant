from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QComboBox, QSpinBox, \
    QGroupBox, QHBoxLayout


class ConfigForm(QDialog):
    def __init__(self, parent=None):
        super(ConfigForm, self).__init__(parent=parent)
        self.create_form_group_box()

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.form_group_box)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def create_object_detection_form_group_box(self):
        self.ld_form_group_box = QGroupBox("Object detection configuration")

        self.od_confidence_thresh_input = QSpinBox()
        self.od_confidence_thresh_input.setMinimum(20)
        self.od_confidence_thresh_input.setMaximum(100)
        self.od_confidence_thresh_input.setValue(50)

        self.od_iou_thresh_input = QSpinBox()
        self.od_iou_thresh_input.setMinimum(10)
        self.od_iou_thresh_input.setMaximum(100)
        self.od_iou_thresh_input.setValue(40)

        self.image_size_input = QComboBox()
        self.image_size_input.addItem('256x256')
        self.image_size_input.addItem('416x416')
        self.image_size_input.addItem('720x720')
        self.image_size_input.setCurrentIndex(1)

        layout = QFormLayout()
        layout.addRow(QLabel('Image Size:'), self.image_size_input)
        layout.addRow(QLabel("Confidence Threshold (%):"), self.od_confidence_thresh_input)
        layout.addRow(QLabel("IoU Threshold (%):"), self.od_iou_thresh_input)
        self.ld_form_group_box.setLayout(layout)
    
    def create_lane_detection_form_group_box(self):
        self.od_form_group_box = QGroupBox("Lane detection configuration")

        self.ld_confidence_thresh_input = QSpinBox()
        self.ld_confidence_thresh_input.setMinimum(20)
        self.ld_confidence_thresh_input.setMaximum(100)
        self.ld_confidence_thresh_input.setValue(50)

        self.distance_error = QSpinBox()
        self.distance_error.setMinimum(15)
        self.distance_error.setMaximum(50)
        self.distance_error.setValue(15)

        layout = QFormLayout()
        layout.addRow(QLabel("Confidence Threshold (%):"), self.ld_confidence_thresh_input)
        layout.addRow(QLabel("Distance Error (%):"), self.distance_error)
        self.od_form_group_box.setLayout(layout)

    def create_form_group_box(self):
        self.create_object_detection_form_group_box()
        self.create_lane_detection_form_group_box()
        self.form_group_box = QGroupBox("Driving Assistant Configuration")
        layout = QHBoxLayout()
        layout.addWidget(self.ld_form_group_box)
        layout.addWidget(self.od_form_group_box)
        self.form_group_box.setLayout(layout)

    def accept(self) -> None:
        pass

    def reject(self) -> None:
        pass