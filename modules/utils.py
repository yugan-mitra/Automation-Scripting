import re

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
