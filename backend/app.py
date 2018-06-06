from flask import Flask, request, jsonify, make_response, url_for
from flask_sqlalchemy import SQLAlchemy 
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from flask_cors import CORS
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

app = Flask(__name__)
CORS(app)

app.config.from_pyfile("config.cfg") 
mail = Mail(app)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# app.config['SQLALCHEMY_ECHO'] = True

app.config["SECRET_KEY"] = "thisissecretkey"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////Users/grzesiek/tests/flaskRestApi/data.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:admin@localhost/flask_api"

app.config["WHOOSHEE_DIR"] = 'whoosheers'
db = SQLAlchemy(app)

s = URLSafeTimedSerializer(app.config["SECRET_KEY"])


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(200))
    admin = db.Column(db.Boolean)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.String(50))


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

        if not token:
            jsonify({"message": "Token is missing!"})

        try:
            data = jwt.decode(
                token, app.config["SECRET_KEY"], algorithms=['HS256'])
            current_user = User.query.filter_by(
                public_id=data["public_id"]).first()
        except:
            return jsonify({"message": "Token is invalid!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route("/search")
def search_text():
    keywords = request.args.get("keywords")
    print("keywords: ", keywords)
    # result = Todo.query.whooshee_search('asa').all()
    result = db.engine.execute(
        "SELECT todo.id AS todo_id, todo.text AS todo_text, todo.complete AS todo_complete, todo.user_id AS todo_user_id FROM todo")
    print(result)

    print("result: ", result)
    return ""


@app.route("/user", methods=["GET"])
@token_required
def get_all_users(current_user):

    if not current_user.admin:
        return jsonify({"message": "Cannoot perform that function!"})

    data = []
    users = User.query.all()

    if not users:
        return jsonify({"message": "No users found!"})

    for user in users:
        user_data = {}
        user_data["username"] = user.username
        user_data["password"] = user.password
        user_data["public_id"] = user.public_id
        user_data["admin"] = user.admin
        data.append(user_data)

    return jsonify({"users": data})


@app.route("/user/<public_id>", methods=["GET"])
def get_one_user(public_id):

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "No user found!"})

    user_data = {}
    user_data["username"] = user.username
    user_data["password"] = user.password
    user_data["public_id"] = user.public_id
    user_data["admin"] = user.admin
    return jsonify({"user": user_data})


@app.route("/user", methods=["POST"])
def create_user():

    data = request.get_json()
    hashed_password = generate_password_hash(data["password"], method="sha256")
    user = User(public_id=str(uuid.uuid4()),
                username=data["username"], password=hashed_password, admin=True)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "New user created!"})


@app.route("/user/<public_id>", methods=["PUT"])
def promote_user(public_id):

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "No user found!"})

    user.admin = True
    db.session.commit()

    return jsonify({"message": "User has been promoted!"})


@app.route("/user/<public_id>", methods=["DELETE"])
def delete_user(public_id):

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "No user found!"})

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User has been deleted!"})


@app.route("/login", methods=["POST"])
def login():
    auth = request.get_json()

    if not auth or not auth["username"] or not auth["password"]:
        return make_response("Could not verify", 401, {"WWW-Authenticate": 'Basic realm="Logi requireed!"'})

    user = User.query.filter_by(username=auth["username"]).first()

    if not user:
        return make_response("Could not verify", 401, {"WWW-Authenticate": 'Basic realm="Logi requireed!"'})

    if (check_password_hash(user.password, auth["password"])):
        data = {"public_id": user.public_id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=90)}
        token = jwt.encode(data, "thisissecretkey", 'HS256').decode('utf-8')

        return jsonify({"token": token})

    return make_response("Could not verify", 401, {"WWW-Authenticate": 'Basic realm="Logi requireed!"'})


@app.route("/todos", methods=["GET"])
@token_required
def get_all_todo(current_user):
    todos = Todo.query.all()
    todos_return = []

    for item in todos:
        todo = {}
        todo["id"] = item.id
        todo["text"] = item.text
        todo["complete"] = item.complete
        todo["user_id"] = item.user_id
        todos_return.append(todo)

    return jsonify({"todos": todos_return})


@app.route("/todo/<int:page_num>", methods=["GET"])
@token_required
def get_todo(current_user, page_num):

    todos_return = []

    todos = Todo.query.filter_by(user_id=current_user.public_id).paginate(
        per_page=5, page=page_num, error_out=False)
    for item in todos.items:
        todo = {}
        todo["id"] = item.id
        todo["text"] = item.text
        todo["complete"] = item.complete
        todo["user_id"] = item.user_id
        todos_return.append(todo)

    return jsonify({
        "todos": todos_return,
        "paginate": {
            "pages": todos.pages,
            "page": todos.page,
            "next": todos.next_num,
            "prev": todos.prev_num,
            "has_prev": todos.has_prev,
            "has_next": todos.has_next
        }
    })


@app.route("/todo", methods=["POST"])
@token_required
def add_todo(current_user):
    data = request.get_json()
    print(data)

    todo = Todo(text=data["text"], complete=data["complete"],
                user_id=current_user.public_id)
    db.session.add(todo)
    db.session.commit()

    return jsonify({"message": "Todo was created!"})


@app.route("/todo/<todo_id>", methods=["PUT"])
@token_required
def get_one_todo(current_user, id):

    todo = Todo.query.filter_by(
        id=todo_id, user_id=current_user.public_id).first()

    if not todo:
        return jsonify({"message": "No todo found!"})

    todo.complete = True
    db.session.commit()

    return jsonify({"message": "Todo was changed!"})


@app.route("/todo/<todo_id>", methods=["DELETE"])
@token_required
def delete_todo(current_user, todo_id):
    print(int(todo_id))

    todo = Todo.query.filter_by(
        id=todo_id, user_id=current_user.public_id).first()

    print("todo: ", todo)

    if not todo:
        return jsonify({"message": "No todo found!"})
    db.session.delete(todo)
    db.session.commit()

    return jsonify({"message": "Todo was deleted!"})


@app.route("/send_email", methods=["POST"])
def send_email():

    data = request.get_json()
    token = s.dumps(data["email"], salt="email-confirm")
    link = url_for("confirm_email", token=token, _external=True)

    msg = Message("Hello", sender="grzesupel@gmail.com",
                  recipients=["grzesiek@o3enzyme.com"])
    msg.body = link
    mail.send(msg)

    return jsonify({"message": "Message was send to mail!"})


@app.route("/confirm_email/<token>")
def confirm_email(token):

    try:
        email = s.loads(token, salt="email-confirm", max_age=40)
    except SignatureExpired:
        return jsonify({"message": "Token is expired!"})

    return jsonify({"message": "Token was verified!"})


@app.route("/test")
def test():
    return jsonify({"message": "Test message"})


if __name__ == "__main__":
    app.run(debug=True)
