import os
import sys
import argparse
import re
import time
from datetime import datetime

# --- MODULE 1: HELPER FUNCTIONS ---

def parse_size(size_input):
    """
    Parses a string like '10MB' or '500kb' into bytes.
    Returns the size in bytes (int).
    """
    size_input = str(size_input).strip().upper()

    if size_input.isdigit():
        return int(size_input)

    match = re.match(r"^(\d*\.?\d+)\s*([A-Z]+)$", size_input)
    if not match:
        raise ValueError(f"Invalid size format: '{size_input}'")

    number, unit = match.groups()
    number = float(number)

    units = {
        'B': 1, 'K': 1024, 'KB': 1024,
        'M': 1024 ** 2, 'MB': 1024 ** 2,
        'G': 1024 ** 3, 'GB': 1024 ** 3,
        'T': 1024 ** 4, 'TB': 1024 ** 4
    }

    if unit not in units:
        raise ValueError(f"Unknown unit: '{unit}'. Supported: B, KB, MB, GB, TB")

    return int(number * units[unit])

def format_size(size_bytes):
    """
    Converts bytes to a human-readable format (e.g., 1024 -> 1.00 KB).
    Used for display purposes in the Report and Tree.
    """
    if size_bytes == 0:
        return "0 B"
        
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0

    while size_bytes >= 1024 and unit_index < len(units) - 1:
        size_bytes /= 1024
        unit_index += 1

    return f"{size_bytes:.2f} {units[unit_index]}"

# --- MODULE 2: INPUT HANDLER ---

def get_args():
    parser = argparse.ArgumentParser(
        description="High-Performance Data Folder Analyzer",
        epilog="Example: python analyzer.py 'C:/Downloads' --min-size 10MB --ext .jpg .png"
    )
    parser.add_argument("folder_path", type=str, help="Path to the target directory")
    parser.add_argument("--min-size", type=str, default="0", help="Minimum file size (e.g., 10MB)")
    parser.add_argument("--ext", nargs='+', default=None, help="Filter by extensions")
    parser.add_argument("--output", type=str, default="report.txt", help="Output report filename")
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

    # 3. Extension Normalization (Set for O(1) lookup)
    allowed_extensions = None
    if args.ext:
        allowed_extensions = { 
            (e.lower() if e.startswith('.') else f".{e.lower()}") 
            for e in args.ext 
        }
    
    return args.folder_path, min_size_bytes, allowed_extensions, args.output

# --- MODULE 3: CORE ENGINE (GENERATOR) ---

def analyze_folder_generator(folder_path, min_size_bytes, allowed_exts):
    """
    Yields: (full_path, size_in_bytes, extension)
    Scans efficiently without loading everything to RAM.
    """
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            try:
                # Metadata extraction
                _, ext = os.path.splitext(file)
                ext = ext.lower() if ext else "(no extension)"
                
                # Filter: Extension
                if allowed_exts and ext not in allowed_exts:
                    continue

                full_path = os.path.join(root, file)
                size_bytes = os.path.getsize(full_path)

                # Filter: Size
                if size_bytes < min_size_bytes:
                    continue

                yield full_path, size_bytes, ext

            except OSError:
                continue

# --- MODULE 4: VISUALIZER (TREE) ---

def generate_tree(dir_path, prefix="", min_size_bytes=0, allowed_exts=None, progress_tracker=None):
    """
    Recursively generates a visual tree structure with file sizes.
    Updates progress_tracker['count'] for real-time feedback.
    """
    tree_str = ""
    
    # Initialize tracker if first call
    if progress_tracker is None:
        progress_tracker = {'count': 0}

    try:
        items = sorted(os.listdir(dir_path))
    except OSError:
        return ""

    # Pre-filtering items for the tree
    filtered_items = []
    
    for item in items:
        full_path = os.path.join(dir_path, item)
        
        # Update Real-time Progress
        progress_tracker['count'] += 1
        if progress_tracker['count'] % 50 == 0:
            # \r moves cursor to start of line, avoiding new lines
            sys.stdout.write(f"\r🌳 Building Tree... Scanned {progress_tracker['count']} items")
            sys.stdout.flush()

        if os.path.isdir(full_path):
            filtered_items.append(item)
        else:
            try:
                size = os.path.getsize(full_path)
                _, ext = os.path.splitext(item)
                ext = ext.lower() if ext else "(no extension)"

                if allowed_exts and ext not in allowed_exts:
                    continue
                if size < min_size_bytes:
                    continue
                
                filtered_items.append(item)
            except OSError:
                continue

    # Drawing the tree
    count = len(filtered_items)
    for i, item in enumerate(filtered_items):
        full_path = os.path.join(dir_path, item)
        
        is_last = (i == count - 1)
        connector = "└── " if is_last else "├── "
        
        # Determine display text (Add size if it's a file)
        display_text = item
        if not os.path.isdir(full_path):
            try:
                size = os.path.getsize(full_path)
                display_text = f"{item} ({format_size(size)})"
            except OSError:
                pass

        tree_str += f"{prefix}{connector}{display_text}\n"

        if os.path.isdir(full_path):
            new_prefix = prefix + ("    " if is_last else "│   ")
            tree_str += generate_tree(full_path, new_prefix, min_size_bytes, allowed_exts, progress_tracker)

    return tree_str

# --- MAIN EXECUTION ---

def main():
    # 1. Setup
    raw_args = get_args()
    folder_path, min_size_bytes, allowed_exts, output_file = validate_and_normalize_inputs(raw_args)

    # 2. Capture Time (Start)
    start_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_timer = time.time()

    print(f"🚀 Starting Scan on: {folder_path}")
    print(f"   - Min Size Filter: {format_size(min_size_bytes)}")
    print(f"   - Extensions: {allowed_exts if allowed_exts else 'All'}")
    print("-" * 50)

    # 3. Processing
    total_size = 0
    total_files = 0
    
    try:
        # Phase 1: Generate Tree (Passes a mutable dictionary for tracking count)
        progress_tracker = {'count': 0}
        tree_structure = generate_tree(folder_path, "", min_size_bytes, allowed_exts, progress_tracker)
        print(f"\r✅ Tree built! Scanned {progress_tracker['count']} items.            ") # Clear line

        # Phase 2: Calculate Stats (Consuming Generator)
        print("📊 Calculating Statistics...")
        
        for _, size, _ in analyze_folder_generator(folder_path, min_size_bytes, allowed_exts):
            total_files += 1
            total_size += size
            
            # Real-time counter for the stats phase
            if total_files % 50 == 0:
                sys.stdout.write(f"\r🔍 Analyzing files... Found {total_files}")
                sys.stdout.flush()

        # Clear the progress line one last time
        sys.stdout.write(f"\r✅ Analysis complete! Processed {total_files} matching files.      \n")

        # 4. Capture Time (End)
        end_timer = time.time()
        time_spent_seconds = end_timer - start_timer
        
        if time_spent_seconds < 60:
            time_spent_str = f"{time_spent_seconds:.2f} seconds"
        else:
            minutes = int(time_spent_seconds // 60)
            seconds = int(time_spent_seconds % 60)
            time_spent_str = f"{minutes}m {seconds}s"

        # 5. Write Report
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"📁 FOLDER ANALYSIS REPORT\n")
            f.write("="*50 + "\n")
            
            # Meta Data
            f.write(f"📍 Target Path:   {folder_path}\n")
            f.write(f"📅 Scan Time:     {start_timestamp}\n")
            f.write(f"⏱️ Duration:      {time_spent_str}\n")
            f.write("-" * 50 + "\n")
            f.write(f"🔍 APPLIED FILTERS:\n")
            f.write(f"   • Min File Size: {format_size(min_size_bytes)}\n")
            f.write(f"   • Extensions:    {', '.join(allowed_exts) if allowed_exts else 'All'}\n")
            f.write("="*50 + "\n\n")

            # Statistics
            f.write("📊 SUMMARY STATISTICS\n")
            f.write("-" * 30 + "\n")
            f.write(f"📂 Total Files Found: {total_files}\n")
            f.write(f"💾 Total Size:        {format_size(total_size)}\n")
            f.write("\n" + "="*50 + "\n\n")

            # Tree Structure
            f.write("🌳 DIRECTORY TREE STRUCTURE\n")
            f.write("-" * 30 + "\n")
            f.write(f"{os.path.basename(folder_path)}/\n")
            f.write(tree_structure)
            f.write("\n" + "="*50 + "\n")

        print(f"\n✨ Success! Report generated in {time_spent_str}.")
        print(f"📄 Saved to: {os.path.abspath(output_file)}")

    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")

if __name__ == "__main__":
    main()