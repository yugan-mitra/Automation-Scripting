import os
import sys
import argparse
from .utils import parse_size

def get_args():
    parser = argparse.ArgumentParser(
        description="High-Performance Data Folder Analyzer",
        epilog="Example: python main.py 'C:/Downloads' --min-size 10MB --email boss@company.com"
    )
    parser.add_argument("folder_path", type=str, help="Path to the target directory")
    parser.add_argument("--min-size", type=str, default="0", help="Minimum file size (e.g., 10MB)")
    parser.add_argument("--ext", nargs='+', default=None, help="Filter by extensions")
    parser.add_argument("--output", type=str, default="output/report.txt", help="Output report filename")
    
    # [NEW] Email Argument
    parser.add_argument("--email", type=str, default=None, help="Recipient email address to send the report")
    
    return parser.parse_args()

def validate_and_normalize_inputs(args):
    # 1. Path Validation
    if not os.path.exists(args.folder_path):
        print(f"❌ Error: The path '{args.folder_path}' does not exist.")
        sys.exit(1)
    if not os.path.isdir(args.folder_path):
        print(f"❌ Error: '{args.folder_path}' is not a directory.")
        sys.exit(1)

    # 2. Size Parsing & Validation
    try:
        min_size_bytes = parse_size(args.min_size)
    except ValueError as e:
        print(f"❌ Input Error: {e}")
        sys.exit(1)

    if min_size_bytes < 0:
        print("❌ Error: Minimum size cannot be negative.")
        sys.exit(1)

    # 3. Extension Normalization
    allowed_extensions = None
    if args.ext:
        allowed_extensions = { 
            (e.lower() if e.startswith('.') else f".{e.lower()}") 
            for e in args.ext 
        }
    
    # Return email as well
    return args.folder_path, min_size_bytes, allowed_extensions, args.output, args.email