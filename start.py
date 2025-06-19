# start.py (Your main Flask application file)
from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# Set a secret key for session management and flashing messages.
# It's highly recommended to store this in an environment variable for production.
app.secret_key = os.getenv("FLASK_SECRET", "a_very_secret_and_complex_fallback_key")

# Import and register the fileflow Blueprint.
# This connects all routes defined in src/fileflow/routes.py to your main app.
from src.fileflow.routes import fileflow_bp
app.register_blueprint(fileflow_bp)

# You can still define root-level routes here if needed,
# but avoid duplicating paths defined in blueprints.
# For example, if the Blueprint already handles '/', do not define it here again.

if __name__ == "__main__":
    # Run the Flask development server.
    # In a production environment, you would use a WSGI server like Gunicorn or uWSGI.
    app.run(debug=True) # debug=True is for development only.
