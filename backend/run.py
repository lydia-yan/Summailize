from app import create_app

app = create_app()

if __name__ == '__main__':
    # Run the application in development mode
    app.run(debug=True, host='0.0.0.0', port=8000) 