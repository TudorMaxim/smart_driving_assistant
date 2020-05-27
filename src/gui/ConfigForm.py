from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QFormLayout, QLabel, QComboBox, QSpinBox, \
    QGroupBox, QFileDialog, QPushButton, QWidget, QRadioButton
from utils.Constants import Constants


class ConfigForm(QDialog):
    def __init__(self, parent=None):
        super(ConfigForm, self).__init__(parent=parent)
        self.create_form_group_box()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.form_group_box)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)
        self.setStyleSheet(open(Constants.STYLES_PATH + 'ConfigForm.css').read())

    def create_form_group_box(self):
        self.form_group_box = QGroupBox("Run the detector")
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

        self.od_use_tiny_yolo = QRadioButton()
        self.od_use_tiny_yolo.setChecked(False)

        self.path = ''
        self.selected_path = QLabel()
        self.error_message = QLabel()
        self.error_message.setStyleSheet("QLabel {color: red;}")
        self.browse_button = QPushButton('Browse')
        sub_layout = QVBoxLayout()
        sub_layout.addWidget(self.browse_button)
        sub_layout.addWidget(self.selected_path)
        sub_layout.addWidget(self.error_message)
        sub_layout.setContentsMargins(0, 0, 0, 0)
        select_widget = QWidget()
        select_widget.setLayout(sub_layout)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout = QFormLayout()
        layout.addRow(QLabel('Image Size:'), self.image_size_input)
        layout.addRow(QLabel("Confidence Threshold (%):"), self.od_confidence_thresh_input)
        layout.addRow(QLabel("IoU Threshold (%):"), self.od_iou_thresh_input)
        layout.addRow(QLabel("Direction Error (%):"), self.ld_direction_error_input)
        layout.addRow(QLabel('Use Tiny YoloV3:'), self.od_use_tiny_yolo)
        layout.addRow(QLabel('Select a folder:'), select_widget)
        layout.addWidget(self.button_box)

        self.form_group_box.setLayout(layout)

    def browse(self):
        self.path = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        if self.path != '' and self.error_message.text() != '':
            self.error_message.setText('')
        self.selected_path.setText(self.truncate_path())

    def browse_video(self):
        self.path, _ = QFileDialog.getOpenFileName(self, "Select a video", 'C:\\', "*.mp4")
        if self.path != '' and self.error_message.text() != '':
            self.error_message.setText('')
        self.selected_path.setText(self.truncate_path())

    def clear_form(self):
        self.path = ''
        self.selected_path.setText(self.path)
        self.error_message.setText('')
        self.ld_direction_error_input.setValue(15)
        self.od_iou_thresh_input.setValue(40)
        self.od_confidence_thresh_input.setValue(50)
        self.image_size_input.setCurrentIndex(1)
        self.od_use_tiny_yolo.setChecked(False)

    def truncate_path(self):
        truncated = self.path.split("/")
        if len(truncated) > 2:
            return truncated[0] + '/.../' + truncated[-1]
        return self.path