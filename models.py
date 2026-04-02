from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# ---------------- USER TABLE ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))  # admin / student / company

# ---------------- COMPANY TABLE ----------------
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    hr_contact = db.Column(db.String(100))
    website = db.Column(db.String(200))
    approved = db.Column(db.Boolean, default=False)

# ---------------- STUDENT TABLE ----------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    resume = db.Column(db.String(200))  

# ---------------- PLACEMENT DRIVE ----------------
class PlacementDrive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    deadline = db.Column(db.String(50))
    status = db.Column(db.String(20))  # pending / approved / closed


# ---------------- APPLICATION ----------------
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'))
    status = db.Column(db.String(20))  # applied / selected / rejected