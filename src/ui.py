import streamlit as st
import json # For handling analysis result JSON operations
from datetime import datetime # For timestamps
from .session import add_message # For chat messages

from PyPDF2 import PdfReader # For reading PDF page count
from PyPDF2.errors import PdfReadError # For catching PyPDF2-specific read errors
from io import BytesIO # For processing uploaded files in memory

def render_css():
    """Applies custom CSS styles for the application."""
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .chat-message {
            padding: 1.2rem;
            margin: 1rem 0;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            color: #1a1a1a;
        }
        .user-message {
            background: #e1f5fe;
            border-left: 5px solid #0288d1;
        }
        .bot-message {
            background: #f3e5f5;
            border-left: 5px solid #8e24aa;
        }
        .json-container {
            background-color: #282c34;
            border-radius: 8px;
            padding: 1rem;
            font-family: 'Courier New', monospace;
            max-height: 450px;
            overflow-y: auto;
        }
        .stButton>button {
            width: 100%;
            height: 3rem;
        }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Creates the main header of the page."""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 PDF Analysis Chatbot</h1>
        <p>Upload your PDF files, select page range, and analyze with AI!</p>
    </div>
    """, unsafe_allow_html=True)

def render_control_panel():
    """Creates the control panel on the left side (file upload, page selection, etc.)."""
    st.header("🎛️ Control Panel")
    
    uploaded_file = st.file_uploader(
        "Select PDF File", type=['pdf'], help="Upload the PDF file to be analyzed"
    )
    
    selected_pages = []
    actual_total_pages = 0  # Actual total page count in the PDF
    pdf_is_valid_for_processing = False # Flag indicating whether the PDF is readable and processable

    if uploaded_file:
        try:
            # Get the byte content of the uploaded file and create a stream in memory
            pdf_bytes = uploaded_file.getvalue()
            pdf_stream = BytesIO(pdf_bytes)
            reader = PdfReader(pdf_stream)
            
            # Check if reader.pages is empty or None
            if not reader.pages:
                 actual_total_pages = 0
            else:
                actual_total_pages = len(reader.pages)

            if actual_total_pages > 0:
                st.success(f"✅ {uploaded_file.name} uploaded ({actual_total_pages} pages).")
                pdf_is_valid_for_processing = True
            else:
                # If actual_total_pages is 0 (e.g. empty PDF or PyPDF2 issue)
                # Show warning once per file
                if not st.session_state.get(f"warning_shown_zero_pages_{uploaded_file.id}", False):
                    st.warning(f"⚠️ Could not read page count from {uploaded_file.name} or it contains 0 pages.")
                    st.session_state[f"warning_shown_zero_pages_{uploaded_file.id}"] = True
                pdf_is_valid_for_processing = False

        except PdfReadError: # PyPDF2-specific file read error
            if not st.session_state.get(f"error_shown_read_error_{uploaded_file.id}", False):
                st.error(f"❌ {uploaded_file.name} is not a valid PDF file or is corrupted. Please upload a valid PDF.")
                st.session_state[f"error_shown_read_error_{uploaded_file.id}"] = True
            pdf_is_valid_for_processing = False
        except Exception as e: # Catch other possible errors
            if not st.session_state.get(f"error_shown_generic_{uploaded_file.id}", False):
                st.error(f"❌ An error occurred while reading PDF: {e}. Please upload a valid PDF.")
                st.session_state[f"error_shown_generic_{uploaded_file.id}"] = True
            pdf_is_valid_for_processing = False

        # Show page selection area only if PDF is valid and contains pages
        if pdf_is_valid_for_processing:
            st.subheader("📖 Page Selection")
            col_start, col_end = st.columns(2)
            
            # Initial values for number_input widgets
            # These values are used when the widget is first rendered or when the file changes.
            initial_start_page_value = 1
            
            start_page = col_start.number_input(
                "Start Page", 
                min_value=1, 
                max_value=actual_total_pages, # Start page cannot exceed total page count
                value=initial_start_page_value,
                key=f"start_page_{uploaded_file.file_id}" # Resets widget state when new file is uploaded
            )
            
            # Default value for end page should be the current start page
            # and number_input's own min_value/max_value will ensure validity.
            default_end_page_value = start_page 

            end_page = col_end.number_input(
                "End Page", 
                min_value=start_page, # End page cannot be less than start page
                max_value=actual_total_pages, # End page cannot exceed total page count
                value=default_end_page_value, 
                key=f"end_page_{uploaded_file.file_id}" # Resets widget state when new file is uploaded
            )
            
            selected_pages = list(range(start_page, end_page + 1))
            st.info(f"Selected pages: {selected_pages}")
        else:
            # If PDF is not valid for processing, selected_pages remains empty
            selected_pages = []
    else: 
        # If no file is uploaded, selected_pages should be empty
        selected_pages = []

    st.subheader("🧠 Model Settings")
    model_name = st.selectbox(
        "AI Model",
        ["deepseek/deepseek-r1-0528-qwen3-8b"],
        index=0,
        key="model_name_select" 
    )
    
    prompt_key = st.selectbox(
        "Analysis Type (Prompt)", 
        ["summary"], 
        index=0, 
        help="Currently only 'summary' prompt is supported.",
        key="prompt_key_select"
    )
    
    # Determine whether analysis can be started
    can_start_analysis = (
        uploaded_file is not None and           # A file must be uploaded
        pdf_is_valid_for_processing and         # PDF must be readable and contain pages
        bool(selected_pages)                    # A valid page range must be selected
    )

    start_button = st.button(
        "🚀 Start Analysis",
        type="primary",
        disabled=st.session_state.get('processing', False) or not can_start_analysis
    )
    
    return uploaded_file, selected_pages, model_name, prompt_key, start_button

def render_chat_and_results():
    """Shows the chat history and analysis results on the right side."""
    st.header("💬 Chat and Results")
    
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.get('chat_history', []):
            css_class = "user-message" if message["role"] == "user" else "bot-message"
            role_icon = "👤" if message["role"] == "user" else "🤖"
            role_name = "You" if message["role"] == "user" else "AI Assistant"
            st.markdown(f"""
            <div class="chat-message {css_class}">
                <strong>{role_icon} {role_name} ({message["timestamp"]}):</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)

    if st.session_state.get('current_result'):
        st.subheader("📊 Analysis Result")
        try:
            result_json = st.session_state.current_result
            if isinstance(result_json, str):
                 result_json = json.loads(result_json)
            
            st.markdown('<div class="json-container">', unsafe_allow_html=True)
            st.json(result_json)
            st.markdown('</div>', unsafe_allow_html=True)
            
            _render_save_buttons(result_json)

        except Exception as e:
            st.error(f"Error displaying result: {e}")
    
    if st.button("🗑️ Clear History"):
        st.session_state.chat_history = []
        st.session_state.current_result = None
        st.rerun()

def _render_save_buttons(result_json):
    """Creates buttons for saving results."""
    st.subheader("💾 Save Results")
    col_save1, col_save2, col_save3 = st.columns(3)
    
    now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_str = json.dumps(result_json, ensure_ascii=False, indent=2)
    
    with col_save1:
        st.download_button(
            label="📄 Download JSON",
            data=json_str,
            file_name=f"analysis_{now_str}.json",
            mime="application/json"
        )
    
    with col_save2:
        summary_text = result_json.get("summary", str(result_json))
        st.download_button(
            label="📝 Download Text",
            data=summary_text,
            file_name=f"analysis_{now_str}.txt",
            mime="text/plain"
        )
        
    with col_save3:
        if st.button("💽 Save Locally (.json)"):
            filename = f"analysis_{now_str}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(json_str)
            st.success(f"✅ Result saved as '{filename}'!")
            # add_message adds to chat history, here it can be done with st.session_state.chat_history.append or add_message can be used for UI visibility.
            # However, since this is called outside of callback, add_message might be more appropriate.
            if 'chat_history' in st.session_state: # Without waiting for add_message to initialize session_state
                 add_message("bot", f"Result saved locally as '{filename}' file.")


def render_how_to_use():
    """Creates the 'How to Use?' section at the bottom of the page."""
    with st.expander("ℹ️ How to Use?"):
        st.markdown("""
        ### 📋 Usage Steps:
        1. **Upload PDF**: Select your PDF file from the left panel.
        2. **Page Range**: Specify the pages to be analyzed. (Limited by the actual page count of the PDF)
        3. **Select Model**: Choose the AI model you want to use.
        4. **Start Analysis**: Begin the process with the 'Start Analysis' button. Follow the process in real-time from the chat screen.
        5. **Review Results**: Once analysis is complete, results will appear in JSON format on the right panel.
        6. **Save**: Download results in JSON or text format, or save to local disk.
        """)