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


def company_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"message": "Login required"}), 401
        role = current_user.roles[0].name if current_user.roles else None
        if role != "Company":
            return jsonify({"message": "Company access required"}), 403
        company = Company.query.filter_by(user_id=current_user.id).first()
        if not company:
            return jsonify({"message": "Company profile not found"}), 404
        if not company.is_approved:
            return jsonify({"message": "Company not approved yet"}), 403
        if company.is_blacklisted:
            return jsonify({"message": "Company is blacklisted"}), 403
        return f(*args, **kwargs)
    return decorated_function


@app.route("/api/company/profile", methods=["GET"])
@auth_required("token")
@company_required
def company_get_profile():
    company = Company.query.filter_by(user_id=current_user.id).first()
    return jsonify({
        "id": company.id,
        "company_name": company.company_name,
        "industry": company.industry,
        "location": company.location,
        "website": company.website,
        "description": company.description,
        "company_logo": company.company_logo,
        "is_approved": company.is_approved,
        "email": current_user.email
    }), 200


@app.route("/api/company/profile", methods=["PUT"])
@auth_required("token")
@company_required
def company_update_profile():
    company = Company.query.filter_by(user_id=current_user.id).first()
    data = request.get_json()

    if data.get("company_name"):
        company.company_name = data.get("company_name")
    if data.get("industry") is not None:
        company.industry = data.get("industry")
    if data.get("location") is not None:
        company.location = data.get("location")
    if data.get("website") is not None:
        company.website = data.get("website")
    if data.get("description") is not None:
        company.description = data.get("description")

    db.session.commit()
    return jsonify({"message": "Profile updated successfully"}), 200


@app.route("/api/company/stats", methods=["GET"])
@auth_required("token")
@company_required
def company_stats():
    company = Company.query.filter_by(user_id=current_user.id).first()
    total_jobs = JobPosition.query.filter_by(company_id=company.id).count()
    active_jobs = JobPosition.query.filter_by(company_id=company.id, status="Active").count()

    job_ids = [j.id for j in JobPosition.query.filter_by(company_id=company.id).all()]
    total_applications = 0
    shortlisted = 0
    selected = 0
    if job_ids:
        total_applications = Application.query.filter(Application.job_id.in_(job_ids)).count()
        shortlisted = Application.query.filter(Application.job_id.in_(job_ids), Application.status == "Shortlisted").count()
        selected = Application.query.filter(Application.job_id.in_(job_ids), Application.status == "Selected").count()

    return jsonify({
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_applications": total_applications,
        "shortlisted": shortlisted,
        "selected": selected
    }), 200


@app.route("/api/company/jobs", methods=["GET"])
@auth_required("token")
@company_required
def company_get_jobs():
    company = Company.query.filter_by(user_id=current_user.id).first()
    jobs = JobPosition.query.filter_by(company_id=company.id).all()
    job_list = []
    for j in jobs:
        app_count = Application.query.filter_by(job_id=j.id).count()
        job_list.append({
            "id": j.id,
            "title": j.title,
            "description": j.description,
            "location": j.location,
            "salary": j.salary,
            "skills_required": j.skills_required,
            "experience_required": j.experience_required,
            "benefits": j.benefits,
            "status": j.status,
            "is_approved": j.is_approved,
            "last_date": j.last_date,
            "application_count": app_count,
            "created_at": str(j.created_at) if j.created_at else ""
        })
    return jsonify(job_list), 200


@app.route("/api/company/jobs", methods=["POST"])
@auth_required("token")
@company_required
def company_create_job():
    company = Company.query.filter_by(user_id=current_user.id).first()
    data = request.get_json()

    title = data.get("title")
    if not title:
        return jsonify({"message": "Job title is required"}), 400

    new_job = JobPosition(
        company_id=company.id,
        title=title,
        description=data.get("description", ""),
        location=data.get("location", ""),
        salary=data.get("salary", ""),
        skills_required=data.get("skills_required", ""),
        experience_required=data.get("experience_required", ""),
        benefits=data.get("benefits", ""),
        last_date=data.get("last_date", ""),
        status="Active",
        is_approved=False
    )
    db.session.add(new_job)
    db.session.commit()

    return jsonify({"message": "Job posted successfully. Waiting for admin approval."}), 201


@app.route("/api/company/jobs/<int:job_id>", methods=["PUT"])
@auth_required("token")
@company_required
def company_update_job(job_id):
    company = Company.query.filter_by(user_id=current_user.id).first()
    job = JobPosition.query.get(job_id)

    if not job or job.company_id != company.id:
        return jsonify({"message": "Job not found"}), 404

    data = request.get_json()
    if data.get("title"):
        job.title = data.get("title")
    if data.get("description") is not None:
        job.description = data.get("description")
    if data.get("location") is not None:
        job.location = data.get("location")
    if data.get("salary") is not None:
        job.salary = data.get("salary")
    if data.get("skills_required") is not None:
        job.skills_required = data.get("skills_required")
    if data.get("experience_required") is not None:
        job.experience_required = data.get("experience_required")
    if data.get("benefits") is not None:
        job.benefits = data.get("benefits")
    if data.get("last_date") is not None:
        job.last_date = data.get("last_date")
    if data.get("status") is not None:
        job.status = data.get("status")

    db.session.commit()
    return jsonify({"message": "Job updated successfully"}), 200


@app.route("/api/company/jobs/<int:job_id>/close", methods=["PUT"])
@auth_required("token")
@company_required
def company_close_job(job_id):
    company = Company.query.filter_by(user_id=current_user.id).first()
    job = JobPosition.query.get(job_id)

    if not job or job.company_id != company.id:
        return jsonify({"message": "Job not found"}), 404

    if job.status == "Active":
        job.status = "Closed"
    else:
        job.status = "Active"

    db.session.commit()
    return jsonify({"message": "Job status updated to " + job.status}), 200


@app.route("/api/company/jobs/<int:job_id>/applicants", methods=["GET"])
@auth_required("token")
@company_required
def company_get_applicants(job_id):
    company = Company.query.filter_by(user_id=current_user.id).first()
    job = JobPosition.query.get(job_id)

    if not job or job.company_id != company.id:
        return jsonify({"message": "Job not found"}), 404

    applications = Application.query.filter_by(job_id=job_id).all()
    applicant_list = []
    for a in applications:
        student = Student.query.get(a.student_id)
        user = User.query.get(student.user_id) if student else None
        applicant_list.append({
            "application_id": a.id,
            "student_id": a.student_id,
            "student_name": student.full_name if student else "",
            "student_email": user.email if user else "",
            "education": student.education if student else "",
            "skills": student.skills if student else "",
            "experience": student.experience if student else "",
            "phone": student.phone if student else "",
            "status": a.status,
            "feedback": a.feedback,
            "interview_date": a.interview_date,
            "interview_time": a.interview_time,
            "interview_location": a.interview_location,
            "applied_date": str(a.applied_date) if a.applied_date else ""
        })

    return jsonify(applicant_list), 200


@app.route("/api/company/applications/<int:app_id>/status", methods=["PUT"])
@auth_required("token")
@company_required
def company_update_application_status(app_id):
    company = Company.query.filter_by(user_id=current_user.id).first()
    application = Application.query.get(app_id)

    if not application:
        return jsonify({"message": "Application not found"}), 404

    job = JobPosition.query.get(application.job_id)
    if not job or job.company_id != company.id:
        return jsonify({"message": "Not authorized"}), 403

    data = request.get_json()
    new_status = data.get("status")
    feedback = data.get("feedback")

    allowed_statuses = ["Applied", "Shortlisted", "Interview", "Selected", "Rejected"]
    if new_status not in allowed_statuses:
        return jsonify({"message": "Invalid status"}), 400

    application.status = new_status
    if feedback is not None:
        application.feedback = feedback

    db.session.commit()

    if new_status == "Selected":
        existing = Placement.query.filter_by(
            student_id=application.student_id,
            company_id=company.id,
            job_id=application.job_id
        ).first()
        if not existing:
            new_placement = Placement(
                student_id=application.student_id,
                company_id=company.id,
                job_id=application.job_id,
                position=job.title,
                salary=job.salary
            )
            db.session.add(new_placement)
            db.session.commit()

    return jsonify({"message": "Application status updated to " + new_status}), 200


@app.route("/api/company/applications/<int:app_id>/interview", methods=["PUT"])
@auth_required("token")
@company_required
def company_schedule_interview(app_id):
    company = Company.query.filter_by(user_id=current_user.id).first()
    application = Application.query.get(app_id)

    if not application:
        return jsonify({"message": "Application not found"}), 404

    job = JobPosition.query.get(application.job_id)
    if not job or job.company_id != company.id:
        return jsonify({"message": "Not authorized"}), 403

    data = request.get_json()
    application.interview_date = data.get("interview_date", "")
    application.interview_time = data.get("interview_time", "")
    application.interview_location = data.get("interview_location", "")
    application.status = "Interview"

    db.session.commit()
    return jsonify({"message": "Interview scheduled successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
