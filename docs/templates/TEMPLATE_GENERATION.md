# ODCS Excel Template Generation

## Overview

The ODCS Converter CLI provides a powerful template generation feature that helps users create Excel templates for ODCS data contract configuration. These templates include clear field indicators, examples, and documentation to minimize errors and streamline the contract creation process.

## Features

### 🎨 Color-Coded Headers
- **🔴 RED headers**: Required fields that must be filled
- **🔵 BLUE headers**: Optional fields that can be left empty

### 📝 Built-in Documentation
- Comprehensive instructions sheet
- Cell comments with field explanations
- Example values for guidance
- Clear indication of data types and formats

### 📋 Three Template Types
1. **Minimal**: Essential required fields only
2. **Required**: All required fields plus common optional fields
3. **Full**: Complete coverage of all ODCS fields

---

## Quick Start

### Generate a Template

```bash
# Generate a minimal template
odcs-converter generate-template minimal_template.xlsx --type minimal

# Generate a full template with all fields
odcs-converter generate-template full_template.xlsx --type full

# Generate without example values
odcs-converter generate-template template.xlsx --type required --no-examples
```

### Fill Out the Template

1. Open the generated Excel file
2. Read the **📖 Instructions** sheet
3. Fill in your data (replace example rows)
4. Focus on RED headers (required fields) first
5. Optionally fill BLUE headers for additional details
6. Save your changes

### Convert to ODCS

```bash
# Convert your filled template to ODCS JSON
odcs-converter excel-to-odcs your_template.xlsx

# Convert to YAML format
odcs-converter excel-to-odcs your_template.xlsx --format yaml

# Specify output location
odcs-converter excel-to-odcs your_template.xlsx -o output/contract.json
```

---

## Template Types Comparison

### 1. Minimal Template

**Purpose**: Quick proof-of-concept or simple data contracts

**Worksheets Included**:
- Basic Information (5 fields)
- Schema (2 fields)
- Schema Properties (3 fields)

**Use Cases**:
- Rapid prototyping
- Simple data sources
- Initial contract drafts
- Learning the ODCS structure

**Example**:
```bash
odcs-converter generate-template minimal.xlsx --type minimal
```

### 2. Required Template

**Purpose**: Standard production data contracts

**Worksheets Included**:
- Basic Information (7 fields)
- Servers (3 fields)
- Schema (4 fields)
- Schema Properties (5 fields)

**Use Cases**:
- Production data contracts
- Standard data products
- Team collaborations
- Most common use cases

**Example**:
```bash
odcs-converter generate-template required.xlsx --type required
```

### 3. Full Template

**Purpose**: Comprehensive data contracts with maximum detail

**Worksheets Included** (15 total):
- Basic Information (11 fields)
- Tags
- Description
- Servers (12 fields)
- Schema (7 fields)
- Schema Properties (17 fields)
- Logical Type Options
- Quality Rules
- Support
- Pricing
- Team
- Roles
- SLA Properties
- Authoritative Definitions
- Custom Properties

**Use Cases**:
- Complex data products
- Regulatory compliance needs
- Data governance requirements
- Enterprise-grade contracts

**Example**:
```bash
odcs-converter generate-template full.xlsx --type full
```

---

## Worksheet Details

### Basic Information
Core metadata about the data contract.

**Required Fields**:
- `version`: Contract version (e.g., "1.0.0")
- `kind`: Must be "DataContract"
- `apiVersion`: ODCS API version (e.g., "v3.0.2")
- `id`: Unique identifier
- `name`: Human-readable name

**Optional Fields**:
- `tenant`: Organization/team name
- `status`: Contract status (active, draft, deprecated)
- `dataProduct`: Data product name
- `domain`: Business domain
- `slaDefaultElement`: Default SLA element
- `contractCreatedTs`: Creation timestamp

### Servers
Database/data source connection information.

**Required Fields**:
- `server`: Server identifier
- `type`: Server type (snowflake, bigquery, postgresql, etc.)

**Optional Fields** (type-specific):
- `description`, `environment`, `account`, `database`, `schema`, `warehouse`, `project`, `dataset`, `host`, `port`

### Schema
Dataset or table definitions.

**Required Fields**:
- `name`: Schema object name
- `logicalType`: Usually "object" for tables

**Optional Fields**:
- `physicalName`, `description`, `businessName`, `dataGranularityDescription`, `tags`

### Schema Properties
Column/field definitions within schema objects.

**Required Fields**:
- `schemaName`: Parent schema object name
- `name`: Property/column name
- `logicalType`: Data type (string, integer, date, etc.)

**Optional Fields**:
- `physicalType`, `description`, `required`, `primaryKey`, `primaryKeyPosition`, `classification`, `pii`, `examples`, `pattern`, `minLength`, `maxLength`, `minimum`, `maximum`, `tags`

### Quality Rules
Data quality validation rules.

**Fields**:
- `schemaName`: Schema object name
- `name`: Rule name
- `description`: Rule description
- `dimension`: Quality dimension (uniqueness, completeness, etc.)
- `type`: Rule type (library, custom)
- `rule`: Rule specification
- `mustBe`: Expected value
- `mustNotBe`: Disallowed value
- `severity`: error, warning, or info

### SLA Properties
Service Level Agreement specifications.

**Fields**:
- `property`: SLA property (availability, freshness, latency)
- `value`: SLA value
- `unit`: Measurement unit
- `element`: Target element
- `driver`: Driver (operational, regulatory)

---

## Field Indicators Guide

### Required vs Optional

| Indicator | Meaning | Action |
|-----------|---------|--------|
| 🔴 RED Header | **REQUIRED** | Must provide a value |
| 🔵 BLUE Header | **OPTIONAL** | Can leave empty |

### Data Type Indicators

Templates include help text for each field indicating:
- Expected data type
- Format requirements
- Example values
- Valid options (for enums)

### Cell Comments

Hover over header cells (look for red corner indicator) to see:
- Detailed field description
- Format specifications
- Usage guidelines

---

## Best Practices

### 1. Start with the Right Template Type

```bash
# Learning or prototyping → minimal
odcs-converter generate-template learning.xlsx --type minimal

# Production use → required
odcs-converter generate-template production.xlsx --type required

# Complex requirements → full
odcs-converter generate-template enterprise.xlsx --type full
```

### 2. Read Instructions First

Always review the **📖 Instructions** sheet before filling data. It contains:
- Color coding guide
- Field requirement summary
- Tips and best practices
- Links to documentation

### 3. Use Example Values as Guidelines

- Example rows show proper formatting
- Delete example rows before final conversion
- Copy format patterns for your data

### 4. Validate as You Go

```bash
# Dry-run to check for errors without saving
odcs-converter excel-to-odcs template.xlsx --dry-run

# Verbose mode for detailed validation
odcs-converter excel-to-odcs template.xlsx -v
```

### 5. Fill Required Fields First

1. Complete all RED header fields
2. Test conversion with minimal data
3. Add optional fields (BLUE headers) incrementally
4. Validate after each addition

### 6. Use Consistent Naming

- Schema names: `snake_case`
- Property names: `snake_case`
- IDs: `kebab-case`
- Business names: `Title Case`

---

## Common Use Cases

### Case 1: New Data Product

```bash
# 1. Generate full template
odcs-converter generate-template my-product.xlsx --type full

# 2. Fill in details (focus on required fields first)
# 3. Validate
odcs-converter excel-to-odcs my-product.xlsx --dry-run -v

# 4. Convert to ODCS
odcs-converter excel-to-odcs my-product.xlsx -o contracts/my-product.json
```

### Case 2: Quick Prototype

```bash
# 1. Generate minimal template
odcs-converter generate-template prototype.xlsx --type minimal

# 2. Fill essential fields only
# 3. Convert and iterate
odcs-converter excel-to-odcs prototype.xlsx -o prototype.json
```

### Case 3: Team Template

```bash
# 1. Generate template without examples (cleaner for sharing)
odcs-converter generate-template team-template.xlsx --type required --no-examples

# 2. Add team-specific instructions (edit Instructions sheet)
# 3. Share with team members
# 4. Each team member fills and converts
```

### Case 4: Migration from Existing System

```bash
# 1. Generate full template to see all available fields
odcs-converter generate-template migration.xlsx --type full

# 2. Map existing fields to ODCS structure
# 3. Import/copy data from existing system
# 4. Validate and convert
odcs-converter excel-to-odcs migration.xlsx -v
```

---

## Troubleshooting

### Issue: Template Generation Fails

```bash
# Check permissions
ls -la /path/to/output/

# Use verbose mode
odcs-converter generate-template template.xlsx --type full -v

# Try different output location
odcs-converter generate-template ~/Downloads/template.xlsx --type full
```

### Issue: Conversion Errors After Filling

**Check Required Fields**:
- All RED headers must have values
- No empty cells in required columns

**Validate Field Formats**:
- Dates: ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
- Booleans: true/false (case-insensitive)
- Numbers: No text or special characters
- URLs: Valid HTTP/HTTPS URLs

**Use Dry Run**:
```bash
odcs-converter excel-to-odcs template.xlsx --dry-run -v
```

### Issue: Missing Worksheets

Templates create only relevant worksheets based on type:
- **Minimal**: 3 worksheets
- **Required**: 4 worksheets
- **Full**: 16 worksheets (15 data + 1 instructions)

### Issue: Cannot See Cell Comments

- Look for small red triangle in cell corner
- Hover over the cell to view comment
- In Excel: Review → Show All Comments

---

## Advanced Features

### Custom Template Creation

While the CLI doesn't support custom template creation directly, you can:

1. Generate a full template
2. Delete unwanted worksheets
3. Save as new template
4. Reuse for similar contracts

### Template Modification

You can modify generated templates:
- Add custom validation rules
- Add conditional formatting
- Add additional helper columns (will be ignored during conversion)
- Customize colors (keep header structure)

### Batch Template Generation

```bash
# Generate multiple templates
for type in minimal required full; do
  odcs-converter generate-template "template_${type}.xlsx" --type $type
done
```

---

## Integration with Workflow

### Version Control

```bash
# Generate template
odcs-converter generate-template contract.xlsx --type required

# Fill template (manual step)
# Convert to ODCS
odcs-converter excel-to-odcs contract.xlsx -o contract.json

# Commit both files
git add contract.xlsx contract.json
git commit -m "Add data contract for analytics pipeline"
```

### CI/CD Pipeline

```yaml
# Example GitHub Actions workflow
- name: Validate Data Contract
  run: |
    odcs-converter excel-to-odcs contract.xlsx --dry-run -v
    
- name: Convert to ODCS
  run: |
    odcs-converter excel-to-odcs contract.xlsx -o contract.json
    
- name: Validate ODCS
  run: |
    odcs-converter to-excel contract.json -o validated.xlsx
```

### Documentation Generation

Templates can serve as living documentation:
1. Generate template with examples
2. Don't delete example rows
3. Use as reference documentation
4. Share with stakeholders

---

## Command Reference

### generate-template

```bash
odcs-converter generate-template [OPTIONS] OUTPUT
```

**Arguments**:
- `OUTPUT`: Path to save the Excel template

**Options**:
- `--type, -t`: Template type (minimal, required, full) [default: full]
- `--no-examples`: Don't include example values
- `--verbose, -v`: Show detailed information
- `--quiet, -q`: Suppress output except errors
- `--env, --environment`: Logging environment

**Examples**:

```bash
# Basic usage
odcs-converter generate-template template.xlsx

# Minimal template
odcs-converter generate-template minimal.xlsx -t minimal

# Without examples
odcs-converter generate-template clean.xlsx --no-examples

# Verbose mode
odcs-converter generate-template template.xlsx -v

# Quiet mode (only errors)
odcs-converter generate-template template.xlsx -q
```

---

## FAQ

### Q: Which template type should I use?

**A**: 
- **Minimal**: For learning or simple contracts (< 5 fields)
- **Required**: For most production use cases (standard complexity)
- **Full**: For complex contracts needing all ODCS features

### Q: Can I modify the generated template?

**A**: Yes! You can:
- Add/remove worksheets
- Add helper columns (ignored during conversion)
- Modify examples
- Keep header structure and colors for clarity

### Q: What happens to example rows during conversion?

**A**: Example rows should be deleted before conversion. They're included only as formatting guides.

### Q: Can I create a template without examples?

**A**: Yes, use the `--no-examples` flag:
```bash
odcs-converter generate-template template.xlsx --no-examples
```

### Q: How do I know which fields are required?

**A**: Look for:
1. RED header background color
2. Cell comments (hover over headers)
3. Instructions sheet summary

### Q: Can I use the template with other tools?

**A**: Yes! The template is a standard Excel file and can be:
- Opened in Excel, Google Sheets, LibreOffice
- Programmatically populated with scripts
- Imported from databases or APIs

### Q: What ODCS versions are supported?

**A**: Templates support ODCS API versions:
- v3.0.2 (recommended)
- v3.0.1, v3.0.0
- v2.2.2, v2.2.1, v2.2.0

### Q: How do I report issues with templates?

**A**: Open an issue on GitHub with:
- Template type used
- Command executed
- Error message (use `-v` for details)
- Sample data (if possible)

---

## See Also

- [ODCS Specification](https://open-data-contract-standard.github.io/)
- [CLI Documentation](../CLI.md)
- [Excel to ODCS Conversion](../EXCEL_TO_ODCS.md)
- [Examples](../../examples/)