from flask import Flask, redirect, request, session, jsonify

app = FastAPI()


# initialize task to connect the databse
@app.on_event("startup")
def init_tasks():
    # check the connection of the database
    try:
        list(db.collections()) 
        print("Firestore is connected")
    except Exception as e:
        print("Failed to connect to Firestore:", e)
        raise