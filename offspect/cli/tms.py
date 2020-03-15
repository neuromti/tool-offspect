from pathlib import Path
from offspect.cache.file import CacheFile, populate
import argparse
import yaml


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
        

    """
    print(args)
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
    elif fmt == "autoxdf":
        from offspect.input.tms.xdfprot import prepare_annotations  # type: ignore

        kwargs = dict()
        for source in args.sources:
            if Path(source).suffix == ".xml":
                kwargs["xmfile"] = source
            if Path(source).suffix == ".xdf":
                xdffile = source

        annotation = prepare_annotations(  # type: ignore
            xdffile=xdffile,
            readout=args.readout,
            channel=args.channel,
            pre_in_ms=float(args.prepost[0]),
            post_in_ms=float(args.prepost[1]),
            **kwargs,
        )

    # ---------------

    print(yaml.dump(annotation))


# populate(args.to, [annotation], [traces])

