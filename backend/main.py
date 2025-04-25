import sys
import os

# add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from app.api.routes import api  # import the Flask Blueprint
from app.storage.db import db  # ensure the database is loaded early
from app.scheduler.task_scheduler import start_scheduler, stop_scheduler


app = Flask(__name__)

# register the API blueprint
app.register_blueprint(api)

# define the application startup function
def init_db_and_scheduler():
    # check the database connection
    try:
        list(db.collections()) 
        print("Firestore is connected")
        
        # start the email summary scheduler
        start_scheduler()
        print("Email summary scheduler started")
    except Exception as e:
        print("Failed to connect to Firestore:", e)
        raise

# define a simple root route as a health check
@app.route('/')
def index():
    return "Email summary API service is running!"

# define the cleanup tasks when the application shuts down
@app.teardown_appcontext
def shutdown_tasks(exception=None):
    # stop the email summary scheduler
    try:
        stop_scheduler()
        print("Email summary scheduler stopped")
    except Exception as e:
        print("Error stopping scheduler:", e)

if __name__ == "__main__":
    # initialize the application
    init_db_and_scheduler()
    app.run(debug=True, host='0.0.0.0', port=8000)