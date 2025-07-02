import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

# Try importing pandas with fallback
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

from a_core.a_fileflow.aa05_database import DatabaseManager
from a_core.e_utils.ae02_logging_utils import LoggingUtils

class ActivityTimeline:
    """Component for displaying activity timeline and system logs"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = LoggingUtils()
        
        # Activity type colors and icons for better visualization
        self.activity_styles = {
            'file_processed': {'icon': '📄', 'color': '#28a745'},
            'monitoring_started': {'icon': '▶️', 'color': '#007bff'},
            'monitoring_stopped': {'icon': '⏹️', 'color': '#6c757d'},
            'ai_analysis_complete': {'icon': '🧠', 'color': '#17a2b8'},
            'embedding_stored': {'icon': '🔗', 'color': '#fd7e14'},
            'context_updated': {'icon': '🔄', 'color': '#20c997'},
            'error': {'icon': '❌', 'color': '#dc3545'},
            'user_action': {'icon': '👤', 'color': '#6f42c1'},
            'performance': {'icon': '⚡', 'color': '#ffc107'},
            'database_initialized': {'icon': '🗄️', 'color': '#28a745'},
            'file_operation': {'icon': '📁', 'color': '#fd7e14'},
            'ai_operation': {'icon': '🤖', 'color': '#e83e8c'}
        }
    
    def render(self):
        """Render the activity timeline interface"""
        st.header("📈 Activity Timeline")
        
        # Timeline controls
        self._render_timeline_controls()
        
        # Activity statistics
        self._render_activity_stats()
        
        # Main timeline display
        self._render_timeline()
        
        # Activity search and filters
        self._render_activity_search()
    
    def _render_timeline_controls(self):
        """Render timeline control options"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            time_range = st.selectbox(
                "Time Range",
                options=[
                    ("Last Hour", 1/24),
                    ("Last 6 Hours", 6/24),
                    ("Last 24 Hours", 1),
                    ("Last 3 Days", 3),
                    ("Last Week", 7),
                    ("Last Month", 30)
                ],
                index=2,  # Default to "Last 24 Hours"
                format_func=lambda x: x[0]
            )
            
            st.session_state.timeline_days = time_range[1]
        
        with col2:
            activity_types = self._get_available_activity_types()
            selected_types = st.multiselect(
                "Filter by Activity Type",
                options=activity_types,
                default=[],
                help="Leave empty to show all activity types"
            )
            
            st.session_state.timeline_filters = selected_types
        
        with col3:
            auto_refresh = st.checkbox(
                "Auto-refresh",
                value=False,
                help="Automatically refresh timeline every 30 seconds"
            )
            
            if auto_refresh:
                # Auto-refresh every 30 seconds
                import time
                time.sleep(30)
                st.rerun()
    
    def _render_activity_stats(self):
        """Render activity statistics overview"""
        try:
            days = st.session_state.get('timeline_days', 1)
            activities = self.db_manager.get_activity_timeline(int(days))
            
            if not activities:
                st.info("No activities found for the selected time range.")
                return
            
            # Calculate statistics
            stats = self._calculate_activity_stats(activities)
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Activities", stats['total_activities'])
            
            with col2:
                st.metric("Files Processed", stats['files_processed'])
            
            with col3:
                st.metric("Errors", stats['error_count'])
            
            with col4:
                st.metric("AI Operations", stats['ai_operations'])
            
            # Activity breakdown chart
            if stats['activity_breakdown']:
                st.subheader("Activity Breakdown")
                if PANDAS_AVAILABLE and pd is not None:
                    breakdown_df = pd.DataFrame([
                        {'Activity Type': k, 'Count': v} 
                        for k, v in stats['activity_breakdown'].items()
                    ])
                    st.bar_chart(breakdown_df.set_index('Activity Type'))
                else:
                    # Fallback display without pandas
                    for activity_type, count in stats['activity_breakdown'].items():
                        st.write(f"• **{activity_type}**: {count}")
                
        except Exception as e:
            st.error(f"Error loading activity statistics: {str(e)}")
    
    def _render_timeline(self):
        """Render the main activity timeline"""
        try:
            days = st.session_state.get('timeline_days', 1)
            filters = st.session_state.get('timeline_filters', [])
            
            activities = self.db_manager.get_activity_timeline(int(days))
            
            if not activities:
                st.info("No activities found for the selected time range.")
                return
            
            # Apply filters
            if filters:
                activities = [a for a in activities if a['activity_type'] in filters]
            
            if not activities:
                st.info("No activities match the selected filters.")
                return
            
            st.subheader(f"Timeline ({len(activities)} activities)")
            
            # Group activities by date for better organization
            grouped_activities = self._group_activities_by_date(activities)
            
            for date, daily_activities in grouped_activities.items():
                st.write(f"**{date}**")
                
                for activity in daily_activities:
                    self._render_activity_item(activity)
                
                st.divider()
                
        except Exception as e:
            st.error(f"Error loading timeline: {str(e)}")
    
    def _render_activity_item(self, activity: Dict[str, Any]):
        """Render a single activity item"""
        activity_type = activity['activity_type']
        style = self.activity_styles.get(activity_type, {'icon': '📋', 'color': '#6c757d'})
        
        # Parse timestamp
        try:
            timestamp = datetime.fromisoformat(activity['timestamp'])
            time_str = timestamp.strftime("%H:%M:%S")
        except:
            time_str = "Unknown"
        
        # Create the activity display
        col1, col2 = st.columns([1, 8])
        
        with col1:
            st.write(f"{style['icon']} `{time_str}`")
        
        with col2:
            # Activity description
            st.write(f"**{activity['description']}**")
            
            # Show metadata if available and relevant
            metadata = activity.get('metadata', {})
            if metadata:
                self._render_activity_metadata(activity_type, metadata)
    
    def _render_activity_metadata(self, activity_type: str, metadata: Dict[str, Any]):
        """Render activity metadata in a user-friendly way"""
        if not metadata:
            return
        
        # Customize metadata display based on activity type
        if activity_type == 'file_processed':
            if 'suggested_name' in metadata:
                st.write(f"   → Suggested name: `{metadata['suggested_name']}`")
            if 'entities' in metadata:
                entities = metadata['entities']
                if entities:
                    st.write(f"   → Entities: {', '.join(entities)}")
        
        elif activity_type == 'ai_operation':
            if 'model' in metadata:
                st.write(f"   → Model: {metadata['model']}")
            if 'tokens_used' in metadata:
                st.write(f"   → Tokens: {metadata['tokens_used']}")
        
        elif activity_type == 'performance':
            if 'duration_seconds' in metadata:
                duration = metadata['duration_seconds']
                st.write(f"   → Duration: {duration:.2f}s")
            if 'performance_level' in metadata:
                level = metadata['performance_level']
                level_emoji = {'fast': '🟢', 'normal': '🟡', 'slow': '🟠', 'very_slow': '🔴'}
                st.write(f"   → Performance: {level_emoji.get(level, '⚪')} {level}")
        
        elif activity_type == 'error':
            if 'error' in metadata:
                st.error(f"   Error details: {metadata['error']}")
        
        else:
            # Generic metadata display for other activity types
            important_keys = ['file_path', 'operation', 'status', 'count']
            for key in important_keys:
                if key in metadata:
                    st.write(f"   → {key.replace('_', ' ').title()}: `{metadata[key]}`")
    
    def _render_activity_search(self):
        """Render activity search functionality"""
        st.subheader("🔍 Search Activities")
        
        col1, col2 = st.columns(2)
        
        with col1:
            search_term = st.text_input(
                "Search in descriptions",
                placeholder="Enter search term...",
                help="Search within activity descriptions"
            )
        
        with col2:
            entity_search = st.text_input(
                "Search by entity",
                placeholder="Enter entity name...",
                help="Search for activities related to a specific entity"
            )
        
        if search_term or entity_search:
            try:
                days = st.session_state.get('timeline_days', 7)  # Broader search
                activities = self.db_manager.get_activity_timeline(int(days))
                
                # Filter activities based on search terms
                filtered_activities = []
                
                for activity in activities:
                    match = False
                    
                    # Search in description
                    if search_term and search_term.lower() in activity['description'].lower():
                        match = True
                    
                    # Search in metadata for entity
                    if entity_search:
                        metadata = activity.get('metadata', {})
                        if isinstance(metadata, dict):
                            # Check entities in metadata
                            entities = metadata.get('entities', [])
                            if isinstance(entities, list):
                                for entity in entities:
                                    if entity_search.lower() in str(entity).lower():
                                        match = True
                                        break
                    
                    if match:
                        filtered_activities.append(activity)
                
                if filtered_activities:
                    st.write(f"**Found {len(filtered_activities)} matching activities:**")
                    
                    # Display results
                    for activity in filtered_activities[:20]:  # Limit to 20 results
                        self._render_activity_item(activity)
                else:
                    st.info("No activities found matching your search criteria.")
                    
            except Exception as e:
                st.error(f"Error searching activities: {str(e)}")
    
    def _get_available_activity_types(self) -> List[str]:
        """Get list of available activity types from database"""
        try:
            activities = self.db_manager.get_activity_timeline(30)  # Last 30 days
            activity_types = list(set(a['activity_type'] for a in activities))
            return sorted(activity_types)
        except Exception:
            return list(self.activity_styles.keys())
    
    def _calculate_activity_stats(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics from activities list"""
        stats = {
            'total_activities': len(activities),
            'files_processed': 0,
            'error_count': 0,
            'ai_operations': 0,
            'activity_breakdown': {}
        }
        
        for activity in activities:
            activity_type = activity['activity_type']
            
            # Count by type
            stats['activity_breakdown'][activity_type] = \
                stats['activity_breakdown'].get(activity_type, 0) + 1
            
            # Specific counters
            if activity_type == 'file_processed':
                stats['files_processed'] += 1
            elif activity_type == 'error':
                stats['error_count'] += 1
            elif activity_type in ['ai_analysis_complete', 'ai_operation']:
                stats['ai_operations'] += 1
        
        return stats
    
    def _group_activities_by_date(self, activities: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group activities by date for better timeline organization"""
        grouped = {}
        
        for activity in activities:
            try:
                timestamp = datetime.fromisoformat(activity['timestamp'])
                date_key = timestamp.strftime("%Y-%m-%d (%A)")
            except:
                date_key = "Unknown Date"
            
            if date_key not in grouped:
                grouped[date_key] = []
            
            grouped[date_key].append(activity)
        
        # Sort dates in descending order (most recent first)
        sorted_dates = sorted(grouped.keys(), reverse=True)
        return {date: grouped[date] for date in sorted_dates}
