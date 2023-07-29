from flask import Flask, jsonify, request, g
from flask_cors import CORS
import config
from chat_service import ChatService
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from prompts import Prompts

app = Flask(__name__)
app.config.from_object(config.config["DEV"])
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.post('/chat')
def home():
    user_prompt = request.get_json()['message']
    userid = request.get_json()['user_id']
    sender_name = request.get_json()['sender']
    try:
        chat_history = get_chat_history(userid, user_prompt, sender_name)
        response = ChatService.generateChatResponse(chat_history)
        
        res = {'sender': 'Bot', "message": response}
        
        new_chat = Chat(
            userid = userid,
            name = sender_name,
            request = user_prompt,
            response = response,
        )
        
        db.session.add(new_chat)
        
        db.session.commit()
        
        return jsonify(res), 200
    
    except Exception as e:
        print(e)
        if e.code == 'context_length_exceeded':
            return jsonify({'Error': 'The content length is exceeded'}), 400
        else:
            return jsonify({'error': 'The rate limit exceeded'}), 400


def get_chat_history(userid, prompt, name):
    messages = []
    messages.append(
        {
            'role': 'system',
            'content': Prompts.get_general_prompts(name),
        }
    )
    chats = Chat.query.filter_by(userid = userid).all()
    chats_as_dicts = [chat.__dict__ for chat in chats]
    for chat in chats_as_dicts:
        question = {}
        question['role'] = 'user'
        question['content'] = chat['request']
        messages.append(question)
    messages.append({'role':'user', 'content': prompt})
    return messages

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
    app.run()
