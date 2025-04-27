import sys
import os
import atexit  # add atexit module
from dotenv import load_dotenv


# add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from flask_cors import CORS
from app.api.routes import api  # import the Flask Blueprint
from app.storage.db import db  # ensure the database is loaded early
from app.scheduler.task_scheduler import start_scheduler, stop_scheduler

load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # 開發環境暫時允許 HTTP（推薦開發用）


# add CORS support, allow Chrome extension to send requests
CORS(app, resources={r"/api/*": {"origins": ["*", "chrome-extension://bgfhhdhlljldlnmjfpndoeglimej"]}})

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

# use atexit to ensure the scheduler is stopped when the application exits
def cleanup_before_exit():
    try:
        stop_scheduler()
        print("Email summary scheduler stopped on application exit")
    except Exception as e:
        print("Error stopping scheduler on exit:", e)

# register the exit handler
atexit.register(cleanup_before_exit)

# define the cleanup tasks when the application shuts down
@app.teardown_appcontext
def shutdown_tasks(exception=None):
    # remove the scheduler stop code, avoid stopping the scheduler on each request
    pass

if __name__ == "__main__":
    # initialize the application
    init_db_and_scheduler()
    app.run(debug=True, host='0.0.0.0', port=8000)