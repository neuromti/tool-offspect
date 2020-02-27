import yaml
from pathlib import Path
from typing import Union, Dict, List


def snippet():
    fname = Path(__file__).parent / "../templates/events_<identifier>.yml"
    with fname.open() as f:
        tmp = f.read()
        yml = [x for x in yaml.load_all(tmp, Loader=yaml.Loader)][0]

    def print_yml(yml: dict, offset: int = 0, shift: int = 15):
        off = " "
        for key, val in yml.items():
            if type(val) is dict:
                print(f"{key:{shift}}:{{")
                print_yml(val, offset=offset + shift + 2, shift=1)
                print(" " * (offset + shift), "}")
            else:
                print(f"{off*offset}{key:{shift}}:", val)

    print_yml(yml)


def load(fname: Union[str, Path]) -> List[Dict]:
    """load an event file and return a list of their contents
    
    args
    ----
    fname: 
        Path to the eventfile
    
    returns
    -------
    ymls
        a List of dictionaries read from the .yml file

    Usually, there would be only a single entry, but if the efile
    was merged, it would contain multiple entries.
    """
    fname = Path(fname)
    if fname.suffix != ".yml" or fname.name[0:6] == "events_":
        print(fname.name[0:6])
        raise Exception(f"{str(fname)} is not a valid eventfile")

    with fname.open() as f:
        tmp = f.read()
        yml = [yml for yml in yaml.load_all(tmp, Loader=yaml.Loader)]
    return yml
