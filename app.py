from flask import Flask, jsonify, request, g
from flask_cors import CORS
import config
from chat_service import ChatService  # custom module
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from prompts import Prompts  # custom module

# Initialize Flask app
app = Flask(__name__)

# Load app configuration from the config module (e.g., DEV config)
app.config.from_object(config.config['DEV'])

# Enable Cross-Origin Resource Sharing (CORS)
CORS(app)

# Configure SQLite database URI for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# Initialize SQLAlchemy and Migrate for database management
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Endpoint to handle chat requests via HTTP POST
@app.post('/chat')
def home():
    # Extract data from the JSON request body
    user_prompt = request.get_json()['message']
    userid = request.get_json()['user_id']
    sender_name = request.get_json()['sender']
    
    try:
        # Retrieve chat history for the user
        chat_history = get_chat_history(userid, user_prompt, sender_name)
        
        # Generate chat response using the ChatService class
        response = ChatService.generateChatResponse(chat_history)
        
        # Prepare the response object to be returned as JSON
        res = {'sender': 'Bot', 'message': response}
        
        # Create a new Chat object and store it in the database
        new_chat = Chat(
            userid=userid,
            name=sender_name,
            request=user_prompt,
            response=response,
        )
        
        # Add the new_chat to the database session and commit changes
        db.session.add(new_chat)
        db.session.commit()
        
        # Return the response object and 200 status code for successful request
        return jsonify(res), 200
    
    except Exception as e:
        # Handle exceptions, such as token limit exceeded or rate limit exceeded
        print(e)
        if e.code == 'context_length_exceeded':
            return jsonify({'Error': 'The content length is exceeded'}), 400
        else:
            return jsonify({'error': 'The rate limit exceeded'}), 400


# Function to get chat history for a user
def get_chat_history(userid, prompt, name):
    messages = []
    messages.append(
        {
            'role': 'system',
            'content': Prompts.get_general_prompts(name),
        }
    )
    # Fetch previous chats from the database for the given user
    chats = Chat.query.filter_by(userid=userid).all()
    chats_as_dicts = [chat.__dict__ for chat in chats]
    for chat in chats_as_dicts:
        question = {}
        question['role'] = 'user'
        question['content'] = chat['request']
        messages.append(question)
    messages.append({'role': 'user', 'content': prompt})
    return messages


# Define the Chat model for the database
class Chat(db.Model):
    id = userid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, unique=False, nullable=False)
    name = db.Column(db.String, unique=False, nullable=False)
    request = db.Column(db.String, unique=False, nullable=False)
    response = db.Column(db.String, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Chat {self.name}>'


if __name__ == "__main__":
    # Start the Flask development server
    app.run()
