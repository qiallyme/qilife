import streamlit as st
from pathlib import Path
from typing import List, Dict, Any
import os

# Try importing pandas with fallback
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

from core.database import DatabaseManager
from utils.file_utils import FileUtils

class FileReview:
    """Component for reviewing and approving file rename suggestions"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def render(self):
        """Render the file review interface"""
        st.header("📋 File Review & Approval")
        
        # Get pending reviews
        pending_files = self.db_manager.get_pending_reviews()
        
        if not pending_files:
            st.info("No files pending review! All processed files have been reviewed.")
            self._render_processed_files_summary()
            return
        
        st.write(f"**{len(pending_files)} files** are waiting for your review:")
        
        # Bulk spreadsheet-style interface
        self._render_bulk_approval_table(pending_files)
        
        st.divider()
        
        # Quick batch actions
        self._render_batch_actions(pending_files)
        
        # Individual file review (collapsed by default)
        with st.expander("Individual File Review (Advanced)", expanded=False):
            self._render_individual_review(pending_files)
    
    def _render_bulk_approval_table(self, pending_files: List[Dict[str, Any]]):
        """Render spreadsheet-like bulk approval interface"""
        st.subheader("Bulk File Review")
        
        # Initialize session state for selections
        if 'selected_files' not in st.session_state:
            st.session_state.selected_files = {}
        if 'custom_names' not in st.session_state:
            st.session_state.custom_names = {}
        
        # Header row
        col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 2, 2.5, 1.5, 1, 1, 1])
        with col1:
            st.write("**Select**")
        with col2:
            st.write("**Original Name**")
        with col3:
            st.write("**Suggested Name**")
        with col4:
            st.write("**Entities**")
        with col5:
            st.write("**Confidence**")
        with col6:
            st.write("**Action**")
        with col7:
            st.write("**Custom Name**")
        
        st.divider()
        
        # File rows
        for file_data in pending_files:
            file_id = file_data['id']
            col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 2, 2.5, 1.5, 1, 1, 1])
            
            with col1:
                # Checkbox for selection
                selected = st.checkbox(
                    "", 
                    key=f"select_{file_id}",
                    value=st.session_state.selected_files.get(file_id, False)
                )
                st.session_state.selected_files[file_id] = selected
            
            with col2:
                # Original name (truncated if too long)
                original = file_data['original_name']
                if len(original) > 25:
                    st.write(f"**{original[:22]}...**")
                    st.caption(original)
                else:
                    st.write(f"**{original}**")
            
            with col3:
                # Suggested name (editable)
                suggested = st.text_input(
                    "",
                    value=file_data['suggested_name'],
                    key=f"suggested_{file_id}",
                    label_visibility="collapsed"
                )
            
            with col4:
                # Entities
                entities = ', '.join(file_data['entities']) if file_data['entities'] else 'None'
                if len(entities) > 20:
                    st.write(f"{entities[:17]}...")
                    st.caption(entities)
                else:
                    st.write(entities)
            
            with col5:
                # Confidence with color coding
                confidence = file_data['confidence']
                if confidence >= 0.9:
                    st.success(f"{confidence:.2f}")
                elif confidence >= 0.7:
                    st.warning(f"{confidence:.2f}")
                else:
                    st.error(f"{confidence:.2f}")
            
            with col6:
                # Quick action buttons
                col6a, col6b = st.columns(2)
                with col6a:
                    if st.button("Approve", key=f"approve_{file_id}", help="Approve this file"):
                        self.db_manager.approve_file_rename(file_id, suggested)
                        st.rerun()
                with col6b:
                    if st.button("Reject", key=f"reject_{file_id}", help="Reject this file"):
                        self.db_manager.reject_file_rename(file_id)
                        st.rerun()
            
            with col7:
                # Custom name option
                custom_name = st.text_input(
                    "",
                    key=f"custom_{file_id}",
                    placeholder="Custom name...",
                    label_visibility="collapsed"
                )
                if custom_name:
                    st.session_state.custom_names[file_id] = custom_name
        
        # Bulk action buttons at bottom
        st.divider()
        selected_count = sum(1 for selected in st.session_state.selected_files.values() if selected)
        
        if selected_count > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button(f"Approve Selected ({selected_count})", type="primary"):
                    self._approve_selected_files(pending_files)
                    st.rerun()
            
            with col2:
                if st.button(f"Reject Selected ({selected_count})", type="secondary"):
                    self._reject_selected_files(pending_files)
                    st.rerun()
            
            with col3:
                if st.button("Select All"):
                    for file_data in pending_files:
                        st.session_state.selected_files[file_data['id']] = True
                    st.rerun()
            
            with col4:
                if st.button("Clear Selection"):
                    st.session_state.selected_files = {}
                    st.rerun()
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Select All"):
                    for file_data in pending_files:
                        st.session_state.selected_files[file_data['id']] = True
                    st.rerun()
    
    def _approve_selected_files(self, pending_files: List[Dict[str, Any]]):
        """Approve selected files"""
        approved_count = 0
        for file_data in pending_files:
            file_id = file_data['id']
            if st.session_state.selected_files.get(file_id, False):
                # Use custom name if provided, otherwise use suggested name from form
                custom_name = st.session_state.custom_names.get(file_id)
                suggested_name = st.session_state.get(f"suggested_{file_id}", file_data['suggested_name'])
                final_name = custom_name if custom_name else suggested_name
                
                self.db_manager.approve_file_rename(file_id, final_name)
                approved_count += 1
        
        st.success(f"Approved {approved_count} files")
        # Clear selections
        st.session_state.selected_files = {}
        st.session_state.custom_names = {}
    
    def _reject_selected_files(self, pending_files: List[Dict[str, Any]]):
        """Reject selected files"""
        rejected_count = 0
        for file_data in pending_files:
            file_id = file_data['id']
            if st.session_state.selected_files.get(file_id, False):
                self.db_manager.reject_file_rename(file_id)
                rejected_count += 1
        
        st.success(f"Rejected {rejected_count} files")  
        # Clear selections
        st.session_state.selected_files = {}

    def _render_batch_actions(self, pending_files: List[Dict[str, Any]]):
        """Render batch action controls"""
        st.subheader("Quick Batch Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Approve All", type="primary"):
                self._approve_all_files(pending_files)
                st.rerun()
        
        with col2:
            if st.button("Reject All", type="secondary"):
                self._reject_all_files(pending_files)
                st.rerun()
        
        with col3:
            confidence_threshold = st.slider(
                "Auto-approve above confidence:", 
                min_value=0.5, 
                max_value=1.0, 
                value=0.9, 
                step=0.05
            )
            
        with col4:
            if st.button(f"Auto-approve ≥{confidence_threshold:.0%}"):
                approved_count = self._auto_approve_by_confidence(pending_files, confidence_threshold)
                st.success(f"Auto-approved {approved_count} files")
                st.rerun()
    
    def _render_individual_review(self, pending_files: List[Dict[str, Any]]):
        """Render individual file review interface"""
        st.subheader("Individual File Review")
        
        if PANDAS_AVAILABLE and pd is not None:
            # Create DataFrame for better display
            df_data = []
            for file_data in pending_files:
                df_data.append({
                    'ID': file_data['id'],
                    'Original Name': file_data['original_name'],
                    'Suggested Name': file_data['suggested_name'],
                    'Entities': ', '.join(file_data['entities']) if file_data['entities'] else 'None',
                    'Confidence': f"{file_data['confidence']:.2f}",
                    'Created': file_data['created_at'][:19]  # Remove microseconds
                })
            
            df = pd.DataFrame(df_data)
            
            # Display interactive table
            if not df.empty:
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # File selection for detailed review
                selected_file_id = st.selectbox(
                    "Select file for detailed review:",
                    options=[f"{row['ID']} - {row['Original Name']}" for _, row in df.iterrows()],
                    index=0 if not df.empty else None
                )
        else:
            # Fallback display without pandas
            st.write("**Files pending review:**")
            for i, file_data in enumerate(pending_files):
                with st.expander(f"{file_data['original_name']} (ID: {file_data['id']})"):
                    st.write(f"**Suggested Name:** {file_data['suggested_name']}")
                    st.write(f"**Entities:** {', '.join(file_data['entities']) if file_data['entities'] else 'None'}")
                    st.write(f"**Confidence:** {file_data['confidence']:.2f}")
                    st.write(f"**Created:** {file_data['created_at'][:19]}")
            
            # File selection for detailed review
            file_options = [f"{file_data['id']} - {file_data['original_name']}" for file_data in pending_files]
            selected_file_id = st.selectbox(
                "Select file for detailed review:",
                options=file_options,
                index=0 if file_options else None
            )
            
            if selected_file_id:
                file_id = int(selected_file_id.split(' - ')[0])
                self._render_detailed_file_review(pending_files, file_id)
    
    def _render_detailed_file_review(self, pending_files: List[Dict[str, Any]], file_id: int):
        """Render detailed review for a specific file"""
        # Find the selected file
        selected_file = None
        for file_data in pending_files:
            if file_data['id'] == file_id:
                selected_file = file_data
                break
        
        if not selected_file:
            st.error("File not found")
            return
        
        st.divider()
        st.subheader(f"📄 Reviewing: {selected_file['original_name']}")
        
        # File information
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Original Information:**")
            st.write(f"• **File Path:** `{selected_file['file_path']}`")
            st.write(f"• **Original Name:** `{selected_file['original_name']}`")
            
            # Check if file still exists
            if os.path.exists(selected_file['file_path']):
                file_info = FileUtils.get_file_info(selected_file['file_path'])
                st.write(f"• **File Size:** {file_info.get('size_mb', 'Unknown')} MB")
                st.write(f"• **Modified:** {file_info.get('modified_date', 'Unknown')}")
                st.success("✅ File exists")
            else:
                st.error("❌ File no longer exists")
        
        with col2:
            st.write("**AI Analysis:**")
            st.write(f"• **Suggested Name:** `{selected_file['suggested_name']}`")
            st.write(f"• **Confidence:** {selected_file['confidence']:.2f}")
            st.write(f"• **Entities:** {', '.join(selected_file['entities']) if selected_file['entities'] else 'None'}")
        
        # AI Reasoning
        if selected_file['reasoning']:
            st.write("**AI Reasoning:**")
            st.info(selected_file['reasoning'])
        
        # Custom name input
        st.write("**Review Options:**")
        custom_name = st.text_input(
            "Custom name (optional):",
            value=selected_file['suggested_name'],
            help="Modify the suggested name if needed"
        )
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Approve", key=f"approve_{file_id}", type="primary"):
                final_name = custom_name if custom_name != selected_file['suggested_name'] else None
                self.db_manager.approve_file_rename(file_id, final_name)
                
                # Perform the actual file rename if file exists
                if os.path.exists(selected_file['file_path']):
                    new_name = custom_name if custom_name else selected_file['suggested_name']
                    if FileUtils.safe_rename_file(selected_file['file_path'], new_name):
                        st.success(f"✅ File approved and renamed to: {new_name}")
                    else:
                        st.warning("⚠️ File approved but rename failed - file may be in use")
                else:
                    st.success("✅ File approved (original file no longer exists)")
                
                st.rerun()
        
        with col2:
            if st.button("❌ Reject", key=f"reject_{file_id}", type="secondary"):
                self.db_manager.reject_file_rename(file_id)
                st.success("❌ File rename rejected")
                st.rerun()
        
        with col3:
            if st.button("⏭️ Skip", key=f"skip_{file_id}"):
                st.info("Skipped - file remains in pending status")
    
    def _render_processed_files_summary(self):
        """Show summary of already processed files"""
        st.subheader("📊 Processing Summary")
        
        try:
            stats = self.db_manager.get_database_stats()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Files Processed", stats.get('total_files', 0))
            
            with col2:
                approved_count = stats.get('total_files', 0) - stats.get('pending_reviews', 0)
                st.metric("Files Approved", approved_count)
            
            with col3:
                st.metric("Pending Reviews", stats.get('pending_reviews', 0))
                
        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")
    
    def _approve_all_files(self, pending_files: List[Dict[str, Any]]):
        """Approve all pending files"""
        for file_data in pending_files:
            try:
                self.db_manager.approve_file_rename(file_data['id'])
                
                # Attempt to rename the actual file
                if os.path.exists(file_data['file_path']):
                    FileUtils.safe_rename_file(
                        file_data['file_path'],
                        file_data['suggested_name']
                    )
            except Exception as e:
                st.error(f"Error approving file {file_data['original_name']}: {str(e)}")
    
    def _reject_all_files(self, pending_files: List[Dict[str, Any]]):
        """Reject all pending files"""
        for file_data in pending_files:
            try:
                self.db_manager.reject_file_rename(file_data['id'])
            except Exception as e:
                st.error(f"Error rejecting file {file_data['original_name']}: {str(e)}")
    
    def _auto_approve_by_confidence(self, pending_files: List[Dict[str, Any]], 
                                   threshold: float) -> int:
        """Auto-approve files with confidence above threshold"""
        approved_count = 0
        
        for file_data in pending_files:
            if file_data['confidence'] >= threshold:
                try:
                    self.db_manager.approve_file_rename(file_data['id'])
                    
                    # Attempt to rename the actual file
                    if os.path.exists(file_data['file_path']):
                        FileUtils.safe_rename_file(
                            file_data['file_path'],
                            file_data['suggested_name']
                        )
                    
                    approved_count += 1
                    
                except Exception as e:
                    st.error(f"Error auto-approving file {file_data['original_name']}: {str(e)}")
        
        return approved_count
