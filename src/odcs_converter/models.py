"""Pydantic models for ODCS data validation."""

from datetime import datetime
from typing import Any, List, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


class ApiVersionEnum(str, Enum):
    """Supported ODCS API versions."""

    V3_1_0 = "v3.1.0"
    V3_0_2 = "v3.0.2"
    V3_0_1 = "v3.0.1"
    V3_0_0 = "v3.0.0"
    V2_2_2 = "v2.2.2"
    V2_2_1 = "v2.2.1"
    V2_2_0 = "v2.2.0"


class KindEnum(str, Enum):
    """Supported ODCS kinds."""

    DATA_CONTRACT = "DataContract"


class ServerTypeEnum(str, Enum):
    """Supported server types."""

    API = "api"
    ATHENA = "athena"
    AZURE = "azure"
    BIGQUERY = "bigquery"
    CLICKHOUSE = "clickhouse"
    DATABRICKS = "databricks"
    DENODO = "denodo"
    DREMIO = "dremio"
    DUCKDB = "duckdb"
    GLUE = "glue"
    CLOUDSQL = "cloudsql"
    DB2 = "db2"
    INFORMIX = "informix"
    KAFKA = "kafka"
    KINESIS = "kinesis"
    LOCAL = "local"
    MYSQL = "mysql"
    ORACLE = "oracle"
    POSTGRESQL = "postgresql"
    POSTGRES = "postgres"
    PRESTO = "presto"
    PUBSUB = "pubsub"
    REDSHIFT = "redshift"
    S3 = "s3"
    SFTP = "sftp"
    SNOWFLAKE = "snowflake"
    SQLSERVER = "sqlserver"
    SYNAPSE = "synapse"
    TRINO = "trino"
    VERTICA = "vertica"
    CUSTOM = "custom"


class LogicalTypeEnum(str, Enum):
    """Supported logical types."""

    STRING = "string"
    DATE = "date"
    NUMBER = "number"
    INTEGER = "integer"
    OBJECT = "object"
    ARRAY = "array"
    BOOLEAN = "boolean"


class QualityDimensionEnum(str, Enum):
    """Data quality dimensions."""

    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    CONFORMITY = "conformity"
    CONSISTENCY = "consistency"
    COVERAGE = "coverage"
    TIMELINESS = "timeliness"
    UNIQUENESS = "uniqueness"


class CustomProperty(BaseModel):
    """Custom property key-value pair."""

    property: str = Field(..., description="The name of the key")
    value: Any = Field(..., description="The value of the key")


class AuthoritativeDefinition(BaseModel):
    """Authoritative definition reference."""

    url: HttpUrl = Field(..., description="URL to the authority")
    type: str = Field(..., description="Type of definition")


class Tag(str):
    """Tag model - simplified to just be a string."""

    pass


class Role(BaseModel):
    """IAM role definition."""

    role: str = Field(..., description="Name of the IAM role")
    description: Optional[str] = Field(None, description="Description of the IAM role")
    access: Optional[str] = Field(None, description="Type of access provided")
    firstLevelApprovers: Optional[str] = Field(
        None, description="First-level approvers"
    )
    secondLevelApprovers: Optional[str] = Field(
        None, description="Second-level approvers"
    )
    customProperties: Optional[List[CustomProperty]] = Field(
        None, description="Custom properties"
    )


class Team(BaseModel):
    """Team member definition."""

    username: Optional[str] = Field(None, description="Username or email")
    name: Optional[str] = Field(None, description="User's name")
    description: Optional[str] = Field(None, description="User's description")
    role: Optional[str] = Field(None, description="User's job role")
    dateIn: Optional[str] = Field(None, description="Date when user joined")
    dateOut: Optional[str] = Field(None, description="Date when user left")
    replacedByUsername: Optional[str] = Field(None, description="Replacement username")


class SupportItem(BaseModel):
    """Support channel definition."""

    channel: str = Field(..., description="Channel name or identifier")
    url: HttpUrl = Field(..., description="Access URL")
    description: Optional[str] = Field(None, description="Channel description")
    tool: Optional[str] = Field(None, description="Tool name")
    scope: Optional[str] = Field(None, description="Channel scope")
    invitationUrl: Optional[HttpUrl] = Field(None, description="Invitation URL")


class Pricing(BaseModel):
    """Pricing information."""

    priceAmount: Optional[float] = Field(None, description="Price per unit")
    priceCurrency: Optional[str] = Field(None, description="Currency")
    priceUnit: Optional[str] = Field(None, description="Unit of measure")


class DataQuality(BaseModel):
    """Data quality rule definition."""

    name: Optional[str] = Field(None, description="Name of the quality check")
    description: Optional[str] = Field(None, description="Quality check description")
    dimension: Optional[QualityDimensionEnum] = Field(
        None, description="Quality dimension"
    )
    type: Optional[str] = Field("library", description="Type of quality check")
    severity: Optional[str] = Field(None, description="Severity level")
    businessImpact: Optional[str] = Field(None, description="Business impact")
    schedule: Optional[str] = Field(None, description="Execution schedule")
    scheduler: Optional[str] = Field(None, description="Scheduler type")
    tags: Optional[List[str]] = Field(None, description="Quality tags")


class SchemaProperty(BaseModel):
    """Schema property definition."""

    name: str = Field(..., description="Property name")
    logicalType: Optional[LogicalTypeEnum] = Field(
        None, description="Logical data type"
    )
    physicalType: Optional[str] = Field(None, description="Physical data type")
    physicalName: Optional[str] = Field(None, description="Physical name")
    description: Optional[str] = Field(None, description="Property description")
    businessName: Optional[str] = Field(None, description="Business name")
    required: Optional[bool] = Field(False, description="Whether required")
    unique: Optional[bool] = Field(False, description="Whether unique")
    primaryKey: Optional[bool] = Field(False, description="Whether primary key")
    primaryKeyPosition: Optional[int] = Field(-1, description="Primary key position")
    partitioned: Optional[bool] = Field(False, description="Whether partitioned")
    partitionKeyPosition: Optional[int] = Field(
        -1, description="Partition key position"
    )
    classification: Optional[str] = Field(None, description="Data classification")
    criticalDataElement: Optional[bool] = Field(False, description="Whether CDE")
    examples: Optional[List[Any]] = Field(None, description="Example values")
    tags: Optional[List[str]] = Field(None, description="Property tags")
    customProperties: Optional[List[CustomProperty]] = Field(
        None, description="Custom properties"
    )
    quality: Optional[List[DataQuality]] = Field(None, description="Quality checks")

    @model_validator(mode="after")
    def validate_primary_key_position(self):
        """Validate that primaryKey requires primaryKeyPosition."""
        if self.primaryKey and (
            self.primaryKeyPosition is None or self.primaryKeyPosition < 0
        ):
            raise ValueError("primaryKeyPosition is required when primaryKey is True")
        return self


class SchemaObject(BaseModel):
    """Schema object definition."""

    name: str = Field(..., description="Object name")
    logicalType: Optional[str] = Field("object", description="Logical type")
    physicalName: Optional[str] = Field(None, description="Physical name")
    physicalType: Optional[str] = Field(None, description="Physical type")
    description: Optional[str] = Field(None, description="Object description")
    businessName: Optional[str] = Field(None, description="Business name")
    dataGranularityDescription: Optional[str] = Field(
        None, description="Data granularity"
    )
    properties: Optional[List[SchemaProperty]] = Field(
        None, description="Object properties"
    )
    tags: Optional[List[str]] = Field(None, description="Object tags")
    customProperties: Optional[List[CustomProperty]] = Field(
        None, description="Custom properties"
    )
    quality: Optional[List[DataQuality]] = Field(None, description="Quality checks")


class Server(BaseModel):
    """Server definition."""

    server: str = Field(..., description="Server identifier")
    type: ServerTypeEnum = Field(..., description="Server type")
    description: Optional[str] = Field(None, description="Server description")
    environment: Optional[str] = Field(None, description="Server environment")
    roles: Optional[List[Role]] = Field(None, description="Server roles")
    customProperties: Optional[List[CustomProperty]] = Field(
        None, description="Custom properties"
    )

    # Server-specific fields (simplified - in reality these would be conditional)
    location: Optional[str] = Field(None, description="Server location/URL")
    host: Optional[str] = Field(None, description="Server host")
    port: Optional[int] = Field(None, description="Server port")
    database: Optional[str] = Field(None, description="Database name")
    schema: Optional[str] = Field(None, description="Schema name")
    project: Optional[str] = Field(None, description="Project name")
    catalog: Optional[str] = Field(None, description="Catalog name")
    format: Optional[str] = Field(None, description="Data format")


class Description(BaseModel):
    """Dataset description."""

    usage: Optional[str] = Field(None, description="Intended usage")
    purpose: Optional[str] = Field(None, description="Dataset purpose")
    limitations: Optional[str] = Field(None, description="Dataset limitations")
    authoritativeDefinitions: Optional[List[AuthoritativeDefinition]] = Field(
        None, description="Authoritative definitions"
    )
    customProperties: Optional[List[CustomProperty]] = Field(
        None, description="Custom properties"
    )


class ServiceLevelAgreementProperty(BaseModel):
    """SLA property definition."""

    property: str = Field(..., description="SLA property name")
    value: Union[str, int, float, bool, None] = Field(
        ..., description="Agreement value"
    )
    unit: Optional[str] = Field(None, description="Value unit")
    element: Optional[str] = Field(None, description="Element to check")
    driver: Optional[str] = Field(None, description="SLA importance driver")


class ODCSDataContract(BaseModel):
    """Main ODCS Data Contract model."""

    # Required fields
    version: str = Field(..., description="Contract version")
    kind: KindEnum = Field(KindEnum.DATA_CONTRACT, description="Contract kind")
    apiVersion: ApiVersionEnum = Field(..., description="ODCS API version")
    id: str = Field(..., description="Unique identifier")
    status: str = Field(..., description="Contract status")

    # Optional fields
    name: Optional[str] = Field(None, description="Contract name")
    tenant: Optional[str] = Field(None, description="Associated tenant")
    tags: Optional[List[str]] = Field(None, description="Contract tags")
    servers: Optional[List[Server]] = Field(None, description="Data servers")
    dataProduct: Optional[str] = Field(None, description="Data product name")
    description: Optional[Description] = Field(None, description="Dataset description")
    domain: Optional[str] = Field(None, description="Logical data domain")
    schema: Optional[List[SchemaObject]] = Field(None, description="Schema objects")
    support: Optional[List[SupportItem]] = Field(None, description="Support channels")
    price: Optional[Pricing] = Field(None, description="Pricing information")
    team: Optional[List[Team]] = Field(None, description="Team members")
    roles: Optional[List[Role]] = Field(None, description="Access roles")
    slaDefaultElement: Optional[str] = Field(None, description="Default SLA element")
    slaProperties: Optional[List[ServiceLevelAgreementProperty]] = Field(
        None, description="SLA properties"
    )
    authoritativeDefinitions: Optional[List[AuthoritativeDefinition]] = Field(
        None, description="Authoritative definitions"
    )
    customProperties: Optional[List[CustomProperty]] = Field(
        None, description="Custom properties"
    )
    contractCreatedTs: Optional[datetime] = Field(
        None, description="Contract creation timestamp"
    )

    @field_validator("id", "version", "status")
    @classmethod
    def validate_non_empty_string(cls, v: str) -> str:
        """Validate that required string fields are not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        validate_assignment = True
        extra = "forbid"
