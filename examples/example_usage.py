#!/usr/bin/env python3
"""Example usage of ODCS Excel Generator."""

from pathlib import Path
from odcs_excel_generator import ODCSExcelGenerator


def main():
    """Demonstrate basic usage of the ODCS Excel Generator."""
    
    # Initialize the generator
    generator = ODCSExcelGenerator()
    
    # Get paths
    current_dir = Path(__file__).parent
    input_file = current_dir / "example_contract.json"
    output_file = current_dir / "example_output.xlsx"
    
    print(f"Reading ODCS contract from: {input_file}")
    print(f"Generating Excel file: {output_file}")
    
    try:
        # Generate Excel from JSON file  
        generator.generate_from_file(input_file, output_file)
        print(f"✅ Successfully generated Excel file: {output_file}")
        
        # You can also generate from a URL
        # generator.generate_from_url("https://example.com/contract.json", "output.xlsx")
        
        # Or from a dictionary
        # data = {...}  # Your ODCS data
        # generator.generate_from_dict(data, "output.xlsx")
        
    except Exception as e:
        print(f"❌ Error generating Excel file: {e}")


if __name__ == "__main__":
    main()
