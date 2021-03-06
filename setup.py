#!/usr/bin/env python

import os
from importlib.util import module_from_spec, spec_from_file_location

from setuptools import find_packages, setup

_PATH_ROOT = os.path.dirname(__file__)


def _load_py_module(fname, pkg="hp_space_generator"):
    spec = spec_from_file_location(
        os.path.join(pkg, fname), os.path.join(_PATH_ROOT, pkg, fname)
    )
    py = module_from_spec(spec)
    spec.loader.exec_module(py)
    return py


setup_tools = _load_py_module("setup_tools.py")

REQUIREMENTS = [req.strip() for req in open("requirements.txt").readlines()]

setup(
    name="hp_space_generator",
    version="0.0.1",
    description="Generator Hyper Parameter space around the given choices of hyper-parameters with Grid Search and Random Search strategies",
    author="Kushashwa Ravi Shrimali, Ethan Harris",
    author_email="kush@lightning.ai",
    url="https://github.com/Lightning-AI/LAI-Hyper-Parameter-Space-Generator-Component",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=setup_tools._load_requirements(_PATH_ROOT),
)
