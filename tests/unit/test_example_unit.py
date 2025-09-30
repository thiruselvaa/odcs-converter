"""Example unit test demonstrating the new testing structure and utilities."""

import pytest
from unittest.mock import patch

from odcs_converter.models import ODCSDataContract, Server, SchemaProperty
from tests.unit.utils import (
    unit_test,
    parametrize_logical_types,
    parametrize_server_types,
    parametrize_api_versions,
)


class TestODCSModelValidation:
    """Unit tests for ODCS model validation using new test utilities."""

    def test_minimal_odcs_creation(self, unit_test_helper):
        """Test creating minimal ODCS contract."""
        minimal_data = unit_test_helper.create_minimal_odcs_dict()

        # Should not raise any validation errors
        contract = ODCSDataContract(**minimal_data)

        assert contract.version == "1.0.0"
        assert contract.kind == "DataContract"
        assert contract.id == "unit-test-minimal"
        assert contract.status == "active"

    def test_server_creation(self, unit_test_helper):
        """Test creating server objects."""
        server_data = unit_test_helper.create_sample_server()

        server = Server(**server_data)

        assert server.server == "unit-test-db"
        assert server.type == "postgresql"
        assert server.port == 5432

    def test_schema_property_creation(self, unit_test_helper):
        """Test creating schema property objects."""
        property_data = unit_test_helper.create_sample_schema_property()

        prop = SchemaProperty(**property_data)

        assert prop.name == "test_id"
        assert prop.logicalType == "integer"
        assert prop.primaryKey is True
        assert prop.primaryKeyPosition == 1

    @parametrize_logical_types
    def test_logical_type_validation(self, logical_type, is_valid):
        """Test logical type validation with parameterized data."""
        property_data = {
            "name": "test_field",
            "logicalType": logical_type,
            "description": "Test field",
        }

        if is_valid:
            # Should not raise validation error
            prop = SchemaProperty(**property_data)
            assert prop.logicalType == logical_type
        else:
            # Should raise validation error
            with pytest.raises(Exception):
                SchemaProperty(**property_data)

    @parametrize_server_types
    def test_server_type_validation(self, server_type, is_valid):
        """Test server type validation with parameterized data."""
        server_data = {
            "server": "test-server",
            "type": server_type,
            "description": "Test server",
        }

        if is_valid:
            server = Server(**server_data)
            assert server.type == server_type
        else:
            with pytest.raises(Exception):
                Server(**server_data)

    @parametrize_api_versions
    def test_api_version_validation(self, api_version, is_valid, unit_test_helper):
        """Test API version validation with parameterized data."""
        odcs_data = unit_test_helper.create_minimal_odcs_dict()
        odcs_data["apiVersion"] = api_version

        if is_valid:
            contract = ODCSDataContract(**odcs_data)
            assert contract.apiVersion == api_version
        else:
            with pytest.raises(Exception):
                ODCSDataContract(**odcs_data)

    def test_invalid_data_variants(self, unit_test_helper):
        """Test various invalid data combinations."""
        invalid_variants = unit_test_helper.create_invalid_data_variants()

        for invalid_data in invalid_variants:
            with pytest.raises(Exception):
                ODCSDataContract(**invalid_data)

    @unit_test
    def test_validation_helper_functions(self, validation_helper, unit_test_helper):
        """Test validation helper functions."""
        # Test valid ODCS validation
        valid_data = unit_test_helper.create_minimal_odcs_dict()
        validation_helper.assert_odcs_contract_valid(valid_data)

        # Test valid server validation
        server_data = unit_test_helper.create_sample_server()
        validation_helper.assert_server_valid(server_data)

        # Test valid schema property validation
        prop_data = unit_test_helper.create_sample_schema_property()
        validation_helper.assert_schema_property_valid(prop_data)

    def test_mock_factory_usage(self, mock_factory):
        """Test using mock factory for creating test mocks."""
        # Test file response mock
        mock_file = mock_factory.create_mock_file_response("test content")
        assert mock_file.read() == b"test content"

        # Test requests response mock
        mock_response = mock_factory.create_mock_requests_response(
            json_data={"test": "data"}, status_code=200
        )
        assert mock_response.json() == {"test": "data"}
        assert mock_response.status_code == 200

        # Test path mock
        mock_path = mock_factory.create_mock_path(exists=True, is_file=True)
        assert mock_path.exists() is True
        assert mock_path.is_file() is True


class TestModelFieldValidation:
    """Test individual model field validation."""

    def test_required_field_validation(self):
        """Test that required fields are properly validated."""
        # Missing version should fail
        with pytest.raises(Exception):
            ODCSDataContract(
                kind="DataContract", apiVersion="v3.0.2", id="test", status="active"
            )

    def test_enum_field_validation(self):
        """Test enum field validation."""
        # Valid enum values
        contract = ODCSDataContract(
            version="1.0.0",
            kind="DataContract",
            apiVersion="v3.0.2",
            id="test",
            status="active",
        )
        assert contract.kind == "DataContract"

        # Invalid enum value should fail
        with pytest.raises(Exception):
            ODCSDataContract(
                version="1.0.0",
                kind="InvalidKind",
                apiVersion="v3.0.2",
                id="test",
                status="active",
            )

    def test_primary_key_position_validation(self):
        """Test primary key position validation logic."""
        # Primary key with position should work
        prop = SchemaProperty(
            name="id", logicalType="integer", primaryKey=True, primaryKeyPosition=1
        )
        assert prop.primaryKeyPosition == 1

        # Primary key without position should fail validation
        with pytest.raises(Exception):
            SchemaProperty(
                name="id",
                logicalType="integer",
                primaryKey=True,
                # Missing primaryKeyPosition
            )


class TestModelEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_collections(self):
        """Test behavior with empty collections."""
        contract = ODCSDataContract(
            version="1.0.0",
            kind="DataContract",
            apiVersion="v3.0.2",
            id="test",
            status="active",
            tags=[],  # Empty list
            servers=[],  # Empty list
            schema=[],  # Empty list
        )

        assert contract.tags == []
        assert contract.servers == []
        assert contract.schema == []

    def test_none_values(self):
        """Test handling of None values for optional fields."""
        contract = ODCSDataContract(
            version="1.0.0",
            kind="DataContract",
            apiVersion="v3.0.2",
            id="test",
            status="active",
            name=None,  # Optional field
            description=None,  # Optional field
        )

        assert contract.name is None
        assert contract.description is None

    @pytest.mark.parametrize(
        "field_value,expected",
        [
            ("", False),  # Empty string
            ("  ", False),  # Whitespace only
            ("valid_id", True),  # Valid ID
            ("valid-id-123", True),  # Valid ID with hyphens and numbers
        ],
    )
    def test_id_field_validation(self, field_value, expected):
        """Test ID field validation with various inputs."""
        if expected:
            contract = ODCSDataContract(
                version="1.0.0",
                kind="DataContract",
                apiVersion="v3.0.2",
                id=field_value,
                status="active",
            )
            assert contract.id == field_value
        else:
            with pytest.raises(Exception):
                ODCSDataContract(
                    version="1.0.0",
                    kind="DataContract",
                    apiVersion="v3.0.2",
                    id=field_value,
                    status="active",
                )


@pytest.mark.unit
class TestUtilityFunctions:
    """Test utility functions used in unit testing."""

    def test_file_helper_json_creation(self, file_helper):
        """Test JSON file creation helper."""
        test_data = {"test": "data", "number": 123}

        with file_helper.create_temp_json_file(test_data) as json_file:
            assert json_file.exists()
            assert json_file.suffix == ".json"

            # Read back and verify
            import json

            with open(json_file) as f:
                loaded_data = json.load(f)

            assert loaded_data == test_data

    def test_file_helper_text_creation(self, file_helper):
        """Test text file creation helper."""
        test_content = "This is test content\nWith multiple lines"

        with file_helper.create_temp_text_file(test_content, ".txt") as text_file:
            assert text_file.exists()
            assert text_file.suffix == ".txt"

            # Read back and verify
            with open(text_file) as f:
                loaded_content = f.read()

            assert loaded_content == test_content

    def test_parameterized_test_data_access(self, parameterized_test_data):
        """Test access to parameterized test data."""
        logical_types = parameterized_test_data.get_logical_type_test_cases()
        assert len(logical_types) > 0

        server_types = parameterized_test_data.get_server_type_test_cases()
        assert len(server_types) > 0

        api_versions = parameterized_test_data.get_api_version_test_cases()
        assert len(api_versions) > 0

        # Verify structure of test cases
        for logical_type, is_valid in logical_types:
            assert isinstance(logical_type, (str, type(None), int))
            assert isinstance(is_valid, bool)


# Example of testing with mocked dependencies
class TestMockedDependencies:
    """Examples of unit tests with mocked dependencies."""

    @patch("odcs_converter.models.datetime")
    def test_datetime_field_with_mock(self, mock_datetime):
        """Test datetime field handling with mocked datetime."""
        # Mock datetime.now() to return a fixed value
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-15T10:00:00Z"

        # Test would go here - this is just an example structure
        assert mock_datetime.now.called is False  # Not called yet

        # If our code called datetime.now(), we could verify it
        # mock_datetime.now.assert_called_once()

    def test_with_file_system_mock(self, mock_factory):
        """Test file system operations with mocks."""
        mock_path = mock_factory.create_mock_path(exists=False)

        # Test code that checks if file exists
        assert mock_path.exists() is False
        mock_path.exists.assert_called()

    def test_with_requests_mock(self, mock_factory):
        """Test HTTP requests with mocked responses."""
        mock_response = mock_factory.create_mock_requests_response(
            json_data={"status": "success"}, status_code=200
        )

        # Simulate using the mock response
        assert mock_response.status_code == 200
        assert mock_response.json() == {"status": "success"}

        # Verify methods were called
        mock_response.json.assert_called()
