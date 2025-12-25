import os
import sys
from .utils import format_size

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
