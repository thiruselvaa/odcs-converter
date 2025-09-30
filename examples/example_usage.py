#!/usr/bin/env python3
"""Example usage of ODCS Converter - Bidirectional conversion between ODCS and Excel."""

import json
from pathlib import Path
from odcs_converter import ODCSToExcelConverter, ExcelToODCSParser, YAMLConverter


def demo_odcs_to_excel():
    """Demonstrate ODCS to Excel conversion."""
    print("🔄 ODCS → Excel Conversion")
    print("=" * 50)

    # Initialize the converter
    converter = ODCSToExcelConverter()

    # Get paths
    current_dir = Path(__file__).parent
    input_file = current_dir / "example_contract.json"
    output_file = current_dir / "example_output.xlsx"

    print(f"📖 Reading ODCS contract from: {input_file}")
    print(f"📊 Generating Excel file: {output_file}")

    try:
        # Generate Excel from JSON file
        converter.generate_from_file(input_file, output_file)
        print(f"✅ Successfully generated Excel file: {output_file}")

        # You can also generate from a URL
        # converter.generate_from_url("https://example.com/contract.json", "output.xlsx")

        # Or from a dictionary
        # data = {...}  # Your ODCS data
        # converter.generate_from_dict(data, "output.xlsx")

        return output_file

    except Exception as e:
        print(f"❌ Error generating Excel file: {e}")
        return None


def demo_excel_to_odcs(excel_file):
    """Demonstrate Excel to ODCS conversion."""
    print("\n🔄 Excel → ODCS Conversion")
    print("=" * 50)

    if not excel_file or not Path(excel_file).exists():
        print("❌ No Excel file available for conversion")
        return

    # Initialize the parser
    parser = ExcelToODCSParser()

    # Get output paths
    current_dir = Path(__file__).parent
    json_output = current_dir / "roundtrip_output.json"
    yaml_output = current_dir / "roundtrip_output.yaml"

    print(f"📊 Reading Excel file: {excel_file}")
    print(f"📝 Generating JSON file: {json_output}")
    print(f"📝 Generating YAML file: {yaml_output}")

    try:
        # Parse Excel back to ODCS dictionary
        odcs_data = parser.parse_from_file(excel_file)

        # Validate the parsed data
        is_valid = parser.validate_odcs_data(odcs_data)
        if is_valid:
            print("✅ Parsed ODCS data passes validation")
        else:
            print("⚠️  Parsed ODCS data has validation warnings (but continuing)")

        # Save as JSON
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(odcs_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Successfully generated JSON file: {json_output}")

        # Save as YAML
        YAMLConverter.dict_to_yaml(odcs_data, yaml_output)
        print(f"✅ Successfully generated YAML file: {yaml_output}")

        # Display summary
        print(f"\n📊 Conversion Summary:")
        print(f"   • Contract ID: {odcs_data.get('id', 'N/A')}")
        print(f"   • Contract Name: {odcs_data.get('name', 'N/A')}")
        print(f"   • Version: {odcs_data.get('version', 'N/A')}")
        print(f"   • Status: {odcs_data.get('status', 'N/A')}")
        print(f"   • Tags: {len(odcs_data.get('tags', []))} tag(s)")
        print(f"   • Servers: {len(odcs_data.get('servers', []))} server(s)")
        print(f"   • Team Members: {len(odcs_data.get('team', []))} member(s)")

    except Exception as e:
        print(f"❌ Error parsing Excel file: {e}")


def demo_yaml_roundtrip():
    """Demonstrate YAML roundtrip conversion."""
    print("\n🔄 YAML Roundtrip Conversion")
    print("=" * 50)

    current_dir = Path(__file__).parent

    try:
        # Convert JSON to YAML first
        json_file = current_dir / "example_contract.json"
        yaml_file = current_dir / "example_contract.yaml"
        excel_file = current_dir / "yaml_roundtrip.xlsx"

        print(f"📖 Converting JSON to YAML: {json_file} → {yaml_file}")

        # Load JSON and save as YAML
        with open(json_file, 'r') as f:
            data = json.load(f)

        YAMLConverter.dict_to_yaml(data, yaml_file)
        print(f"✅ YAML file created: {yaml_file}")

        # Convert YAML to Excel
        print(f"📊 Converting YAML to Excel: {yaml_file} → {excel_file}")
        converter = ODCSToExcelConverter()
        yaml_data = YAMLConverter.yaml_to_dict(yaml_file)
        converter.generate_from_dict(yaml_data, excel_file)
        print(f"✅ Excel file created from YAML: {excel_file}")

        # Clean up temporary files
        yaml_file.unlink(missing_ok=True)
        excel_file.unlink(missing_ok=True)

    except Exception as e:
        print(f"❌ Error in YAML roundtrip: {e}")


def demo_all_formats():
    """Demonstrate conversion between all supported formats."""
    print("\n🔄 All Format Conversions")
    print("=" * 50)

    current_dir = Path(__file__).parent

    formats = {
        'json': current_dir / "multi_format.json",
        'yaml': current_dir / "multi_format.yaml",
        'excel': current_dir / "multi_format.xlsx"
    }

    try:
        # Start with original JSON
        original_file = current_dir / "example_contract.json"

        # JSON → Excel
        print("📖 JSON → Excel")
        converter = ODCSToExcelConverter()
        converter.generate_from_file(original_file, formats['excel'])

        # Excel → YAML
        print("📊 Excel → YAML")
        parser = ExcelToODCSParser()
        parsed_data = parser.parse_from_file(formats['excel'])
        YAMLConverter.dict_to_yaml(parsed_data, formats['yaml'])

        # YAML → JSON
        print("📝 YAML → JSON")
        yaml_data = YAMLConverter.yaml_to_dict(formats['yaml'])
        with open(formats['json'], 'w') as f:
            json.dump(yaml_data, f, indent=2)

        print("✅ All format conversions completed successfully!")
        print("📁 Generated files:")
        for format_name, file_path in formats.items():
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"   • {format_name.upper()}: {file_path.name} ({size:,} bytes)")

        # Clean up
        for file_path in formats.values():
            file_path.unlink(missing_ok=True)

    except Exception as e:
        print(f"❌ Error in multi-format conversion: {e}")


def main():
    """Demonstrate all features of the ODCS Converter."""
    print("🚀 ODCS Converter - Bidirectional Conversion Demo")
    print("=" * 60)
    print("This demo shows conversion between ODCS and Excel formats")
    print("Supports: JSON ↔ Excel ↔ YAML")
    print()

    # Demo 1: ODCS to Excel
    excel_file = demo_odcs_to_excel()

    # Demo 2: Excel to ODCS (both JSON and YAML)
    demo_excel_to_odcs(excel_file)

    # Demo 3: YAML roundtrip
    demo_yaml_roundtrip()

    # Demo 4: All format conversions
    demo_all_formats()

    # Clean up demo files
    current_dir = Path(__file__).parent
    cleanup_files = [
        "example_output.xlsx",
        "roundtrip_output.json",
        "roundtrip_output.yaml"
    ]

    print(f"\n🧹 Cleaning up demo files...")
    for filename in cleanup_files:
        file_path = current_dir / filename
        if file_path.exists():
            file_path.unlink()
            print(f"   🗑️  Removed: {filename}")

    print("\n🎉 Demo completed! All conversions successful.")
    print("\nNext steps:")
    print("• Try the CLI: odcs-converter input.json output.xlsx")
    print("• Or reverse: odcs-converter data.xlsx contract.yaml")
    print("• Use --validate flag to check ODCS compliance")


if __name__ == "__main__":
    main()
