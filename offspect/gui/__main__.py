from offspect.gui.ui import get_ui, start_window


def main(args):
    app, UI = get_ui(args.resolution)
    window = UI(filename=args.filename)
    start_window(app, window)


if __name__ == "__main__":
    app, UI = get_ui()
    window = UI(filename=None)
    start_window(app, window)
