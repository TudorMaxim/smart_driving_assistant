from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QFormLayout, QLabel, QComboBox, QSpinBox, \
    QGroupBox, QFileDialog, QPushButton, QWidget, QHBoxLayout


class ConfigForm(QDialog):
    def __init__(self, parent=None):
        super(ConfigForm, self).__init__(parent=parent)
        self.create_form_group_box()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.form_group_box)
        self.setLayout(main_layout)
        self.setStyleSheet(open('../../styles/ConfigForm.css').read())

    def create_form_group_box(self):
        self.form_group_box = QGroupBox("Choose your configuration")

        self.image_size_input = QComboBox()
        self.image_size_input.addItem('256x256')
        self.image_size_input.addItem('416x416')
        self.image_size_input.addItem('720x720')
        self.image_size_input.setCurrentIndex(1)

        self.od_confidence_thresh_input = QSpinBox()
        self.od_confidence_thresh_input.setMinimum(20)
        self.od_confidence_thresh_input.setMaximum(100)
        self.od_confidence_thresh_input.setValue(50)

        self.od_iou_thresh_input = QSpinBox()
        self.od_iou_thresh_input.setMinimum(10)
        self.od_iou_thresh_input.setMaximum(100)
        self.od_iou_thresh_input.setValue(40)

        self.ld_direction_error_input = QSpinBox()
        self.ld_direction_error_input.setMinimum(15)
        self.ld_direction_error_input.setMaximum(50)
        self.ld_direction_error_input.setValue(15)

        self.path = ''
        self.selected_path = QLabel()
        browse_button = QPushButton('Browse')
        browse_button.clicked.connect(self.browse)
        sub_layout = QHBoxLayout()
        sub_layout.addWidget(browse_button)
        sub_layout.addWidget(self.selected_path)
        sub_layout.setContentsMargins(0, 0, 0, 0)
        select_widget = QWidget()
        select_widget.setLayout(sub_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.run_detector)
        button_box.rejected.connect(self.reset_fields)

        layout = QFormLayout()
        layout.addRow(QLabel('Image Size:'), self.image_size_input)
        layout.addRow(QLabel("Confidence Threshold (%):"), self.od_confidence_thresh_input)
        layout.addRow(QLabel("IoU Threshold (%):"), self.od_iou_thresh_input)
        layout.addRow(QLabel("Direction Error (%):"), self.ld_direction_error_input)
        layout.addRow(QLabel('Select a folder:'), select_widget)
        layout.addWidget(button_box)
        self.form_group_box.setLayout(layout)

    def browse(self):
        self.path = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        self.selected_path.setText(self.path)

    def run_detector(self):
        print("TODO: run the detector on a different thread")

    def reset_fields(self):
        print("TODO: reset all input fields")
