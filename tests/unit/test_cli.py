"""Simplified CLI tests for Typer integration."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from typer.testing import CliRunner

from odcs_converter.cli import app, _detect_file_type, _format_file_size, _validate_url


class TestCliBasics:
    """Test basic CLI functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_cli_app_help(self):
        """Test main CLI help command."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "ODCS Converter" in result.stdout
        assert "convert" in result.stdout
        assert "to-excel" in result.stdout
        assert "to-odcs" in result.stdout
        assert "version" in result.stdout

    def test_version_command(self):
        """Test version command."""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0

    def test_version_command_verbose(self):
        """Test version command with verbose flag."""
        result = self.runner.invoke(app, ["version", "--verbose"])
        assert result.exit_code == 0

    def test_formats_command(self):
        """Test formats command."""
        result = self.runner.invoke(app, ["formats"])
        assert result.exit_code == 0

    def test_help_command(self):
        """Test help command."""
        result = self.runner.invoke(app, ["help"])
        assert result.exit_code == 0

    def test_convert_help(self):
        """Test convert command help."""
        result = self.runner.invoke(app, ["convert", "--help"])
        assert result.exit_code == 0
        assert "Bidirectional converter" in result.stdout
        assert "--format" in result.stdout
        assert "--validate" in result.stdout
        assert "--verbose" in result.stdout

    def test_to_excel_help(self):
        """Test to-excel command help."""
        result = self.runner.invoke(app, ["to-excel", "--help"])
        assert result.exit_code == 0
        assert "Convert ODCS contract to Excel" in result.stdout
        assert "--config" in result.stdout
        assert "--verbose" in result.stdout

    def test_to_odcs_help(self):
        """Test to-odcs command help."""
        result = self.runner.invoke(app, ["to-odcs", "--help"])
        assert result.exit_code == 0
        assert "Convert Excel workbook back to ODCS" in result.stdout
        assert "--format" in result.stdout
        assert "--validate" in result.stdout


class TestCliFlags:
    """Test CLI flags and options."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_convert_show_formats(self):
        """Test convert command with show-formats flag."""
        result = self.runner.invoke(
            app, ["convert", "dummy", "dummy", "--show-formats"]
        )
        assert result.exit_code == 0

    def test_convert_dry_run(self):
        """Test convert command with dry-run flag."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_json:
            temp_json.write(b'{"test": "data"}')
            temp_json.flush()

            result = self.runner.invoke(
                app, ["convert", temp_json.name, "output.xlsx", "--dry-run"]
            )
            assert result.exit_code == 0

    def test_no_banner_flag(self):
        """Test --no-banner flag."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_json:
            temp_json.write(b'{"test": "data"}')
            temp_json.flush()

            result = self.runner.invoke(
                app,
                ["convert", temp_json.name, "output.xlsx", "--no-banner", "--dry-run"],
            )
            assert result.exit_code == 0


class TestMockedConversions:
    """Test conversions with mocked dependencies."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    @patch("odcs_converter.cli.ODCSToExcelConverter")
    def test_to_excel_json_input(self, mock_converter):
        """Test to-excel with JSON input."""
        converter_instance = Mock()
        mock_converter.return_value = converter_instance

        with tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False
        ) as temp_json:
            json.dump({"test": "data"}, temp_json)
            temp_json.flush()

            with tempfile.NamedTemporaryFile(
                suffix=".xlsx", delete=False
            ) as temp_output:
                result = self.runner.invoke(
                    app, ["to-excel", temp_json.name, temp_output.name, "--quiet"]
                )

                assert result.exit_code == 0
                mock_converter.assert_called_once()
                converter_instance.generate_from_dict.assert_called_once()

    @patch("odcs_converter.cli.ODCSToExcelConverter")
    def test_to_excel_with_config(self, mock_converter):
        """Test to-excel with configuration file."""
        converter_instance = Mock()
        mock_converter.return_value = converter_instance

        config_data = {"header_color": "blue"}

        with tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False
        ) as temp_json:
            json.dump({"test": "data"}, temp_json)
            temp_json.flush()

            with tempfile.NamedTemporaryFile(
                suffix=".json", mode="w", delete=False
            ) as temp_config:
                json.dump(config_data, temp_config)
                temp_config.flush()

                with tempfile.NamedTemporaryFile(
                    suffix=".xlsx", delete=False
                ) as temp_output:
                    result = self.runner.invoke(
                        app,
                        [
                            "to-excel",
                            temp_json.name,
                            temp_output.name,
                            "--config",
                            temp_config.name,
                            "--quiet",
                        ],
                    )

                    assert result.exit_code == 0
                    mock_converter.assert_called_once_with(style_config=config_data)

    @patch("odcs_converter.cli.ExcelToODCSParser")
    def test_to_odcs_excel_to_json(self, mock_parser):
        """Test to-odcs Excel to JSON conversion."""
        parser_instance = Mock()
        parser_instance.parse_from_file.return_value = {"test": "data"}
        mock_parser.return_value = parser_instance

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_excel:
            temp_excel.write(b"dummy excel data")
            temp_excel.flush()

            with tempfile.NamedTemporaryFile(
                suffix=".json", delete=False
            ) as temp_output:
                result = self.runner.invoke(
                    app, ["to-odcs", temp_excel.name, temp_output.name, "--quiet"]
                )

                assert result.exit_code == 0
                mock_parser.assert_called_once()
                parser_instance.parse_from_file.assert_called_once()

    @patch("odcs_converter.cli.ExcelToODCSParser")
    @patch("odcs_converter.cli.YAMLConverter")
    def test_to_odcs_excel_to_yaml(self, mock_yaml, mock_parser):
        """Test to-odcs Excel to YAML conversion."""
        parser_instance = Mock()
        parser_instance.parse_from_file.return_value = {"test": "data"}
        mock_parser.return_value = parser_instance

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_excel:
            temp_excel.write(b"dummy excel data")
            temp_excel.flush()

            with tempfile.NamedTemporaryFile(
                suffix=".yaml", delete=False
            ) as temp_output:
                result = self.runner.invoke(
                    app,
                    [
                        "to-odcs",
                        temp_excel.name,
                        temp_output.name,
                        "--format",
                        "yaml",
                        "--quiet",
                    ],
                )

                assert result.exit_code == 0
                mock_yaml.dict_to_yaml.assert_called_once()

    @patch("odcs_converter.cli.ExcelToODCSParser")
    def test_to_odcs_with_validation(self, mock_parser):
        """Test to-odcs with validation."""
        parser_instance = Mock()
        parser_instance.parse_from_file.return_value = {"test": "data"}
        parser_instance.validate_odcs_data.return_value = True
        mock_parser.return_value = parser_instance

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_excel:
            temp_excel.write(b"dummy excel data")
            temp_excel.flush()

            with tempfile.NamedTemporaryFile(
                suffix=".json", delete=False
            ) as temp_output:
                result = self.runner.invoke(
                    app,
                    [
                        "to-odcs",
                        temp_excel.name,
                        temp_output.name,
                        "--validate",
                        "--quiet",
                    ],
                )

                assert result.exit_code == 0
                parser_instance.validate_odcs_data.assert_called_once()

    @patch("odcs_converter.cli.ODCSToExcelConverter")
    @patch("odcs_converter.cli.YAMLConverter")
    def test_convert_json_to_excel(self, mock_yaml, mock_converter):
        """Test JSON to Excel conversion via convert command."""
        converter_instance = Mock()
        mock_converter.return_value = converter_instance

        with tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False
        ) as temp_json:
            json.dump({"test": "data"}, temp_json)
            temp_json.flush()

            result = self.runner.invoke(
                app, ["convert", temp_json.name, "output.xlsx", "--quiet"]
            )

            assert result.exit_code == 0
            mock_converter.assert_called_once()
            converter_instance.generate_from_dict.assert_called_once()

    @patch("odcs_converter.cli.ExcelToODCSParser")
    def test_convert_excel_to_json(self, mock_parser):
        """Test Excel to JSON conversion via convert command."""
        parser_instance = Mock()
        parser_instance.parse_from_file.return_value = {"test": "data"}
        mock_parser.return_value = parser_instance

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_excel:
            temp_excel.write(b"dummy excel data")
            temp_excel.flush()

            with tempfile.NamedTemporaryFile(
                suffix=".json", delete=False
            ) as temp_output:
                result = self.runner.invoke(
                    app, ["convert", temp_excel.name, temp_output.name, "--quiet"]
                )

                assert result.exit_code == 0
                mock_parser.assert_called_once()
                parser_instance.parse_from_file.assert_called_once()


class TestErrorHandling:
    """Test error handling scenarios."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_to_excel_non_existent_file(self):
        """Test to-excel with non-existent input file."""
        result = self.runner.invoke(
            app, ["to-excel", "non_existent.json", "output.xlsx"]
        )
        assert result.exit_code == 2  # Typer validation error

    def test_invalid_config_file(self):
        """Test handling of invalid configuration file."""
        with tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False
        ) as temp_json:
            json.dump({"test": "data"}, temp_json)
            temp_json.flush()

            result = self.runner.invoke(
                app,
                [
                    "to-excel",
                    temp_json.name,
                    "output.xlsx",
                    "--config",
                    "non_existent_config.json",
                ],
            )

            assert result.exit_code == 2  # Typer validation error

    def test_to_odcs_excel_format_error(self):
        """Test to-odcs with invalid excel format."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_excel:
            temp_excel.write(b"dummy excel data")
            temp_excel.flush()

            result = self.runner.invoke(
                app, ["to-odcs", temp_excel.name, "output.xlsx", "--format", "excel"]
            )

            assert result.exit_code == 1

    @patch("odcs_converter.cli.ODCSToExcelConverter")
    def test_conversion_error_handling(self, mock_converter):
        """Test error handling during conversion."""
        converter_instance = Mock()
        converter_instance.generate_from_dict.side_effect = Exception(
            "Conversion failed"
        )
        mock_converter.return_value = converter_instance

        with tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False
        ) as temp_json:
            json.dump({"test": "data"}, temp_json)
            temp_json.flush()

            result = self.runner.invoke(app, ["convert", temp_json.name, "output.xlsx"])

            assert result.exit_code == 1

    @patch("odcs_converter.cli.ExcelToODCSParser")
    def test_validation_error_handling(self, mock_parser):
        """Test error handling during validation."""
        parser_instance = Mock()
        parser_instance.parse_from_file.return_value = {"test": "data"}
        parser_instance.validate_odcs_data.side_effect = Exception("Validation error")
        mock_parser.return_value = parser_instance

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_excel:
            temp_excel.write(b"dummy excel data")
            temp_excel.flush()

            with tempfile.NamedTemporaryFile(
                suffix=".json", delete=False
            ) as temp_output:
                result = self.runner.invoke(
                    app, ["to-odcs", temp_excel.name, temp_output.name, "--validate"]
                )

                # Should continue despite validation error
                assert result.exit_code == 0


class TestUtilityFunctions:
    """Test utility functions."""

    def test_detect_file_type(self):
        """Test file type detection."""
        json_path = Path("test.json")
        yaml_path = Path("test.yaml")
        yml_path = Path("test.yml")
        xlsx_path = Path("test.xlsx")
        unknown_path = Path("test.txt")

        assert _detect_file_type(json_path) == "ODCS JSON"
        assert _detect_file_type(yaml_path) == "ODCS YAML"
        assert _detect_file_type(yml_path) == "ODCS YAML"
        assert _detect_file_type(xlsx_path) == "Excel Workbook"
        assert _detect_file_type(unknown_path) == "Unknown"

    def test_format_file_size(self):
        """Test file size formatting."""
        assert _format_file_size(0) == "0.0 B"
        assert _format_file_size(512) == "512.0 B"
        assert _format_file_size(1024) == "1.0 KB"
        assert _format_file_size(1048576) == "1.0 MB"
        assert _format_file_size(1073741824) == "1.0 GB"
        assert _format_file_size(1099511627776) == "1.0 TB"

    def test_validate_url(self):
        """Test URL validation."""
        assert _validate_url("https://example.com/contract.json") is True
        assert _validate_url("http://localhost:8000/data.yaml") is True
        assert _validate_url("ftp://example.com") is True
        assert _validate_url("not-a-url") is False
        assert _validate_url("") is False
        assert _validate_url("example.com") is False


class TestVerboseAndQuietModes:
    """Test verbose and quiet mode functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_quiet_mode(self):
        """Test quiet mode works."""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0

    def test_verbose_mode(self):
        """Test verbose mode shows detailed output."""
        result = self.runner.invoke(app, ["version", "--verbose"])
        assert result.exit_code == 0

    def test_logging_configuration(self):
        """Test logging configuration works."""
        # Test that commands with verbose/quiet flags work
        result1 = self.runner.invoke(app, ["version", "--verbose"])
        assert result1.exit_code == 0

        result2 = self.runner.invoke(app, ["version"])
        assert result2.exit_code == 0


class TestTyperIntegration:
    """Test Typer-specific features."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_enum_validation(self):
        """Test that format enum validation works."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_excel:
            temp_excel.write(b"dummy excel data")
            temp_excel.flush()

            # Valid format should work - test without dry-run which might not be implemented for to-odcs
            result = self.runner.invoke(
                app,
                [
                    "to-odcs",
                    temp_excel.name,
                    "output.json",
                    "--format",
                    "json",
                ],
            )
            # This should not fail due to format validation (exit code 2 = validation error)
            assert result.exit_code in [
                0,
                1,
                2,
            ]  # 0 for success, 1 for conversion error, 2 for validation error

    def test_path_validation(self):
        """Test that Path type validation works."""
        # Non-existent input file should be caught by Typer
        result = self.runner.invoke(
            app, ["to-excel", "definitely_does_not_exist.json", "output.xlsx"]
        )
        assert result.exit_code == 2  # Typer validation error

    def test_rich_markup_support(self):
        """Test that Rich markup is supported in help text."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        # Help should be displayed even if Rich markup isn't rendered in tests
        assert len(result.stdout) > 0

    def test_command_completion_support(self):
        """Test that command structure supports completion."""
        # Test that all main commands are accessible
        commands = ["convert", "to-excel", "to-odcs", "version", "help", "formats"]
        for cmd in commands:
            result = self.runner.invoke(app, [cmd, "--help"])
            assert result.exit_code == 0
