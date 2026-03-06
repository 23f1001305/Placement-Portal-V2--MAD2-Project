from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()


roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    active = db.Column(db.Boolean, default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    roles = db.relationship("Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic"))

    company_profile = db.relationship("Company", backref="user", uselist=False)
    student_profile = db.relationship("Student", backref="user", uselist=False)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100))
    location = db.Column(db.String(200))
    website = db.Column(db.String(200))
    description = db.Column(db.Text)
    company_logo = db.Column(db.String(300))
    is_approved = db.Column(db.Boolean, default=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    job_positions = db.relationship("JobPosition", backref="company", lazy=True)
    placements = db.relationship("Placement", backref="company", lazy=True)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    roll_number = db.Column(db.String(50))
    education = db.Column(db.String(300))
    skills = db.Column(db.Text)
    experience = db.Column(db.Text)
    resume = db.Column(db.String(300))
    profile_picture = db.Column(db.String(300))
    phone = db.Column(db.String(20))
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    applications = db.relationship("Application", backref="student", lazy=True)
    placements = db.relationship("Placement", backref="student", lazy=True)


class JobPosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    salary = db.Column(db.String(100))
    skills_required = db.Column(db.Text)
    experience_required = db.Column(db.String(100))
    benefits = db.Column(db.Text)
    status = db.Column(db.String(20), default="Active")
    is_approved = db.Column(db.Boolean, default=False)
    last_date = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    applications = db.relationship("Application", backref="job_position", lazy=True)


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("job_position.id"), nullable=False)
    status = db.Column(db.String(30), default="Applied")
    applied_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    feedback = db.Column(db.Text)
    interview_date = db.Column(db.String(50))
    interview_time = db.Column(db.String(50))
    interview_location = db.Column(db.String(200))
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class Placement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("job_position.id"), nullable=False)
    position = db.Column(db.String(200))
    salary = db.Column(db.String(100))
    joining_date = db.Column(db.String(50))
    offer_letter = db.Column(db.String(300))
    placed_date = db.Column(db.DateTime, default=db.func.current_timestamp())
