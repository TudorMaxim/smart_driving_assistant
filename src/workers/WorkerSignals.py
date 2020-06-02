from PyQt5.QtCore import QObject, pyqtSignal


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal()
