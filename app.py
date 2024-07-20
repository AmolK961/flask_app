import  os
from flask import Flask, render_template,redirect, url_for, request, flash,abort
from flask_login import LoginManager,UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify



# from models import User,Task  # Import your User model




from werkzeug.security import generate_password_hash, check_password_hash










app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SECRET_KEY'] = 'nothingissecrete here'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    def is_active(self):
        # You can customize this based on your application's requirements
        return True

    def is_authenticated(self):
        return True  # Assuming all users are authenticated for simplicity

    def is_anonymous(self):
        return False



class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Task %r>' % self.id









# User model


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


@app.route("/index")
def welcome():
    return  render_template("index.html")


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        abort(403)  # Forbidden
    # Render admin dashboard
    return render_template('admin_dashboard.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'user')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully. Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Login request has been came here")
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(username,password)

        user = User.query.filter_by(username=username).first()


        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return render_template("index.html")
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')








@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return render_template("index.html")

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', username=current_user.username)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# create task


@app.route('/tasks', methods=['POST'])
@login_required
def create_task():
    print("creating task")
    data = request.get_json()
    new_task = Task(title=data['title'], description=data.get('description', ''))
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'New task created!'}), 201



# get task
@app.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.query.all()
    output = []
    for task in tasks:
        task_data = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed
        }
        output.append(task_data)
    return jsonify({'tasks': output})


@app.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)
    db.session.commit()
    return jsonify({'message': 'Task updated!'})


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    print(task_id)
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted!'})



if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        db.create_all()


        app.run(debug=True)
