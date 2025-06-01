import streamlit as st
from src.Utils.logger_config import get_logger
from src.session import init_session_state, add_message
from src.ui import (
    render_css,
    render_header,
    render_control_panel,
    render_chat_and_results,
    render_how_to_use,
)
from src.app_logic import process_pdf_pipeline

# Page configuration (looks better in wide mode)
st.set_page_config(
    page_title="PDF Analysis Chatbot 📄",
    page_icon="🤖",
    layout="wide"
)

# Initialize logger
logger = get_logger(console=True)

# Load CSS styles and session state
render_css()
init_session_state()

# Create main header
render_header()

# Main layout (2-column structure)
col1, col2 = st.columns([1, 2])

# Left Panel: Control Panel
with col1:
    # Render control panel and get user inputs
    uploaded_file, selected_pages, model_name, prompt_key, start_button = render_control_panel()

# Right Panel: Chat and Results Display
with col2:
    # Render chat and results display area
    render_chat_and_results()

# "How to Use?" section
render_how_to_use()

# Run pipeline when analysis button is clicked
if start_button:
    # Callback function for real-time chat updates
    def status_callback(role, content):
        add_message(role, content)
        # st.rerun() removed from this function.
        # UI refresh will be done in the finally block
        # after the entire process is completed.

    # Disable button when processing starts
    st.session_state.processing = True
    
    # Send initial message to user
    status_callback("user", f"PDF analysis started: {uploaded_file.name} (Pages: {selected_pages})")

    with st.spinner("🤖 Processing PDF, please wait..."):
        try:
            # Run main processing pipeline
            result = process_pdf_pipeline(
                pdf_file=uploaded_file,
                selected_pages=selected_pages,
                model_name=model_name,
                prompt_key=prompt_key,
                logger=logger,
                status_callback=status_callback
            )
            
            # Save result to session state
            st.session_state.current_result = result
            status_callback("bot", "✅ Analysis completed! Results are displayed below.")

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            status_callback("bot", f"❌ Error occurred: {e}")
        
        finally:
            # Re-enable button after processing
            st.session_state.processing = False
            # Refresh UI one last time
            st.rerun()