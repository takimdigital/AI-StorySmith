import os
from .file_utils import save_to_file
from fpdf import FPDF

class BookCompiler:
    def __init__(self, base_dir, title, toc, chapters):
        self.base_dir = base_dir
        self.title = title
        self.toc = toc
        self.chapters = chapters
        self.sanitized_title = self._sanitize(title)

    def _sanitize(self, filename):
        # Basic sanitization for filenames
        return "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '-')]).rstrip()

    def _get_full_content_txt(self):
        content = f"{self.title}\n\nTable of Contents:\n{self.toc}\n\n"
        for i, chapter_text in enumerate(self.chapters):
            content += f"\n\n---\n\nChapter {i+1}\n\n{chapter_text}"
        return content

    def _get_full_content_md(self):
        content = f"# {self.title}\n\n## Table of Contents\n{self.toc}\n\n"
        for i, chapter_text in enumerate(self.chapters):
            content += f"\n\n---\n\n## Chapter {i+1}\n\n{chapter_text}"
        return content

    def save_as_txt(self):
        content = self._get_full_content_txt()
        save_to_file(self.base_dir, f"{self.sanitized_title}.txt", content)
        print(f"Successfully saved book as {self.sanitized_title}.txt")

    def save_as_md(self):
        content = self._get_full_content_md()
        save_to_file(self.base_dir, f"{self.sanitized_title}.md", content)
        print(f"Successfully saved book as {self.sanitized_title}.md")

    def save_as_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=24)

        # Title
        pdf.cell(200, 10, txt=self.title, ln=True, align='C')

        # Table of Contents
        pdf.add_page()
        pdf.set_font("Arial", size=16)
        pdf.cell(200, 10, txt="Table of Contents", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=self.toc)

        # Chapters
        for i, chapter_text in enumerate(self.chapters):
            pdf.add_page()
            pdf.set_font("Arial", size=16)
            pdf.cell(200, 10, txt=f"Chapter {i+1}", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, txt=chapter_text)

        pdf.output(os.path.join(self.base_dir, f"{self.sanitized_title}.pdf"))
        print(f"Successfully saved book as {self.sanitized_title}.pdf")

def compile_book(base_dir, title, toc, chapters, formats):
    compiler = BookCompiler(base_dir, title, toc, chapters)
    if 'txt' in formats:
        compiler.save_as_txt()
    if 'md' in formats:
        compiler.save_as_md()
    if 'pdf' in formats:
        compiler.save_as_pdf()
