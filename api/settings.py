# -*- coding: utf-8 -*-
"""Settings for ``dtmsdg``."""
import dataclasses
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Self, final, get_type_hints

from loguru import logger
from pandas import DateOffset, Period, Timedelta, Timestamp
from yaml import safe_load

_TIME_TYPES = {Period, Timestamp, Timedelta, DateOffset}


class SettingsError(Exception):
    """Raised when settings class fails."""


class NotDataClassError(SettingsError):
    """Raised when settings class is not defined as a dataclass."""


class MissingParamError(SettingsError):
    """Raised when settings class load is not given all the expected parameters."""


class _AbstractSettings:
    """Settings.

    It includes ``load`` class method to read settings from a file.

    Parameters to read in child classes and their data types are defined in class annotations::

        ChildSettings(Settings):

            attr_name: attr_type

    All child classes must be dataclasses.
    """

    @final
    @classmethod
    def load(cls, filepaths: str | Path | Iterable[str | Path] | None = None, **params) -> Self:
        """Create a settings container from config file's or a list of config files' contents.

        Parameters can be added after the config filepath to override the settings added from
        the file.

        This method can be used by each of the settings subclasses.

        Example::

            >> config_path = "config/config.yaml"
            >> preprocess_settings = PreprocessSettings.load(config_path, board_id="board_id")

        In the example above we load settings from the config_db.yaml file and we override the
        settings board_id with the string given.

        ``run_post_load`` can be reimplemented in order to define post load actions.

        :param filepaths: Path to file containing settings or list of paths of config files.
        :param params: Parameters to override config file contents.
        :raises NotDataClassError: When the class using ``load`` is not a dataclass.
        :raises MissingParamError: When a required parameter is not given.
        :return: Settings container created from config file contents.
        """
        if not dataclasses.is_dataclass(cls):
            raise NotDataClassError("The class using this method is not a dataclass.")

        fields = set(get_type_hints(cls).keys())

        settings = {}

        if filepaths:
            filepaths = _process_filepaths(filepaths)

            for filepath in filepaths:
                with Path(filepath).open(encoding="utf-8") as file:
                    content = safe_load(file)

                content = {field: value for field, value in content.items() if field in fields}

                if set(settings.keys()).intersection(content.keys()):
                    logger.warning(
                        "Configuration files provided have duplicated parameters. Value from the "
                        "latest provided will be kept."
                    )

                settings.update(content)

        settings.update({field: value for field, value in params.items() if value is not None})

        settings = cls._convert_to_time(settings)

        try:
            return cls(**settings)

        except TypeError as exc:
            raise MissingParamError(
                "Not all necessary parameters were given to load via configuration file or "
                "additional parameter."
            ) from exc

    @final
    @classmethod
    def _convert_to_time(cls, settings: dict) -> dict:
        """Convert all the parameters in settings that should have a time format from python default
        string to the corresponding format.

        :param settings: Dictionary of settings.
        :return: Settings with time parameters converted to the required types.
        """
        time_field_types = {
            field: field_type
            for field, field_type in get_type_hints(cls).items()
            if field in settings and field_type in _TIME_TYPES
        }

        for field, field_type in time_field_types.items():
            if settings[field] is not None:
                settings[field] = field_type(settings[field])

        return settings


def _process_filepaths(filepaths: str | Path | Iterable[str | Path]) -> list[Path | str]:
    """Process filepath to obtain a list of paths.

    :param filepaths: Valid ``filepaths`` input given to load function.
    :return: ``filepaths`` as a list of file paths.
    """
    if isinstance(filepaths, Path | str):
        filepaths = [filepaths]

    elif not isinstance(filepaths, list):
        filepaths = list(filepaths)

    return filepaths


@dataclass(frozen=True)
class PreparationSettings(_AbstractSettings):
    """Settings for data preparation.

    :param target: Target column name.
    :param test_size: Test set size.
    :param in_path: Path where raw data is read from.
    :param out_train: Path where prepared train data is stored.
    :param out_test: Path where prepared test data is stored.
    """

    target: str
    test_size: float
    in_path: Path
    out_train: Path
    out_test: Path
