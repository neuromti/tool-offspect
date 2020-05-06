import setuptools
from distutils.core import setup
from pathlib import Path


with (Path(__file__).parent / "readme.md").open("r") as f:
    long_description = f.read()

with (Path(__file__).parent / "requirements.txt").open("r") as f:
    requirements = [l for l in f.readlines() if not "http" in l]


packages = setuptools.find_namespace_packages(exclude=["tests*", "docs*", "htmlcov*"])

setup(
    name="offspect",
    version="0.1.2",
    description="Visually inspect evoked responses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Robert Guggenberger",
    author_email="robert.guggenberger@uni-tuebingen.de",
    url="https://github.com/pyreiz/ctrl-localite",
    download_url="https://github.com/pyreiz/ctrl-localite",
    license="MIT",
    packages=packages,
    entry_points={"console_scripts": ["offspect=offspect.cli.__main__:main",],},
    install_requires=requirements,
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
