"""Unit tests for YAML conversion utilities."""

import pytest
from pathlib import Path

from odcs_converter.yaml_converter import YAMLConverter


@pytest.mark.unit
class TestYAMLConverter:
    """Unit tests for YAMLConverter class."""

    def test_dict_to_yaml_string_simple(self):
        """Test converting simple dictionary to YAML string."""
        data = {"name": "test", "value": 42, "active": True}

        yaml_string = YAMLConverter.dict_to_yaml_string(data)

        assert "name: test" in yaml_string
        assert "value: 42" in yaml_string
        assert "active: true" in yaml_string

    def test_dict_to_yaml_string_nested(self):
        """Test converting nested dictionary to YAML string."""
        data = {
            "parent": {"child1": "value1", "child2": {"grandchild": "nested_value"}},
            "list_field": ["item1", "item2", "item3"],
        }

        yaml_string = YAMLConverter.dict_to_yaml_string(data)

        assert "parent:" in yaml_string
        assert "child1: value1" in yaml_string
        assert "grandchild: nested_value" in yaml_string
        assert "- item1" in yaml_string
        assert "- item2" in yaml_string

    def test_dict_to_yaml_string_with_special_characters(self):
        """Test YAML string generation with special characters."""
        data = {
            "description": "This contains: special & characters",
            "path": "/home/user/file.txt",
            "query": "SELECT * FROM table WHERE id = 'test'",
        }

        yaml_string = YAMLConverter.dict_to_yaml_string(data)

        # Should handle special characters properly
        assert "description:" in yaml_string
        assert "path:" in yaml_string
        assert "query:" in yaml_string

    def test_dict_to_yaml_string_empty_dict(self):
        """Test converting empty dictionary to YAML string."""
        data = {}

        yaml_string = YAMLConverter.dict_to_yaml_string(data)

        assert yaml_string.strip() == "{}"

    def test_dict_to_yaml_string_none_values(self):
        """Test YAML string generation with None values."""
        data = {"field1": "value1", "field2": None, "field3": "value3"}

        yaml_string = YAMLConverter.dict_to_yaml_string(data)

        assert "field1: value1" in yaml_string
        assert "field2: null" in yaml_string or "field2:" in yaml_string
        assert "field3: value3" in yaml_string

    def test_dict_to_yaml_string_invalid_data(self):
        """Test YAML string generation with invalid data."""

        # Test with non-serializable object - YAML converter handles this gracefully
        class NonSerializable:
            pass

        data = {"valid": "value", "invalid": NonSerializable()}

        # YAML converter should handle this without raising an exception
        result = YAMLConverter.dict_to_yaml_string(data)
        assert isinstance(result, str)
        assert "valid: value" in result

    def test_yaml_string_to_dict_simple(self):
        """Test parsing simple YAML string to dictionary."""
        yaml_string = """
        name: test
        value: 42
        active: true
        """

        data = YAMLConverter.yaml_string_to_dict(yaml_string)

        assert data["name"] == "test"
        assert data["value"] == 42
        assert data["active"] is True

    def test_yaml_string_to_dict_nested(self):
        """Test parsing nested YAML string to dictionary."""
        yaml_string = """
        parent:
          child1: value1
          child2:
            grandchild: nested_value
        list_field:
          - item1
          - item2
          - item3
        """

        data = YAMLConverter.yaml_string_to_dict(yaml_string)

        assert data["parent"]["child1"] == "value1"
        assert data["parent"]["child2"]["grandchild"] == "nested_value"
        assert data["list_field"] == ["item1", "item2", "item3"]

    def test_yaml_string_to_dict_empty_string(self):
        """Test parsing empty YAML string."""
        yaml_string = ""

        with pytest.raises(ValueError, match="Cannot process YAML string"):
            YAMLConverter.yaml_string_to_dict(yaml_string)

    def test_yaml_string_to_dict_invalid_yaml(self):
        """Test parsing invalid YAML string."""
        yaml_string = """
        invalid: yaml: content:
          - unclosed list
            missing close
        """

        with pytest.raises(ValueError, match="Invalid YAML format"):
            YAMLConverter.yaml_string_to_dict(yaml_string)

    def test_yaml_string_to_dict_non_dict_root(self):
        """Test parsing YAML string that doesn't have dict at root."""
        yaml_string = "- item1\n- item2\n- item3"

        with pytest.raises(ValueError, match="dictionary/object at root level"):
            YAMLConverter.yaml_string_to_dict(yaml_string)

    def test_dict_to_yaml_file(self, temp_dir):
        """Test converting dictionary to YAML file."""
        data = {"version": "1.0.0", "name": "test_contract", "tags": ["test", "unit"]}

        yaml_file = temp_dir / "test.yaml"
        YAMLConverter.dict_to_yaml(data, yaml_file)

        assert yaml_file.exists()

        # Verify file content
        with open(yaml_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "version: 1.0.0" in content
        assert "name: test_contract" in content
        assert "- test" in content

    def test_dict_to_yaml_file_creates_parent_dir(self, temp_dir):
        """Test that dict_to_yaml creates parent directories."""
        data = {"test": "value"}

        nested_dir = temp_dir / "nested" / "directory"
        yaml_file = nested_dir / "test.yaml"

        YAMLConverter.dict_to_yaml(data, yaml_file)

        assert yaml_file.exists()
        assert nested_dir.exists()

    def test_dict_to_yaml_file_permission_error(self, temp_dir, monkeypatch):
        """Test handling of permission errors when writing YAML file."""
        data = {"test": "value"}
        yaml_file = temp_dir / "readonly.yaml"

        # Create file and make it readonly
        yaml_file.touch()
        yaml_file.chmod(0o444)

        try:
            with pytest.raises(ValueError, match="Cannot serialize data to YAML"):
                YAMLConverter.dict_to_yaml(data, yaml_file)
        finally:
            # Restore permissions for cleanup
            yaml_file.chmod(0o644)

    def test_yaml_to_dict_file(self, temp_dir):
        """Test loading YAML file to dictionary."""
        yaml_content = """
        version: 2.0.0
        kind: DataContract
        metadata:
          created: 2024-01-15
          tags:
            - production
            - validated
        """

        yaml_file = temp_dir / "contract.yaml"
        with open(yaml_file, "w", encoding="utf-8") as f:
            f.write(yaml_content)

        data = YAMLConverter.yaml_to_dict(yaml_file)

        assert data["version"] == "2.0.0"
        assert data["kind"] == "DataContract"
        # YAML automatically parses dates, so check the parsed date
        from datetime import date

        assert data["metadata"]["created"] == date(2024, 1, 15)
        assert "production" in data["metadata"]["tags"]

    def test_yaml_to_dict_file_not_found(self):
        """Test handling of non-existent YAML file."""
        non_existent_file = Path("/non/existent/file.yaml")

        with pytest.raises(FileNotFoundError, match="YAML file not found"):
            YAMLConverter.yaml_to_dict(non_existent_file)

    def test_yaml_to_dict_invalid_file_content(self, temp_dir):
        """Test handling of invalid YAML file content."""
        yaml_file = temp_dir / "invalid.yaml"
        with open(yaml_file, "w", encoding="utf-8") as f:
            f.write("invalid: yaml: content: [\n  unclosed")

        with pytest.raises(ValueError, match="Invalid YAML format"):
            YAMLConverter.yaml_to_dict(yaml_file)

    def test_yaml_to_dict_non_dict_file(self, temp_dir):
        """Test handling of YAML file with non-dict root."""
        yaml_file = temp_dir / "list.yaml"
        with open(yaml_file, "w", encoding="utf-8") as f:
            f.write("- item1\n- item2\n- item3")

        with pytest.raises(ValueError, match="dictionary/object at root level"):
            YAMLConverter.yaml_to_dict(yaml_file)

    def test_is_yaml_file_extensions(self):
        """Test YAML file extension detection."""
        assert YAMLConverter.is_yaml_file("contract.yaml") is True
        assert YAMLConverter.is_yaml_file("contract.yml") is True
        assert YAMLConverter.is_yaml_file("CONTRACT.YAML") is True
        assert YAMLConverter.is_yaml_file("CONTRACT.YML") is True

        assert YAMLConverter.is_yaml_file("contract.json") is False
        assert YAMLConverter.is_yaml_file("contract.txt") is False
        assert YAMLConverter.is_yaml_file("contract.xml") is False
        assert YAMLConverter.is_yaml_file("contract") is False

    def test_is_yaml_file_with_path_objects(self):
        """Test YAML file extension detection with Path objects."""
        assert YAMLConverter.is_yaml_file(Path("contract.yaml")) is True
        assert YAMLConverter.is_yaml_file(Path("contract.yml")) is True
        assert YAMLConverter.is_yaml_file(Path("contract.json")) is False

    def test_normalize_yaml_extension_prefer_yaml(self):
        """Test YAML extension normalization preferring .yaml."""
        result = YAMLConverter.normalize_yaml_extension(
            "contract.txt", prefer_yaml=True
        )
        assert result == Path("contract.yaml")

        result = YAMLConverter.normalize_yaml_extension("contract", prefer_yaml=True)
        assert result == Path("contract.yaml")

        # Should preserve existing YAML extensions
        result = YAMLConverter.normalize_yaml_extension(
            "contract.yml", prefer_yaml=True
        )
        assert result == Path("contract.yml")

        result = YAMLConverter.normalize_yaml_extension(
            "contract.yaml", prefer_yaml=True
        )
        assert result == Path("contract.yaml")

    def test_normalize_yaml_extension_prefer_yml(self):
        """Test YAML extension normalization preferring .yml."""
        result = YAMLConverter.normalize_yaml_extension(
            "contract.txt", prefer_yaml=False
        )
        assert result == Path("contract.yml")

        result = YAMLConverter.normalize_yaml_extension("contract", prefer_yaml=False)
        assert result == Path("contract.yml")

        # Should preserve existing YAML extensions
        result = YAMLConverter.normalize_yaml_extension(
            "contract.yaml", prefer_yaml=False
        )
        assert result == Path("contract.yaml")

        result = YAMLConverter.normalize_yaml_extension(
            "contract.yml", prefer_yaml=False
        )
        assert result == Path("contract.yml")

    def test_normalize_yaml_extension_with_path_objects(self):
        """Test YAML extension normalization with Path objects."""
        result = YAMLConverter.normalize_yaml_extension(Path("contract.txt"))
        assert result == Path("contract.yaml")

        result = YAMLConverter.normalize_yaml_extension(Path("contract.json"))
        assert result == Path("contract.yaml")

    def test_roundtrip_conversion(self):
        """Test roundtrip conversion: dict -> YAML string -> dict."""
        original_data = {
            "version": "1.0.0",
            "kind": "DataContract",
            "metadata": {
                "description": "Test contract",
                "tags": ["test", "roundtrip"],
                "active": True,
                "count": 42,
            },
            "nullable_field": None,
        }

        # Convert to YAML string
        yaml_string = YAMLConverter.dict_to_yaml_string(original_data)

        # Convert back to dict
        converted_data = YAMLConverter.yaml_string_to_dict(yaml_string)

        # Verify data integrity
        assert converted_data["version"] == original_data["version"]
        assert converted_data["kind"] == original_data["kind"]
        assert (
            converted_data["metadata"]["description"]
            == original_data["metadata"]["description"]
        )
        assert converted_data["metadata"]["tags"] == original_data["metadata"]["tags"]
        assert (
            converted_data["metadata"]["active"] == original_data["metadata"]["active"]
        )
        assert converted_data["metadata"]["count"] == original_data["metadata"]["count"]

    def test_roundtrip_file_conversion(self, temp_dir):
        """Test roundtrip file conversion: dict -> YAML file -> dict."""
        original_data = {
            "contract": {
                "name": "file_roundtrip_test",
                "version": "2.1.0",
                "servers": [
                    {"name": "server1", "type": "postgresql"},
                    {"name": "server2", "type": "snowflake"},
                ],
            }
        }

        yaml_file = temp_dir / "roundtrip.yaml"

        # Write to file
        YAMLConverter.dict_to_yaml(original_data, yaml_file)

        # Read from file
        loaded_data = YAMLConverter.yaml_to_dict(yaml_file)

        # Verify data integrity
        assert loaded_data == original_data

    def test_unicode_handling(self):
        """Test proper handling of Unicode characters."""
        data = {
            "description": "Contract with émojis 🚀 and spëcial chars: àáâãäåæçèé",
            "unicode_field": "Contains unicode: ñ, ü, ø, ß",
            "chinese": "测试数据",
            "arabic": "بيانات الاختبار",
        }

        # Test string conversion
        yaml_string = YAMLConverter.dict_to_yaml_string(data)
        converted_data = YAMLConverter.yaml_string_to_dict(yaml_string)

        assert converted_data["description"] == data["description"]
        assert converted_data["unicode_field"] == data["unicode_field"]
        assert converted_data["chinese"] == data["chinese"]
        assert converted_data["arabic"] == data["arabic"]

    def test_large_data_structure(self):
        """Test handling of large data structures."""
        # Create a reasonably large nested structure
        large_data = {
            "metadata": {
                f"item_{i}": {"id": f"item_{i}", "value": i * 2} for i in range(100)
            }
        }
        large_data["nested"] = {
            "level1": {
                "level2": {"level3": {"items": [f"item_{i}" for i in range(50)]}}
            }
        }

        # Should handle large structures without issues
        yaml_string = YAMLConverter.dict_to_yaml_string(large_data)
        converted_data = YAMLConverter.yaml_string_to_dict(yaml_string)

        assert len(converted_data["metadata"]) == 100
        assert (
            len(converted_data["nested"]["level1"]["level2"]["level3"]["items"]) == 50
        )
        assert converted_data["metadata"]["item_50"]["value"] == 100
