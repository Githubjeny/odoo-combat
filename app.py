from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from forms import LoginForm, RegistrationForm, TaskForm, CommentForm
from models import db, User, Task, Comment
from config import Config
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
login = LoginManager(app)
login.login_view = 'login'
socketio = SocketIO(app)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
@app.route('/index')
@login_required
def index():
    tasks = Task.query.all()
    form = TaskForm()
    return render_template('index.html', title='Home', tasks=tasks, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, description=form.description.data, due_date=form.due_date.data,
                    priority=form.priority.data, author=current_user)
        db.session.add(task)
        db.session.commit()
        emit('new_task', {'task': render_template('task.html', task=task)}, broadcast=True)
        flash('Task added successfully!')
    return redirect(url_for('index'))

@app.route('/update_task/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get(task_id)
    if task.author != current_user:
        return redirect(url_for('index'))
    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.priority = form.priority.data
        db.session.commit()
        emit('update_task', {'task': render_template('task.html', task=task)}, broadcast=True)
        flash('Task updated successfully!')
    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task.author != current_user:
        return redirect(url_for('index'))
    db.session.delete(task)
    db.session.commit()
    emit('delete_task', {'task_id': task_id}, broadcast=True)
    flash('Task deleted successfully!')
    return redirect(url_for('index'))

@app.route('/task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def task(task_id):
    task = Task.query.get_or_404(task_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, task=task, author=current_user)
        db.session.add(comment)
        db.session.commit()
        emit('new_comment', {'comment': render_template('comment.html', comment=comment)}, broadcast=True)
        flash('Comment added successfully!')
    return render_template('task.html', task=task, form=form)

@socketio.on('join')
def join(message):
    room = message['room']
    join_room(room)
    emit('status', {'msg': current_user.username + ' has entered the room.'}, room=room)

@socketio.on('leave')
def leave(message):
    room = message['room']
    leave_room(room)
    emit('status', {'msg': current_user.username + ' has left the room.'}, room=room)

if __name__ == '_main_':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)