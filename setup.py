import setuptools
from distutils.core import setup
from pathlib import Path

with (Path(__file__).parent / "readme.md").open("r") as f:
    long_description = f.read()

setup(
    name="offline-inspect,
    version="0.0.1",
    description="Visually inspect evoked responses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Robert Guggenberger",
    author_email="robert.guggenberger@uni-tuebingen.de",
    url="https://github.com/pyreiz/ctrl-localite",
    download_url="https://github.com/pyreiz/ctrl-localite",
    license="MIT",
    packages=["offspect",
    entry_points={
        "console_scripts": [
            "offspect-populate=offspect.cli:populate",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
