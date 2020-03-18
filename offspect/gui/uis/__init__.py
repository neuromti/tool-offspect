from importlib import import_module


def get_ui(resolution: str = ""):

    if resolution == "":
        from offspect.gui.uis import visual_inspection_gui as pygui
    else:
        pygui = import_module(f"offspect.gui.uis.visual_inspection_gui_{resolution}")

    class useUI(Ui, pygui.Ui_MainWindow):
        pass

    return useUI
