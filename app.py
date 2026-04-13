from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(
    os.getenv('DB_USER', 'root'),
    os.getenv('DB_PASSWORD', '12345'),
    os.getenv('DB_HOST', 'mysql'),
    os.getenv('DB_NAME', 'flask')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/', methods=["GET"])
def index():
    return render_template('index.html')

@app.route('/api/todos', methods=["GET"])
def get_todos():
    todos = Todo.query.all()
    todos_list = [{"id": t.id, "title": t.title, "complete": t.complete} for t in todos]
    return jsonify(todos_list)

@app.route('/add', methods=["POST"])
def add():
    title = request.form.get("title") or (request.json and request.json.get("title"))
    if not title:
        return jsonify({"error": "title is required"}), 400
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({"id": new_todo.id, "title": new_todo.title, "complete": new_todo.complete})

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

@app.route('/suggest', methods=["POST"])
def suggest():
    data = request.json
    if not data or not data.get("title"):
        return jsonify({"error": "title is required"}), 400

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"error": "AI not configured"}), 503

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = (
            f'Fix spelling and grammar in this task title, make it clear and concise. '
            f'Return only the corrected title, nothing else: "{data["title"]}"'
        )
        response = model.generate_content(prompt)
        return jsonify({"suggestion": response.text.strip()})
    except Exception:
        return jsonify({"error": "AI suggestion failed"}), 500


if __name__ == "__main__":
    app.run(host=os.getenv('IP', '0.0.0.0'), debug=True)
