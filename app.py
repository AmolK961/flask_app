from flask import Flask, render_template
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify

from werkzeug.security import generate_password_hash, check_password_hash




app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Task %r>' % self.id



@app.route("/")
def welcome():
    return  render_template("/index.html")

# create task


@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    new_task = Task(title=data['title'], description=data.get('description', ''))
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'New task created!'}), 201



# get task
@app.route('/tasks', methods=['GET'])
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
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)
    db.session.commit()
    return jsonify({'message': 'Task updated!'})


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted!'})



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
