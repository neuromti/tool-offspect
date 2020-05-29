import argparse


def cli_gui(args: argparse.Namespace):
    from offspect.gui.api import get_ui

    app, UI = get_ui(args.resolution)
    window = UI(filename=args.filename)
    window.show()
    app.exec_()


def cli_peek(args: argparse.Namespace):
    from offspect.cache.file import CacheFile

    print(CacheFile(args.fname))


def cli_merge(args: argparse.Namespace):
    from offspect.cache.file import CacheFile, merge

    tf = merge(to=args.to, sources=args.sources)
    if args.verbose:
        print("Content of target file is now:")
        print(CacheFile(tf))
