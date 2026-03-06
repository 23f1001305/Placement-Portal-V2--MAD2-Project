from flask import Flask
from flask_cors import CORS
from flask_security import Security, SQLAlchemyUserDatastore
from config import Config
from models import db, User, Role

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
db.init_app(app)

datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, datastore)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return "Placement Portal API is running"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
