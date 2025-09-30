"""Utilities for unit tests."""

import json
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional
from unittest.mock import MagicMock
import pytest


class UnitTestHelper:
    """Helper class for unit test operations."""

    @staticmethod
    def create_minimal_odcs_dict() -> Dict[str, Any]:
        """Create minimal valid ODCS data for unit testing."""
        return {
            "version": "1.0.0",
            "kind": "DataContract",
            "apiVersion": "v3.0.2",
            "id": "unit-test-minimal",
            "status": "active",
        }

    @staticmethod
    def create_sample_server() -> Dict[str, Any]:
        """Create sample server data for unit testing."""
        return {
            "server": "unit-test-db",
            "type": "postgresql",
            "description": "Unit test database",
            "environment": "test",
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "schema": "public",
        }

    @staticmethod
    def create_sample_schema_property() -> Dict[str, Any]:
        """Create sample schema property for unit testing."""
        return {
            "name": "test_id",
            "logicalType": "integer",
            "physicalType": "BIGINT",
            "description": "Test identifier",
            "required": True,
            "primaryKey": True,
            "primaryKeyPosition": 1,
        }

    @staticmethod
    def create_sample_schema_object() -> Dict[str, Any]:
        """Create sample schema object for unit testing."""
        return {
            "name": "test_table",
            "logicalType": "object",
            "physicalName": "test_table_v1",
            "description": "Unit test table",
            "businessName": "Test Table",
            "properties": [UnitTestHelper.create_sample_schema_property()],
        }

    @staticmethod
    def create_invalid_data_variants() -> List[Dict[str, Any]]:
        """Create various invalid data combinations for negative testing."""
        base = UnitTestHelper.create_minimal_odcs_dict()

        return [
            # Missing required fields
            {k: v for k, v in base.items() if k != "version"},
            {k: v for k, v in base.items() if k != "apiVersion"},
            {k: v for k, v in base.items() if k != "id"},
            {k: v for k, v in base.items() if k != "status"},
            # Invalid enum values
            {**base, "kind": "InvalidKind"},
            {**base, "apiVersion": "v999.0.0"},
            # Invalid types
            {**base, "version": 123},
            {**base, "id": ""},  # Empty string should fail
            {**base, "tags": "not_a_list"},
        ]


class MockFactory:
    """Factory for creating mock objects for unit tests."""

    @staticmethod
    def create_mock_file_response(content: str, encoding: str = "utf-8") -> MagicMock:
        """Create a mock file response."""
        mock_file = MagicMock()
        mock_file.read.return_value = (
            content.encode(encoding) if isinstance(content, str) else content
        )
        mock_file.__enter__.return_value = mock_file
        mock_file.__exit__.return_value = None
        return mock_file

    @staticmethod
    def create_mock_requests_response(
        json_data: Optional[Dict[str, Any]] = None,
        text_data: Optional[str] = None,
        status_code: int = 200,
        raise_for_status: Optional[Exception] = None,
    ) -> MagicMock:
        """Create a mock requests response."""
        mock_response = MagicMock()
        mock_response.status_code = status_code

        if json_data is not None:
            mock_response.json.return_value = json_data

        if text_data is not None:
            mock_response.text = text_data

        if raise_for_status:
            mock_response.raise_for_status.side_effect = raise_for_status
        else:
            mock_response.raise_for_status.return_value = None

        return mock_response

    @staticmethod
    def create_mock_path(
        exists: bool = True, is_file: bool = True, is_dir: bool = False
    ) -> MagicMock:
        """Create a mock Path object."""
        mock_path = MagicMock()
        mock_path.exists.return_value = exists
        mock_path.is_file.return_value = is_file
        mock_path.is_dir.return_value = is_dir
        mock_path.suffix = ".json" if is_file else ""
        return mock_path


class ValidationHelper:
    """Helper for validation testing."""

    @staticmethod
    def assert_odcs_contract_valid(contract_dict: Dict[str, Any]) -> None:
        """Assert that a dictionary represents a valid ODCS contract."""
        # Basic required fields
        required_fields = ["version", "kind", "apiVersion", "id", "status"]
        for field in required_fields:
            assert field in contract_dict, f"Missing required field: {field}"
            assert contract_dict[field] is not None, f"Field {field} cannot be None"

        # Validate enum values
        assert contract_dict["kind"] in [
            "DataContract"
        ], f"Invalid kind: {contract_dict['kind']}"
        assert contract_dict["status"] in [
            "active",
            "inactive",
            "deprecated",
        ], f"Invalid status: {contract_dict['status']}"

    @staticmethod
    def assert_server_valid(server_dict: Dict[str, Any]) -> None:
        """Assert that a dictionary represents a valid server."""
        required_fields = ["server", "type"]
        for field in required_fields:
            assert field in server_dict, f"Missing required field: {field}"
            assert server_dict[field] is not None, f"Field {field} cannot be None"

    @staticmethod
    def assert_schema_property_valid(property_dict: Dict[str, Any]) -> None:
        """Assert that a dictionary represents a valid schema property."""
        required_fields = ["name", "logicalType"]
        for field in required_fields:
            assert field in property_dict, f"Missing required field: {field}"
            assert property_dict[field] is not None, f"Field {field} cannot be None"

        # If primaryKey is True, primaryKeyPosition should be set
        if property_dict.get("primaryKey"):
            assert (
                "primaryKeyPosition" in property_dict
            ), "Primary key must have position"
            assert isinstance(
                property_dict["primaryKeyPosition"], int
            ), "Primary key position must be integer"


class FileHelper:
    """Helper for file operations in unit tests."""

    @staticmethod
    @contextmanager
    def create_temp_json_file(data: Dict[str, Any]) -> Generator[Path, None, None]:
        """Create temporary JSON file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f, indent=2)
            temp_path = Path(f.name)

        try:
            yield temp_path
        finally:
            temp_path.unlink(missing_ok=True)

    @staticmethod
    @contextmanager
    def create_temp_text_file(
        content: str, suffix: str = ".txt"
    ) -> Generator[Path, None, None]:
        """Create temporary text file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            yield temp_path
        finally:
            temp_path.unlink(missing_ok=True)


class ParameterizedTestData:
    """Provides parameterized test data for comprehensive unit testing."""

    @staticmethod
    def get_logical_type_test_cases() -> List[tuple]:
        """Get test cases for logical type validation."""
        valid_cases = [
            ("string", True),
            ("integer", True),
            ("number", True),
            ("boolean", True),
            ("date", True),
            ("object", True),
            ("array", True),
        ]

        invalid_cases = [
            ("timestamp", False),  # Not in current model
            ("invalid_type", False),
            ("String", False),  # Case sensitive
            ("INTEGER", False),
            ("", False),
            (123, False),
        ]

        return valid_cases + invalid_cases

    @staticmethod
    def get_server_type_test_cases() -> List[tuple]:
        """Get test cases for server type validation."""
        valid_cases = [
            ("postgresql", True),
            ("mysql", True),
            ("snowflake", True),
            ("bigquery", True),
            ("redshift", True),
            ("databricks", True),
            ("oracle", True),
            ("sqlserver", True),
            ("s3", True),
        ]

        invalid_cases = [
            ("mongodb", False),  # Not in current model
            ("invalid_server", False),
            ("PostgreSQL", False),  # Case sensitive
            ("MYSQL", False),
            ("", False),
            (None, False),
        ]

        return valid_cases + invalid_cases

    @staticmethod
    def get_api_version_test_cases() -> List[tuple]:
        """Get test cases for API version validation."""
        valid_cases = [
            ("v3.0.0", True),
            ("v3.0.1", True),
            ("v3.0.2", True),
            ("v3.1.0", True),
        ]

        invalid_cases = [
            ("v2.0.0", False),
            ("v4.0.0", False),
            ("3.0.0", False),  # Missing 'v' prefix
            ("v3", False),
            ("invalid", False),
            ("", False),
            (None, False),
        ]

        return valid_cases + invalid_cases


# Pytest fixtures specific to unit tests
@pytest.fixture
def unit_test_helper():
    """Provide unit test helper instance."""
    return UnitTestHelper()


@pytest.fixture
def mock_factory():
    """Provide mock factory instance."""
    return MockFactory()


@pytest.fixture
def validation_helper():
    """Provide validation helper instance."""
    return ValidationHelper()


@pytest.fixture
def file_helper():
    """Provide file helper instance."""
    return FileHelper()


@pytest.fixture
def parameterized_test_data():
    """Provide parameterized test data."""
    return ParameterizedTestData()


# Custom decorators for unit tests
def unit_test(func):
    """Decorator to mark a function as a unit test."""
    return pytest.mark.unit(func)


def parametrize_logical_types(func):
    """Decorator to parametrize tests with logical type test cases."""
    test_cases = ParameterizedTestData.get_logical_type_test_cases()
    return pytest.mark.parametrize("logical_type,is_valid", test_cases)(func)


def parametrize_server_types(func):
    """Decorator to parametrize tests with server type test cases."""
    test_cases = ParameterizedTestData.get_server_type_test_cases()
    return pytest.mark.parametrize("server_type,is_valid", test_cases)(func)


def parametrize_api_versions(func):
    """Decorator to parametrize tests with API version test cases."""
    test_cases = ParameterizedTestData.get_api_version_test_cases()
    return pytest.mark.parametrize("api_version,is_valid", test_cases)(func)
