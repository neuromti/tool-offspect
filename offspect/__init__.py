from pkg_resources import get_distribution as _get_version

release = _get_version("offspect").version

from offspect.gui import __main__
