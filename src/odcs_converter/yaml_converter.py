"""YAML conversion utilities for ODCS data."""

import logging
from pathlib import Path
from typing import Any, Dict, Union
import yaml

logger = logging.getLogger(__name__)


class YAMLConverter:
    """Convert between ODCS dictionary and YAML format."""

    @staticmethod
    def dict_to_yaml(data: Dict[str, Any], output_path: Union[str, Path]) -> None:
        """Convert ODCS dictionary to YAML file.

        Args:
            data: ODCS data dictionary
            output_path: Path to output YAML file

        Raises:
            ValueError: If data cannot be serialized to YAML
            IOError: If file cannot be written
        """
        output_path = Path(output_path)

        try:
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    data,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    indent=2,
                    width=120,
                    allow_unicode=True,
                )

            logger.info(f"YAML file written successfully: {output_path}")

        except Exception as e:
            logger.error(f"Failed to write YAML file {output_path}: {e}")
            raise ValueError(f"Cannot serialize data to YAML: {e}")

    @staticmethod
    def yaml_to_dict(yaml_path: Union[str, Path]) -> Dict[str, Any]:
        """Load YAML file and convert to dictionary.

        Args:
            yaml_path: Path to YAML file

        Returns:
            Dictionary containing YAML data

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            ValueError: If YAML file is invalid
        """
        yaml_path = Path(yaml_path)

        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")

        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                raise ValueError(
                    "YAML file must contain a dictionary/object at root level"
                )

            logger.info(f"YAML file loaded successfully: {yaml_path}")
            return data

        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML file {yaml_path}: {e}")
            raise ValueError(f"Invalid YAML format: {e}")
        except Exception as e:
            logger.error(f"Failed to read YAML file {yaml_path}: {e}")
            raise ValueError(f"Cannot read YAML file: {e}")

    @staticmethod
    def dict_to_yaml_string(data: Dict[str, Any]) -> str:
        """Convert ODCS dictionary to YAML string.

        Args:
            data: ODCS data dictionary

        Returns:
            YAML formatted string

        Raises:
            ValueError: If data cannot be serialized to YAML
        """
        try:
            return yaml.dump(
                data,
                default_flow_style=False,
                sort_keys=False,
                indent=2,
                width=120,
                allow_unicode=True,
            )
        except Exception as e:
            logger.error(f"Failed to serialize data to YAML string: {e}")
            raise ValueError(f"Cannot serialize data to YAML: {e}")

    @staticmethod
    def yaml_string_to_dict(yaml_string: str) -> Dict[str, Any]:
        """Parse YAML string and convert to dictionary.

        Args:
            yaml_string: YAML formatted string

        Returns:
            Dictionary containing YAML data

        Raises:
            ValueError: If YAML string is invalid
        """
        try:
            data = yaml.safe_load(yaml_string)

            if not isinstance(data, dict):
                raise ValueError(
                    "YAML string must contain a dictionary/object at root level"
                )

            return data

        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML string: {e}")
            raise ValueError(f"Invalid YAML format: {e}")
        except Exception as e:
            logger.error(f"Failed to process YAML string: {e}")
            raise ValueError(f"Cannot process YAML string: {e}")

    @staticmethod
    def is_yaml_file(file_path: Union[str, Path]) -> bool:
        """Check if file has YAML extension.

        Args:
            file_path: Path to file

        Returns:
            True if file has YAML extension (.yaml or .yml)
        """
        file_path = Path(file_path)
        return file_path.suffix.lower() in [".yaml", ".yml"]

    @staticmethod
    def normalize_yaml_extension(
        file_path: Union[str, Path], prefer_yaml: bool = True
    ) -> Path:
        """Normalize YAML file extension.

        Args:
            file_path: Original file path
            prefer_yaml: If True, use .yaml extension; otherwise use .yml

        Returns:
            Path with normalized YAML extension
        """
        file_path = Path(file_path)

        if file_path.suffix.lower() in [".yaml", ".yml"]:
            return file_path

        # Add appropriate YAML extension
        extension = ".yaml" if prefer_yaml else ".yml"
        return file_path.with_suffix(extension)
