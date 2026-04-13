from flask import Flask, render_template, request, redirect, url_for, jsonify
# Rota para retornar todos os todos em JSON
@app.route('/api/todos', methods=["GET"])
def get_todos():
    todos = Todo.query.all()
    todos_list = [{"id": t.id, "title": t.title, "complete": t.complete} for t in todos]
    return jsonify(todos_list)
from flask_sqlalchemy import SQLAlchemy
import os
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(
    os.getenv('DB_USER', 'root'),
    os.getenv('DB_PASSWORD', '12345'),
    os.getenv('DB_HOST', 'mysql'),
    os.getenv('DB_NAME', 'flask')
)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Run server:
# First method: python app.py (app.run needs to be included, like the if statement below)
# Second method: flask run (after exporting 2 env variables:
# export FLASK_ENV=development, export FLASK_APP=app.py)
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)

# create the DB on demand
@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/', methods=["GET"])
def index():
    t = Todo.query.all()
    todos_list = [{"id": todo.id, "title": todo.title, "complete": todo.complete} for todo in t]
    return jsonify(todos_list)

@app.route('/add', methods=["POST"])
def add():
    # Aceita tanto form quanto JSON
    title = request.form.get("title") or (request.json and request.json.get("title"))
    if not title:
        return jsonify({"error": "title is required"}), 400
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({"id": new_todo.id, "title": new_todo.title, "complete": new_todo.complete}), 201

@app.route('/update/<int:todo_id>')
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    if not todo:
        return jsonify({"error": "not found"}), 404
    todo.complete = not todo.complete
    db.session.commit()
    return jsonify({"id": todo.id, "title": todo.title, "complete": todo.complete})

@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    if not todo:
        return jsonify({"error": "not found"}), 404
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"result": "deleted", "id": todo_id})

if __name__ == "__main__":
    #db.create_all()
    app.run(host=os.getenv('IP', '0.0.0.0'), debug=True)
    # app.run(host=os.getenv('IP', '0.0.0.0'), debug=True,
    #         port=int(os.getenv('PORT', 4444)))