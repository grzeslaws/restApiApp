from flask import Flask, request, jsonify, make_response, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from flask_cors import CORS
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, pprint

from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend
from flask_dance.consumer import oauth_authorized
from sqlalchemy.orm.exc import NoResultFound
from flask_login import LoginManager, login_user, UserMixin, current_user, logout_user, login_required

app = Flask(__name__) 
CORS(app)

# twitter login
twitter_blueprint = make_twitter_blueprint(api_key='Wxheh706myGRPdIzg1UG8NCmD', api_secret='z2gPTdT8v1pCTNEX7xxtf0bbqLwLJgfiqgdgDa03GTf7M5m13T')
app.register_blueprint(twitter_blueprint, url_prefix='/twitter_login')
login_manager = LoginManager() 
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
login_manager.refresh_view = "index"

app.config.from_pyfile("config.cfg")
mail = Mail(app)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# app.config['SQLALCHEMY_ECHO'] = True

app.config["SECRET_KEY"] = "thisissecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////Users/grzesiek/tests/restApiApp/backend/data.db"
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:admin@localhost/flask_api"

app.config["WHOOSHEE_DIR"] = 'whoosheers' 

db = SQLAlchemy(app)
ma = Marshmallow(app)

s = URLSafeTimedSerializer(app.config["SECRET_KEY"])


class User(UserMixin, db.Model):
    __tablename__ = "User"
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

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

class UserSchema(ma.ModelSchema):
    class Meta:
        model = User

class TodoSchema(ma.ModelSchema):
    class Meta:
        model = Todo

twitter_blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user = current_user, user_required=False)

@app.route('/twitter') 
def twitter_login():
    
    if not twitter.authorized:
        print('\x1b[6;30;42m' + 'sdsdsds' + '\x1b[0m')
        return redirect(url_for('twitter.login'))

    account_info = twitter.get('account/settings.json')
    account_info_json = account_info.json()

    return '<h1>Your Twitter name is @{}'.format(account_info_json['screen_name']) 

@oauth_authorized.connect_via(twitter_blueprint)
def twitter_logged_in(blueprint, token):
    
    if not token:
        flash("Failed to log in with Twitter.", category="error")
        return False

    account_info_settings = twitter.get('account/settings.json')
    account_info_settings_json = account_info_settings.json()
    account_info = blueprint.session.get('account/verify_credentials.json')

    if not account_info.ok:
        msg = "Failed to fetch user info from Twitter." 
        flash(msg, category="error")
        return False

    account_info_json = account_info.json()
    twitter_user_id = str(account_info_json["id"])

    query = OAuth.query.filter_by(
        provider = blueprint.name,
        id = twitter_user_id
    )

    try:
        oauth = query.one()
        login_user(oauth.user)
    except NoResultFound:
        oauth = OAuth(
            provider = blueprint.name,
            id = twitter_user_id,
            token = token,
        )
    
    if oauth.user:
        login_user(oauth.user)
        flash("Successfull signed by Twitter!")

    else:
        user = User(
            # email = "grzesupel@gmail.com",
            username = account_info_settings_json["screen_name"]
        )

        oauth.user = user
        db.session.add_all([user, oauth])
        db.session.commit()
        login_user(user)
        flash("Successfull created account by Twitter!")

    return False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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

    users = User.query.all()

    if not users:
        return jsonify({"message": "No users found!"})

    user_schema = UserSchema(many=True)
    result = user_schema.dump(users)

    return jsonify({"users": result})


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

    todo_schema = TodoSchema(many=True)
    result = todo_schema.dump(todos)
    return jsonify({"todos": result})


@app.route("/todo/<int:page_num>", methods=["GET"])
@token_required
def get_todo(current_user, page_num):

    todos = Todo.query.filter_by(user_id=current_user.public_id).paginate(
        per_page=5, page=page_num, error_out=False)

    todo_schema = TodoSchema(many=True)
    result = todo_schema.dump(todos.items)

    return jsonify({
        "todos": result,
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
