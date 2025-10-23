import re
import os

def sanitize_filename(filename):
    """
    Sanitizes filenames to remove or replace invalid characters.
    """
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def save_to_file(base_dir, filename, content):
    """
    Saves 'content' to a file named 'filename' in the specified base directory.
    """
    filepath = os.path.join(base_dir, filename)
    with open(filepath, "w", encoding='utf-8') as file:
        file.write(content)

def load_from_file(base_dir, filename):
    """
    Loads content from a file named 'filename' in the specified base directory.
    """
    filepath = os.path.join(base_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None
