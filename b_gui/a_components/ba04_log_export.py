import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
import csv
import io

# Try importing pandas with fallback
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

from core.database import DatabaseManager
from utils.logging_utils import LoggingUtils

class LogExport:
    """Component for exporting logs and activity data"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = LoggingUtils()
    
    def render(self):
        """Render the log export interface"""
        st.header("📤 Export Logs")
        
        # Export options
        self._render_export_options()
        
        # Export preview
        self._render_export_preview()
        
        # Export statistics
        self._render_export_stats()
    
    def _render_export_options(self):
        """Render export configuration options"""
        st.subheader("Export Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Time range selection
            export_range = st.selectbox(
                "Time Range",
                options=[
                    ("Last Hour", 1/24),
                    ("Last 6 Hours", 6/24),
                    ("Last 24 Hours", 1),
                    ("Last 3 Days", 3),
                    ("Last Week", 7),
                    ("Last Month", 30),
                    ("All Time", None)
                ],
                index=3,  # Default to "Last 3 Days"
                format_func=lambda x: x[0]
            )
            
            # Format selection
            export_format = st.selectbox(
                "Export Format",
                options=["CSV", "JSON", "Excel"],
                index=0
            )
        
        with col2:
            # Data type selection
            data_types = st.multiselect(
                "Data to Export",
                options=[
                    "Activity Log",
                    "File Analysis",
                    "Entity Data",
                    "Performance Metrics",
                    "Error Log"
                ],
                default=["Activity Log"],
                help="Select what data to include in the export"
            )
            
            # Activity type filters
            activity_types = self._get_available_activity_types()
            selected_activity_types = st.multiselect(
                "Filter Activity Types",
                options=activity_types,
                default=[],
                help="Leave empty to include all activity types"
            )
        
        # Export actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Preview Export", type="secondary"):
                self._generate_preview(export_range[1], data_types, selected_activity_types)
        
        with col2:
            if st.button("📥 Download Export", type="primary"):
                self._generate_download(
                    export_range[1], 
                    export_format, 
                    data_types, 
                    selected_activity_types
                )
        
        with col3:
            if st.button("📧 Schedule Export", type="secondary"):
                st.info("⚠️ Scheduled exports not implemented yet")
    
    def _render_export_preview(self):
        """Render export preview"""
        if 'export_preview' in st.session_state:
            st.subheader("📋 Export Preview")
            
            preview_data = st.session_state.export_preview
            
            if preview_data:
                # Show summary
                st.write(f"**Records to export:** {len(preview_data)}")
                
                # Convert to DataFrame for display
                if isinstance(preview_data, list) and preview_data:
                    if PANDAS_AVAILABLE and pd is not None:
                        df = pd.DataFrame(preview_data)
                        
                        # Show first few rows
                        st.write("**First 10 rows:**")
                        st.dataframe(df.head(10), use_container_width=True)
                        
                        # Show column information
                        st.write("**Columns:**")
                        for col in df.columns:
                            st.write(f"• {col} ({df[col].dtype})")
                    else:
                        # Fallback display without pandas
                        st.write("**First 10 rows:**")
                        for i, row in enumerate(preview_data[:10]):
                            with st.expander(f"Row {i+1}"):
                                for key, value in row.items():
                                    st.write(f"**{key}:** {value}")
                else:
                    st.info("No data to preview")
            else:
                st.info("No data available for the selected criteria")
    
    def _render_export_stats(self):
        """Render export statistics"""
        st.subheader("📊 Export Statistics")
        
        try:
            # Get database statistics
            stats = self.db_manager.get_database_stats()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Files", stats.get('total_files', 0))
            
            with col2:
                st.metric("Total Activities", stats.get('total_activities', 0))
            
            with col3:
                st.metric("Total Entities", stats.get('total_entities', 0))
            
            with col4:
                # Calculate total exportable records
                total_exportable = (
                    stats.get('total_files', 0) + 
                    stats.get('total_activities', 0) + 
                    stats.get('total_entities', 0)
                )
                st.metric("Exportable Records", total_exportable)
            
            # Recent export activity
            self._show_recent_exports()
            
        except Exception as e:
            st.error(f"Error loading export statistics: {str(e)}")
    
    def _generate_preview(self, days: Optional[float], data_types: list, activity_filters: list):
        """Generate preview of export data"""
        try:
            export_data = []
            
            if "Activity Log" in data_types:
                activities = self._get_activity_data(days, activity_filters)
                export_data.extend(activities)
            
            if "File Analysis" in data_types:
                file_data = self._get_file_analysis_data()
                export_data.extend(file_data)
            
            if "Entity Data" in data_types:
                entity_data = self._get_entity_data()
                export_data.extend(entity_data)
            
            if "Performance Metrics" in data_types:
                perf_data = self._get_performance_data(days)
                export_data.extend(perf_data)
            
            if "Error Log" in data_types:
                error_data = self._get_error_data(days)
                export_data.extend(error_data)
            
            st.session_state.export_preview = export_data
            st.success(f"Preview generated: {len(export_data)} records")
            st.rerun()
            
        except Exception as e:
            st.error(f"Error generating preview: {str(e)}")
    
    def _generate_download(self, days: Optional[float], format_type: str, 
                          data_types: list, activity_filters: list):
        """Generate and offer download of export data"""
        try:
            # Generate the data
            export_data = []
            
            if "Activity Log" in data_types:
                activities = self._get_activity_data(days, activity_filters)
                export_data.extend(activities)
            
            if "File Analysis" in data_types:
                file_data = self._get_file_analysis_data()
                export_data.extend(file_data)
            
            if "Entity Data" in data_types:
                entity_data = self._get_entity_data()
                export_data.extend(entity_data)
            
            if "Performance Metrics" in data_types:
                perf_data = self._get_performance_data(days)
                export_data.extend(perf_data)
            
            if "Error Log" in data_types:
                error_data = self._get_error_data(days)
                export_data.extend(error_data)
            
            if not export_data:
                st.warning("No data to export")
                return
            
            # Convert to requested format
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format_type == "CSV":
                if PANDAS_AVAILABLE and pd is not None:
                    df = pd.DataFrame(export_data)
                    csv_data = df.to_csv(index=False)
                else:
                    # Fallback CSV generation without pandas
                    output = io.StringIO()
                    if export_data:
                        fieldnames = list(export_data[0].keys())
                        writer = csv.DictWriter(output, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(export_data)
                    csv_data = output.getvalue()
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"second_brain_export_{timestamp}.csv",
                    mime="text/csv"
                )
            
            elif format_type == "JSON":
                json_data = json.dumps(export_data, indent=2, default=str)
                
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name=f"second_brain_export_{timestamp}.json",
                    mime="application/json"
                )
            
            elif format_type == "Excel":
                if PANDAS_AVAILABLE and pd is not None:
                    df = pd.DataFrame(export_data)
                    
                    # Create Excel file in memory
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Export', index=False)
                    
                    st.download_button(
                        label="📥 Download Excel",
                        data=output.getvalue(),
                        file_name=f"second_brain_export_{timestamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error("Excel export requires pandas library which is not available. Please use CSV or JSON format instead.")
            
            # Log the export
            self.logger.log_activity(
                "data_export",
                f"Data exported: {len(export_data)} records in {format_type} format",
                {
                    "record_count": len(export_data),
                    "format": format_type,
                    "data_types": data_types,
                    "days_range": days
                }
            )
            
            st.success(f"✅ Export ready! {len(export_data)} records in {format_type} format")
            
        except Exception as e:
            st.error(f"Error generating export: {str(e)}")
            self.logger.log_error("export_error", str(e), {"format": format_type})
    
    def _get_activity_data(self, days: Optional[float], activity_filters: list) -> list:
        """Get activity log data for export"""
        try:
            if days is None:
                # Get all activities - we'll limit to reasonable amount
                activities = self.db_manager.get_activity_timeline(365)  # Last year max
            else:
                activities = self.db_manager.get_activity_timeline(int(days))
            
            # Apply activity type filters
            if activity_filters:
                activities = [a for a in activities if a['activity_type'] in activity_filters]
            
            # Flatten the data for export
            export_data = []
            for activity in activities:
                row = {
                    'timestamp': activity['timestamp'],
                    'activity_type': activity['activity_type'],
                    'description': activity['description'],
                    'data_type': 'activity_log'
                }
                
                # Add metadata fields
                metadata = activity.get('metadata', {})
                if isinstance(metadata, dict):
                    for key, value in metadata.items():
                        if isinstance(value, (str, int, float, bool)):
                            row[f'metadata_{key}'] = value
                        else:
                            row[f'metadata_{key}'] = str(value)
                
                export_data.append(row)
            
            return export_data
            
        except Exception as e:
            self.logger.log_error("activity_export_error", str(e))
            return []
    
    def _get_file_analysis_data(self) -> list:
        """Get file analysis data for export"""
        try:
            # This would need to be implemented in DatabaseManager
            # For now, return empty list
            return []
        except Exception as e:
            self.logger.log_error("file_export_error", str(e))
            return []
    
    def _get_entity_data(self) -> list:
        """Get entity data for export"""
        try:
            entities = self.db_manager.get_all_entities()
            
            export_data = []
            for entity in entities:
                row = {
                    'data_type': 'entity',
                    'entity_name': entity['entity_name'],
                    'usage_count': entity['usage_count'],
                    'first_seen': entity['first_seen'],
                    'last_seen': entity['last_seen'],
                    'variations': ', '.join(entity['variations']) if entity['variations'] else ''
                }
                export_data.append(row)
            
            return export_data
            
        except Exception as e:
            self.logger.log_error("entity_export_error", str(e))
            return []
    
    def _get_performance_data(self, days: Optional[float]) -> list:
        """Get performance metrics for export"""
        try:
            if days is None:
                activities = self.db_manager.get_activity_timeline(365)
            else:
                activities = self.db_manager.get_activity_timeline(int(days))
            
            # Filter for performance activities
            perf_activities = [a for a in activities if a['activity_type'] == 'performance']
            
            export_data = []
            for activity in perf_activities:
                metadata = activity.get('metadata', {})
                row = {
                    'timestamp': activity['timestamp'],
                    'data_type': 'performance',
                    'operation': metadata.get('operation', 'unknown'),
                    'duration_seconds': metadata.get('duration_seconds', 0),
                    'performance_level': metadata.get('performance_level', 'unknown'),
                    'description': activity['description']
                }
                export_data.append(row)
            
            return export_data
            
        except Exception as e:
            self.logger.log_error("performance_export_error", str(e))
            return []
    
    def _get_error_data(self, days: Optional[float]) -> list:
        """Get error log data for export"""
        try:
            if days is None:
                activities = self.db_manager.get_activity_timeline(365)
            else:
                activities = self.db_manager.get_activity_timeline(int(days))
            
            # Filter for error activities
            error_activities = [a for a in activities if a['activity_type'] == 'error']
            
            export_data = []
            for activity in error_activities:
                metadata = activity.get('metadata', {})
                row = {
                    'timestamp': activity['timestamp'],
                    'data_type': 'error',
                    'error_type': metadata.get('error_type', 'unknown'),
                    'description': activity['description'],
                    'context': json.dumps(metadata) if metadata else ''
                }
                export_data.append(row)
            
            return export_data
            
        except Exception as e:
            self.logger.log_error("error_export_error", str(e))
            return []
    
    def _get_available_activity_types(self) -> list:
        """Get available activity types from recent data"""
        try:
            activities = self.db_manager.get_activity_timeline(30)  # Last 30 days
            activity_types = list(set(a['activity_type'] for a in activities))
            return sorted(activity_types)
        except Exception:
            return [
                'file_processed', 'monitoring_started', 'monitoring_stopped',
                'ai_analysis_complete', 'error', 'user_action', 'performance'
            ]
    
    def _show_recent_exports(self):
        """Show recent export activities"""
        try:
            # Get recent export activities
            activities = self.db_manager.get_activity_timeline(7)  # Last week
            export_activities = [a for a in activities if a['activity_type'] == 'data_export']
            
            if export_activities:
                st.write("**Recent Exports:**")
                for activity in export_activities[:5]:  # Show last 5
                    timestamp = datetime.fromisoformat(activity['timestamp'])
                    metadata = activity.get('metadata', {})
                    
                    st.write(f"• {timestamp.strftime('%Y-%m-%d %H:%M')} - "
                           f"{metadata.get('record_count', 'Unknown')} records "
                           f"({metadata.get('format', 'Unknown')} format)")
            else:
                st.info("No recent exports")
                
        except Exception as e:
            st.error(f"Error loading recent exports: {str(e)}")
