# ODCS Template Generation - Quick Reference

## Command Syntax

```bash
odcs-converter generate-template [OUTPUT] [OPTIONS]
```

---

## Template Types

| Type | Worksheets | Fields | Use Case |
|------|-----------|--------|----------|
| `minimal` | 3 | ~10 | Learning, prototypes |
| `required` | 4 | ~20 | Production, standard use |
| `full` | 16 | ~100 | Enterprise, complex needs |

---

## Common Commands

```bash
# Generate minimal template
odcs-converter generate-template minimal.xlsx --type minimal

# Generate required fields template
odcs-converter generate-template required.xlsx --type required

# Generate full template
odcs-converter generate-template full.xlsx --type full

# Generate without examples
odcs-converter generate-template clean.xlsx --no-examples

# Generate with verbose output
odcs-converter generate-template template.xlsx -v
```

---

## Color Coding

| Color | Meaning | Required? |
|-------|---------|-----------|
| 🔴 **RED** | Required field | ✅ Must fill |
| 🔵 **BLUE** | Optional field | ⬜ Can skip |

---

## Workflow

```
1. Generate Template
   ↓
2. Open in Excel/Sheets
   ↓
3. Read Instructions Sheet
   ↓
4. Fill Required Fields (RED)
   ↓
5. Fill Optional Fields (BLUE)
   ↓
6. Delete Example Rows
   ↓
7. Save File
   ↓
8. Convert to ODCS
   ↓
9. Validate Output
```

---

## Required Fields by Worksheet

### Basic Information
- `version` - Contract version (e.g., "1.0.0")
- `kind` - Always "DataContract"
- `apiVersion` - ODCS version (e.g., "v3.0.2")
- `id` - Unique identifier
- `name` - Contract name

### Servers
- `server` - Server identifier
- `type` - Server type (snowflake, bigquery, etc.)

### Schema
- `name` - Schema/table name
- `logicalType` - Usually "object"

### Schema Properties
- `schemaName` - Parent schema name
- `name` - Column/property name
- `logicalType` - Data type (string, integer, date, etc.)

---

## Conversion Commands

```bash
# Dry run (validate without saving)
odcs-converter excel-to-odcs template.xlsx --dry-run

# Convert to JSON (default)
odcs-converter excel-to-odcs template.xlsx

# Convert to YAML
odcs-converter excel-to-odcs template.xlsx --format yaml

# Specify output location
odcs-converter excel-to-odcs template.xlsx -o output/contract.json

# Verbose validation
odcs-converter excel-to-odcs template.xlsx --dry-run -v
```

---

## Data Type Formats

| Type | Format | Example |
|------|--------|---------|
| **string** | Any text | "user_id" |
| **integer** | Whole numbers | 42 |
| **number** | Decimals | 3.14 |
| **date** | ISO 8601 | "2024-01-15T10:30:00Z" |
| **boolean** | true/false | true, false, 1, 0 |
| **array** | Comma-separated | "tag1,tag2,tag3" |

---

## Server Types

Common server types:
- `snowflake`
- `bigquery`
- `postgresql`
- `mysql`
- `redshift`
- `databricks`
- `s3`
- `api`

See full list in template examples.

---

## Logical Types

- `string` - Text values
- `integer` - Whole numbers
- `number` - Decimal numbers
- `date` - Dates/timestamps
- `boolean` - True/false
- `object` - Nested structures
- `array` - Lists

---

## Quality Dimensions

- `uniqueness` / `uq` - No duplicates
- `completeness` / `cp` - No nulls
- `accuracy` / `ac` - Correct values
- `consistency` / `cs` - Cross-field consistency
- `timeliness` / `tm` - Data freshness
- `conformity` / `cf` - Format compliance
- `coverage` / `cv` - Data coverage

---

## Troubleshooting

### Template won't generate
```bash
# Check permissions
ls -la /output/path/

# Try different location
odcs-converter generate-template ~/Downloads/template.xlsx -t full
```

### Conversion fails
```bash
# Validate with dry-run
odcs-converter excel-to-odcs template.xlsx --dry-run -v

# Check required fields (RED headers)
# Verify data formats match examples
```

### Can't see comments
- Look for red triangle in cell corner
- Hover mouse over cell
- Excel: Review → Show All Comments

---

## Tips

✅ **DO**
- Read Instructions sheet first
- Fill RED headers completely
- Use example values as format guide
- Delete examples before converting
- Validate with `--dry-run` first
- Use consistent naming conventions

❌ **DON'T**
- Leave RED headers empty
- Modify header names
- Mix data formats in same column
- Keep example rows in final version
- Skip validation step

---

## Help Commands

```bash
# Template generation help
odcs-converter generate-template --help

# Conversion help
odcs-converter excel-to-odcs --help

# General help
odcs-converter --help

# Show all commands
odcs-converter help
```

---

## Examples

### Quick Prototype
```bash
odcs-converter generate-template proto.xlsx -t minimal
# Fill minimal fields
odcs-converter excel-to-odcs proto.xlsx -o proto.json
```

### Production Contract
```bash
odcs-converter generate-template prod.xlsx -t required
# Fill required + important optional fields
odcs-converter excel-to-odcs prod.xlsx --dry-run -v
odcs-converter excel-to-odcs prod.xlsx -o contracts/prod.json
```

### Enterprise Contract
```bash
odcs-converter generate-template enterprise.xlsx -t full
# Fill comprehensively
odcs-converter excel-to-odcs enterprise.xlsx --dry-run -v
odcs-converter excel-to-odcs enterprise.xlsx -o contracts/enterprise.yaml --format yaml
```

---

## Support

- Full Documentation: `docs/templates/TEMPLATE_GENERATION.md`
- CLI Help: `odcs-converter --help`
- Issues: GitHub Issues
- ODCS Spec: https://open-data-contract-standard.github.io/