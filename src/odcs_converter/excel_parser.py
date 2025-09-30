"""Excel to ODCS parser - Convert Excel files back to ODCS JSON/YAML format."""

import logging
from pathlib import Path
from typing import Any, Dict, Union
from datetime import datetime

import pandas as pd
from openpyxl import load_workbook

from .models import ODCSDataContract

logger = logging.getLogger(__name__)


class ExcelToODCSParser:
    """Parse Excel files and convert them back to ODCS format."""

    def __init__(self):
        """Initialize the Excel parser."""
        self.workbook = None
        self.worksheets = {}

    def parse_from_file(self, excel_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse Excel file and return ODCS dictionary.

        Args:
            excel_path: Path to Excel file

        Returns:
            Dictionary containing ODCS data

        Raises:
            FileNotFoundError: If Excel file doesn't exist
            ValueError: If Excel file format is invalid
        """
        excel_path = Path(excel_path)
        if not excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {excel_path}")

        try:
            self.workbook = load_workbook(excel_path, read_only=True)
            self._load_all_worksheets()

            odcs_data = self._parse_odcs_data()

            logger.info(f"Successfully parsed Excel file: {excel_path}")
            return odcs_data

        except Exception as e:
            logger.error(f"Failed to parse Excel file {excel_path}: {e}")
            raise ValueError(f"Invalid Excel file format: {e}")
        finally:
            if self.workbook:
                self.workbook.close()

    def _load_all_worksheets(self) -> None:
        """Load all worksheets into pandas DataFrames."""
        self.worksheets = {}
        for sheet_name in self.workbook.sheetnames:
            try:
                # Read worksheet into DataFrame, treating first row as headers
                # Use openpyxl engine and get data directly from workbook
                sheet = self.workbook[sheet_name]
                data = []
                headers = []

                # Get headers from first row
                first_row = next(
                    sheet.iter_rows(min_row=1, max_row=1, values_only=True), None
                )
                if first_row:
                    headers = [cell for cell in first_row if cell is not None]

                # Get data from subsequent rows
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    if any(cell is not None for cell in row):  # Skip empty rows
                        row_data = list(row[: len(headers)] if headers else row)
                        data.append(row_data)

                # Create DataFrame
                if headers and data:
                    df = pd.DataFrame(data, columns=headers)
                elif headers:
                    df = pd.DataFrame(columns=headers)
                else:
                    df = pd.DataFrame()
                # Convert empty strings to None for better data handling
                df = df.where(df != "", None)
                self.worksheets[sheet_name] = df
                logger.debug(f"Loaded worksheet '{sheet_name}' with {len(df)} rows")
            except Exception as e:
                logger.warning(f"Could not load worksheet '{sheet_name}': {e}")

    def _parse_odcs_data(self) -> Dict[str, Any]:
        """Parse all worksheets and construct ODCS data structure."""
        odcs_data = {}

        # Parse each worksheet type
        odcs_data.update(self._parse_basic_information())
        odcs_data.update(self._parse_tags())
        odcs_data.update(self._parse_description())
        odcs_data.update(self._parse_servers())
        odcs_data.update(self._parse_schema())
        odcs_data.update(self._parse_support())
        odcs_data.update(self._parse_pricing())
        odcs_data.update(self._parse_team())
        odcs_data.update(self._parse_roles())
        odcs_data.update(self._parse_sla_properties())
        odcs_data.update(self._parse_authoritative_definitions())
        odcs_data.update(self._parse_custom_properties())

        # Remove None values and empty structures
        odcs_data = self._clean_data(odcs_data)

        return odcs_data

    def _parse_basic_information(self) -> Dict[str, Any]:
        """Parse Basic Information worksheet."""
        sheet_name = "Basic Information"
        if sheet_name not in self.worksheets:
            logger.warning(f"Worksheet '{sheet_name}' not found")
            return {}

        df = self.worksheets[sheet_name]
        if df.empty or "Field" not in df.columns or "Value" not in df.columns:
            return {}

        data = {}
        for _, row in df.iterrows():
            field = row.get("Field")
            value = row.get("Value")

            if field and value is not None:
                # Handle special field mappings
                if field == "contractCreatedTs" and value:
                    try:
                        # Try to parse datetime if it's a string
                        if isinstance(value, str):
                            data[field] = datetime.fromisoformat(
                                value.replace("Z", "+00:00")
                            ).isoformat()
                        else:
                            data[field] = value
                    except (ValueError, AttributeError):
                        data[field] = str(value)
                else:
                    data[field] = self._convert_value(value)

        return data

    def _parse_tags(self) -> Dict[str, Any]:
        """Parse Tags worksheet."""
        sheet_name = "Tags"
        if sheet_name not in self.worksheets:
            return {}

        df = self.worksheets[sheet_name]
        if df.empty or "Tag" not in df.columns:
            return {}

        tags = []
        for _, row in df.iterrows():
            tag = row.get("Tag")
            if tag:
                tags.append(str(tag))

        return {"tags": tags} if tags else {}

    def _parse_description(self) -> Dict[str, Any]:
        """Parse Description worksheet."""
        sheet_name = "Description"
        if sheet_name not in self.worksheets:
            return {}

        df = self.worksheets[sheet_name]
        if df.empty or "Field" not in df.columns or "Value" not in df.columns:
            return {}

        description = {}
        for _, row in df.iterrows():
            field = row.get("Field")
            value = row.get("Value")

            if field and value is not None:
                description[field] = str(value)

        return {"description": description} if description else {}

    def _parse_servers(self) -> Dict[str, Any]:
        """Parse Servers worksheet."""
        sheet_name = "Servers"
        if sheet_name not in self.worksheets:
            return {}

        df = self.worksheets[sheet_name]
        if df.empty:
            return {}

        servers = []
        for _, row in df.iterrows():
            server = {}

            # Map common server fields
            field_mappings = {
                "Server": "server",
                "Type": "type",
                "Description": "description",
                "Environment": "environment",
                "Location": "location",
                "Host": "host",
                "Port": "port",
                "Database": "database",
                "Schema": "schema",
                "Project": "project",
                "Catalog": "catalog",
                "Format": "format",
            }

            for excel_field, odcs_field in field_mappings.items():
                value = row.get(excel_field)
                if value is not None and value != "":
                    if odcs_field == "port":
                        try:
                            server[odcs_field] = int(value)
                        except (ValueError, TypeError):
                            server[odcs_field] = value
                    else:
                        server[odcs_field] = str(value)

            if server:  # Only add if we have some data
                servers.append(server)

        return {"servers": servers} if servers else {}

    def _parse_schema(self) -> Dict[str, Any]:
        """Parse Schema worksheet."""
        sheet_name = "Schema"
        if sheet_name not in self.worksheets:
            return {}

        df = self.worksheets[sheet_name]
        if df.empty:
            return {}

        schema_objects = []
        for _, row in df.iterrows():
            schema_obj = {}

            # Map schema object fields
            field_mappings = {
                "Object Name": "name",
                "Physical Name": "physicalName",
                "Logical Type": "logicalType",
                "Physical Type": "physicalType",
                "Description": "description",
                "Business Name": "businessName",
            }

            for excel_field, odcs_field in field_mappings.items():
                value = row.get(excel_field)
                if value is not None and value != "":
                    schema_obj[odcs_field] = str(value)

            if schema_obj:  # Only add if we have some data
                schema_objects.append(schema_obj)

        return {"schema": schema_objects} if schema_objects else {}

    def _parse_support(self) -> Dict[str, Any]:
        """Parse Support worksheet."""
        sheet_name = "Support"
        if sheet_name not in self.worksheets:
            return {}

        df = self.worksheets[sheet_name]
        if df.empty:
            return {}

        support_items = []
        for _, row in df.iterrows():
            support_item = {}

            field_mappings = {
                "Channel": "channel",
                "URL": "url",
                "Description": "description",
                "Tool": "tool",
                "Scope": "scope",
            }

            for excel_field, odcs_field in field_mappings.items():
                value = row.get(excel_field)
                if value is not None and value != "":
                    support_item[odcs_field] = str(value)

            if support_item:
                support_items.append(support_item)

        return {"support": support_items} if support_items else {}

    def _parse_pricing(self) -> Dict[str, Any]:
        """Parse Pricing worksheet."""
        sheet_name = "Pricing"
        if sheet_name not in self.worksheets:
            return {}

        df = self.worksheets[sheet_name]
        if df.empty or "Field" not in df.columns or "Value" not in df.columns:
            return {}

        pricing = {}
        for _, row in df.iterrows():
            field = row.get("Field")
            value = row.get("Value")

            if field and value is not None:
                if field == "priceAmount":
                    try:
                        pricing[field] = float(value)
                    except (ValueError, TypeError):
                        pricing[field] = value
                else:
                    pricing[field] = str(value)

        return {"price": pricing} if pricing else {}

    def _parse_team(self) -> Dict[str, Any]:
        """Parse Team worksheet."""
        sheet_name = "Team"
        if sheet_name not in self.worksheets:
            return {}

        df = self.worksheets[sheet_name]
        if df.empty:
            return {}

        team_members = []
        for _, row in df.iterrows():
            member = {}

            field_mappings = {
                "Username": "username",
                "Name": "name",
                "Role": "role",
                "Description": "description",
                "Date In": "dateIn",
                "Date Out": "dateOut",
            }

            for excel_field, odcs_field in field_mappings.items():
                value = row.get(excel_field)
                if value is not None and value != "":
                    member[odcs_field] = str(value)

            if member:
                team_members.append(member)

        return {"team": team_members} if team_members else {}

    def _parse_roles(self) -> Dict[str, Any]:
        """Parse Roles worksheet."""
        sheet_name = "Roles"
        if sheet_name not in self.worksheets:
            return {}

        df = self.worksheets[sheet_name]
        if df.empty:
            return {}

        roles = []
        for _, row in df.iterrows():
            role = {}

            field_mappings = {
                "Role": "role",
                "Description": "description",
                "Access": "access",
                "First Level Approvers": "firstLevelApprovers",
                "Second Level Approvers": "secondLevelApprovers",
            }

            for excel_field, odcs_field in field_mappings.items():
                value = row.get(excel_field)
                if value is not None and value != "":
                    role[odcs_field] = str(value)

            if role:
                roles.append(role)

        return {"roles": roles} if roles else {}

    def _parse_sla_properties(self) -> Dict[str, Any]:
        """Parse SLA Properties worksheet."""
        sheet_name = "SLA Properties"
        if sheet_name not in self.worksheets:
            return {}

        df = self.worksheets[sheet_name]
        if df.empty:
            return {}

        sla_properties = []
        for _, row in df.iterrows():
            sla_prop = {}

            field_mappings = {
                "Property": "property",
                "Value": "value",
                "Unit": "unit",
                "Element": "element",
                "Driver": "driver",
            }

            for excel_field, odcs_field in field_mappings.items():
                value = row.get(excel_field)
                if value is not None and value != "":
                    if odcs_field == "value":
                        # Try to convert to appropriate type
                        sla_prop[odcs_field] = self._convert_value(value)
                    else:
                        sla_prop[odcs_field] = str(value)

            if sla_prop:
                sla_properties.append(sla_prop)

        return {"slaProperties": sla_properties} if sla_properties else {}

    def _parse_authoritative_definitions(self) -> Dict[str, Any]:
        """Parse Authoritative Definitions worksheet."""
        sheet_name = "Authoritative Definitions"
        if sheet_name not in self.worksheets:
            return {}

        df = self.worksheets[sheet_name]
        if df.empty:
            return {}

        definitions = []
        for _, row in df.iterrows():
            definition = {}

            url = row.get("URL")
            type_val = row.get("Type")

            if url and url != "":
                definition["url"] = str(url)
            if type_val and type_val != "":
                definition["type"] = str(type_val)

            if definition:
                definitions.append(definition)

        return {"authoritativeDefinitions": definitions} if definitions else {}

    def _parse_custom_properties(self) -> Dict[str, Any]:
        """Parse Custom Properties worksheet."""
        sheet_name = "Custom Properties"
        if sheet_name not in self.worksheets:
            return {}

        df = self.worksheets[sheet_name]
        if df.empty or "Property" not in df.columns or "Value" not in df.columns:
            return {}

        custom_properties = []
        for _, row in df.iterrows():
            prop = row.get("Property")
            value = row.get("Value")

            if prop and value is not None:
                custom_properties.append(
                    {"property": str(prop), "value": self._convert_value(value)}
                )

        return {"customProperties": custom_properties} if custom_properties else {}

    def _convert_value(self, value: Any) -> Any:
        """Convert Excel value to appropriate Python type."""
        if value is None or value == "":
            return None

        # If it's already a basic type, return as-is
        if isinstance(value, (bool, int, float)):
            return value

        value_str = str(value).strip()

        # Try boolean
        if value_str.lower() in ("true", "false"):
            return value_str.lower() == "true"

        # Try integer
        try:
            if "." not in value_str and value_str.isdigit():
                return int(value_str)
        except (ValueError, AttributeError):
            pass

        # Try float
        try:
            if "." in value_str:
                return float(value_str)
        except (ValueError, AttributeError):
            pass

        # Return as string
        return value_str

    def _clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove None values and empty structures from data."""
        cleaned = {}

        for key, value in data.items():
            if value is None:
                continue
            elif isinstance(value, dict):
                cleaned_dict = self._clean_data(value)
                if cleaned_dict:  # Only add non-empty dicts
                    cleaned[key] = cleaned_dict
            elif isinstance(value, list):
                cleaned_list = []
                for item in value:
                    if isinstance(item, dict):
                        cleaned_item = self._clean_data(item)
                        if cleaned_item:
                            cleaned_list.append(cleaned_item)
                    elif item is not None and item != "":
                        cleaned_list.append(item)
                if cleaned_list:  # Only add non-empty lists
                    cleaned[key] = cleaned_list
            elif value != "" and value is not None:
                cleaned[key] = value

        return cleaned

    def validate_odcs_data(self, data: Dict[str, Any]) -> bool:
        """Validate parsed data against ODCS schema.

        Args:
            data: Parsed ODCS data dictionary

        Returns:
            True if valid, False otherwise
        """
        try:
            ODCSDataContract(**data)
            logger.info("ODCS data validation successful")
            return True
        except Exception as e:
            logger.warning(f"ODCS data validation failed: {e}")
            return False
