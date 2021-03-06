from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from cypher_server.blueprints import messages, users
from dotenv import load_dotenv
from cypher_server.models import user as User
from cypher_server.internal import CheckToken
import itsdangerous
import traceback
import base64
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///local.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("TOKEN_SECRET")
app.db = SQLAlchemy(app)


@app.route("/auth/validate")
def validate():
    CheckToken(request.headers.get("Authorization"))
    return "", 204


@app.route("/auth/generate", methods=['POST'])
def generate():
    if request.method == 'POST':
        data_user = request.json['username']
        data_password = request.json['password']

        try:
            current_user = User.query.filter_by(username=data_user).first()

            return jsonify({"token": itsdangerous.TimestampSigner(app.config["SECRET_KEY"]).sign(base64.b64encode(str(current_user.id).encode())).decode()}) if current_user and current_user.password == data_password else "Wrong credentials."
        except:
            traceback.print_exc()
            return "Something went wrong..", 400
    else:
        return "Method not allowed", 400


app.register_blueprint(messages)
app.register_blueprint(users)

if __name__ == "__main__":
    app.run(debug=True)
