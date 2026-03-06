from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_security import Security, SQLAlchemyUserDatastore, auth_required, current_user, hash_password
from config import Config
from models import db, User, Role, Company, Student, JobPosition, Application, Placement
import uuid
from functools import wraps

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


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"message": "Login required"}), 401
        role = current_user.roles[0].name if current_user.roles else None
        if role != "Admin":
            return jsonify({"message": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function


@app.route("/api/admin/stats", methods=["GET"])
@auth_required("token")
@admin_required
def admin_stats():
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_jobs = JobPosition.query.count()
    total_applications = Application.query.count()
    total_placements = Placement.query.count()
    pending_companies = Company.query.filter_by(is_approved=False).count()
    pending_jobs = JobPosition.query.filter_by(is_approved=False).count()

    return jsonify({
        "total_students": total_students,
        "total_companies": total_companies,
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "total_placements": total_placements,
        "pending_companies": pending_companies,
        "pending_jobs": pending_jobs
    }), 200


@app.route("/api/admin/companies", methods=["GET"])
@auth_required("token")
@admin_required
def admin_get_companies():
    search = request.args.get("search", "")
    if search:
        companies = Company.query.filter(
            (Company.company_name.ilike("%" + search + "%")) |
            (Company.industry.ilike("%" + search + "%"))
        ).all()
    else:
        companies = Company.query.all()

    company_list = []
    for c in companies:
        user = User.query.get(c.user_id)
        company_list.append({
            "id": c.id,
            "company_name": c.company_name,
            "industry": c.industry,
            "location": c.location,
            "website": c.website,
            "description": c.description,
            "is_approved": c.is_approved,
            "is_blacklisted": c.is_blacklisted,
            "email": user.email if user else "",
            "created_at": str(c.created_at) if c.created_at else ""
        })

    return jsonify(company_list), 200


@app.route("/api/admin/companies/<int:company_id>/approve", methods=["PUT"])
@auth_required("token")
@admin_required
def admin_approve_company(company_id):
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"message": "Company not found"}), 404

    company.is_approved = True
    db.session.commit()

    return jsonify({"message": "Company approved successfully"}), 200


@app.route("/api/admin/companies/<int:company_id>/remove", methods=["DELETE"])
@auth_required("token")
@admin_required
def admin_remove_company(company_id):
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"message": "Company not found"}), 404

    jobs = JobPosition.query.filter_by(company_id=company.id).all()
    for job in jobs:
        Application.query.filter_by(job_id=job.id).delete()
    JobPosition.query.filter_by(company_id=company.id).delete()
    Placement.query.filter_by(company_id=company.id).delete()

    user = User.query.get(company.user_id)
    db.session.delete(company)
    if user:
        db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "Company removed successfully"}), 200


@app.route("/api/admin/companies/<int:company_id>/blacklist", methods=["PUT"])
@auth_required("token")
@admin_required
def admin_blacklist_company(company_id):
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"message": "Company not found"}), 404

    company.is_blacklisted = not company.is_blacklisted
    db.session.commit()

    status = "blacklisted" if company.is_blacklisted else "unblacklisted"
    return jsonify({"message": "Company " + status + " successfully"}), 200


@app.route("/api/admin/students", methods=["GET"])
@auth_required("token")
@admin_required
def admin_get_students():
    search = request.args.get("search", "")
    if search:
        students = Student.query.filter(
            (Student.full_name.ilike("%" + search + "%")) |
            (Student.roll_number.ilike("%" + search + "%")) |
            (Student.phone.ilike("%" + search + "%"))
        ).all()
    else:
        students = Student.query.all()

    student_list = []
    for s in students:
        user = User.query.get(s.user_id)
        student_list.append({
            "id": s.id,
            "full_name": s.full_name,
            "roll_number": s.roll_number,
            "education": s.education,
            "skills": s.skills,
            "phone": s.phone,
            "is_blacklisted": s.is_blacklisted,
            "email": user.email if user else "",
            "created_at": str(s.created_at) if s.created_at else ""
        })

    return jsonify(student_list), 200


@app.route("/api/admin/students/<int:student_id>/blacklist", methods=["PUT"])
@auth_required("token")
@admin_required
def admin_blacklist_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student not found"}), 404

    student.is_blacklisted = not student.is_blacklisted
    db.session.commit()

    status = "blacklisted" if student.is_blacklisted else "unblacklisted"
    return jsonify({"message": "Student " + status + " successfully"}), 200


@app.route("/api/admin/students/<int:student_id>/remove", methods=["DELETE"])
@auth_required("token")
@admin_required
def admin_remove_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student not found"}), 404

    Application.query.filter_by(student_id=student.id).delete()
    Placement.query.filter_by(student_id=student.id).delete()

    user = User.query.get(student.user_id)
    db.session.delete(student)
    if user:
        db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "Student removed successfully"}), 200


@app.route("/api/admin/jobs", methods=["GET"])
@auth_required("token")
@admin_required
def admin_get_jobs():
    jobs = JobPosition.query.all()
    job_list = []
    for j in jobs:
        company = Company.query.get(j.company_id)
        app_count = Application.query.filter_by(job_id=j.id).count()
        job_list.append({
            "id": j.id,
            "title": j.title,
            "description": j.description,
            "location": j.location,
            "salary": j.salary,
            "skills_required": j.skills_required,
            "status": j.status,
            "is_approved": j.is_approved,
            "company_name": company.company_name if company else "",
            "application_count": app_count,
            "created_at": str(j.created_at) if j.created_at else ""
        })

    return jsonify(job_list), 200


@app.route("/api/admin/jobs/<int:job_id>/approve", methods=["PUT"])
@auth_required("token")
@admin_required
def admin_approve_job(job_id):
    job = JobPosition.query.get(job_id)
    if not job:
        return jsonify({"message": "Job not found"}), 404

    job.is_approved = True
    db.session.commit()

    return jsonify({"message": "Job approved successfully"}), 200


@app.route("/api/admin/jobs/<int:job_id>/remove", methods=["DELETE"])
@auth_required("token")
@admin_required
def admin_remove_job(job_id):
    job = JobPosition.query.get(job_id)
    if not job:
        return jsonify({"message": "Job not found"}), 404

    Application.query.filter_by(job_id=job.id).delete()
    db.session.delete(job)
    db.session.commit()

    return jsonify({"message": "Job removed successfully"}), 200


@app.route("/api/admin/applications", methods=["GET"])
@auth_required("token")
@admin_required
def admin_get_applications():
    applications = Application.query.all()
    app_list = []
    for a in applications:
        student = Student.query.get(a.student_id)
        job = JobPosition.query.get(a.job_id)
        company_name = ""
        if job:
            company = Company.query.get(job.company_id)
            company_name = company.company_name if company else ""

        app_list.append({
            "id": a.id,
            "student_name": student.full_name if student else "",
            "student_email": User.query.get(student.user_id).email if student else "",
            "job_title": job.title if job else "",
            "company_name": company_name,
            "status": a.status,
            "applied_date": str(a.applied_date) if a.applied_date else ""
        })

    return jsonify(app_list), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
