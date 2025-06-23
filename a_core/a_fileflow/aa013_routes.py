# src/fileflow/routes.py
from flask import render_template, redirect, url_for, flash, Blueprint

# Define the Blueprint.
# 'fileflow' is the blueprint's name.
# '__name__' tells Flask where to find the blueprint's resources.
# 'template_folder' specifies the relative path to the templates for this blueprint.
# It goes up two levels from src/fileflow/ to the project root, then into 'templates'.
fileflow_bp = Blueprint('fileflow', __name__, template_folder='../../templates')

@fileflow_bp.route('/')
def home():
    """
    Handles the root URL for the entire application.
    This can be redirected to a more specific landing page or dashboard.
    """
    return "🚀 QiLife is alive and running!"

@fileflow_bp.route('/fileflow')
def fileflow_home():
    """
    Renders the main FileFlow dashboard page.
    This is where the user will interact with file operations.
    """
    return render_template('fileflow.html')

@fileflow_bp.route('/fileflow/rename', methods=['POST'])
def trigger_rename():
    """
    Handles the POST request for triggering a file renaming operation.
    Currently, it flashes a message and redirects back to the FileFlow home.
    """
    flash("🌀 Rename triggered (logic not wired yet)", "info")
    # Redirect back to the blueprint's fileflow_home route
    return redirect(url_for('fileflow.fileflow_home'))

@fileflow_bp.route('/fileflow/create-folders', methods=['POST'])
def trigger_create_folders():
    """
    Handles the POST request for triggering a folder creation operation.
    Currently, it flashes a message and redirects back to the FileFlow home.
    """
    flash("📁 Folder creation triggered (logic not wired yet)", "info")
    # Redirect back to the blueprint's fileflow_home route
    return redirect(url_for('fileflow.fileflow_home'))

@fileflow_bp.route('/fileflow/merge-folders', methods=['POST'])
def trigger_merge_folders():
    """
    Handles the POST request for triggering a folder merging operation.
    Currently, it flashes a message and redirects back to the FileFlow home.
    """
    flash("🧩 Merge triggered (logic not wired yet)", "info")
    # Redirect back to the blueprint's fileflow_home route
    return redirect(url_for('fileflow.fileflow_home'))

