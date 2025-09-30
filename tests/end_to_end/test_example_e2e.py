"""Example end-to-end test demonstrating full workflow testing."""

import json
import tempfile
from pathlib import Path
import pytest

from tests.end_to_end.utils import (
    EndToEndTestHelper,
    CLITestHelper,
    PerformanceTestHelper,
    ScenarioTestHelper,
    ErrorScenarioTestHelper,
    e2e_test,
    slow_e2e_test,
    cli_test,
    performance_test,
)


@pytest.mark.e2e
class TestCompleteWorkflows:
    """Test complete end-to-end workflows."""

    @e2e_test
    def test_data_engineer_complete_workflow(self, temp_dir, scenario_test_helper):
        """Test complete data engineer workflow from contract creation to deployment."""
        success, results, errors = scenario_test_helper.simulate_data_engineer_workflow(
            temp_dir
        )

        assert success, f"Workflow failed with errors: {errors}"
        assert "Created ODCS JSON contract" in results["steps_completed"]
        assert "Converted to Excel via CLI" in results["steps_completed"]
        assert "Business user reviewed and modified Excel" in results["steps_completed"]
        assert "Converted updated Excel back to JSON" in results["steps_completed"]
        assert "Business changes preserved in roundtrip" in results["steps_completed"]

        # Verify files were created
        assert len(results["files_generated"]) >= 3
        for file_path in results["files_generated"]:
            assert Path(file_path).exists()

    @e2e_test
    def test_compliance_review_workflow(self, temp_dir, scenario_test_helper):
        """Test compliance team reviewing data contracts end-to-end."""
        success, results, errors = (
            scenario_test_helper.simulate_compliance_review_workflow(temp_dir)
        )

        assert success, f"Compliance review failed: {results['issues_found']}"
        assert "Contract exported to Excel for review" in results["compliance_checks"]
        assert "GDPR compliance flag verified" in results["compliance_checks"]
        assert "Data classification present" in results["compliance_checks"]
        assert "PII handling documented in schema" in results["compliance_checks"]

        # Should have no compliance issues
        assert len(results["issues_found"]) == 0

    @slow_e2e_test
    def test_large_contract_processing(self, temp_dir, production_like_odcs):
        """Test processing of large, production-like contracts."""
        # Create a larger contract by duplicating schema objects
        large_contract = production_like_odcs.copy()

        # Add more schema objects to simulate large contract
        base_schema = large_contract["schema"][0]
        for i in range(20):  # Add 20 more tables
            table_copy = base_schema.copy()
            table_copy["name"] = f"large_table_{i}"
            table_copy["physicalName"] = f"large_table_{i}_v1"

            # Add more properties to each table
            properties = table_copy["properties"]
            for j in range(30):  # 30 properties per table
                prop_copy = properties[0].copy()
                prop_copy["name"] = f"field_{j}"
                prop_copy["primaryKey"] = False
                if "primaryKeyPosition" in prop_copy:
                    del prop_copy["primaryKeyPosition"]
                properties.append(prop_copy)

            large_contract["schema"].append(table_copy)

        # Test conversion to Excel
        excel_path = temp_dir / "large_contract.xlsx"

        from odcs_converter.generator import ODCSToExcelConverter

        converter = ODCSToExcelConverter()
        converter.generate_from_dict(large_contract, excel_path)

        assert excel_path.exists()
        assert excel_path.stat().st_size > 10000  # Should be reasonably large file

        # Test conversion back
        from odcs_converter.excel_parser import ExcelToODCSParser

        parser = ExcelToODCSParser()
        parsed_contract = parser.parse_from_file(excel_path)

        # Verify key structure is preserved
        assert parsed_contract["id"] == large_contract["id"]
        assert len(parsed_contract["schema"]) == len(large_contract["schema"])


@pytest.mark.e2e
@pytest.mark.cli
class TestCLIWorkflows:
    """Test CLI-based workflows end-to-end."""

    @cli_test
    def test_cli_help_and_version(self, cli_test_helper):
        """Test basic CLI help and version functionality."""
        # Test help command
        success, help_output = cli_test_helper.test_cli_help()
        assert success
        assert "odcs-converter" in help_output.lower()
        assert "usage" in help_output.lower()

    @cli_test
    def test_cli_odcs_to_excel_conversion(
        self, temp_dir, cli_test_helper, complete_odcs_data
    ):
        """Test ODCS to Excel conversion via CLI."""
        # Create input JSON file
        input_json = temp_dir / "input.json"
        with open(input_json, "w") as f:
            json.dump(complete_odcs_data, f, indent=2)

        # Define output Excel file
        output_excel = temp_dir / "output.xlsx"

        # Run CLI conversion
        success, stdout, stderr = cli_test_helper.test_odcs_to_excel_cli(
            input_json, output_excel
        )

        assert success, f"CLI conversion failed: {stderr}"
        assert output_excel.exists()

        # Verify Excel file is valid by trying to parse it
        from odcs_converter.excel_parser import ExcelToODCSParser

        parser = ExcelToODCSParser()
        parsed_data = parser.parse_from_file(output_excel)

        assert parsed_data["id"] == complete_odcs_data["id"]

    @cli_test
    def test_cli_excel_to_odcs_conversion(
        self, temp_dir, cli_test_helper, complete_odcs_data
    ):
        """Test Excel to ODCS conversion via CLI."""
        # First create an Excel file
        excel_input = temp_dir / "input.xlsx"
        from odcs_converter.generator import ODCSToExcelConverter

        converter = ODCSToExcelConverter()
        converter.generate_from_dict(complete_odcs_data, excel_input)

        # Define output JSON file
        output_json = temp_dir / "output.json"

        # Run CLI conversion
        success, stdout, stderr = cli_test_helper.test_excel_to_odcs_cli(
            excel_input, output_json, "json"
        )

        assert success, f"CLI conversion failed: {stderr}"
        assert output_json.exists()

        # Verify JSON file content
        with open(output_json, "r") as f:
            parsed_data = json.load(f)

        assert parsed_data["id"] == complete_odcs_data["id"]
        assert parsed_data["version"] == complete_odcs_data["version"]

    @cli_test
    def test_cli_roundtrip_conversion(
        self, temp_dir, cli_test_helper, complete_odcs_data
    ):
        """Test complete roundtrip conversion via CLI."""
        # Step 1: Save original as JSON
        original_json = temp_dir / "original.json"
        with open(original_json, "w") as f:
            json.dump(complete_odcs_data, f, indent=2)

        # Step 2: Convert to Excel
        intermediate_excel = temp_dir / "intermediate.xlsx"
        success1, _, stderr1 = cli_test_helper.test_odcs_to_excel_cli(
            original_json, intermediate_excel
        )
        assert success1, f"JSON to Excel failed: {stderr1}"

        # Step 3: Convert back to JSON
        final_json = temp_dir / "final.json"
        success2, _, stderr2 = cli_test_helper.test_excel_to_odcs_cli(
            intermediate_excel, final_json, "json"
        )
        assert success2, f"Excel to JSON failed: {stderr2}"

        # Step 4: Compare original and final
        with open(final_json, "r") as f:
            final_data = json.load(f)

        # Key fields should be preserved
        key_fields = ["version", "kind", "apiVersion", "id", "status", "name"]
        for field in key_fields:
            if field in complete_odcs_data:
                assert final_data.get(field) == complete_odcs_data.get(field), (
                    f"Field {field} changed during roundtrip"
                )


@pytest.mark.e2e
@pytest.mark.performance
class TestPerformanceWorkflows:
    """Test performance characteristics in end-to-end scenarios."""

    @performance_test
    def test_conversion_performance_benchmarks(
        self, temp_dir, performance_test_helper, complete_odcs_data
    ):
        """Test conversion performance with various dataset sizes."""
        # Test small dataset (baseline)
        small_times = performance_test_helper.test_large_dataset_performance(
            complete_odcs_data, table_count=1, properties_per_table=5
        )

        # Test medium dataset
        medium_times = performance_test_helper.test_large_dataset_performance(
            complete_odcs_data, table_count=5, properties_per_table=20
        )

        # Test large dataset
        large_times = performance_test_helper.test_large_dataset_performance(
            complete_odcs_data, table_count=10, properties_per_table=50
        )

        # Performance should be reasonable (under 30 seconds for large datasets)
        assert small_times["odcs_to_excel"] < 5.0, "Small dataset conversion too slow"
        assert medium_times["odcs_to_excel"] < 15.0, (
            "Medium dataset conversion too slow"
        )
        assert large_times["odcs_to_excel"] < 30.0, "Large dataset conversion too slow"

        # Excel to ODCS should also be reasonable
        assert large_times["excel_to_odcs"] < 30.0, "Large dataset parsing too slow"

    @performance_test
    def test_memory_usage_during_conversion(
        self, temp_dir, performance_test_helper, complete_odcs_data
    ):
        """Test memory usage during large conversions."""
        from odcs_converter.generator import ODCSToExcelConverter

        excel_path = temp_dir / "memory_test.xlsx"
        converter = ODCSToExcelConverter()

        # Measure memory usage during conversion
        result, memory_stats = performance_test_helper.memory_usage_test(
            converter.generate_from_dict, complete_odcs_data, excel_path
        )

        if "error" not in memory_stats:
            # Memory increase should be reasonable (under 100MB for typical contracts)
            memory_increase = memory_stats.get("memory_increase_mb", 0)
            assert memory_increase < 100, f"Memory usage too high: {memory_increase}MB"


@pytest.mark.e2e
class TestErrorHandlingWorkflows:
    """Test error handling in complete workflows."""

    @e2e_test
    def test_file_system_error_scenarios(self, temp_dir, error_scenario_test_helper):
        """Test various file system error scenarios end-to-end."""
        errors_handled = error_scenario_test_helper.test_file_system_errors(temp_dir)

        # Should handle at least basic error scenarios
        expected_errors = [
            "Non-existent file error handled",
            "Invalid output directory error handled",
            "Permission denied error handled",
        ]

        for expected_error in expected_errors:
            assert expected_error in errors_handled, (
                f"Missing error handling: {expected_error}"
            )

    @e2e_test
    def test_data_corruption_scenarios(self, temp_dir, error_scenario_test_helper):
        """Test handling of corrupted or malformed data end-to-end."""
        scenarios_tested = error_scenario_test_helper.test_data_corruption_scenarios(
            temp_dir
        )

        expected_scenarios = [
            "Corrupted Excel file handled",
            "Malformed JSON data handled",
        ]

        for expected_scenario in expected_scenarios:
            assert expected_scenario in scenarios_tested, (
                f"Missing scenario handling: {expected_scenario}"
            )

    @e2e_test
    def test_invalid_cli_usage(self, cli_test_helper):
        """Test CLI error handling with invalid usage."""
        # Test with non-existent input file
        success, stdout, stderr = cli_test_helper.run_cli_command(
            ["odcs-converter", "to-excel", "/nonexistent/file.json", "/tmp/output.xlsx"]
        )

        assert not success  # Should fail gracefully
        assert len(stderr) > 0  # Should provide error message

        # Test with invalid arguments
        success, stdout, stderr = cli_test_helper.run_cli_command(
            ["odcs-converter", "invalid-command"]
        )

        assert not success  # Should fail gracefully
        assert (
            "usage" in stderr.lower() or "help" in stderr.lower()
        )  # Should show usage info


@pytest.mark.e2e
@pytest.mark.smoke
class TestSmokeTestWorkflows:
    """Smoke tests for basic functionality verification."""

    def test_basic_conversion_smoke_test(self, temp_dir):
        """Basic smoke test for conversion functionality."""
        # Create minimal test data
        minimal_odcs = {
            "version": "1.0.0",
            "kind": "DataContract",
            "apiVersion": "v3.0.2",
            "id": "smoke-test",
            "status": "active",
        }

        # Test basic conversion workflow
        from odcs_converter.generator import ODCSToExcelConverter
        from odcs_converter.excel_parser import ExcelToODCSParser

        converter = ODCSToExcelConverter()
        parser = ExcelToODCSParser()

        # Convert to Excel
        excel_path = temp_dir / "smoke_test.xlsx"
        converter.generate_from_dict(minimal_odcs, excel_path)
        assert excel_path.exists()

        # Convert back
        parsed_data = parser.parse_from_file(excel_path)
        assert parsed_data["id"] == minimal_odcs["id"]

    def test_yaml_integration_smoke_test(self, temp_dir):
        """Smoke test for YAML integration."""
        from odcs_converter.yaml_converter import YAMLConverter

        test_data = {
            "version": "1.0.0",
            "kind": "DataContract",
            "apiVersion": "v3.0.2",
            "id": "yaml-smoke-test",
            "status": "active",
            "description": {"usage": "YAML smoke test"},
        }

        # Save as YAML
        yaml_path = temp_dir / "smoke_test.yaml"
        YAMLConverter.dict_to_yaml(test_data, yaml_path)
        assert yaml_path.exists()

        # Load back from YAML
        loaded_data = YAMLConverter.yaml_to_dict(yaml_path)
        assert loaded_data["id"] == test_data["id"]
        assert loaded_data["description"]["usage"] == test_data["description"]["usage"]

    def test_cli_basic_functionality_smoke_test(self, cli_test_helper):
        """Smoke test for basic CLI functionality."""
        # Test that CLI is accessible and shows help
        success, output = cli_test_helper.test_cli_help()
        assert success
        assert len(output) > 0
        assert "usage" in output.lower() or "commands" in output.lower()
