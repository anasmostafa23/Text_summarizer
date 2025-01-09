from flask import Blueprint, render_template, request, redirect, url_for, jsonify, Response , flash
from .database import User, Transaction, MLTask , db 
from .utils import summarize_text
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import RegistrationForm, LoginForm, RechargeForm
from .tasks import *



main_page = Blueprint('main_page', __name__,template_folder="static")

@main_page.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main_page.dashboard'))  # Redirect to dashboard if logged in
    return render_template('index.html')  # Show home page for unauthenticated users


# Route for registration
@main_page.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password_hash= generate_password_hash(form.password.data ))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('main_page.recharge'))
    return render_template('register.html', form=form)

# Route for login
@main_page.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash ,form.password.data):
            login_user(user)
            return redirect(url_for('main_page.dashboard'))
    return render_template('login.html', form=form)

# Route for recharge

@main_page.route('/recharge', methods=['GET', 'POST'])
@login_required
def recharge():
    form = RechargeForm()
    if form.validate_on_submit():
        amount = form.amount.data
        current_user.balance += amount
        transaction = Transaction(user_id=current_user.id, amount=amount, transaction_type='credit')
        db.session.add(transaction)
        db.session.commit()
        return redirect(url_for('main_page.dashboard'))
    return render_template('recharge.html', form=form)

@main_page.route('/submit_task', methods=['GET', 'POST'])
@login_required 
def submit_task():

    
    if request.method == 'POST':
        prompt = request.form['text_to_summarize']
        ngrokUrl = request.form['ngrok_url']
        
        
        if current_user.balance >= 10:
            current_user.balance -= 10
            transaction = Transaction(user_id=current_user.id, amount=-10, transaction_type='debit')
            db.session.add(transaction)
            db.session.commit()
            task_data = {
                'user_id': current_user.id,
                'prompt': prompt,
                'ngrok_url': ngrokUrl
            }
            publish_task_to_queue(task_data)
            flash('Task submitted successfully! The result will be available soon.')
            return render_template('submit_task.html',prompt=prompt, ngrokUrl=ngrokUrl)

        else:
            error = "Insufficient Balance."
            return render_template('submit_task.html', error=error, prompt=prompt, ngrokUrl=ngrokUrl)

    return render_template('submit_task.html')

@main_page.route('/admin/view_users')
def view_users():
    users = User.query.all()
    user_list = [{"id": user.id, "username": user.username, "balance": user.balance} for user in users]
    return jsonify(user_list)

@main_page.route('/dashboard')
@login_required
def dashboard():
    tasks = MLTask.query.filter_by(user_id=current_user.id).all()
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', balance=current_user.balance, tasks=tasks, transactions=transactions)

@main_page.route('/logout')
@login_required
def logout():
    logout_user()  # Log out the current user
    return redirect(url_for('main_page.index'))  # Redirect to home or login page

# Add the clear history route
@main_page.route('/clear_history', methods=['POST'])
@login_required
def clear_history():
    # Get the current user
    user = current_user
    # Delete all tasks for the current user
    tasks = MLTask.query.filter_by(user_id=user.id).all()
    for task in tasks:
        db.session.delete(task)
    db.session.commit()

    return redirect(url_for('main_page.dashboard'))  # Redirect to the dashboard after clearing history

@main_page.route('/api/submit_task', methods=['POST'])
def submit_task_tg():
    data = request.json
    user_id = data.get('user_id')
    prompt = data.get('text_to_summarize')
    ngrokUrl = data.get('ngrok_url')
    
    user = User.query.filter_by(id=user_id).first()
    if user and user.balance >= 10:
        user.balance -= 10
        transaction = Transaction(user_id=user.id, amount=-10, transaction_type='debit')
        db.session.add(transaction)
        db.session.commit()
        task_data = {
                'user_id': current_user.id,
                'prompt': prompt,
                'ngrok_url': ngrokUrl
            }
        publish_task_to_queue(task_data)
        flash('Task submitted successfully! The result will be available soon.')
        return jsonify({"message": "Task submitted successfully! Processing will begin shortly.", "balance": user.balance}), 200
    else:
        return jsonify({"error": "Insufficient balance."}), 400


@main_page.route('/api/recharge', methods=['POST'])
def api_recharge():
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount')

    if not user_id :
        return jsonify({"error": "Missing user_id"}), 400
    if not amount:
        return jsonify({"balance": user.balance}), 200

    user = User.query.filter_by(id=user_id).first()
    
    
    if not user:
        user = User(id=user_id, username=f'telegram_{user_id}', password_hash='placeholder', balance=0)
        db.session.add(user)
        db.session.commit()


    # Add the recharge amount
    user.balance += amount
    transaction = Transaction(user_id=user.id, amount=amount, transaction_type='credit')
    db.session.add(transaction)
    db.session.commit()

    return jsonify({"balance": user.balance}), 200
