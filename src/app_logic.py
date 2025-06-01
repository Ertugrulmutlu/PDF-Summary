import os
import tempfile
from .Utils.pdf_util import PdfUtils
from .Utils.llm_utils import LlmUtils

# --- Log Decorator (for normal functions) ---
def log_decorator(func):
    def wrapper(*args, **kwargs):
        logger = kwargs.get('logger', None)
        if logger:
            logger.info(f"[{func.__name__}] start")
        try:
            result = func(*args, **kwargs)
            if logger:
                logger.info(f"[{func.__name__}] finish")
            return result
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            if logger:
                logger.error(f"[{func.__name__}] ERROR: {e}\nTraceback:\n{tb}")
            raise
    return wrapper

@log_decorator
def process_pdf_pipeline(pdf_file, selected_pages, model_name, prompt_key, logger, status_callback):
    """
    Runs PDF processing and LLM analysis pipeline.
    
    Args:
        pdf_file: Uploaded PDF file (Streamlit UploadedFile object).
        selected_pages (list): Page numbers to be analyzed (1-based).
        model_name (str): LLM model to be used.
        prompt_key (str): Prompt key to be used.
        logger: Logging object.
        status_callback (function): Callback function for real-time status updates.
    """
    try:
        # 1. Write PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_file.getvalue())
            pdf_path = tmp_file.name
        
        # Convert page indices to 0-based
        page_indices = [i - 1 for i in selected_pages]
        
        # 2. Split PDF according to selected pages
        status_callback("bot", f"📄 Splitting PDF... Pages: {selected_pages}")
        splitter = PdfUtils.PdfSplitter(pdf_path, page_indices, logger)
        splitter.run()
        
        # 3. Extract text from split PDF
        status_callback("bot", "🔍 Extracting text...")
        pdf_utils = PdfUtils(logger)
        extracted_text = pdf_utils.extract_text_from_pdf(splitter.output1_path)
        
        if not extracted_text or not extracted_text.strip():
            logger.warning("Could not extract text from PDF or extracted text is empty.")
            raise ValueError("Could not extract text from selected pages. Please select different pages or check the PDF.")
        
        # 4. Process text with LLM
        status_callback("bot", f"🤖 Starting analysis with '{model_name}' model...")
        
        # Specify the path to the prompt file correctly
        # We assume this file is in the main directory of the project.
        prompt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Prompts', 'prompt.json')
        
        llm_utils = LlmUtils(
            logger=logger,
            model=model_name,
            pdf_text=extracted_text,
            prompt_key=prompt_key,
            prompt_path=prompt_path # Explicitly provide prompt path
        )
        
        result = llm_utils.run_full_pipeline()
        
        if not result:
            raise Exception("Could not get a valid response from the LLM model.")
            
        return result
        
    finally:
        # Clean up temporary files
        if 'pdf_path' in locals() and os.path.exists(pdf_path):
            os.unlink(pdf_path)
        if 'splitter' in locals():
            if os.path.exists(splitter.output1_path):
                os.unlink(splitter.output1_path)
            if os.path.exists(splitter.output2_path):
                os.unlink(splitter.output2_path)