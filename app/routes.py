from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from .database import User, Transaction, MLTask, db
from .utils import summarize_text

main_page = Blueprint('main_page', __name__,template_folder="static")

@main_page.route('/')
def index():
    return render_template('index.html')

@main_page.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"message": "User already exists"}), 400
        new_user = User(username=data['username'], balance=10.0)  # Default balance
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main_page.index'))
    return render_template('register.html')

@main_page.route('/login', methods=['GET', 'POST'])
def login():
    # Add login functionality here
    return render_template('login.html')

@main_page.route('/recharge', methods=['GET', 'POST'])
def recharge():
    if request.method == 'POST':
        amount = request.form['amount']
        user = User.query.first()  # Get the current logged-in user
        user.balance += float(amount)  # Add the recharge amount to the user's balance
        transaction = Transaction(user_id=user.id, amount=float(amount))
        db.session.add(transaction)
        db.session.commit()
        return redirect(url_for('main_page.index'))
    return render_template('recharge.html')

@main_page.route('/submit_task', methods=['GET', 'POST'])
def submit_task():
    if request.method == 'POST':
        prompt = request.form['prompt']
        user = User.query.first()  # Get the current logged-in user
        if user.balance <= 0:
            return jsonify({"message": "Insufficient balance"}), 400
        user.balance -= 10  # Deduct 10 credits per task
        db.session.commit()

        # Summarize the text
        summary = summarize_text(prompt)
        
        # Save the task in the database
        task = MLTask(user_id=user.id, prompt=prompt, result=summary)
        db.session.add(task)
        db.session.commit()

        return render_template('submit_task.html', summary=summary)
    return render_template('submit_task.html')
