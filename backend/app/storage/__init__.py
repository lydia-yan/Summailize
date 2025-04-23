from backend.app.storage.db import db

# Check Firestore connectivity (e.g., try to list collections)
try:
    list(db.collections())  # simple ping
    print("Firestore connection test passed in __init__.py")
except Exception as e:
    print("Firestore connection failed:", str(e))
    raise