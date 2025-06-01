# 🤖 PDF Summary Chatbot

A modern, user-friendly PDF analysis application. Upload your PDF files, select specific page ranges, and perform comprehensive analysis with local AI models.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.0+-red.svg)
![LM Studio](https://img.shields.io/badge/LM%20Studio-Required-green.svg)

## ✨ Features

- 📄 **PDF Upload & Page Selection**: Upload PDF files and specify page ranges for summary
- 🤖 **Local AI Analysis**: Secure summary using local AI models via LM Studio
- 💬 **Real-time Chat**: Track the analysis process in real-time
- 📊 **Rich Results**: Detailed analysis results in JSON format
- 💾 **Multiple Export Options**: Save as JSON, TXT, or local files
- 🎨 **Modern Interface**: Responsive and user-friendly design

## 🚀 Quick Start

### Requirements

1. **Python 3.8+**
2. **LM Studio** (Must be installed!)

### LM Studio Setup

**LM Studio** is a platform for managing locally running AI models. This application accesses AI models through LM Studio.

1. [Download LM Studio](https://lmstudio.ai/) and install it
2. Launch LM Studio
3. Download a model (e.g., `deepseek/deepseek-r1-0528-qwen3-8b`)
4. Go to **Local Server** tab and start the server
5. Default port should be `1234`

> **⚠️ Important**: If LM Studio server is not running or no model is loaded, the application will throw errors!

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/pdf-analyzer-chatbot.git
cd pdf-analyzer-chatbot

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt

# Run the application
streamlit run main.py
```

## 📁 Project Structure

```
pdf-analyzer-chatbot/
├── main.py                 # Main application file
├── src/
│   ├── app_logic.py        # Business logic and pipeline
│   ├── session.py          # Streamlit session management
│   ├── ui.py              # User interface components
│   ├── Prompts/
│   │   └── prompt.json    # AI prompt templates
│   └── Utils/
│       ├── logger_config.py    # Logging configuration
│       ├── llm_utils.py       # AI model operations
│       └── pdf_util.py        # PDF processing tools
├── app.log                # Application logs
└── README.md
```

## 🔧 Core Components

### 1. **main.py** - Main Orchestrator
```python
# Streamlit configuration, CSS loading and main page layout
st.set_page_config(page_title="PDF Analysis Chatbot 📄", layout="wide")
```

**Key Functions:**
- Streamlit page configuration
- 2-column layout (control panel + results)
- Analysis button trigger

### 2. **app_logic.py** - Processing Pipeline
```python
def process_pdf_pipeline(pdf_file, selected_pages, model_name, prompt_key, logger, status_callback):
```

**Pipeline Steps:**
1. Write PDF to temporary file
2. Split selected pages (`PdfSplitter`)
3. Extract text (`PdfUtils`)
4. Analyze with AI (`LlmUtils`)
5. Return results

### 3. **ui.py** - User Interface

#### Main Functions:
- `render_control_panel()`: Left panel (file upload, settings)
- `render_chat_and_results()`: Right panel (chat + results)
- `render_css()`: Custom style definitions

#### PDF Validation:
```python
reader = PdfReader(pdf_stream)
actual_total_pages = len(reader.pages)
if actual_total_pages > 0:
    pdf_is_valid_for_processing = True
```

### 4. **llm_utils.py** - AI Operations

**Main Classes:**
- `PromptHandler`: Load and prepare prompts
- `ModelRunner`: Communication with LM Studio
- `OutputProcessor`: Clean responses and extract JSON

```python
def run_full_pipeline(self):
    prompt = self.prompt_handler.prepare(self.pdf_text)
    raw_output = self.model_runner.run(prompt)
    cleaned = self.output_processor.clean_text(raw_output)
    json_result = self.output_processor.extract_json(cleaned)
```

### 5. **pdf_util.py** - PDF Operations

**Main Classes:**
- `PdfUtils`: Text extraction
- `PdfSplitter`: Page splitting and separation

```python
def extract_text_from_pdf(self, file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
```

## 📊 Logging System

### Log File: `app.log`
All system logs are written here:
```
2024-06-01 10:30:15 - INFO - [process_pdf_pipeline] start
2024-06-01 10:30:16 - INFO - PDF splitting... Pages: [1, 2, 3]
2024-06-01 10:30:18 - INFO - [extract_text_from_pdf] finish
```

### Log Decorators
Every important function is wrapped with `@log_decorator`:
```python
@log_decorator
def process_pdf_pipeline(...):
    # Automatically logs start/finish/error messages
```

### Console Logs
In `main.py`, `get_logger(console=True)` also prints logs to console.

## ⚙️ Customization Guide

### 🤖 Adding New AI Models

1. **Download Model in LM Studio**
2. **Edit ui.py**:
```python
model_name = st.selectbox(
    "AI Model",
    [
        "deepseek/deepseek-r1-0528-qwen3-8b",
        "your-new-model/model-name",  # Add new model
        "another-model/name"
    ]
)
```

### 📝 Adding New Prompt Types

1. **Edit src/Prompts/prompt.json**:
```json
{
  "summary": "Existing prompt...",
  "detailed_analysis": "New prompt: Analyze {text} in detail...",
  "key_extraction": "Extract key points from: {text}"
}
```

2. **Add option in ui.py**:
```python
prompt_key = st.selectbox(
    "Analysis Type (Prompt)", 
    ["summary", "detailed_analysis", "key_extraction"]
)
```

### 🎨 Changing Interface Colors

**ui.py** - `render_css()` function:
```css
.main-header {
    background: linear-gradient(135deg, #your-color1 0%, #your-color2 100%);
}
.user-message {
    background: #your-user-color;
    border-left: 5px solid #your-border-color;
}
```

### 📁 Customizing Output Format

**llm_utils.py** - `OutputProcessor.extract_json()`:
```python
def extract_json(self, text, output_path="custom_output.json"):
    # Modify JSON extraction logic
    # Update regex for different formats
```

## 🐛 Troubleshooting

### Common Issues

1. **LM Studio Connection Error**
   ```
   ERROR: Connection refused to localhost:1234
   ```
   - Ensure LM Studio is running
   - Verify Local Server is started
   - Check that port 1234 is open

2. **PDF Reading Error**
   ```
   ERROR: PDF could not be read
   ```
   - Ensure PDF file is not corrupted
   - Note that encrypted PDFs are not supported

3. **Model Not Responding**
   ```
   ERROR: No response from model
   ```
   - Verify model is loaded in LM Studio
   - Check that model name is correct

### Debug Mode
For more detailed logs:
```python
logger = get_logger(console=True)  # in main.py
logger.setLevel(logging.DEBUG)      # in logger_config.py
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ⭐ Support

If this project is helpful, please give it a ⭐!

Use the Issues section for questions.

---

**Made with ❤️ using Streamlit & LM Studio**
