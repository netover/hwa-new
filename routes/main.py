"""
Main Application Routes

This module defines the main application routes and initializes the Flask app.
"""

from flask import Flask, request, abort
from .api import api
from .websocket import socketio

app = Flask(__name__)
app.register_blueprint(api)

# Initialize SocketIO with the app
socketio.init_app(app)

@app.route('/login')
def login() -> str:
    return 'Login Page'

@app.route('/api/chat', methods=['POST'])
def chat() -> None:
    if request.method != 'POST':
        abort(405, description='Method Not Allowed - Use POST')
    # Process chat message"""