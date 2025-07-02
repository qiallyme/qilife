import threading
from a_core.a_fileflow.aa011_monitor import FileMonitor

def start_monitoring(folder_path, session_state):
    print(f"[MONITOR_CONTROL] Starting monitoring on: {folder_path}")
    file_monitor = FileMonitor(
        folder_path=folder_path,
        db_manager=session_state.db_manager,
        vector_storage=session_state.vector_storage,
        context_memory=session_state.context_memory
    )
    
    monitor_thread = threading.Thread(
        target=file_monitor.start_monitoring,
        daemon=True
    )
    monitor_thread.start()

    session_state.file_monitor = file_monitor
    session_state.monitoring_active = True
    session_state.selected_folder = folder_path
    print("[MONITOR_CONTROL] Thread started.")

def stop_monitoring(session_state):
    print("[MONITOR_CONTROL] Stopping monitoring.")
    if session_state.file_monitor:
        session_state.file_monitor.stop_monitoring()
        session_state.file_monitor = None

    session_state.monitoring_active = False
    session_state.selected_folder = None
    print("[MONITOR_CONTROL] Monitoring stopped.")
