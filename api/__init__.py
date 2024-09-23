# -*- coding: utf-8 -*-
"""Top level package for Alexion MLOps Test."""
import os
from importlib import metadata
from pathlib import Path

__version__ = metadata.version("alxn_test")


BASEPATH = Path(__file__).parent
WORKDIR = Path(os.getenv("WORKDIR", BASEPATH.parent))

CONFIG_DIR = WORKDIR / "config"
DATA_DIR = WORKDIR / "data"
MODEL_DIR = WORKDIR / "models"
SEED = 2345
