from flask import Blueprint, render_template, request, jsonify
from .models import User, MLTask, db

app = Blueprint('main', __name__)

@app.route('/')
def index():
    return render_template('index.html')  # Render a home page

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "User already exists"}), 400
    new_user = User(username=data['username'], balance=10.0)  # Default balance
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"})

@app.route('/submit_task', methods=['POST'])
def submit_task():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    if user.balance <= 0:
        return jsonify({"message": "Insufficient balance"}), 400
    task = MLTask(user_id=user.id, prompt=data['prompt'])
    user.balance -= 1.0  # Deduct balance for task submission
    db.session.add(task)
    db.session.commit()
    return jsonify({"message": "Task submitted successfully", "task_id": task.id})

@app.route('/tasks/<username>', methods=['GET'])
def get_tasks(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    tasks = MLTask.query.filter_by(user_id=user.id).all()
    return jsonify([{"id": task.id, "prompt": task.prompt, "result": task.result} for task in tasks])
