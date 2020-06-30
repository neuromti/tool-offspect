import argparse


def cli_gui(args: argparse.Namespace):
    from offspect.gui.api import get_ui

    app, UI = get_ui(args.resolution)
    window = UI(filename=args.filename)
    window.show()
    app.exec_()


def cli_peek(args: argparse.Namespace):
    from offspect.api import CacheFile, decode
    from offspect.cache.steps import process_data
    from collections import defaultdict
    import numpy as np

    cf = CacheFile(args.fname)
    print(cf)

    D: defaultdict = defaultdict(list)
    for ix, (data, attrs) in enumerate(cf):
        data = process_data(data, attrs, verbose=False)
        traceID = attrs["id"]
        D[traceID].append((data, ix))

    # overlap = len([key for key, count in D.items() if len(count) > 1])
    # print(f"{overlap} of {len(cf)} traces share the same id")
    if args.similarity is not None:
        for key, values in D.items():
            if len(values) > 1:
                traces = [v[0] for v in values]
                idx = [v[1] + 1 for v in values]
                with np.errstate(invalid="ignore"):
                    r = np.corrcoef(np.asanyarray(traces))
                for row in range(len(traces)):
                    for col in range(len(traces)):
                        if row > col:
                            coeff = r[row, col]
                            if abs(coeff) > args.similarity:
                                print(
                                    f"WARNING: traces [{idx[col]}, {idx[row]}] share ID {key} and are similar with r = {coeff:3.2f}"
                                )


def cli_merge(args: argparse.Namespace):
    from offspect.cache.file import CacheFile, merge

    tf = merge(to=args.to, sources=args.sources)
    if args.verbose:
        print("Content of target file is now:")
        print(CacheFile(tf))


def cli_plot(args: argparse.Namespace):
    from offspect.cache.file import CacheFile
    from offspect.cache.plot import plot_map

    cf = CacheFile(args.cfname)
    if args.kwargs is None:
        display = plot_map(cf)
    else:
        display = plot_map(cf, **args.kwargs)
    display.show()
    if args.sfname is not None:
        display.savefig(args.sfname)
        print("Saving to", args.sfname)

