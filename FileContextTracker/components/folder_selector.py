import streamlit as st
import os
from pathlib import Path
from typing import Optional

from utils.file_utils import FileUtils

class FolderSelector:
    """Component for selecting and managing folder monitoring"""
    
    def __init__(self):
        self.supported_extensions = {
            '.pdf', '.docx', '.doc', '.txt', '.md',
            '.jpg', '.jpeg', '.png', '.bmp', '.tiff'
        }
    
    def render(self):
        """Render the folder selection interface"""
        st.header("📁 Folder Monitoring")
        
        # Folder selection section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Select Folder to Monitor")
            
            # Manual path input
            folder_path = st.text_input(
                "Folder Path",
                value=st.session_state.get('selected_folder', ''),
                placeholder="Enter the full path to the folder you want to monitor",
                help="Enter the complete path to the folder containing files you want to process"
            )
            
            # Path validation
            if folder_path:
                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    st.success(f"✅ Valid folder: {folder_path}")
                    
                    # Show folder statistics
                    self._show_folder_stats(folder_path)
                    
                    # Monitor button
                    if not st.session_state.monitoring_active:
                        if st.button("Start Monitoring", type="primary"):
                            from app import start_monitoring
                            start_monitoring(folder_path)
                            st.rerun()
                    else:
                        st.info("Currently monitoring this folder")
                        
                elif folder_path:
                    st.error("❌ Invalid folder path or folder does not exist")
            
            # Quick folder suggestions
            st.subheader("Quick Access")
            self._render_quick_folders()
        
        with col2:
            st.subheader("Monitoring Status")
            
            if st.session_state.monitoring_active:
                st.success("🟢 Active")
                st.write(f"**Folder:** `{st.session_state.selected_folder}`")
                
                if st.button("Stop Monitoring", type="secondary"):
                    from app import stop_monitoring
                    stop_monitoring()
                    st.rerun()
            else:
                st.info("🔴 Inactive")
                st.write("No folder is currently being monitored")
            
            # Supported file types
            st.subheader("Supported File Types")
            for ext in sorted(self.supported_extensions):
                st.write(f"• {ext.upper()}")
    
    def _show_folder_stats(self, folder_path: str):
        """Show statistics about the selected folder"""
        try:
            # Count files by type
            total_files = FileUtils.count_files_in_directory(folder_path)
            supported_files = FileUtils.count_files_in_directory(folder_path, self.supported_extensions)
            folder_size = FileUtils.get_directory_size(folder_path)
            
            # Display stats in metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Files", total_files)
            
            with col2:
                st.metric("Supported Files", supported_files)
            
            with col3:
                st.metric("Folder Size", FileUtils.format_file_size(folder_size))
            
            # Show file breakdown
            if supported_files > 0:
                st.subheader("File Breakdown")
                file_breakdown = self._get_file_breakdown(folder_path)
                
                for category, count in file_breakdown.items():
                    if count > 0:
                        st.write(f"• **{category.title()}**: {count} files")
                        
        except Exception as e:
            st.error(f"Error analyzing folder: {str(e)}")
    
    def _get_file_breakdown(self, folder_path: str) -> dict:
        """Get breakdown of files by category"""
        breakdown = {'documents': 0, 'images': 0, 'other': 0}
        
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_ext = Path(file).suffix.lower()
                    if file_ext in self.supported_extensions:
                        if file_ext in {'.pdf', '.docx', '.doc', '.txt', '.md'}:
                            breakdown['documents'] += 1
                        elif file_ext in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}:
                            breakdown['images'] += 1
                        else:
                            breakdown['other'] += 1
        except Exception:
            pass
        
        return breakdown
    
    def _render_quick_folders(self):
        """Render quick access to common folders"""
        common_folders = []
        
        # Add common user directories
        home_dir = Path.home()
        potential_folders = [
            home_dir / "Documents",
            home_dir / "Downloads",
            home_dir / "Desktop",
            Path.cwd(),  # Current working directory
        ]
        
        for folder in potential_folders:
            if folder.exists() and folder.is_dir():
                common_folders.append(str(folder))
        
        if common_folders:
            st.write("**Common Folders:**")
            for folder in common_folders:
                if st.button(f"📁 {Path(folder).name}", key=f"quick_{folder}"):
                    st.session_state.selected_folder = folder
                    # Update the text input by rerunning
                    st.rerun()
        
        # Allow custom folder browsing hint
        st.info("💡 **Tip:** You can also paste any folder path directly into the text field above")
    
    def validate_folder_path(self, folder_path: str) -> tuple[bool, str]:
        """Validate if the folder path is suitable for monitoring"""
        if not folder_path:
            return False, "Please enter a folder path"
        
        if not os.path.exists(folder_path):
            return False, "Folder does not exist"
        
        if not os.path.isdir(folder_path):
            return False, "Path is not a directory"
        
        if not os.access(folder_path, os.R_OK):
            return False, "No read access to folder"
        
        # Check if folder contains supported files
        supported_count = FileUtils.count_files_in_directory(folder_path, self.supported_extensions)
        if supported_count == 0:
            return True, f"Warning: No supported files found in folder (will monitor for new files)"
        
        return True, f"Ready to monitor {supported_count} supported files"
