from app import app
from models import db, User, Role
from flask_security import hash_password
import uuid


def create_admin():
    with app.app_context():
        db.create_all()

        admin_role = Role.query.filter_by(name="Admin").first()
        if not admin_role:
            admin_role = Role(name="Admin", description="Administrator")
            db.session.add(admin_role)
            db.session.commit()
            print("Admin role created")

        company_role = Role.query.filter_by(name="Company").first()
        if not company_role:
            company_role = Role(name="Company", description="Company User")
            db.session.add(company_role)
            db.session.commit()
            print("Company role created")

        student_role = Role.query.filter_by(name="Student").first()
        if not student_role:
            student_role = Role(name="Student", description="Student User")
            db.session.add(student_role)
            db.session.commit()
            print("Student role created")

        admin_user = User.query.filter_by(email="admin@placementportal.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@placementportal.com",
                password=hash_password("admin123"),
                active=True,
                fs_uniquifier=str(uuid.uuid4()),
                roles=[admin_role]
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created")
            print("Email: admin@placementportal.com")
            print("Password: admin123")
        else:
            print("Admin user already exists")


if __name__ == "__main__":
    create_admin()
