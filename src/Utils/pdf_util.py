from PyPDF2 import PdfReader, PdfWriter
import os
import traceback
from io import BytesIO

# --- Log Decorator ---
def log_decorator(func):
    def wrapper(self, *args, **kwargs):
        self.logger.info(f"[{func.__name__}] start")
        try:
            result = func(self, *args, **kwargs)
            self.logger.info(f"[{func.__name__}] finish")
            return result
        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error(f"[{func.__name__}] ERROR: {e}\nTraceback:\n{tb}")
            raise
    return wrapper

class PdfUtils:
    def __init__(self, logger):
        self.logger = logger

    @log_decorator
    def extract_text_from_pdf(self, file_path):
        self.logger.info(f"PDF text extraction started: {file_path}")
        try:
            reader = PdfReader(file_path)
            text = ""
            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        self.logger.debug(f"Page {i} successfully read.")
                    else:
                        self.logger.warning(f"Page {i} is empty or unreadable.")
                except Exception as e:
                    self.logger.error(f"Error reading page {i}: {e}")
            self.logger.info("PDF text extraction completed.")
            return text
        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error(f"Could not read PDF: {e}\n{tb}")
            return None

    class PdfSplitter:
        def __init__(self, input_path, selected_pages, logger):
            try:
                self.logger = logger
                self.input_path = input_path
                self.selected_pages = selected_pages
                self.reader = None
                self.writer_selected = PdfWriter()
                self.writer_rest = PdfWriter()

                base_dir = os.path.dirname(input_path) or "."
                self.output1_path = os.path.join(base_dir, "1.pdf")
                self.output2_path = os.path.join(base_dir, "2.pdf")
                self.logger.info("PdfSplitter initialized.")
                self.logger.info(f"File path: {self.input_path}")
                self.logger.info(f"Selected pages: {self.selected_pages}")
            except Exception as e:
                tb = traceback.format_exc()
                self.logger.error(f"Constructor error: {e}\n{tb}")
                raise

        @log_decorator
        def load_pdf(self):
            self.logger.info("Loading PDF file...")
            with open(self.input_path, "rb") as f:
                pdf_data = f.read()
                self.logger.info(f"{len(pdf_data)} bytes read.")
            self.reader = PdfReader(BytesIO(pdf_data))
            self.logger.info("PDF file successfully loaded into memory.")
            self.logger.info(f"Total page count: {len(self.reader.pages)}")
            self._split_pages()

        @log_decorator
        def _split_pages(self):
            self.logger.info("Splitting pages...")
            for page_num in range(len(self.reader.pages)):
                if page_num in self.selected_pages:
                    self.writer_selected.add_page(self.reader.pages[page_num])
                    self.logger.info(f"Selected page added: {page_num}")
                else:
                    self.writer_rest.add_page(self.reader.pages[page_num])
                    self.logger.info(f"Other page added: {page_num}")
            self.logger.info("Page splitting completed.")

        @log_decorator
        def save_pdfs(self):
            self.logger.info("Saving PDFs...")
            with open(self.output1_path, "wb") as f1:
                self.writer_selected.write(f1)
                self.logger.info(f"Selected pages saved: {self.output1_path}")
            with open(self.output2_path, "wb") as f2:
                self.writer_rest.write(f2)
                self.logger.info(f"Remaining pages saved: {self.output2_path}")
            self.logger.info("PDF save operation completed.")

        def run(self):
            try:
                self.logger.info("PDF splitting process started.")
                self.load_pdf()
                self.save_pdfs()
                self.logger.info("PDF splitting process completed successfully.")
            except Exception as e:
                self.logger.error(f"run() error: {e}")