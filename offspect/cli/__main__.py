from pathlib import Path
from typing import Union, List
from offspect.cache.file import CacheFile, merge, populate
import argparse
from ast import literal_eval


def cli_peek(args: argparse.Namespace):
    print(CacheFile(args.fname))


def cli_merge(args: argparse.Namespace):
    tf = merge(to=args.to, sources=args.sources)
    if args.verbose:
        print("Content of target file is now:")
        print(CacheFile(tf))


def cli_tms(args: argparse.Namespace):
    """

    Example::

        offspect tms -t test.hdf5 -f /media/rgugg/tools/python3/tool-load-tms/tests/coords_contralesional.xml /media/rgugg/tools/python3/tool-load-tms/tests/map_contralesional.mat -pp 100 100 -r contralateral_mep -c EDC_L


    .. admonition:: smartmove

        eep-peek /media/rgugg/server/mnt/data/data02/RawData/2019_ST_RoboTMS_EEG/AmWo/20190704/AmWo_AmWo_2019-07-04_15-51-55.cnt

        tells you which events are in the cnt file

        offspect tms -t test.hdf5 -f /media/rgugg/server/mnt/data/data02/RawData/2019_ST_RoboTMS_EMG/AmWo/20190704/AmWo1\ 2019-07-04_15-51-37.cnt /media/rgugg/server/mnt/data/data02/RawData/2019_ST_RoboTMS_EEG/AmWo/20190704/AmWo_AmWo_2019-07-04_15-51-55.cnt /media/rgugg/server/mnt/data/data02/RawData/2019_ST_RoboTMS_Coordinates/AmWo/20190704/documentation.txt -r contralateral_mep -c Ch1 -pp 100 100 -e 1

        populates a cachefile

    """
    suffices = []
    for s in args.sources:
        suffices.append(Path(s).suffix)

    if ".mat" in suffices and ".xml" in suffices:
        fmt = "matprot"
    elif ".cnt" in suffices and ".txt" in suffices:
        fmt = "smartmove"
    elif ".xdf" in suffices:
        if ".xml" in suffices:
            fmt = "manuxdf"
        else:
            fmt = "autoxdf"
    else:
        raise NotImplementedError("Unknown input format")

    print(f"Assuming source data is from {fmt} protocol")
    if fmt == "matprot":
        from offspect.input.tms.matprotconv import (  # type: ignore
            prepare_annotations,
            cut_traces,
        )

        for s in args.sources:
            if Path(s).suffix == ".xml":
                xmlfile = Path(s)
            if Path(s).suffix == ".mat":
                matfile = Path(s)

        annotation = prepare_annotations(  # type: ignore
            xmlfile=xmlfile,
            matfile=matfile,
            readout=args.readout,
            channel=args.channel,
            pre_in_ms=float(args.prepost[0]),
            post_in_ms=float(args.prepost[1]),
        )
        traces = cut_traces(matfile, annotation)
    elif fmt == "smartmove":
        from offspect.input.tms.smartmove import (  # type: ignore
            prepare_annotations,
            cut_traces,
            is_eeg_file,
        )

        cntfiles = []
        for s in args.sources:
            if Path(s).suffix == ".cnt":
                cntfiles.append(Path(s))
            if Path(s).suffix == ".txt":
                docfile = Path(s)

        if len(cntfiles) != 2:
            raise ValueError("too many input .cnt files")
        for f in cntfiles:
            if is_eeg_file(f):
                eegfile = f
            else:
                emgfile = f

        annotation = prepare_annotations(  # type: ignore
            docfile=docfile,
            eegfile=eegfile,
            emgfile=emgfile,
            readout=args.readout,
            channel=args.channel,
            pre_in_ms=float(args.prepost[0]),
            post_in_ms=float(args.prepost[1]),
            select_events=args.select_events,
        )
        for f in cntfiles:
            if f.name == annotation["origin"]:
                traces = cut_traces(f, annotation)
    # ---------------

    populate(args.to, [annotation], [traces])


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="offspect",
        description="Create, manipulate and inspect cachefiles for offline inspection of evoked potentials",
    )
    subparsers = parser.add_subparsers(dest="sub")

    # PEEK --------------------------------------------------------------------
    peek = subparsers.add_parser(
        name="peek", help="peek into a cachefile and print essential information"
    )
    peek.add_argument("fname", help="filename to peek into", type=str)

    # MERGE -------------------------------------------------------------------
    merge = subparsers.add_parser(name="merge", help="merge two cachefiles into one")
    merge.add_argument(
        "-t",
        "--to",
        help="filename to merge into. May not already exist",
        type=str,
        required=True,
        dest="to",
    )
    merge.add_argument(
        "-f",
        "--from",
        nargs="+",
        help="<Required> list of files to merge",
        required=True,
        dest="sources",
    )
    merge.add_argument("-verbose", "-v", help="be more verbose", action="store_true")

    # tms ---------------------------------------------------------------------
    tms = subparsers.add_parser(
        name="tms", help="prepare cachefiles for a tms protocol"
    )
    tms.add_argument(
        "-t",
        "--to",
        help="filename of the cachefile to be populated",
        type=str,
        required=True,
        dest="to",
    )
    tms.add_argument(
        "-f",
        "--from",
        nargs="+",
        help="<Required> list of input files",
        required=True,
        dest="sources",
    )
    tms.add_argument(
        "-r",
        "--readout",
        type=str,
        help="the desired readout",
        required=True,
        dest="readout",
    )
    tms.add_argument(
        "-c",
        "--channel",
        type=str,
        help="the desired channel",
        required=True,
        dest="channel",
    )
    tms.add_argument(
        "-pp",
        "--prepost",
        nargs="+",
        help="<Required> positional arguments of pre and post duration",
        required=True,
        dest="prepost",
    )
    tms.add_argument(
        "-e",
        "--events",
        nargs="+",
        help="<Required> select event",
        required=False,
        type=str,
        dest="select_events",
    )
    # ------------------------------------------------------------------------
    return parser


def main():
    # get the parser
    parser = get_parser()
    # parse and run respective subcommands
    args, _ = parser.parse_known_args()
    if args.sub == "peek":
        cli_peek(args)
    elif args.sub == "merge":
        cli_merge(args)
    elif args.sub == "tms":
        cli_tms(args)
    else:
        print("No valid subcommand specified")


# ----------------------------------------------------------------------------

from typing import Iterator


def format_help(parser) -> Iterator[str]:  # pragma no cover
    cb = ".. code-block:: none\n\n"

    title = parser.prog + "\n" + "~" * len(parser.prog)
    helpstr = parser.format_help()
    yield title + "\n"
    yield cb
    for line in helpstr.splitlines():
        yield "   " + line + "\n"
    yield "\n\n"
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for choice, subparser in action.choices.items():
                title = subparser.prog + "\n" + "~" * len(subparser.prog)
                yield title + "\n"
                yield cb
                for line in subparser.format_help().splitlines():
                    yield "   " + line + "\n"
                yield "\n\n"


def create_cli_rst(fname: str):  # pragma no cover
    desc = """
   
offspect offers a command line interface. This interface can be accessed after installation of the package from the terminal, e.g. peek into a CacheFile with 

.. code-block:: bash

   offspect peek example.hdf5

"""
    helpstr = format_help(get_parser())
    with open(fname, "w") as f:
        f.write("Command Line Interface\n")
        f.write("----------------------\n")
        f.write(desc)
        for h in helpstr:
            f.write(h)
