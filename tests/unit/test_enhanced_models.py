"""Tests for enhanced ODCS models with all new advanced fields."""

import pytest
from pydantic import ValidationError

from odcs_converter.models import (
    ODCSDataContract,
    SchemaProperty,
    SchemaObject,
    DataQuality,
    LogicalTypeOptions,
    ServiceLevelAgreementProperty,
    QualityDimensionEnum,
    LogicalTypeEnum,
)


class TestLogicalTypeOptions:
    """Test LogicalTypeOptions model."""

    def test_string_options(self):
        """Test string-specific logical type options."""
        options = LogicalTypeOptions(
            format="email",
            minLength=5,
            maxLength=255,
            pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        )

        assert options.format == "email"
        assert options.minLength == 5
        assert options.maxLength == 255
        assert options.pattern == r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    def test_number_options(self):
        """Test number-specific logical type options."""
        options = LogicalTypeOptions(
            minimum=0,
            maximum=100,
            exclusiveMinimum=False,
            exclusiveMaximum=True,
            multipleOf=5,
        )

        assert options.minimum == 0
        assert options.maximum == 100
        assert options.exclusiveMinimum is False
        assert options.exclusiveMaximum is True
        assert options.multipleOf == 5

    def test_array_options(self):
        """Test array-specific logical type options."""
        options = LogicalTypeOptions(minItems=1, maxItems=10, uniqueItems=True)

        assert options.minItems == 1
        assert options.maxItems == 10
        assert options.uniqueItems is True

    def test_object_options(self):
        """Test object-specific logical type options."""
        options = LogicalTypeOptions(
            minProperties=1, maxProperties=50, required=["id", "name"]
        )

        assert options.minProperties == 1
        assert options.maxProperties == 50
        assert options.required == ["id", "name"]

    def test_empty_options(self):
        """Test LogicalTypeOptions with no fields set."""
        options = LogicalTypeOptions()

        assert options.format is None
        assert options.minLength is None
        assert options.maxLength is None
        assert options.pattern is None
        assert options.minimum is None
        assert options.maximum is None


class TestEnhancedDataQuality:
    """Test enhanced DataQuality model with all new fields."""

    def test_basic_quality_rule(self):
        """Test basic data quality rule."""
        rule = DataQuality(
            name="Email Format Check",
            description="Validates email format",
            type="library",
            dimension=QualityDimensionEnum.CONFORMITY,
        )

        assert rule.name == "Email Format Check"
        assert rule.description == "Validates email format"
        assert rule.type == "library"
        assert rule.dimension == QualityDimensionEnum.CONFORMITY

    def test_library_rule_with_operators(self):
        """Test library rule with comparison operators."""
        rule = DataQuality(
            name="Row Count Check",
            rule="rowCount",
            unit="rows",
            mustBeBetween=[1000, 10000],
            dimension=QualityDimensionEnum.COMPLETENESS,
        )

        assert rule.name == "Row Count Check"
        assert rule.rule == "rowCount"
        assert rule.unit == "rows"
        assert rule.mustBeBetween == [1000, 10000]
        assert rule.dimension == QualityDimensionEnum.COMPLETENESS

    def test_sql_rule(self):
        """Test SQL-based quality rule."""
        rule = DataQuality(
            name="Null Check",
            type="sql",
            query="SELECT COUNT(*) FROM ${object} WHERE ${property} IS NULL",
            mustBe=0,
            dimension=QualityDimensionEnum.COMPLETENESS,
        )

        assert rule.name == "Null Check"
        assert rule.type == "sql"
        assert rule.query == "SELECT COUNT(*) FROM ${object} WHERE ${property} IS NULL"
        assert rule.mustBe == 0

    def test_custom_rule(self):
        """Test custom engine quality rule."""
        rule = DataQuality(
            name="Soda Check",
            type="custom",
            engine="soda",
            implementation="""
            type: duplicate_percent
            columns:
              - email
            must_be_less_than: 1.0
            """,
            dimension=QualityDimensionEnum.UNIQUENESS,
        )

        assert rule.name == "Soda Check"
        assert rule.type == "custom"
        assert rule.engine == "soda"
        assert "duplicate_percent" in rule.implementation

    def test_all_comparison_operators(self):
        """Test all comparison operators."""
        rule = DataQuality(
            name="Comprehensive Check",
            mustBe=100,
            mustNotBe=0,
            mustBeGreaterThan=50,
            mustBeGreaterOrEqualTo=51,
            mustBeLessThan=200,
            mustBeLessOrEqualTo=199,
            mustBeBetween=[75, 125],
            mustNotBeBetween=[0, 25],
        )

        assert rule.mustBe == 100
        assert rule.mustNotBe == 0
        assert rule.mustBeGreaterThan == 50
        assert rule.mustBeGreaterOrEqualTo == 51
        assert rule.mustBeLessThan == 200
        assert rule.mustBeLessOrEqualTo == 199
        assert rule.mustBeBetween == [75, 125]
        assert rule.mustNotBeBetween == [0, 25]

    def test_valid_values_rule(self):
        """Test rule with valid values."""
        rule = DataQuality(
            name="Status Check",
            rule="validValues",
            validValues=["active", "inactive", "pending"],
            unit="percent",
            mustBe=100,
        )

        assert rule.name == "Status Check"
        assert rule.rule == "validValues"
        assert rule.validValues == ["active", "inactive", "pending"]
        assert rule.unit == "percent"
        assert rule.mustBe == 100

    def test_quality_with_scheduling(self):
        """Test quality rule with scheduling."""
        rule = DataQuality(
            name="Daily Check",
            rule="rowCount",
            scheduler="cron",
            schedule="0 9 * * *",
            severity="critical",
            businessImpact="Data pipeline failure",
        )

        assert rule.name == "Daily Check"
        assert rule.scheduler == "cron"
        assert rule.schedule == "0 9 * * *"
        assert rule.severity == "critical"
        assert rule.businessImpact == "Data pipeline failure"

    def test_quality_dimension_synonyms(self):
        """Test quality dimension synonyms."""
        rule1 = DataQuality(dimension=QualityDimensionEnum.ACCURACY)
        rule2 = DataQuality(dimension=QualityDimensionEnum.AC)

        # Both should be valid
        assert rule1.dimension in ["accuracy", "ac"]
        assert rule2.dimension in ["accuracy", "ac"]


class TestEnhancedSchemaProperty:
    """Test enhanced SchemaProperty model with all new fields."""

    def test_basic_property_with_logical_type_options(self):
        """Test property with logical type options."""
        prop = SchemaProperty(
            name="email",
            logicalType=LogicalTypeEnum.STRING,
            logicalTypeOptions=LogicalTypeOptions(format="email", maxLength=255),
            description="User email address",
            required=True,
        )

        assert prop.name == "email"
        assert prop.logicalType == LogicalTypeEnum.STRING
        assert prop.logicalTypeOptions.format == "email"
        assert prop.logicalTypeOptions.maxLength == 255
        assert prop.description == "User email address"
        assert prop.required is True

    def test_property_with_transform_fields(self):
        """Test property with transformation fields."""
        prop = SchemaProperty(
            name="full_name",
            transformSourceObjects=["users", "profiles"],
            transformLogic="CONCAT(u.first_name, ' ', u.last_name)",
            transformDescription="Concatenate first and last name from user tables",
        )

        assert prop.name == "full_name"
        assert prop.transformSourceObjects == ["users", "profiles"]
        assert prop.transformLogic == "CONCAT(u.first_name, ' ', u.last_name)"
        assert (
            prop.transformDescription
            == "Concatenate first and last name from user tables"
        )

    def test_property_with_encryption(self):
        """Test property with encryption field."""
        prop = SchemaProperty(
            name="ssn",
            encryptedName="ssn_encrypted",
            classification="confidential",
            criticalDataElement=True,
        )

        assert prop.name == "ssn"
        assert prop.encryptedName == "ssn_encrypted"
        assert prop.classification == "confidential"
        assert prop.criticalDataElement is True

    def test_array_property_with_items(self):
        """Test array property with items definition."""
        items_def = SchemaProperty(
            name="item",
            logicalType=LogicalTypeEnum.STRING,
            logicalTypeOptions=LogicalTypeOptions(maxLength=100),
        )

        prop = SchemaProperty(
            name="tags",
            logicalType=LogicalTypeEnum.ARRAY,
            items=items_def,
            logicalTypeOptions=LogicalTypeOptions(
                minItems=1, maxItems=10, uniqueItems=True
            ),
        )

        assert prop.name == "tags"
        assert prop.logicalType == LogicalTypeEnum.ARRAY
        assert isinstance(prop.items, SchemaProperty)
        assert prop.items.name == "item"
        assert prop.items.logicalType == LogicalTypeEnum.STRING
        assert prop.logicalTypeOptions.minItems == 1
        assert prop.logicalTypeOptions.maxItems == 10
        assert prop.logicalTypeOptions.uniqueItems is True

    def test_property_with_quality_rules(self):
        """Test property with quality rules."""
        quality_rules = [
            DataQuality(
                name="Not Null", rule="completeness", mustBe=100, unit="percent"
            ),
            DataQuality(
                name="Unique Values", rule="uniqueness", mustBe=100, unit="percent"
            ),
        ]

        prop = SchemaProperty(
            name="user_id",
            logicalType=LogicalTypeEnum.INTEGER,
            primaryKey=True,
            primaryKeyPosition=1,
            quality=quality_rules,
        )

        assert prop.name == "user_id"
        assert prop.primaryKey is True
        assert prop.primaryKeyPosition == 1
        assert len(prop.quality) == 2
        assert prop.quality[0].name == "Not Null"
        assert prop.quality[1].name == "Unique Values"

    def test_property_with_authoritative_definitions(self):
        """Test property with authoritative definitions."""
        from odcs_converter.models import AuthoritativeDefinition

        auth_defs = [
            AuthoritativeDefinition(
                url="https://docs.company.com/user-id", type="businessDefinition"
            )
        ]

        prop = SchemaProperty(name="user_id", authoritativeDefinitions=auth_defs)

        assert prop.name == "user_id"
        assert len(prop.authoritativeDefinitions) == 1
        assert prop.authoritativeDefinitions[0].type == "businessDefinition"

    def test_primary_key_validation(self):
        """Test primary key position validation."""
        # Valid primary key with position
        prop = SchemaProperty(name="id", primaryKey=True, primaryKeyPosition=1)
        assert prop.primaryKey is True
        assert prop.primaryKeyPosition == 1

        # Invalid: primary key without position should raise error
        with pytest.raises(ValidationError) as exc_info:
            SchemaProperty(name="id", primaryKey=True, primaryKeyPosition=-1)
        assert "primaryKeyPosition is required" in str(exc_info.value)

    def test_complex_property_with_all_fields(self):
        """Test property with all possible fields."""
        from odcs_converter.models import AuthoritativeDefinition, CustomProperty

        prop = SchemaProperty(
            name="customer_email",
            logicalType=LogicalTypeEnum.STRING,
            logicalTypeOptions=LogicalTypeOptions(
                format="email",
                minLength=5,
                maxLength=255,
                pattern=r"^[^@]+@[^@]+\.[^@]+$",
            ),
            physicalType="VARCHAR(255)",
            physicalName="cust_email",
            description="Customer email address",
            businessName="Customer Email",
            required=True,
            unique=True,
            classification="restricted",
            encryptedName="cust_email_enc",
            criticalDataElement=True,
            transformSourceObjects=["customers", "contacts"],
            transformLogic="COALESCE(c.primary_email, ct.email)",
            transformDescription="Use primary email from customers, fallback to contacts",
            examples=["john@example.com", "jane@company.org"],
            tags=["pii", "contact", "required"],
            quality=[
                DataQuality(
                    name="Email Format", rule="validEmail", mustBe=100, unit="percent"
                )
            ],
            authoritativeDefinitions=[
                AuthoritativeDefinition(
                    url="https://wiki.company.com/customer-email",
                    type="businessDefinition",
                )
            ],
            customProperties=[
                CustomProperty(property="dataRetention", value="7 years")
            ],
        )

        # Verify all fields are set correctly
        assert prop.name == "customer_email"
        assert prop.logicalType == LogicalTypeEnum.STRING
        assert prop.logicalTypeOptions.format == "email"
        assert prop.physicalType == "VARCHAR(255)"
        assert prop.required is True
        assert prop.unique is True
        assert prop.classification == "restricted"
        assert prop.encryptedName == "cust_email_enc"
        assert prop.criticalDataElement is True
        assert len(prop.transformSourceObjects) == 2
        assert prop.transformLogic == "COALESCE(c.primary_email, ct.email)"
        assert len(prop.examples) == 2
        assert len(prop.tags) == 3
        assert len(prop.quality) == 1
        assert len(prop.authoritativeDefinitions) == 1
        assert len(prop.customProperties) == 1


class TestEnhancedSchemaObject:
    """Test enhanced SchemaObject model."""

    def test_schema_object_with_authoritative_definitions(self):
        """Test schema object with authoritative definitions."""
        from odcs_converter.models import AuthoritativeDefinition

        auth_defs = [
            AuthoritativeDefinition(
                url="https://catalog.company.com/users-table", type="businessDefinition"
            )
        ]

        obj = SchemaObject(
            name="users",
            description="User information table",
            authoritativeDefinitions=auth_defs,
        )

        assert obj.name == "users"
        assert len(obj.authoritativeDefinitions) == 1
        assert obj.authoritativeDefinitions[0].type == "businessDefinition"

    def test_schema_object_with_quality_rules(self):
        """Test schema object with quality rules."""
        quality_rules = [
            DataQuality(
                name="Row Count",
                rule="rowCount",
                mustBeBetween=[1000, 100000],
                unit="rows",
            )
        ]

        obj = SchemaObject(name="users", quality=quality_rules)

        assert obj.name == "users"
        assert len(obj.quality) == 1
        assert obj.quality[0].name == "Row Count"


class TestEnhancedServiceLevelAgreementProperty:
    """Test enhanced SLA property with valueExt field."""

    def test_sla_property_with_value_ext(self):
        """Test SLA property with extended value."""
        sla = ServiceLevelAgreementProperty(
            property="frequency",
            value=1,
            valueExt=2,
            unit="d",
            element="users.created_at",
            driver="operational",
        )

        assert sla.property == "frequency"
        assert sla.value == 1
        assert sla.valueExt == 2
        assert sla.unit == "d"
        assert sla.element == "users.created_at"
        assert sla.driver == "operational"

    def test_sla_property_without_value_ext(self):
        """Test SLA property without extended value."""
        sla = ServiceLevelAgreementProperty(property="latency", value=4, unit="h")

        assert sla.property == "latency"
        assert sla.value == 4
        assert sla.valueExt is None
        assert sla.unit == "h"


class TestCompleteODCSContract:
    """Test complete ODCS contract with all enhanced features."""

    def test_contract_with_enhanced_schema(self):
        """Test complete contract with enhanced schema features."""
        from odcs_converter.models import ApiVersionEnum

        contract_data = {
            "version": "1.0.0",
            "kind": "DataContract",
            "apiVersion": "v3.0.2",
            "id": "enhanced-contract-001",
            "status": "active",
            "name": "Enhanced Test Contract",
            "schema": [
                {
                    "name": "users",
                    "logicalType": "object",
                    "physicalType": "table",
                    "description": "User information",
                    "properties": [
                        {
                            "name": "email",
                            "logicalType": "string",
                            "logicalTypeOptions": {"format": "email", "maxLength": 255},
                            "required": True,
                            "quality": [
                                {
                                    "name": "Email Format Check",
                                    "rule": "validEmail",
                                    "mustBe": 100,
                                    "unit": "percent",
                                }
                            ],
                        }
                    ],
                    "quality": [
                        {
                            "name": "Row Count Check",
                            "rule": "rowCount",
                            "mustBeBetween": [1000, 100000],
                        }
                    ],
                }
            ],
        }

        contract = ODCSDataContract(**contract_data)

        assert contract.version == "1.0.0"
        assert contract.apiVersion == ApiVersionEnum.V3_0_2
        assert len(contract.schema) == 1

        schema_obj = contract.schema[0]
        assert schema_obj.name == "users"
        assert len(schema_obj.properties) == 1
        assert len(schema_obj.quality) == 1

        prop = schema_obj.properties[0]
        assert prop.name == "email"
        assert prop.logicalTypeOptions.format == "email"
        assert len(prop.quality) == 1

    def test_invalid_contract_validation(self):
        """Test that enhanced validation still works."""
        # Missing required field should still fail
        with pytest.raises(ValidationError):
            ODCSDataContract(
                version="",  # Empty version should fail
                kind="DataContract",
                apiVersion="v3.0.2",
                id="test",
                status="active",
            )

    def test_model_rebuild_works(self):
        """Test that forward references are properly resolved."""
        # This test ensures that the model_rebuild() calls work
        # and circular dependencies are resolved

        from odcs_converter.models import (
            DataQuality,
            CustomProperty,
            AuthoritativeDefinition,
        )

        # Create a DataQuality with custom properties and auth definitions
        custom_props = [CustomProperty(property="test", value="value")]
        auth_defs = [AuthoritativeDefinition(url="https://example.com", type="test")]

        quality = DataQuality(
            name="Test Rule",
            customProperties=custom_props,
            authoritativeDefinitions=auth_defs,
        )

        assert len(quality.customProperties) == 1
        assert len(quality.authoritativeDefinitions) == 1
        assert quality.customProperties[0].property == "test"
        assert quality.authoritativeDefinitions[0].type == "test"
