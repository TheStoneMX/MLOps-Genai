# -*- coding: utf-8 -*-
"""Script for data preparation."""
import sys
from pathlib import Path

import click
import pandas as pd
from loguru import logger
from sklearn import model_selection

from alxn_test import CONFIG_DIR, DATA_DIR, SEED
from alxn_test.settings import PreparationSettings


@click.command("prepare-data")
@click.option(
    "--config-path", default=CONFIG_DIR / "config.yaml", type=click.Path(True, path_type=Path)
)
@click.option(
    "--in-path",
    default=DATA_DIR / "winequality-red.csv",
    type=click.Path(True, path_type=Path),
    help="Path where raw data is read from.",
)
@click.option(
    "--out-train",
    default=DATA_DIR / "train.parquet",
    type=click.Path(path_type=Path),
    help="Path where prepared train data is stored.",
)
@click.option(
    "--out-test",
    default=DATA_DIR / "test.parquet",
    type=click.Path(path_type=Path),
    help="Path where prepared test data is stored.",
)
def prepare_data(config_path: Path, in_path: Path, out_train: Path, out_test: Path) -> None:
    """Prepare train and test raw red wine data.

    :param config_path: Path to configuration file.
    :param in_path: Path where raw data is read from.
    :param out_train: Path where prepared train data is stored.
    :param out_test: Path where prepared test data is stored.
    """
    try:
        logger.info("Cleaning data")

        settings = PreparationSettings.load(
            config_path, in_path=in_path, out_train=out_train, out_test=out_test
        )
        logger.debug("Settings loaded from {} file", config_path.absolute())

        data = pd.read_csv(settings.in_path)
        logger.info("Raw data read from {} file", settings.in_path.absolute())

        train, test = model_selection.train_test_split(
            data, test_size=settings.test_size, random_state=SEED
        )
        logger.debug("Train and test data split")

        train.to_parquet(settings.out_train)
        logger.info("Train data stored in {} file", settings.out_train.absolute())

        test.to_parquet(settings.out_test)
        logger.info("Test data stored in {} file", settings.out_test.absolute())

    except Exception as exc:
        logger.error("Unexpected error")
        logger.error(exc.with_traceback())
        sys.exit(1)


if __name__ == "__main__":
    prepare_data()
