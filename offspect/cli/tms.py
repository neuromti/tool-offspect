from pathlib import Path
from offspect.cache.file import CacheFile, populate
import argparse
import yaml
from typing import List
from liesl.files.xdf.inspect_xdf import peek
from offspect.cache.readout import get_valid_readouts

VALID_READOUTS: List[str] = get_valid_readouts(Path(__file__).stem)


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
    print(args)
    suffixes = dict()
    for source in args.sources:
        suffixes[Path(source).suffix] = source

    if ".mat" in suffixes.keys() and ".xml" in suffixes.keys():
        fmt = "matprot"
    elif ".cnt" in suffixes.keys() and ".txt" in suffixes.keys():
        fmt = "smartmove"
    elif ".xdf" in suffixes.keys():
        fmt = "xdfprot"
    else:
        raise NotImplementedError("Unknown input format")

    print(f"Assuming source data is from {fmt} protocol")
    # MATPROT -----------------------------------------------------------------
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
            channel_of_interest=args.channel,
            pre_in_ms=float(args.prepost[0]),
            post_in_ms=float(args.prepost[1]),
        )
        traces = cut_traces(matfile, annotation)

    # SMARTMOVE ---------------------------------------------------------------
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
        if len(cntfiles) != 2:
            raise ValueError("too many input .cnt files")

        for f in cntfiles:
            if is_eeg_file(f):
                eegfile = f
            else:
                emgfile = f

        annotation = prepare_annotations(  # type: ignore
            docfile=suffixes[".txt"],
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

    # XDF -------------------------------------------------------
    elif fmt == "xdfprot":
        sinfos = peek(suffixes[".xdf"], at_most=99, max_duration=1)
        if "localite_flow" not in (sinfo["name"] for sinfo in sinfos):
            if ".xml" in suffixes:
                fmt = "xmlxdf"
            else:
                fmt = "manuxdf"
        else:
            fmt = "autoxdf"

        from offspect.input.tms.xdfprot import prepare_annotations, cut_traces  # type: ignore

        # if an xml file is present, use that one to fall back to it in case there are no coordinates saved in the streams
        kwargs = {"xmlfile": suffixes.get(".xml", None)}

        annotation = prepare_annotations(  # type: ignore
            xdffile=suffixes[".xdf"],
            readout=args.readout,
            channel=args.channel,
            pre_in_ms=float(args.prepost[0]),
            post_in_ms=float(args.prepost[1]),
            **kwargs,
        )
        traces = cut_traces(suffixes[".xdf"], annotation)

    # ---------------

    print(yaml.dump(annotation))
    populate(args.to, [annotation], [traces])
