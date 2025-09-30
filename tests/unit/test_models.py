"""Unit tests for ODCS data models and validation."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from odcs_converter.models import (
    ODCSDataContract,
    ApiVersionEnum,
    KindEnum,
    ServerTypeEnum,
    LogicalTypeEnum,
    QualityDimensionEnum,
    CustomProperty,
    AuthoritativeDefinition,
    Role,
    Team,
    SupportItem,
    Pricing,
    DataQuality,
    SchemaProperty,
    SchemaObject,
    Server,
    Description,
    ServiceLevelAgreementProperty,
)


@pytest.mark.unit
class TestODCSDataContract:
    """Unit tests for ODCSDataContract model."""

    def test_valid_minimal_contract(self):
        """Test creation of valid minimal ODCS contract."""
        data = {
            "version": "1.0.0",
            "kind": "DataContract",
            "apiVersion": "v3.0.2",
            "id": "test-contract-001",
            "status": "active",
        }

        contract = ODCSDataContract(**data)
        assert contract.version == "1.0.0"
        assert contract.kind == KindEnum.DATA_CONTRACT
        assert contract.apiVersion == ApiVersionEnum.V3_0_2
        assert contract.id == "test-contract-001"
        assert contract.status == "active"

    def test_valid_complete_contract(self, sample_odcs_complete):
        """Test creation of complete ODCS contract."""
        contract = ODCSDataContract(**sample_odcs_complete)

        assert contract.version == "2.0.0"
        assert contract.name == "Complete Test Contract"
        assert contract.tenant == "test-tenant"
        assert len(contract.tags) == 3
        assert len(contract.servers) == 2
        assert len(contract.schema) == 1
        assert contract.description.usage is not None

    def test_missing_required_fields(self):
        """Test validation error for missing required fields."""
        # Missing 'id' field
        data = {
            "version": "1.0.0",
            "kind": "DataContract",
            "apiVersion": "v3.0.2",
            "status": "active",
        }

        with pytest.raises(ValidationError) as excinfo:
            ODCSDataContract(**data)

        errors = excinfo.value.errors()
        field_names = [error["loc"][0] for error in errors]
        assert "id" in field_names

    def test_invalid_enum_values(self):
        """Test validation error for invalid enum values."""
        data = {
            "version": "1.0.0",
            "kind": "InvalidKind",  # Invalid enum value
            "apiVersion": "v3.0.2",
            "id": "test-contract-001",
            "status": "active",
        }

        with pytest.raises(ValidationError) as excinfo:
            ODCSDataContract(**data)

        assert "kind" in str(excinfo.value)

    def test_invalid_api_version(self):
        """Test validation error for invalid API version."""
        data = {
            "version": "1.0.0",
            "kind": "DataContract",
            "apiVersion": "v99.99.99",  # Invalid version
            "id": "test-contract-001",
            "status": "active",
        }

        with pytest.raises(ValidationError):
            ODCSDataContract(**data)

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        data = {
            "version": "1.0.0",
            "kind": "DataContract",
            "apiVersion": "v3.0.2",
            "id": "test-contract-001",
            "status": "active",
            "extraField": "should not be allowed",
        }

        with pytest.raises(ValidationError) as excinfo:
            ODCSDataContract(**data)

        assert "extraField" in str(excinfo.value)

    def test_datetime_field_validation(self):
        """Test datetime field validation."""
        data = {
            "version": "1.0.0",
            "kind": "DataContract",
            "apiVersion": "v3.0.2",
            "id": "test-contract-001",
            "status": "active",
            "contractCreatedTs": "2024-01-15T09:00:00Z",
        }

        contract = ODCSDataContract(**data)
        assert isinstance(contract.contractCreatedTs, datetime)

    def test_invalid_datetime_format(self):
        """Test validation error for invalid datetime format."""
        data = {
            "version": "1.0.0",
            "kind": "DataContract",
            "apiVersion": "v3.0.2",
            "id": "test-contract-001",
            "status": "active",
            "contractCreatedTs": "invalid-datetime",
        }

        with pytest.raises(ValidationError):
            ODCSDataContract(**data)


@pytest.mark.unit
class TestCustomProperty:
    """Unit tests for CustomProperty model."""

    def test_valid_custom_property(self):
        """Test valid custom property creation."""
        prop = CustomProperty(property="testProp", value="testValue")
        assert prop.property == "testProp"
        assert prop.value == "testValue"

    def test_custom_property_with_different_value_types(self):
        """Test custom property with different value types."""
        # String value
        prop1 = CustomProperty(property="stringProp", value="text")
        assert prop1.value == "text"

        # Number value
        prop2 = CustomProperty(property="numberProp", value=42)
        assert prop2.value == 42

        # Boolean value
        prop3 = CustomProperty(property="boolProp", value=True)
        assert prop3.value is True

        # List value
        prop4 = CustomProperty(property="listProp", value=["item1", "item2"])
        assert prop4.value == ["item1", "item2"]

    def test_missing_required_fields(self):
        """Test validation error for missing required fields."""
        with pytest.raises(ValidationError):
            CustomProperty(property="testProp")  # Missing value

        with pytest.raises(ValidationError):
            CustomProperty(value="testValue")  # Missing property


@pytest.mark.unit
class TestServer:
    """Unit tests for Server model."""

    def test_valid_server(self):
        """Test valid server creation."""
        server = Server(
            server="test-server",
            type=ServerTypeEnum.POSTGRESQL,
            description="Test database server",
            host="localhost",
            port=5432,
            database="testdb",
        )

        assert server.server == "test-server"
        assert server.type == ServerTypeEnum.POSTGRESQL
        assert server.host == "localhost"
        assert server.port == 5432

    def test_server_with_minimal_fields(self):
        """Test server with only required fields."""
        server = Server(server="minimal-server", type=ServerTypeEnum.MYSQL)

        assert server.server == "minimal-server"
        assert server.type == ServerTypeEnum.MYSQL
        assert server.description is None

    def test_invalid_server_type(self):
        """Test validation error for invalid server type."""
        with pytest.raises(ValidationError):
            Server(server="test-server", type="invalid_type")

    def test_server_with_all_optional_fields(self):
        """Test server with all optional fields."""
        server = Server(
            server="full-server",
            type=ServerTypeEnum.SNOWFLAKE,
            description="Complete server config",
            environment="production",
            location="https://account.snowflakecomputing.com",
            host="snowflake.example.com",
            port=443,
            database="PROD_DB",
            schema="PUBLIC",
            project="my-project",
            catalog="my-catalog",
            format="parquet",
        )

        assert server.environment == "production"
        assert server.location == "https://account.snowflakecomputing.com"
        assert server.schema == "PUBLIC"


@pytest.mark.unit
class TestSchemaProperty:
    """Unit tests for SchemaProperty model."""

    def test_valid_schema_property(self):
        """Test valid schema property creation."""
        prop = SchemaProperty(
            name="test_field",
            logicalType=LogicalTypeEnum.STRING,
            physicalType="VARCHAR(255)",
            description="Test field description",
            required=True,
            primaryKey=True,
            primaryKeyPosition=1,
        )

        assert prop.name == "test_field"
        assert prop.logicalType == LogicalTypeEnum.STRING
        assert prop.required is True
        assert prop.primaryKey is True

    def test_schema_property_with_minimal_fields(self):
        """Test schema property with only required fields."""
        prop = SchemaProperty(name="minimal_field")

        assert prop.name == "minimal_field"
        assert prop.required is False  # Default value
        assert prop.unique is False  # Default value
        assert prop.primaryKey is False  # Default value

    def test_primary_key_position_validation(self):
        """Test primary key position validation."""
        prop = SchemaProperty(name="id_field", primaryKey=True, primaryKeyPosition=1)

        assert prop.primaryKeyPosition == 1

    def test_invalid_logical_type(self):
        """Test validation error for invalid logical type."""
        with pytest.raises(ValidationError):
            SchemaProperty(name="test_field", logicalType="invalid_type")


@pytest.mark.unit
class TestSchemaObject:
    """Unit tests for SchemaObject model."""

    def test_valid_schema_object(self):
        """Test valid schema object creation."""
        schema_obj = SchemaObject(
            name="test_table",
            logicalType="object",
            physicalName="test_table_v1",
            description="Test table description",
            properties=[
                SchemaProperty(
                    name="id",
                    logicalType=LogicalTypeEnum.INTEGER,
                    primaryKey=True,
                    primaryKeyPosition=1,
                )
            ],
        )

        assert schema_obj.name == "test_table"
        assert schema_obj.logicalType == "object"
        assert len(schema_obj.properties) == 1
        assert schema_obj.properties[0].name == "id"

    def test_schema_object_without_properties(self):
        """Test schema object without properties."""
        schema_obj = SchemaObject(name="simple_table")

        assert schema_obj.name == "simple_table"
        assert schema_obj.properties is None


@pytest.mark.unit
class TestDataQuality:
    """Unit tests for DataQuality model."""

    def test_valid_data_quality(self):
        """Test valid data quality rule creation."""
        quality = DataQuality(
            name="uniqueness_check",
            description="Check for duplicate values",
            dimension=QualityDimensionEnum.UNIQUENESS,
            type="library",
            severity="error",
        )

        assert quality.name == "uniqueness_check"
        assert quality.dimension == QualityDimensionEnum.UNIQUENESS
        assert quality.severity == "error"

    def test_data_quality_with_minimal_fields(self):
        """Test data quality with minimal fields."""
        quality = DataQuality()

        assert quality.type == "library"  # Default value


@pytest.mark.unit
class TestSupportItem:
    """Unit tests for SupportItem model."""

    def test_valid_support_item(self):
        """Test valid support item creation."""
        support = SupportItem(
            channel="help-desk",
            url="https://support.example.com",
            description="Primary support channel",
            tool="web",
            scope="issues",
        )

        assert support.channel == "help-desk"
        assert str(support.url) == "https://support.example.com/"
        assert support.tool == "web"

    def test_support_item_minimal_fields(self):
        """Test support item with only required fields."""
        support = SupportItem(channel="email-support", url="https://email.example.com")

        assert support.channel == "email-support"
        assert support.description is None


@pytest.mark.unit
class TestTeam:
    """Unit tests for Team model."""

    def test_valid_team_member(self):
        """Test valid team member creation."""
        member = Team(
            username="john.doe@example.com",
            name="John Doe",
            role="Data Engineer",
            description="Senior data engineer",
            dateIn="2024-01-15",
            dateOut="2024-12-31",
        )

        assert member.username == "john.doe@example.com"
        assert member.name == "John Doe"
        assert member.role == "Data Engineer"

    def test_team_member_minimal_fields(self):
        """Test team member with minimal fields."""
        member = Team()

        assert member.username is None
        assert member.name is None


@pytest.mark.unit
class TestRole:
    """Unit tests for Role model."""

    def test_valid_role(self):
        """Test valid role creation."""
        role = Role(
            role="data_analyst",
            description="Read-only access to analytics data",
            access="SELECT",
            firstLevelApprovers="manager@example.com",
        )

        assert role.role == "data_analyst"
        assert role.description == "Read-only access to analytics data"
        assert role.access == "SELECT"

    def test_role_minimal_fields(self):
        """Test role with only required fields."""
        role = Role(role="basic_user")

        assert role.role == "basic_user"
        assert role.description is None


@pytest.mark.unit
class TestPricing:
    """Unit tests for Pricing model."""

    def test_valid_pricing(self):
        """Test valid pricing creation."""
        pricing = Pricing(priceAmount=99.99, priceCurrency="USD", priceUnit="per GB")

        assert pricing.priceAmount == 99.99
        assert pricing.priceCurrency == "USD"
        assert pricing.priceUnit == "per GB"

    def test_pricing_minimal_fields(self):
        """Test pricing with minimal fields."""
        pricing = Pricing()

        assert pricing.priceAmount is None
        assert pricing.priceCurrency is None


@pytest.mark.unit
class TestServiceLevelAgreementProperty:
    """Unit tests for SLA Property model."""

    def test_valid_sla_property(self):
        """Test valid SLA property creation."""
        sla = ServiceLevelAgreementProperty(
            property="availability",
            value=99.9,
            unit="percent",
            element="main_table",
            driver="operational",
        )

        assert sla.property == "availability"
        assert sla.value == 99.9
        assert sla.unit == "percent"

    def test_sla_property_different_value_types(self):
        """Test SLA property with different value types."""
        # Numeric value
        sla1 = ServiceLevelAgreementProperty(property="latency", value=100)
        assert sla1.value == 100

        # String value
        sla2 = ServiceLevelAgreementProperty(property="status", value="active")
        assert sla2.value == "active"

        # Boolean value
        sla3 = ServiceLevelAgreementProperty(property="enabled", value=True)
        assert sla3.value is True


@pytest.mark.unit
class TestDescription:
    """Unit tests for Description model."""

    def test_valid_description(self):
        """Test valid description creation."""
        desc = Description(
            usage="Data analysis and reporting",
            purpose="Business intelligence",
            limitations="Batch processing only",
        )

        assert desc.usage == "Data analysis and reporting"
        assert desc.purpose == "Business intelligence"
        assert desc.limitations == "Batch processing only"

    def test_description_minimal_fields(self):
        """Test description with minimal fields."""
        desc = Description()

        assert desc.usage is None
        assert desc.purpose is None


@pytest.mark.unit
class TestAuthoritativeDefinition:
    """Unit tests for AuthoritativeDefinition model."""

    def test_valid_authoritative_definition(self):
        """Test valid authoritative definition creation."""
        auth_def = AuthoritativeDefinition(
            url="https://docs.example.com/data-contract", type="businessDefinition"
        )

        assert str(auth_def.url) == "https://docs.example.com/data-contract"
        assert auth_def.type == "businessDefinition"

    def test_invalid_url_format(self):
        """Test validation error for invalid URL format."""
        with pytest.raises(ValidationError):
            AuthoritativeDefinition(url="not-a-valid-url", type="businessDefinition")


@pytest.mark.unit
class TestEnums:
    """Unit tests for enum validations."""

    def test_api_version_enum(self):
        """Test API version enum values."""
        assert ApiVersionEnum.V3_0_2 == "v3.0.2"
        assert ApiVersionEnum.V3_0_1 == "v3.0.1"
        assert ApiVersionEnum.V2_2_2 == "v2.2.2"

    def test_kind_enum(self):
        """Test kind enum values."""
        assert KindEnum.DATA_CONTRACT == "DataContract"

    def test_server_type_enum(self):
        """Test server type enum values."""
        assert ServerTypeEnum.POSTGRESQL == "postgresql"
        assert ServerTypeEnum.SNOWFLAKE == "snowflake"
        assert ServerTypeEnum.BIGQUERY == "bigquery"

    def test_logical_type_enum(self):
        """Test logical type enum values."""
        assert LogicalTypeEnum.STRING == "string"
        assert LogicalTypeEnum.INTEGER == "integer"
        assert LogicalTypeEnum.BOOLEAN == "boolean"

    def test_quality_dimension_enum(self):
        """Test quality dimension enum values."""
        assert QualityDimensionEnum.ACCURACY == "accuracy"
        assert QualityDimensionEnum.COMPLETENESS == "completeness"
        assert QualityDimensionEnum.UNIQUENESS == "uniqueness"
