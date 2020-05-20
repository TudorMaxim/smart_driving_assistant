from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout


class VideosWidget(QWidget):
    def __init__(self, parent=None):
        super(VideosWidget, self).__init__(parent=parent)
        layout = QVBoxLayout()
        label = QLabel()
        label.setText("process a video!")
        layout.addWidget(label)
        self.setLayout(layout)
