from pathlib import Path
from offspect.cache.file import CacheFile, populate
import argparse
import yaml
from typing import List
from liesl.files.xdf.inspect_xdf import peek
from offspect.cache.readout import get_valid_readouts
from offspect.input import get_protocol_handler

READIN = Path(__file__).stem
VALID_READOUTS: List[str] = get_valid_readouts(READIN)


def cli_tms(args: argparse.Namespace):
    """Look at the CLI signature at :doc:`cli`

    .. admonition::  Matlab protocol
    
        Create a new CacheFile directly from the files for data and targets::

            offspect tms -t test.hdf5 -f coords_contralesional.xml /map_contralesional.mat -pp 100 100 -r contralateral_mep -c EDC_L


    .. admonition:: Smartmove protocol

        Peek into the source file for the eeg::
            
            eep-peek VvNn_VvNn_1970-01-01_00-00-01.cnt

        which tells you which events are in the cnt file. Here, we use the event `1` 

        Create a new CacheFile using the file for targets, emg and eeg::

            offspect tms -t test.hdf5 -f VvNn_VvNn_1970-01-01_00-00-01.cnt VvNn\ 1970-01-01_00-00-01.cnt documentation.txt -r contralateral_mep -c Ch1 -pp 100 100 -e 1
        
    .. admonition:: XDF protocol with localite stream

        Convert directly from the source xdf file::
            
            offspect tms -f mapping_contra_R004.xdf -t map.hdf5 -pp 100 100 -r contralateral_mep -c EDC_L

        

    """
    # print(args)
    suffixes = dict()
    for source in args.sources:
        suffixes[Path(source).suffix] = source

    if ".mat" in suffixes.keys() and ".xml" in suffixes.keys():
        protocol = "mat"
    elif ".cnt" in suffixes.keys() and ".txt" in suffixes.keys():
        protocol = "smartmove"
    elif ".xdf" in suffixes.keys():
        protocol = "xdf"
        from offspect.protocols.xdf import has_localite

        sinfos = peek(suffixes[".xdf"], at_most=99, max_duration=1)
        stream_names = [sinfo["name"] for sinfo in sinfos]
        # check whether localite is present
        if has_localite(stream_names):
            if ".xml" in suffixes:
                protocol = "xdfxml"

    else:
        raise NotImplementedError("Unknown input format")

    print(f"Assuming data is from {protocol} for {READIN}-{args.readout}")
    prepare_annotations, cut_traces = get_protocol_handler(
        READIN, args.readout, protocol
    )

    # MATLAB PROTOCOL ---------------------------------------------------------
    if protocol == "mat":
        for s in args.sources:
            if Path(s).suffix == ".xml":
                xmlfile = Path(s)
            if Path(s).suffix == ".mat":
                matfile = Path(s)

        annotation = prepare_annotations(  # type: ignore
            xmlfile=xmlfile,
            matfile=matfile,
            channel_of_interest=args.channel,
            pre_in_ms=float(args.prepost[0]),
            post_in_ms=float(args.prepost[1]),
        )
        traces = cut_traces(matfile, annotation)

    # SMARTMOVE ---------------------------------------------------------------
    elif protocol == "smartmove":
        cntfiles = []
        for s in args.sources:
            if Path(s).suffix == ".cnt":
                cntfiles.append(Path(s))
        if len(cntfiles) != 2:
            raise ValueError("too many input .cnt files")

        annotation = prepare_annotations(  # type: ignore
            docfile=suffixes[".txt"],
            cntfiles=cntfiles,
            channel=args.channel,
            pre_in_ms=float(args.prepost[0]),
            post_in_ms=float(args.prepost[1]),
            select_events=args.select_events,
        )
        for f in cntfiles:
            if f.name == annotation["origin"]:
                traces = cut_traces(f, annotation)

    # XDF WITH COORDINATES in STREAM ------------------------------------------
    elif protocol == "xdf":
        "classical xdf file with coordinates stored in the xdf as a stream from localite_flow"
        if args.select_events is None:
            event_stream = "localite_marker"
            event_name = "coil_0_didt"
        elif len(args.select_events) == 2:
            event_stream = args.select_events[0]
            event_name = args.select_events[1]
        else:
            raise ValueError("Please specify event_stream and event_name")

        annotation = prepare_annotations(  # type: ignore
            xdffile=suffixes[".xdf"],
            channel=args.channel,
            pre_in_ms=float(args.prepost[0]),
            post_in_ms=float(args.prepost[1]),
            event_stream=event_stream,
            event_name=event_name,
        )
        traces = cut_traces(suffixes[".xdf"], annotation)
    # XDF WITHOUT COORDINATES in STREAM ---------------------------------------
    elif protocol == "xdfxml":
        # if an xml file is present, use that one to fall back to it in case there are no coordinates saved in the streams
        annotation = prepare_annotations(  # type: ignore
            xdffile=suffixes[".xdf"],
            channel=args.channel,
            pre_in_ms=float(args.prepost[0]),
            post_in_ms=float(args.prepost[1]),
            event_name=args.select_events[1],
            event_stream=args.select_events[0],
            xmlfile=suffixes[".xml"],
        )
        traces = cut_traces(suffixes[".xdf"], annotation)
    elif protocol == "xdfnolocalite":
        annotation = prepare_annotations(  # type: ignore
            xdffile=suffixes[".xdf"],
            readout=args.readout,
            channel=args.channel,
            pre_in_ms=float(args.prepost[0]),
            post_in_ms=float(args.prepost[1]),
        )
        traces = cut_traces(suffixes[".xdf"], annotation)
    else:
        print(f"Handling {protocol} for {READIN}-{args.readout} is ot implemented")
    # ---------------

    if len(traces) == 0:
        print("Found no traces. Aborting")
        return

    print(f"Found {len(traces)} traces")
    # print(yaml.dump(annotation))
    populate(args.to, [annotation], [traces])
