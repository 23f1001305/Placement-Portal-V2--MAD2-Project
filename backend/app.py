from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_security import Security, SQLAlchemyUserDatastore, auth_required, current_user, hash_password
from config import Config
from models import db, User, Role, Company, Student
import uuid

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


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if not user.active:
        return jsonify({"message": "Your account is deactivated"}), 403

    if not user.verify_and_update_password(password):
        return jsonify({"message": "Wrong password"}), 401

    role = user.roles[0].name if user.roles else None

    if role == "Company":
        company = Company.query.filter_by(user_id=user.id).first()
        if company and company.is_blacklisted:
            return jsonify({"message": "Your company has been blacklisted"}), 403
        if company and not company.is_approved:
            return jsonify({"message": "Your company is not approved yet. Please wait for admin approval."}), 403

    if role == "Student":
        student = Student.query.filter_by(user_id=user.id).first()
        if student and student.is_blacklisted:
            return jsonify({"message": "Your account has been blacklisted"}), 403

    token = user.get_auth_token()

    return jsonify({
        "token": token,
        "user_id": user.id,
        "email": user.email,
        "role": role
    }), 200


@app.route("/api/register/student", methods=["POST"])
def register_student():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")

    if not email or not password or not full_name:
        return jsonify({"message": "Email, password and full name are required"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "Email already registered"}), 409

    student_role = Role.query.filter_by(name="Student").first()

    new_user = User(
        email=email,
        password=hash_password(password),
        active=True,
        fs_uniquifier=str(uuid.uuid4()),
        roles=[student_role]
    )
    db.session.add(new_user)
    db.session.commit()

    new_student = Student(
        user_id=new_user.id,
        full_name=full_name
    )
    db.session.add(new_student)
    db.session.commit()

    return jsonify({"message": "Student registered successfully"}), 201


@app.route("/api/register/company", methods=["POST"])
def register_company():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    company_name = data.get("company_name")

    if not email or not password or not company_name:
        return jsonify({"message": "Email, password and company name are required"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "Email already registered"}), 409

    company_role = Role.query.filter_by(name="Company").first()

    new_user = User(
        email=email,
        password=hash_password(password),
        active=True,
        fs_uniquifier=str(uuid.uuid4()),
        roles=[company_role]
    )
    db.session.add(new_user)
    db.session.commit()

    new_company = Company(
        user_id=new_user.id,
        company_name=company_name,
        is_approved=False
    )
    db.session.add(new_company)
    db.session.commit()

    return jsonify({"message": "Company registered successfully. Please wait for admin approval."}), 201


@app.route("/api/current_user", methods=["GET"])
@auth_required("token")
def get_current_user():
    role = current_user.roles[0].name if current_user.roles else None
    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "role": role
    }

    if role == "Student":
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student:
            user_data["student_id"] = student.id
            user_data["full_name"] = student.full_name

    if role == "Company":
        company = Company.query.filter_by(user_id=current_user.id).first()
        if company:
            user_data["company_id"] = company.id
            user_data["company_name"] = company.company_name
            user_data["is_approved"] = company.is_approved

    return jsonify(user_data), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
