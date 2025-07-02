import streamlit as st
import os
import threading
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from a_core.e_utils.config_manager import get_config, update_config

load_dotenv()

# Import core modules
from a_core.a_fileflow.aa011_monitor import FileMonitor
from a_core.a_fileflow.aa010_processor import run_full_pipeline
from a_core.a_fileflow.aa014_vector_storage import VectorStorage
from a_core.a_fileflow.aa03_context_memory import ContextMemory

# Import components
from b_gui.a_components.ba03_folder_selector import FolderSelector
from b_gui.a_components.ba02_file_review import FileReview
from b_gui.a_components.ba01_activity_timeline import ActivityTimeline
from b_gui.a_components.ba04_log_export import LogExport

#import other modules
from a_core.a_fileflow.aa03_context_memory import ContextMemory
from a_core.a_fileflow.aa05_database import DatabaseManager
from a_core.a_fileflow.aa014_vector_storage import VectorStorage
from a_core.a_fileflow.aa02_content_extractor import ContentExtractor


# Initialize session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

if 'vector_storage' not in st.session_state:
    st.session_state.vector_storage = VectorStorage()

if 'context_memory' not in st.session_state:
    st.session_state.context_memory = ContextMemory(st.session_state.db_manager)

if 'file_monitor' not in st.session_state:
    st.session_state.file_monitor = None

if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False

if 'selected_folder' not in st.session_state:
    st.session_state.selected_folder = None

def main():
    st.set_page_config(
        page_title="Second Brain - Intelligent File Management",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🧠 Second Brain - Intelligent File Management")
    st.markdown("*Capture, vectorize, and make all computer activity searchable through AI-powered content analysis*")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Select Page",
            ["Folder Monitor", "File Review", "Activity Timeline", "Export Logs", "Settings"]
        )
        
        # OpenAI API Key status
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            st.success("✅ OpenAI API Key loaded")
        else:
            st.warning("⚠️ OpenAI API Key not found in environment")
        
        # Monitoring status
        if st.session_state.monitoring_active:
            st.success(f"📁 Monitoring: {st.session_state.selected_folder}")
            if st.button("Stop Monitoring"):
                stop_monitoring()
        else:
            st.info("📁 No folder being monitored")
    
    # Main content based on selected page
    if page == "Folder Monitor":
        folder_selector = FolderSelector()
        folder_selector.render()
        
    elif page == "File Review":
        file_review = FileReview(st.session_state.db_manager)
        file_review.render()
        
    elif page == "Activity Timeline":
        timeline = ActivityTimeline(st.session_state.db_manager)
        timeline.render()
        
    elif page == "Export Logs":
        log_export = LogExport(st.session_state.db_manager)
        log_export.render()
        
    elif page == "Settings":
        render_settings()

def render_settings():
    """Render the settings page"""
    st.header("⚙️ Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Database Information")
        try:
            stats = st.session_state.db_manager.get_database_stats()
            st.metric("Total Files Processed", stats.get('total_files', 0))
            st.metric("Pending Reviews", stats.get('pending_reviews', 0))
            st.metric("Vector Embeddings", stats.get('total_embeddings', 0))
        except Exception as e:
            st.error(f"Failed to load database stats: {str(e)}")
    
    with col2:
        st.subheader("System Actions")
        if st.button("Clear All Data", type="secondary"):
            if st.checkbox("I understand this will delete all data"):
                try:
                    st.session_state.db_manager.clear_all_data()
                    st.session_state.vector_storage.clear_all_vectors()
                    st.success("All data cleared successfully")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to clear data: {str(e)}")
        
        if st.button("Rebuild Vector Index", type="secondary"):
            try:
                with st.spinner("Rebuilding vector index..."):
                    st.session_state.vector_storage.rebuild_index()
                st.success("Vector index rebuilt successfully")
            except Exception as e:
                st.error(f"Failed to rebuild index: {str(e)}")
    with col3:
        st.subheader("API Keys")
        config = get_config()
        current_key = config.get("OPENAI_API_KEY", "")
        new_key = st.text_input("OpenAI API Key", value=current_key, type="password")

        if st.button("Save API Key"):
            try:
                update_config("OPENAI_API_KEY", new_key)
                load_dotenv(override=True)
                st.success("✅ OpenAI API Key saved to .env successfully")
            except Exception as e:
                st.error(f"❌ Failed to save key: {e}")
               

if __name__ == "__main__":
    main()