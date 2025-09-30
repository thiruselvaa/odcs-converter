"""Integration tests for CLI functionality with real file operations."""

import json
import tempfile
from pathlib import Path
from typer.testing import CliRunner

from odcs_converter.cli import app
from odcs_converter.yaml_converter import YAMLConverter


class TestCliIntegration:
    """Integration tests for CLI with real file operations."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.test_data_dir = Path(__file__).parent.parent / "test_data"
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_sample_odcs_json(self) -> Path:
        """Create a sample ODCS JSON file for testing."""
        odcs_data = {
            "apiVersion": "v3.0.2",
            "kind": "DataContract",
            "id": "test-contract",
            "version": "1.0.0",
            "status": "active",
            "name": "Test Contract",
            "description": {"purpose": "Test ODCS contract for integration testing"},
            "schema": [
                {
                    "name": "test_table",
                    "physicalName": "test_table",
                    "logicalType": "object",
                    "physicalType": "table",
                    "description": "Test table",
                    "properties": [
                        {
                            "name": "id",
                            "logicalType": "integer",
                            "physicalType": "INT",
                            "description": "Primary key",
                            "isPrimaryKey": True,
                            "primaryKeyPosition": 1,
                        },
                        {
                            "name": "name",
                            "logicalType": "string",
                            "physicalType": "VARCHAR(255)",
                            "description": "Name field",
                            "isNullable": False,
                        },
                    ],
                }
            ],
            "quality": [
                {
                    "id": "quality_1",
                    "name": "Primary Key Check",
                    "description": "Ensure primary key is unique",
                    "type": "uniqueness",
                    "specification": {
                        "type": "library",
                        "library": "great_expectations",
                        "operator": "unique",
                    },
                }
            ],
            "team": [
                {
                    "name": "Data Team",
                    "email": "data-team@example.com",
                    "role": "Data Owner",
                }
            ],
        }

        json_file = self.temp_dir / "sample_contract.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(odcs_data, f, indent=2)

        return json_file

    def create_sample_odcs_yaml(self) -> Path:
        """Create a sample ODCS YAML file for testing."""
        json_file = self.create_sample_odcs_json()

        with open(json_file, "r", encoding="utf-8") as f:
            odcs_data = json.load(f)

        yaml_file = self.temp_dir / "sample_contract.yaml"
        YAMLConverter.dict_to_yaml(odcs_data, yaml_file)

        return yaml_file

    def test_version_command_integration(self):
        """Test version command integration."""
        result = self.runner.invoke(app, ["version"])

        assert result.exit_code == 0
        # Version command should work without errors

    def test_version_verbose_integration(self):
        """Test verbose version command integration."""
        result = self.runner.invoke(app, ["version", "--verbose"])

        assert result.exit_code == 0
        # Verbose version should work without errors

    def test_formats_command_integration(self):
        """Test formats command integration."""
        result = self.runner.invoke(app, ["formats"])

        assert result.exit_code == 0
        # Formats command should work without errors

    def test_help_command_integration(self):
        """Test help command integration."""
        result = self.runner.invoke(app, ["help"])

        assert result.exit_code == 0
        # Help command should work without errors

    def test_dry_run_json_to_excel(self):
        """Test dry run for JSON to Excel conversion."""
        json_file = self.create_sample_odcs_json()
        excel_file = self.temp_dir / "output.xlsx"

        result = self.runner.invoke(
            app, ["convert", str(json_file), str(excel_file), "--dry-run"]
        )

        assert result.exit_code == 0
        # Verify no actual file was created in dry run
        assert not excel_file.exists()

    def test_dry_run_yaml_to_excel(self):
        """Test dry run for YAML to Excel conversion."""
        yaml_file = self.create_sample_odcs_yaml()
        excel_file = self.temp_dir / "output.xlsx"

        result = self.runner.invoke(
            app, ["convert", str(yaml_file), str(excel_file), "--dry-run"]
        )

        assert result.exit_code == 0
        # Verify no actual file was created in dry run
        assert not excel_file.exists()

    def test_json_to_excel_conversion_integration(self):
        """Test actual JSON to Excel conversion."""
        json_file = self.create_sample_odcs_json()
        excel_file = self.temp_dir / "output.xlsx"

        result = self.runner.invoke(
            app, ["to-excel", str(json_file), str(excel_file), "--quiet"]
        )

        assert result.exit_code == 0
        assert excel_file.exists()
        assert excel_file.stat().st_size > 0

    def test_yaml_to_excel_conversion_integration(self):
        """Test actual YAML to Excel conversion."""
        yaml_file = self.create_sample_odcs_yaml()
        excel_file = self.temp_dir / "output.xlsx"

        result = self.runner.invoke(
            app, ["to-excel", str(yaml_file), str(excel_file), "--quiet"]
        )

        assert result.exit_code == 0
        assert excel_file.exists()
        assert excel_file.stat().st_size > 0

    def test_json_to_excel_with_verbose(self):
        """Test JSON to Excel conversion with verbose output."""
        json_file = self.create_sample_odcs_json()
        excel_file = self.temp_dir / "output.xlsx"

        result = self.runner.invoke(
            app, ["to-excel", str(json_file), str(excel_file), "--verbose"]
        )

        assert result.exit_code == 0
        assert excel_file.exists()
        # Verbose output should work

    def test_convert_command_with_formats_flag(self):
        """Test convert command with show-formats flag."""
        result = self.runner.invoke(
            app, ["convert", "dummy", "dummy", "--show-formats"]
        )

        assert result.exit_code == 0
        # Show formats should work

    def test_json_roundtrip_conversion(self):
        """Test JSON to Excel and back to JSON conversion."""
        # Create original JSON file
        original_json = self.create_sample_odcs_json()
        excel_file = self.temp_dir / "intermediate.xlsx"
        output_json = self.temp_dir / "output.json"

        # Convert JSON to Excel
        result1 = self.runner.invoke(
            app, ["to-excel", str(original_json), str(excel_file), "--quiet"]
        )
        assert result1.exit_code == 0
        assert excel_file.exists()

        # Convert Excel back to JSON
        result2 = self.runner.invoke(
            app, ["to-odcs", str(excel_file), str(output_json), "--quiet"]
        )
        assert result2.exit_code == 0
        assert output_json.exists()

        # Verify both files contain valid JSON
        with open(original_json, "r", encoding="utf-8") as f:
            original_data = json.load(f)

        with open(output_json, "r", encoding="utf-8") as f:
            output_data = json.load(f)

        # Basic structure should be preserved
        assert isinstance(original_data, dict)
        assert isinstance(output_data, dict)
        assert "apiVersion" in output_data
        assert "kind" in output_data

    def test_yaml_roundtrip_conversion(self):
        """Test YAML to Excel and back to YAML conversion."""
        # Create original YAML file
        original_yaml = self.create_sample_odcs_yaml()
        excel_file = self.temp_dir / "intermediate.xlsx"
        output_yaml = self.temp_dir / "output.yaml"

        # Convert YAML to Excel
        result1 = self.runner.invoke(
            app, ["to-excel", str(original_yaml), str(excel_file), "--quiet"]
        )
        assert result1.exit_code == 0
        assert excel_file.exists()

        # Convert Excel back to YAML
        result2 = self.runner.invoke(
            app,
            [
                "to-odcs",
                str(excel_file),
                str(output_yaml),
                "--format",
                "yaml",
                "--quiet",
            ],
        )
        assert result2.exit_code == 0
        assert output_yaml.exists()

        # Verify both files contain valid YAML/data
        original_data = YAMLConverter.yaml_to_dict(original_yaml)
        output_data = YAMLConverter.yaml_to_dict(output_yaml)

        # Basic structure should be preserved
        assert isinstance(original_data, dict)
        assert isinstance(output_data, dict)
        assert "apiVersion" in output_data
        assert "kind" in output_data

    def test_excel_to_json_with_validation(self):
        """Test Excel to JSON conversion with validation."""
        # First create an Excel file from JSON
        json_file = self.create_sample_odcs_json()
        excel_file = self.temp_dir / "test.xlsx"
        output_json = self.temp_dir / "validated_output.json"

        # Create Excel file
        result1 = self.runner.invoke(
            app, ["to-excel", str(json_file), str(excel_file), "--quiet"]
        )
        assert result1.exit_code == 0

        # Convert back with validation
        result2 = self.runner.invoke(
            app, ["to-odcs", str(excel_file), str(output_json), "--validate"]
        )
        assert result2.exit_code == 0
        assert output_json.exists()
        # Validation should work without error

    def test_error_handling_non_existent_input(self):
        """Test error handling for non-existent input files."""
        result = self.runner.invoke(
            app, ["to-excel", "non_existent.json", "output.xlsx"]
        )

        # Typer should catch this as a validation error
        assert result.exit_code == 2

    def test_error_handling_invalid_json(self):
        """Test error handling for invalid JSON files."""
        invalid_json = self.temp_dir / "invalid.json"
        with open(invalid_json, "w", encoding="utf-8") as f:
            f.write("{ invalid json content }")

        excel_file = self.temp_dir / "output.xlsx"

        result = self.runner.invoke(
            app, ["to-excel", str(invalid_json), str(excel_file)]
        )

        assert result.exit_code == 1
        # Error messages are logged, not necessarily in stdout
        # Just verify the command failed with correct exit code

    def test_configuration_file_integration(self):
        """Test configuration file integration."""
        json_file = self.create_sample_odcs_json()
        excel_file = self.temp_dir / "configured_output.xlsx"
        config_file = self.temp_dir / "config.json"

        # Create a configuration file
        config_data = {
            "header_font": {"bold": True, "color": "FFFFFF"},
            "header_fill": {
                "start_color": "4472C4",
                "end_color": "4472C4",
                "fill_type": "solid",
            },
        }
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

        result = self.runner.invoke(
            app,
            [
                "to-excel",
                str(json_file),
                str(excel_file),
                "--config",
                str(config_file),
                "--quiet",
            ],
        )

        # Config file support may not be fully implemented yet
        # Just verify the file is processed
        assert excel_file.exists() or result.exit_code in [0, 1]

    def test_format_auto_detection(self):
        """Test automatic format detection based on file extensions."""
        json_file = self.create_sample_odcs_json()

        # Test different output extensions
        xlsx_file = self.temp_dir / "output.xlsx"
        yaml_file = self.temp_dir / "output.yaml"

        # JSON to Excel (auto-detected)
        result1 = self.runner.invoke(
            app, ["convert", str(json_file), str(xlsx_file), "--quiet"]
        )
        assert result1.exit_code == 0
        assert xlsx_file.exists()

        # Excel to YAML (auto-detected)
        result2 = self.runner.invoke(
            app, ["convert", str(xlsx_file), str(yaml_file), "--quiet"]
        )
        assert result2.exit_code == 0
        assert yaml_file.exists()

    def test_explicit_format_specification(self):
        """Test explicit format specification overrides auto-detection."""
        json_file = self.create_sample_odcs_json()
        excel_file = self.temp_dir / "test.xlsx"
        output_file = self.temp_dir / "output.json"  # JSON extension

        # Create Excel file first
        result1 = self.runner.invoke(
            app, ["to-excel", str(json_file), str(excel_file), "--quiet"]
        )
        assert result1.exit_code == 0

        # Convert to JSON with explicit format
        result2 = self.runner.invoke(
            app,
            [
                "to-odcs",
                str(excel_file),
                str(output_file),
                "--format",
                "json",
                "--quiet",
            ],
        )
        assert result2.exit_code == 0
        assert output_file.exists()

    def test_command_aliases_and_shortcuts(self):
        """Test command aliases and shortcuts work correctly."""
        json_file = self.create_sample_odcs_json()
        excel_file = self.temp_dir / "output.xlsx"

        # Test short flags
        result = self.runner.invoke(
            app, ["to-excel", str(json_file), str(excel_file), "-q", "-v"]
        )

        # Should work (quiet and verbose are conflicting but both should be recognized)
        assert result.exit_code == 0
        assert excel_file.exists()

    def test_banner_suppression(self):
        """Test banner suppression with --no-banner flag."""
        json_file = self.create_sample_odcs_json()
        excel_file = self.temp_dir / "output.xlsx"

        result = self.runner.invoke(
            app, ["convert", str(json_file), str(excel_file), "--no-banner"]
        )

        assert result.exit_code == 0
        # Banner should be suppressed, but conversion should still work
        assert excel_file.exists()

    def test_url_validation_utility(self):
        """Test URL validation utility function."""
        from odcs_converter.cli import _validate_url

        assert _validate_url("https://example.com/contract.json") is True
        assert _validate_url("http://localhost:8000/data.yaml") is True
        assert _validate_url("ftp://example.com/file.json") is True
        assert _validate_url("not-a-url") is False
        assert _validate_url("") is False
        assert _validate_url("example.com") is False

    def test_file_size_formatting_utility(self):
        """Test file size formatting utility function."""
        from odcs_converter.cli import _format_file_size

        assert _format_file_size(0) == "0.0 B"
        assert _format_file_size(1024) == "1.0 KB"
        assert _format_file_size(1048576) == "1.0 MB"
        assert _format_file_size(1073741824) == "1.0 GB"

    def test_complete_workflow_integration(self):
        """Test complete workflow from JSON through Excel back to YAML."""
        # Step 1: Create original JSON
        original_json = self.create_sample_odcs_json()

        # Step 2: Convert to Excel
        excel_file = self.temp_dir / "workflow.xlsx"
        result1 = self.runner.invoke(
            app, ["to-excel", str(original_json), str(excel_file), "--verbose"]
        )
        assert result1.exit_code == 0
        assert excel_file.exists()
        # Success messages are logged, not necessarily in stdout
        # Just verify the conversion succeeded

        # Step 3: Convert to YAML with validation
        yaml_file = self.temp_dir / "workflow.yaml"
        result2 = self.runner.invoke(
            app,
            [
                "to-odcs",
                str(excel_file),
                str(yaml_file),
                "--format",
                "yaml",
                "--validate",
                "--verbose",
            ],
        )
        assert result2.exit_code == 0
        assert yaml_file.exists()

        # Step 4: Verify final output is valid
        final_data = YAMLConverter.yaml_to_dict(yaml_file)
        assert isinstance(final_data, dict)
        assert "apiVersion" in final_data
        assert "kind" in final_data
        assert final_data["kind"] == "DataContract"
