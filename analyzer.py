import os
import sys
import argparse
import re

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

# --- MODULE 2: INPUT HANDLER ---

def get_args():
    parser = argparse.ArgumentParser(
        description="High-Performance Data Folder Analyzer",
        epilog="Example: python analyzer.py 'C:/Downloads' --min-size 10MB --ext .jpg .png"
    )
    parser.add_argument("folder_path", type=str, help="Path to the target directory")
    # Note: min-size is taken as string to support units like '10MB'
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

# --- MODULE 3: VISUALIZER (TREE) ---

def generate_tree(dir_path, prefix="", min_size_bytes=0, allowed_exts=None):
    """
    Recursively generates a visual tree structure.
    Returns a string containing the full tree.
    """
    tree_str = ""
    
    try:
        items = sorted(os.listdir(dir_path))
    except OSError:
        return ""

    # Filter කරාට පස්සේ ඉතුරු වෙන items ටික දාගන්න තැනක්
    filtered_items = []

    # 2. Pre-filtering
    for item in items:
        full_path = os.path.join(dir_path, item)
        
        if os.path.isdir(full_path):
            # Folder එකක් නම් අපි දැනට ඒක ගන්නවා
            filtered_items.append(item)
        else:
            # File එකක් නම් Filters check කරනවා
            try:
                size = os.path.getsize(full_path)
                _, ext = os.path.splitext(item)
                ext = ext.lower() if ext else "(no extension)"

                # Checks
                if allowed_exts and ext not in allowed_exts:
                    continue
                if size < min_size_bytes:
                    continue
                
                filtered_items.append(item)
            except OSError:
                continue

    # 3. Drawing the Tree
    count = len(filtered_items)
    for i, item in enumerate(filtered_items):
        full_path = os.path.join(dir_path, item)
        
        # අන්තිම item එකද බලනවා
        is_last = (i == count - 1)
        connector = "└── " if is_last else "├── "
        
        # Line එක එකතු කරන්න
        tree_str += f"{prefix}{connector}{item}\n"

        # 4. Recursion Step
        if os.path.isdir(full_path):
            # ඊළඟ level එකට අදාල prefix එක හදාගන්නවා
            # අන්තිම folder එක නම් ඉරක් ඕනේ නෑ ("    "), නැත්නම් ඉරක් ඕනේ ("│   ")
            new_prefix = prefix + ("    " if is_last else "│   ")
            
            # Function එක ඇතුලෙම function එක call කරනවා (Recursive)
            tree_str += generate_tree(full_path, new_prefix, min_size_bytes, allowed_exts)

    return tree_str


# --- MAIN EXECUTION ---

def main():
    # 1. Setup
    raw_args = get_args()
    folder_path, min_size_bytes, allowed_exts, output_file = validate_and_normalize_inputs(raw_args)

    print(f"🚀 Starting Scan on: {folder_path}")
    print(f"   - Min Size: {min_size_bytes} Bytes")
    print(f"   - Extensions: {allowed_exts if allowed_exts else 'All'}")

    # 2. Processing
    total_size = 0
    total_files = 0
    
    try:
        # 1. Tree String එක හදාගන්න
        print("🌳 Generating Tree Structure...")
        tree_structure = generate_tree(folder_path, "", min_size_bytes, allowed_exts)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"REPORT FOR: {folder_path}\n")
            f.write(f"Generated on: {os.path.basename(folder_path)}\n")
            f.write("="*50 + "\n\n")

            # --- SECTION 1: STATISTICS ---
            f.write("📊 STATISTICS & FILE LIST\n")
            f.write("-" * 30 + "\n")
            
            for file_path, size, ext in analyze_folder_generator(folder_path, min_size_bytes, allowed_exts):
                total_files += 1
                total_size += size
                # Console Progress
                if total_files % 50 == 0:
                    print(f"\rScanning files... {total_files}", end="")
                
                # File එක report එකට ලියනවා
                # f.write(f"[{ext}] {size/1024/1024:.2f} MB -> {file_path}\n")

            f.write(f"\nSummary:\n")
            f.write(f"📂 Total Files Found: {total_files}\n")
            f.write(f"💾 Total Size: {total_size / (1024**2):.2f} MB\n")
            f.write("\n" + "="*50 + "\n\n")

            # --- SECTION 2: TREE STRUCTURE ---
            f.write("🌳 DIRECTORY TREE\n")
            f.write("-" * 30 + "\n")
            f.write(f"{os.path.basename(folder_path)}/\n") # Root folder name
            f.write(tree_structure)
            f.write("\n" + "="*50 + "\n")

        print(f"\n\n✅ Scan Complete!")
        print(f"📄 Report saved to: {output_file}")

    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")

if __name__ == "__main__":
    main()