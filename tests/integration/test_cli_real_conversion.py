"""Real conversion tests with example ODCS data to verify CLI functionality."""

import json
import tempfile
from pathlib import Path
from typer.testing import CliRunner

from odcs_converter.cli import app
from odcs_converter.yaml_converter import YAMLConverter


class TestRealConversions:
    """Test real conversions with sample ODCS data."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_valid_odcs_contract(self) -> dict:
        """Create a valid ODCS contract matching the model schema."""
        return {
            "apiVersion": "v3.0.2",
            "kind": "DataContract",
            "id": "retail-sales-contract",
            "version": "1.2.0",
            "status": "active",
            "name": "Retail Sales Data Contract",
            "tenant": "retail-division",
            "tags": ["sales", "retail", "commerce", "internal"],
            "domain": "commerce",
            "description": {
                "purpose": "Complete retail sales data contract showcasing ODCS v3.0.2 features",
                "usage": "Analytics and reporting for retail sales data",
                "limitations": "Data is updated daily, may have 24-hour latency",
            },
            "schema": [
                {
                    "name": "transactions",
                    "logicalType": "object",
                    "physicalName": "sales_transactions",
                    "description": "Transaction records table",
                    "properties": [
                        {
                            "name": "transaction_id",
                            "logicalType": "string",
                            "physicalType": "VARCHAR(36)",
                            "description": "Unique transaction identifier",
                            "primaryKey": True,
                            "primaryKeyPosition": 1,
                            "required": True,
                            "unique": True,
                            "logicalTypeOptions": {
                                "format": "uuid",
                                "pattern": "^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
                            },
                        },
                        {
                            "name": "customer_id",
                            "logicalType": "integer",
                            "physicalType": "BIGINT",
                            "description": "Customer identifier",
                            "required": True,
                            "logicalTypeOptions": {"minimum": 1, "maximum": 999999999},
                        },
                        {
                            "name": "product_id",
                            "logicalType": "string",
                            "physicalType": "VARCHAR(50)",
                            "description": "Product SKU identifier",
                            "required": True,
                            "logicalTypeOptions": {
                                "maxLength": 50,
                                "pattern": "^[A-Z]{3}-[0-9]{6}$",
                            },
                        },
                        {
                            "name": "quantity",
                            "logicalType": "integer",
                            "physicalType": "INT",
                            "description": "Quantity purchased",
                            "required": True,
                            "logicalTypeOptions": {"minimum": 1, "maximum": 100},
                        },
                        {
                            "name": "unit_price",
                            "logicalType": "number",
                            "physicalType": "DECIMAL(10,2)",
                            "description": "Price per unit in USD",
                            "required": True,
                            "logicalTypeOptions": {
                                "minimum": 0.01,
                                "maximum": 9999.99,
                                "multipleOf": 0.01,
                            },
                        },
                        {
                            "name": "total_amount",
                            "logicalType": "number",
                            "physicalType": "DECIMAL(12,2)",
                            "description": "Total transaction amount",
                            "required": True,
                            "transformLogic": "quantity * unit_price",
                            "transformDescription": "Calculated as quantity multiplied by unit price",
                        },
                        {
                            "name": "transaction_date",
                            "logicalType": "date",
                            "physicalType": "TIMESTAMP",
                            "description": "Date and time of transaction",
                            "required": True,
                            "partitioned": True,
                            "partitionKeyPosition": 1,
                        },
                        {
                            "name": "store_location",
                            "logicalType": "string",
                            "physicalType": "VARCHAR(100)",
                            "description": "Store location where transaction occurred",
                            "required": True,
                        },
                        {
                            "name": "payment_method",
                            "logicalType": "string",
                            "physicalType": "VARCHAR(20)",
                            "description": "Method of payment",
                            "required": True,
                        },
                        {
                            "name": "customer_notes",
                            "logicalType": "string",
                            "physicalType": "TEXT",
                            "description": "Optional customer notes",
                            "required": False,
                            "classification": "sensitive",
                        },
                    ],
                    "quality": [
                        {
                            "name": "Unique Transaction ID",
                            "description": "Ensure all transaction IDs are unique",
                            "dimension": "uniqueness",
                            "type": "library",
                            "rule": "unique_values",
                            "severity": "critical",
                        },
                        {
                            "name": "Positive Transaction Amounts",
                            "description": "All transaction amounts must be positive",
                            "dimension": "accuracy",
                            "type": "library",
                            "rule": "range_check",
                            "mustBeGreaterThan": 0,
                        },
                    ],
                }
            ],
            "servers": [
                {
                    "server": "retail-db-prod",
                    "type": "postgresql",
                    "description": "Production PostgreSQL database for retail data",
                    "environment": "production",
                    "host": "retail-db.company.com",
                    "port": 5432,
                    "database": "retail_db",
                    "schema": "sales",
                }
            ],
            "team": [
                {
                    "name": "Sarah Johnson",
                    "username": "sarah.johnson@company.com",
                    "role": "Data Owner",
                    "description": "Lead data engineer for retail domain",
                },
                {
                    "name": "Data Engineering Team",
                    "username": "data-eng@company.com",
                    "role": "Data Engineer",
                    "description": "Core data engineering team",
                },
                {
                    "name": "Analytics Team",
                    "username": "analytics@company.com",
                    "role": "Data Consumer",
                    "description": "Business analytics team",
                },
            ],
            "roles": [
                {
                    "role": "Data Owner",
                    "access": "read-write",
                    "description": "Full access to data and metadata",
                    "firstLevelApprovers": "sarah.johnson@company.com",
                    "secondLevelApprovers": "manager@company.com",
                },
                {
                    "role": "Data Consumer",
                    "access": "read-only",
                    "description": "Read-only access for analytics",
                    "firstLevelApprovers": "data-eng@company.com",
                },
            ],
            "support": [
                {
                    "channel": "data-engineering-support",
                    "url": "https://support.company.com/data-eng",
                    "description": "Data Engineering Support Channel",
                    "tool": "ServiceNow",
                    "scope": "24x7 support for critical issues",
                }
            ],
            "slaProperties": [
                {
                    "property": "availability",
                    "value": "99.9%",
                    "valueExt": "monthly",
                    "unit": "percentage",
                },
                {"property": "retention", "value": "7 years", "unit": "years"},
                {
                    "property": "latency",
                    "value": "100",
                    "valueExt": "p95",
                    "unit": "milliseconds",
                },
            ],
            "price": {
                "priceAmount": 1000.00,
                "priceCurrency": "USD",
                "priceUnit": "monthly",
            },
            "authoritativeDefinitions": [
                {
                    "url": "https://wiki.company.com/retail-data-dictionary",
                    "type": "business-glossary",
                }
            ],
            "customProperties": [
                {"property": "dataClassification", "value": "internal"},
                {"property": "businessDomain", "value": "retail-commerce"},
                {"property": "complianceFramework", "value": ["SOX", "PCI-DSS"]},
            ],
        }

    def create_minimal_odcs_contract(self) -> dict:
        """Create a minimal valid ODCS contract."""
        return {
            "apiVersion": "v3.0.2",
            "kind": "DataContract",
            "id": "minimal-contract",
            "version": "1.0.0",
            "status": "active",
            "name": "Minimal Contract",
        }

    def test_comprehensive_json_to_excel_conversion(self):
        """Test comprehensive JSON to Excel conversion with valid ODCS data."""
        # Create valid ODCS contract
        odcs_data = self.create_valid_odcs_contract()

        # Save to JSON file
        json_file = self.temp_dir / "comprehensive_contract.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(odcs_data, f, indent=2)

        # Convert to Excel
        excel_file = self.temp_dir / "comprehensive_output.xlsx"
        result = self.runner.invoke(
            app, ["to-excel", str(json_file), str(excel_file), "--verbose"]
        )

        # Verify conversion succeeded
        assert result.exit_code == 0
        assert excel_file.exists()
        assert excel_file.stat().st_size > 5000  # Should be substantial file

    def test_yaml_to_excel_conversion(self):
        """Test YAML to Excel conversion."""
        # Create ODCS contract
        odcs_data = self.create_valid_odcs_contract()

        # Save to YAML file
        yaml_file = self.temp_dir / "contract.yaml"
        YAMLConverter.dict_to_yaml(odcs_data, yaml_file)

        # Convert to Excel
        excel_file = self.temp_dir / "yaml_output.xlsx"
        result = self.runner.invoke(
            app, ["to-excel", str(yaml_file), str(excel_file), "--quiet"]
        )

        # Verify conversion succeeded
        assert result.exit_code == 0
        assert excel_file.exists()
        assert excel_file.stat().st_size > 3000

    def test_excel_roundtrip_conversion(self):
        """Test Excel roundtrip conversion (JSON -> Excel -> JSON)."""
        # Create original ODCS contract
        original_data = self.create_valid_odcs_contract()

        # Step 1: Save original JSON
        original_json = self.temp_dir / "original.json"
        with open(original_json, "w", encoding="utf-8") as f:
            json.dump(original_data, f, indent=2)

        # Step 2: Convert JSON to Excel
        excel_file = self.temp_dir / "roundtrip.xlsx"
        result1 = self.runner.invoke(
            app, ["to-excel", str(original_json), str(excel_file), "--quiet"]
        )
        assert result1.exit_code == 0
        assert excel_file.exists()

        # Step 3: Convert Excel back to JSON
        output_json = self.temp_dir / "roundtrip_output.json"
        result2 = self.runner.invoke(
            app, ["to-odcs", str(excel_file), str(output_json), "--quiet"]
        )
        assert result2.exit_code == 0
        assert output_json.exists()

        # Step 4: Verify structure is preserved
        with open(output_json, "r", encoding="utf-8") as f:
            roundtrip_data = json.load(f)

        # Basic structure verification
        assert isinstance(roundtrip_data, dict)
        assert "apiVersion" in roundtrip_data
        assert "kind" in roundtrip_data
        assert roundtrip_data.get("kind") == "DataContract"

        # Verify key fields are preserved
        assert roundtrip_data.get("id") == original_data.get("id")
        assert roundtrip_data.get("version") == original_data.get("version")

    def test_yaml_roundtrip_conversion(self):
        """Test YAML roundtrip conversion (YAML -> Excel -> YAML)."""
        # Create original ODCS contract
        original_data = self.create_valid_odcs_contract()

        # Step 1: Save original YAML
        original_yaml = self.temp_dir / "original.yaml"
        YAMLConverter.dict_to_yaml(original_data, original_yaml)

        # Step 2: Convert YAML to Excel
        excel_file = self.temp_dir / "yaml_roundtrip.xlsx"
        result1 = self.runner.invoke(
            app, ["to-excel", str(original_yaml), str(excel_file), "--quiet"]
        )
        assert result1.exit_code == 0
        assert excel_file.exists()

        # Step 3: Convert Excel back to YAML
        output_yaml = self.temp_dir / "roundtrip_output.yaml"
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

        # Step 4: Verify structure is preserved
        roundtrip_data = YAMLConverter.yaml_to_dict(output_yaml)

        # Basic structure verification
        assert isinstance(roundtrip_data, dict)
        assert "apiVersion" in roundtrip_data
        assert "kind" in roundtrip_data
        assert roundtrip_data.get("kind") == "DataContract"

    def test_convert_command_with_auto_detection(self):
        """Test convert command with automatic format detection."""
        # Create ODCS contract
        odcs_data = self.create_valid_odcs_contract()

        # Save as JSON
        json_file = self.temp_dir / "auto_detect.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(odcs_data, f, indent=2)

        # Use convert command with auto-detection
        excel_file = self.temp_dir / "auto_detect.xlsx"
        result = self.runner.invoke(
            app, ["convert", str(json_file), str(excel_file), "--quiet"]
        )

        # Should automatically detect JSON input and Excel output
        assert result.exit_code == 0
        assert excel_file.exists()

    def test_validation_with_real_data(self):
        """Test validation feature with real ODCS data."""
        # Create ODCS contract
        odcs_data = self.create_valid_odcs_contract()

        # Convert to Excel first
        json_file = self.temp_dir / "validation_test.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(odcs_data, f, indent=2)

        excel_file = self.temp_dir / "validation_test.xlsx"
        result1 = self.runner.invoke(
            app, ["to-excel", str(json_file), str(excel_file), "--quiet"]
        )
        assert result1.exit_code == 0

        # Convert back with validation
        output_json = self.temp_dir / "validated_output.json"
        result2 = self.runner.invoke(
            app,
            ["to-odcs", str(excel_file), str(output_json), "--validate", "--verbose"],
        )

        # Should succeed with validation
        assert result2.exit_code == 0
        assert output_json.exists()

    def test_configuration_file_usage(self):
        """Test using configuration file for styling."""
        # Create ODCS contract
        odcs_data = self.create_valid_odcs_contract()
        json_file = self.temp_dir / "config_test.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(odcs_data, f, indent=2)

        # Create a simple configuration file (empty config to test loading mechanism)
        config_file = self.temp_dir / "style_config.json"
        config_data = {}  # Empty config should use defaults
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

        # Convert with configuration
        excel_file = self.temp_dir / "configured_output.xlsx"
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

        # Should succeed with configuration file loading
        # Even if config is empty, the mechanism should work
        assert result.exit_code == 0
        assert excel_file.exists()

    def test_dry_run_functionality(self):
        """Test dry run functionality doesn't create files."""
        # Create ODCS contract
        odcs_data = self.create_valid_odcs_contract()
        json_file = self.temp_dir / "dry_run_test.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(odcs_data, f, indent=2)

        # Run dry run
        excel_file = self.temp_dir / "dry_run_output.xlsx"
        result = self.runner.invoke(
            app, ["convert", str(json_file), str(excel_file), "--dry-run"]
        )

        # Should succeed but not create output file
        assert result.exit_code == 0
        assert not excel_file.exists()

    def test_error_handling_with_invalid_json(self):
        """Test error handling with invalid JSON input."""
        # Create invalid JSON file
        invalid_json = self.temp_dir / "invalid.json"
        with open(invalid_json, "w", encoding="utf-8") as f:
            f.write("{ invalid json content: missing quotes }")

        excel_file = self.temp_dir / "should_not_exist.xlsx"
        result = self.runner.invoke(
            app, ["to-excel", str(invalid_json), str(excel_file)]
        )

        # Should fail gracefully
        assert result.exit_code == 1
        assert not excel_file.exists()

    def test_file_format_enum_validation(self):
        """Test that format enum validation works correctly."""
        # Create valid Excel file first
        odcs_data = self.create_valid_odcs_contract()
        json_file = self.temp_dir / "format_test.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(odcs_data, f, indent=2)

        excel_file = self.temp_dir / "format_test.xlsx"
        result1 = self.runner.invoke(
            app, ["to-excel", str(json_file), str(excel_file), "--quiet"]
        )
        assert result1.exit_code == 0

        # Test valid format
        output_file = self.temp_dir / "format_output.json"
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
        # Should succeed with valid format
        assert result2.exit_code == 0

    def test_minimal_odcs_contract(self):
        """Test conversion with minimal ODCS contract."""
        minimal_data = self.create_minimal_odcs_contract()

        # Save minimal JSON
        json_file = self.temp_dir / "minimal.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(minimal_data, f, indent=2)

        # Convert to Excel
        excel_file = self.temp_dir / "minimal.xlsx"
        result = self.runner.invoke(
            app, ["to-excel", str(json_file), str(excel_file), "--quiet"]
        )

        # Should handle minimal contract correctly
        assert result.exit_code == 0
        assert excel_file.exists()

    def test_multiple_schema_objects(self):
        """Test conversion with multiple schema objects."""
        # Create contract with multiple schema objects
        multi_schema_data = self.create_valid_odcs_contract()

        # Add a second schema object
        second_schema = {
            "name": "customers",
            "logicalType": "object",
            "description": "Customer information table",
            "properties": [
                {
                    "name": "customer_id",
                    "logicalType": "integer",
                    "physicalType": "BIGINT",
                    "description": "Unique customer identifier",
                    "primaryKey": True,
                    "primaryKeyPosition": 1,
                    "required": True,
                },
                {
                    "name": "customer_name",
                    "logicalType": "string",
                    "physicalType": "VARCHAR(255)",
                    "description": "Customer full name",
                    "required": True,
                },
            ],
        }
        multi_schema_data["schema"].append(second_schema)

        # Save and convert
        json_file = self.temp_dir / "multi_schema.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(multi_schema_data, f, indent=2)

        excel_file = self.temp_dir / "multi_schema.xlsx"
        result = self.runner.invoke(
            app, ["to-excel", str(json_file), str(excel_file), "--quiet"]
        )

        # Should handle multiple schema objects
        assert result.exit_code == 0
        assert excel_file.exists()

    def test_quality_rules_conversion(self):
        """Test conversion with comprehensive quality rules."""
        # Create contract focused on quality rules
        quality_data = self.create_minimal_odcs_contract()
        quality_data["schema"] = [
            {
                "name": "test_table",
                "description": "Table for testing quality rules",
                "properties": [
                    {
                        "name": "id",
                        "logicalType": "integer",
                        "primaryKey": True,
                        "primaryKeyPosition": 1,
                        "quality": [
                            {
                                "name": "ID Uniqueness Check",
                                "description": "Ensure ID values are unique",
                                "dimension": "uniqueness",
                                "type": "library",
                                "rule": "unique_values",
                            },
                            {
                                "name": "ID Range Check",
                                "description": "ID must be positive",
                                "dimension": "accuracy",
                                "type": "library",
                                "mustBeGreaterThan": 0,
                            },
                        ],
                    }
                ],
            }
        ]

        # Save and convert
        json_file = self.temp_dir / "quality_test.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(quality_data, f, indent=2)

        excel_file = self.temp_dir / "quality_test.xlsx"
        result = self.runner.invoke(
            app, ["to-excel", str(json_file), str(excel_file), "--quiet"]
        )

        # Should handle quality rules correctly
        assert result.exit_code == 0
        assert excel_file.exists()

    def test_custom_properties_conversion(self):
        """Test conversion with custom properties."""
        # Create contract with various custom properties
        custom_data = self.create_minimal_odcs_contract()
        custom_data["customProperties"] = [
            {"property": "environment", "value": "production"},
            {"property": "costCenter", "value": "IT-001"},
            {"property": "dataRetention", "value": 365},
            {"property": "encryptionEnabled", "value": True},
            {"property": "tags", "value": ["critical", "pii", "encrypted"]},
        ]

        # Save and convert
        json_file = self.temp_dir / "custom_props.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(custom_data, f, indent=2)

        excel_file = self.temp_dir / "custom_props.xlsx"
        result = self.runner.invoke(
            app, ["to-excel", str(json_file), str(excel_file), "--quiet"]
        )

        # Should handle custom properties correctly
        assert result.exit_code == 0
        assert excel_file.exists()
