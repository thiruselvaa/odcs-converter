# CLI Reference - ODCS Converter

A comprehensive guide to the ODCS Converter command-line interface with modern Typer + Rich integration.

## Overview

The ODCS Converter CLI provides a beautiful, type-safe, and user-friendly interface for converting between ODCS (Open Data Contract Standard) and Excel formats. Built with Typer and Rich, it offers:

- 🎨 **Beautiful terminal output** with colors, tables, and progress bars
- ⚡ **Type-safe commands** with automatic validation
- 🔍 **Smart format detection** based on file extensions
- 🧪 **Dry-run mode** for previewing operations
- 📊 **Real-time progress tracking** during conversions
- ⚙️ **Configuration support** for Excel styling

## Installation

```bash
# Install via pip
pip install odcs-converter

# Or using uv (recommended - ultra fast!)
uv pip install odcs-converter
```

## Basic Usage

```bash
# Show all available commands
odcs-converter --help

# Get version information
odcs-converter version

# Show supported file formats
odcs-converter formats
```

## Command Structure

The CLI follows a modern command structure with subcommands:

```
odcs-converter [GLOBAL-OPTIONS] COMMAND [COMMAND-OPTIONS] [ARGUMENTS]
```

## Global Options

Available for all commands:

- `--help`: Show help message and exit

## Commands

### `convert` - Smart Bidirectional Conversion

Auto-detects conversion direction based on file extensions.

```bash
odcs-converter convert INPUT OUTPUT [OPTIONS]
```

**Arguments:**
- `INPUT`: Input file path or URL (required)
- `OUTPUT`: Output file path (required)

**Options:**
- `--format, -f {json,yaml,excel}`: Force output format (overrides auto-detection)
- `--config, -c PATH`: Configuration file for Excel styling
- `--validate, --check`: Validate ODCS schema compliance (for JSON/YAML output)
- `--verbose, -v`: Enable detailed progress logging
- `--quiet, -q`: Suppress all output except errors
- `--no-banner`: Skip application banner
- `--show-formats`: Show supported formats and exit
- `--dry-run`: Preview conversion without executing

**Examples:**

```bash
# ODCS to Excel (auto-detected)
odcs-converter convert contract.json output.xlsx
odcs-converter convert contract.yaml sales_contract.xlsx --verbose

# Excel to ODCS (auto-detected)
odcs-converter convert data.xlsx contract.json --validate
odcs-converter convert workbook.xlsx contract.yaml

# Remote URL to Excel
odcs-converter convert https://example.com/contract.json local_copy.xlsx

# With configuration
odcs-converter convert contract.json styled_output.xlsx --config custom_style.json

# Dry run (preview only)
odcs-converter convert contract.json output.xlsx --dry-run
```

### `to-excel` - ODCS to Excel Conversion

Converts ODCS contracts (JSON/YAML) to Excel workbooks with 15 comprehensive worksheets.

```bash
odcs-converter to-excel INPUT_FILE OUTPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE`: ODCS input file (JSON/YAML) - must exist
- `OUTPUT_FILE`: Excel output file (.xlsx)

**Options:**
- `--config, -c PATH`: Configuration file for Excel styling
- `--verbose, -v`: Verbose output with detailed progress
- `--quiet, -q`: Suppress output except errors

**Features:**
- Creates 15 comprehensive Excel worksheets
- Supports all ODCS v3.0.2 fields including advanced features
- Handles logical type options, quality rules, and transform documentation
- Customizable styling via configuration files

**Examples:**

```bash
# Basic conversion
odcs-converter to-excel contract.json sales_data.xlsx

# With styling configuration
odcs-converter to-excel contract.yaml report.xlsx --config corporate_style.json

# Verbose mode for debugging
odcs-converter to-excel complex_contract.json debug_output.xlsx --verbose

# Quiet mode for scripts
odcs-converter to-excel contract.json automated_output.xlsx --quiet
```

### `to-odcs` - Excel to ODCS Conversion

Converts Excel workbooks back to ODCS format (JSON/YAML) with complete field reconstruction.

```bash
odcs-converter to-odcs EXCEL_FILE OUTPUT_FILE [OPTIONS]
```

**Arguments:**
- `EXCEL_FILE`: Excel input file (.xlsx, .xls) - must exist
- `OUTPUT_FILE`: ODCS output file (.json, .yaml, .yml)

**Options:**
- `--format, -f {json,yaml}`: Output format (auto-detected from extension if not specified)
- `--validate, --check`: Validate against ODCS v3.0.2 schema after conversion
- `--verbose, -v`: Verbose output with parsing details
- `--quiet, -q`: Suppress output except errors

**Features:**
- Reconstructs complete ODCS structure from Excel worksheets
- Handles complex nested data and arrays
- Type-safe parsing with proper null handling
- Optional schema validation
- Supports both JSON and YAML output

**Examples:**

```bash
# Basic conversion (format auto-detected)
odcs-converter to-odcs data.xlsx contract.json
odcs-converter to-odcs workbook.xlsx contract.yaml

# Explicit format specification
odcs-converter to-odcs data.xlsx output.json --format json
odcs-converter to-odcs data.xlsx output.yaml --format yaml

# With validation
odcs-converter to-odcs data.xlsx validated_contract.json --validate

# Verbose parsing for debugging
odcs-converter to-odcs complex_data.xlsx debug_contract.yaml --verbose --validate
```

### `version` - Version Information

Shows version and system information.

```bash
odcs-converter version [OPTIONS]
```

**Options:**
- `--verbose, -v`: Show detailed version and system information

**Examples:**

```bash
# Basic version info
odcs-converter version

# Detailed system information
odcs-converter version --verbose
```

**Output Example:**
```
╭─────────────────────────────────────╮
│ ODCS Converter v0.2.0               │
│ Complete ODCS v3.0.2 Implementation │
╰─────────────────────────────────────╯

# With --verbose:
              System Information
  Component      Version
 ─────────────────────────────────────────────
  Python         3.11.11
  Platform       macOS-15.6.1-arm64-arm-64bit
  Architecture   arm64

╭───────────────────────── Features ─────────────────────────╮
│ ✅ 100% ODCS v3.0.2 specification coverage                │
│ 📊 15 comprehensive Excel worksheets                       │
│ 🔄 Full bidirectional conversion                          │
│ 🎯 Advanced quality rules and operators                   │
│ 🔧 Logical type options and constraints                   │
│ 📈 Transform documentation and lineage                    │
│ 🛡️  Enterprise-grade validation                          │
╰────────────────────────────────────────────────────────────╯
```

### `formats` - Show Supported Formats

Displays all supported file formats in a beautiful table.

```bash
odcs-converter formats
```

**Output Example:**
```
                        Supported File Formats
╭────────────┬───────────────────┬────────────────────────────────────╮
│ Format     │ Extensions        │ Description                        │
├────────────┼───────────────────┼────────────────────────────────────┤
│ ODCS JSON  │ .json             │ JSON format ODCS contracts         │
│ ODCS YAML  │ .yaml, .yml       │ YAML format ODCS contracts         │
│ Excel      │ .xlsx, .xls       │ Excel workbooks with 15 worksheets │
│ Remote URL │ http://, https:// │ Remote ODCS contracts              │
╰────────────┴───────────────────┴────────────────────────────────────╯
```

### `help` - Comprehensive Help

Shows detailed help information with examples and usage patterns.

```bash
odcs-converter help
```

Displays comprehensive help including:
- Overview and key features
- Command descriptions
- Common options
- Practical examples
- Support information

## File Format Auto-Detection

The CLI automatically detects input and output formats based on file extensions:

### Input Formats
- `.json` → ODCS JSON
- `.yaml`, `.yml` → ODCS YAML
- `.xlsx`, `.xls` → Excel workbook
- `http://`, `https://` → Remote ODCS contract

### Output Formats
- `.json` → ODCS JSON
- `.yaml`, `.yml` → ODCS YAML
- `.xlsx` → Excel workbook

## Configuration Files

Excel styling can be customized using JSON configuration files:

```json
{
  "header_font": {"bold": true, "color": "FFFFFF"},
  "header_fill": {
    "start_color": "4472C4",
    "end_color": "4472C4", 
    "fill_type": "solid"
  },
  "cell_font": {"name": "Calibri", "size": 11}
}
```

Use with `--config` option:
```bash
odcs-converter to-excel contract.json output.xlsx --config style.json
```

## Progress and Feedback

### Progress Bars

During conversions, Rich progress bars show:
- Current operation (Loading, Converting, Saving)
- Progress percentage
- Time elapsed
- Spinner animations

### Verbose Mode

Use `--verbose` for detailed logging:
- File information and validation
- Processing steps
- Performance metrics
- Conversion summaries

### Quiet Mode

Use `--quiet` for minimal output:
- Suppresses banners and progress bars
- Shows only errors and critical messages
- Ideal for automation and scripts

## Dry Run Mode

Preview operations without making changes:

```bash
odcs-converter convert contract.json output.xlsx --dry-run
```

Shows:
- Planned conversion steps
- Input/output file information
- Format detection results
- No files are created or modified

## Validation

ODCS schema validation ensures compliance with the v3.0.2 specification:

```bash
# Validate during Excel to ODCS conversion
odcs-converter to-odcs data.xlsx contract.json --validate

# Also works with convert command
odcs-converter convert data.xlsx contract.yaml --validate
```

Validation includes:
- Required field checking
- Data type validation
- Enum value verification
- Structure compliance

## Error Handling

The CLI provides clear error messages for common issues:

### File Not Found
```
❌ Error: Input file not found: contract.json
```

### Invalid Format
```
❌ Error: Unsupported input file type: document.pdf
```

### Conversion Errors
```
❌ Conversion failed: Invalid ODCS structure - missing required field 'apiVersion'
```

### Validation Errors
```
⚠️  ODCS schema validation found issues:
- Field 'status' is required
- Invalid enum value for 'kind': expected 'DataContract'
```

## Examples

### Basic Conversions

```bash
# ODCS JSON to Excel
odcs-converter to-excel sales_contract.json sales_report.xlsx

# Excel to ODCS YAML
odcs-converter to-odcs data.xlsx contract.yaml --validate

# Remote contract to local Excel
odcs-converter convert https://api.example.com/contract.json local_copy.xlsx
```

### Advanced Usage

```bash
# Styled Excel output with verbose logging
odcs-converter to-excel contract.json report.xlsx \
  --config corporate_style.json \
  --verbose

# Validated conversion with specific format
odcs-converter to-odcs complex_data.xlsx validated_contract.json \
  --format json \
  --validate \
  --verbose

# Preview complex conversion
odcs-converter convert large_contract.yaml massive_report.xlsx \
  --dry-run \
  --verbose
```

### Automation and Scripting

```bash
# Quiet mode for scripts
odcs-converter convert "$INPUT_FILE" "$OUTPUT_FILE" --quiet

# Batch processing with error handling
for file in *.json; do
  if odcs-converter to-excel "$file" "${file%.json}.xlsx" --quiet; then
    echo "✅ Converted: $file"
  else
    echo "❌ Failed: $file"
  fi
done
```

## Performance

### Optimization Tips

1. **Use `--quiet` for bulk operations** to reduce output overhead
2. **Skip validation** during development for faster iterations
3. **Use `--dry-run`** to verify operations before processing large files
4. **Monitor with `--verbose`** to identify bottlenecks

### Typical Performance

- Small contracts (< 50 properties): < 5 seconds
- Medium contracts (50-200 properties): < 15 seconds  
- Large contracts (200-500 properties): < 30 seconds
- Complex contracts (500+ properties): 30-60 seconds

## Integration

### CI/CD Pipeline Example

```yaml
# GitHub Actions example
- name: Validate ODCS Contracts
  run: |
    for contract in contracts/*.xlsx; do
      odcs-converter to-odcs "$contract" "temp.json" --validate --quiet
    done
```

### Docker Usage

```bash
# Using Docker
docker run -v $(pwd):/data thiruselvaa/odcs-converter \
  odcs-converter convert /data/contract.json /data/output.xlsx
```

## Troubleshooting

### Common Issues

1. **File permissions**: Ensure read access to input files and write access to output directories
2. **Path issues**: Use absolute paths or ensure files exist in current directory
3. **Format detection**: Use `--format` to override auto-detection if needed
4. **Memory**: Large contracts may require more memory; monitor system resources

### Debug Mode

Use verbose mode for debugging:

```bash
odcs-converter convert contract.json output.xlsx --verbose --dry-run
```

### Getting Help

1. **Built-in help**: `odcs-converter --help` or `odcs-converter COMMAND --help`
2. **Comprehensive guide**: `odcs-converter help`
3. **Format reference**: `odcs-converter formats`
4. **GitHub Issues**: [Report bugs and feature requests](https://github.com/thiruselvaa/odcs-converter/issues)

## What's New

### v0.2.0 - Modern CLI with Typer + Rich

- **🎨 Beautiful Interface**: Rich tables, progress bars, and colored output
- **⚡ Type Safety**: Typer-powered CLI with enum validation
- **🔍 Smart Detection**: Auto-detects formats from file extensions
- **🧪 Dry Run Mode**: Preview operations without making changes
- **📊 Enhanced Progress**: Real-time progress tracking with spinners
- **⚙️ Configuration**: JSON config files for Excel styling
- **🎯 Better Validation**: Comprehensive ODCS schema validation
- **🔧 Flexible Options**: Verbose, quiet, and no-banner modes

---

**💡 Tip**: Use `odcs-converter help` for a comprehensive guide with examples and usage patterns!