from PyQt5.QtWidgets import QMessageBox


def raise_error(message: str = "Error", info: str = "More iInformation"):
    box = QMessageBox()
    kind, msg, info = message.split(":")
    box.setIcon(QMessageBox.Critical)
    box.setWindowTitle(kind + " Error")
    box.setText(msg)
    box.setInformativeText(info)
    box.exec_()
