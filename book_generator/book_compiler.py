from .file_utils import save_to_file

def compile_book(base_dir, title, toc, chapters):
    compiled_content = f"Title: {title}\n\nTable of Contents:\n{toc}\n\n"

    for i, chapter in enumerate(chapters):
        compiled_content += f"\nChapter {i+1}:\n\n{chapter}\n"

    save_to_file(base_dir, 'compiled_book.txt', compiled_content)
