from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# ---------------- USER TABLE ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))  # admin / student / company
    resume = db.Column(db.String(200))
    is_approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
# ---------------- COMPANY TABLE ----------------
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    hr_contact = db.Column(db.String(100))
    website = db.Column(db.String(200))
    is_approved = db.Column(db.Boolean, default=False)

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
    skills = db.Column(db.String(200))
    status = db.Column(db.String(20))  # pending / approved / closed
    is_approved = db.Column(db.Boolean, default=False)

# ---------------- APPLICATION ----------------
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'))
    status = db.Column(db.String(50), default='applied')
    student = db.relationship('User', backref='applications')
    drive = db.relationship('PlacementDrive', backref='applications')

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    message = db.Column(db.String(200))