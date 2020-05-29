from PyQt5 import QtWidgets


def get_ui(*args, **kwargs):
    app = QtWidgets.QApplication([__file__])
    from offspect.gui.mainwindow import MainWindow as UI

    return app, UI


def cli_gui(args):
    app, UI = get_ui(args.resolution)
    window = UI(filename=args.filename)
    window.show()
    app.exec_()


if __name__ == "__main__":
    app, UI = get_ui()
    window = UI(filename=None)
    window.show()
    app.exec_()
