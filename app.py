from flask import Flask, jsonify, request, g
from flask_cors import CORS
import config
from aiapi import ChatService
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


class Chat(db.Model):
    id = userid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, unique=False, nullable=False)
    name = db.Column(db.String, unique=False, nullable=False)
    request = db.Column(db.String, unique=False, nullable=False)
    response = db.Column(db.String, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Chat {self.name}>"


@app.post("/chat")
def home():
    prompt = request.get_json()["message"]
    userid = request.get_json()["user_id"]
    messages = []
    messages.append(
        {
            "role": "system",
            "content": Prompts.get_general_prompts(request.get_json()["sender"]),
        }
    )
    chats = Chat.query.filter_by(userid=userid).all()
    chats_as_dicts = [chat.__dict__ for chat in chats]
    for chat in chats_as_dicts:
        question = {}
        question["role"] = "user"
        question["content"] = chat["request"]
        messages.append(question)
    messages.append({'role':'user', 'content': prompt})
    try:
        response = ChatService.generateChatResponse(messages)
        res = {"sender": "Bot", "message": response}
        new_chat = Chat(
            userid=request.get_json()["uid"],
            name=request.get_json()["sender"],
            request=request.get_json()["message"],
            response=response,
        )
        db.session.add(new_chat)
        db.session.commit()
        return jsonify(res), 200
    except Exception as e:
        print(e)
        if e.code == "context_length_exceeded":
            return jsonify({"Error": "The content length is exceeded"}), 400
        else:
            return jsonify({"error": "The rate limit exceeded"}), 400


if __name__ == "__main__":
    app.run()
