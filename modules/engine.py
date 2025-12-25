import os

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
