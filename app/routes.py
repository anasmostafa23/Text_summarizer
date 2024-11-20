from flask import Blueprint, render_template, request, jsonify
from .models import User, MLTask, db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/submit_task', methods=['POST'])
def submit_task():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and user.balance > 0:
        task = MLTask(user_id=user.id, prompt=data['prompt'])
        db.session.add(task)
        db.session.commit()
        return jsonify({"message": "Task submitted!"})
    return jsonify({"message": "Insufficient balance"}), 400
