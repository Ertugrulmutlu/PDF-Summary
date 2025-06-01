import os
import json
import re
import traceback
import lmstudio as lms

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


class LlmUtils:
    def __init__(self, logger, model, pdf_text, prompt_key, prompt_path=None):
        if prompt_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            prompt_path = os.path.join(base_dir, "Prompts", "prompt.json")
            logger.info(f"[LlmUtils] prompt_path automatically set: {prompt_path}")
        else:
            logger.info(f"[LlmUtils] prompt_path provided externally: {prompt_path}")
        self.logger = logger
        self.model = model
        self.pdf_text = pdf_text
        self.prompt_handler = self.PromptHandler(prompt_path, prompt_key, logger)
        self.model_runner = self.ModelRunner(model, logger)
        self.output_processor = self.OutputProcessor(logger)

    class PromptHandler:
        def __init__(self, prompt_path, prompt_key, logger):
            self.logger = logger
            self.prompt_path = prompt_path
            self.prompt_key = prompt_key
            self.prompt_template = self._load_prompt()

        @log_decorator
        def _load_prompt(self):
            if not os.path.exists(self.prompt_path):
                raise FileNotFoundError(f"Prompt file not found: {self.prompt_path}")
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                prompts = json.load(f)
            if self.prompt_key not in prompts:
                raise KeyError(f"Prompt '{self.prompt_key}' not found.")
            return prompts[self.prompt_key]

        @log_decorator
        def prepare(self, pdf_text):
            try:
                return self.prompt_template.format(text=pdf_text)
            except Exception as e:
                tb = traceback.format_exc()
                self.logger.error(f"Failed to prepare prompt: {e}\n{tb}")
                return None

    class ModelRunner:
        def __init__(self, model, logger):
            self.model = lms.llm(model)
            self.logger = logger

        @log_decorator
        def run(self, prompt):
            try:
                self.logger.info("Sending prompt to LLM...")
                result = self.model.respond(prompt)
                self.logger.info("Response received.")

                if not isinstance(result, str):
                    result = getattr(result, "text", str(result))

                return result

            except Exception as e:
                tb = traceback.format_exc()
                self.logger.error(f"Model error: {e}\n{tb}")
                return None

    class OutputProcessor:
        def __init__(self, logger):
            self.logger = logger

        @log_decorator
        def clean_text(self, text):
            self.logger.info("Cleaning response...")
            cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
            cleaned = cleaned.strip()
            return cleaned

        @log_decorator
        def extract_json(self, text, output_path="a.json"):
            self.logger.info("Starting JSON extraction...")
            try:
                json_match = re.search(r'\{.*\}', text, flags=re.DOTALL)
                if not json_match:
                    raise ValueError("No valid JSON found in text.")
                json_str = json_match.group(0)
                data = json.loads(json_str)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self.logger.info(f"JSON successfully saved to '{output_path}' file.")
                return data
            except Exception as e:
                tb = traceback.format_exc()
                self.logger.error(f"JSON extraction error: {e}\n{tb}")
                return None

    @log_decorator
    def run_full_pipeline(self):
        prompt = self.prompt_handler.prepare(self.pdf_text)
        if not prompt:
            self.logger.error("Process terminated because prompt could not be prepared.")
            return None

        raw_output = self.model_runner.run(prompt)
        if not raw_output:
            self.logger.error("Process terminated because no response received from model.")
            return None

        cleaned = self.output_processor.clean_text(raw_output)
        json_result = self.output_processor.extract_json(cleaned)
        return json_result