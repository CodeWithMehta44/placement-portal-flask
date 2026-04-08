from flask import Flask
from models import db
from models import *
from flask import session
from flask import render_template, request, redirect
import os
from sqlalchemy import or_
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret123'
# load config file
app.config.from_pyfile('config.py')

db.init_app(app)

#create database 
with app.app_context(): #needed to access DB in flask
    db.create_all()


    
#Check and Login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            if user and not user.is_active:
                return "Your account is blocked by admin."
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect('/dashboard')
        else:
            return redirect('/register')

    return render_template('login.html')



#Regiter, if u are not register 
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        new_user = User(
            name=name,
            email=email,
            password=password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')
    
    return render_template('register.html')

#Dashboard 
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    role = session.get('role')

    if role == 'student':
        return redirect('/student_dashboard')
    elif role == 'company':
        return redirect('/company_dashboard')

    elif role == 'admin':
        return redirect('/admin_dashboard')

    return "Invalid Role"

#Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


#Company will add there their drive 
@app.route('/add_drive', methods=['GET', 'POST'])
def add_drive():
    if 'user_id' not in session or session.get('role') != 'company':
        return redirect('/login')
    company = User.query.get(session['user_id'])
    if not company.is_approved:
        return "Company not approved by admin yet."

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']
        skills = request.form['skills']

        new_drive = PlacementDrive(
            company_id=session['user_id'],
            skills = skills,
            title=title,
            description=description,
            deadline=deadline,
            status='pending',
            is_approved=False
        )

        db.session.add(new_drive)
        db.session.commit()
        return redirect('/company_dashboard')
    return render_template('add_drive.html')



#Student View 
@app.route('/view_drives')
def view_drives():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')

    drives = PlacementDrive.query.filter_by(is_approved=True).all()
    return render_template('view_drive.html', drives=drives)

#If certeria fullfil apply
@app.route('/apply/<int:drive_id>')
def apply(drive_id):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    # check if already applied
    existing = Application.query.filter_by(
        student_id=session['user_id'],
        drive_id=drive_id
    ).first()
    if existing:
        return "You have already applied to this drive."
    new_application = Application(
        student_id=session['user_id'],
        drive_id=drive_id,
        status="pending"
    )
    drive = PlacementDrive.query.get(drive_id)
    if drive.status == "closed":
        return "This drive is closed."

    db.session.add(new_application)
    db.session.commit()
    return "Applied Successfully"

@app.route('/view_applications')
def view_applications():
    if 'user_id' not in session or session.get('role') != 'company':
        return redirect('/login')
    drives = PlacementDrive.query.filter_by(company_id=session['user_id']).all()

    applications = []

    for drive in drives:
        apps = Application.query.filter_by(drive_id=drive.id).all()
        applications.extend(apps)
    return render_template('view_application.html', applications=applications)

@app.route('/view_applications/<int:drive_id>')
def view_applications_by_drive(drive_id):
    if 'user_id' not in session or session.get('role') != 'company':
        return redirect('/login')

    applications = Application.query.filter_by(drive_id=drive_id).all()

    return render_template('view_application.html', applications=applications)


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')

    total_students = User.query.filter_by(role='student').count()
    total_companies = User.query.filter_by(role='company').count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_companies=total_companies,
        total_drives=total_drives,
        total_applications=total_applications
    )

@app.route('/company_dashboard')
def company_dashboard():
    if 'user_id' not in session or session.get('role') != 'company':
        return redirect('/login')
    company = User.query.get(session['user_id'])
    if not company.is_approved:
        return "Waiting for admin approval"
    
    company_id = session['user_id']

    drives = PlacementDrive.query.filter_by(company_id=company_id).all()

    total_drives = len(drives)

    total_applications = 0
    for drive in drives:
        total_applications += Application.query.filter_by(drive_id=drive.id).count()

    return render_template(
        'company_dashboard.html',
        drives=drives,
        total_drives=total_drives,
        total_applications=total_applications
    )


@app.route('/manage_companies')
def manage_companies():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')

    companies = User.query.filter_by(role='company').all()
    return render_template('manage_companies.html', companies=companies)

@app.route('/approve_company/<int:id>')
def approve_company(id):
    company = User.query.get(id)
    company.is_approved = True
    db.session.commit()
    return redirect('/manage_companies')


@app.route('/reject_company/<int:id>')
def reject_company(id):
    company = User.query.get(id)
    company.is_approved = False
    db.session.commit()
    return redirect('/manage_companies')

@app.route('/manage_drives')
def manage_drives():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')

    drives = PlacementDrive.query.all()
    return render_template('manage_drives.html', drives=drives)

@app.route('/approve_drive/<int:id>')
def approve_drive(id):
    drive = PlacementDrive.query.get(id)
    drive.is_approved = True
    drive.status = 'open'
    db.session.commit()
    return redirect('/manage_drives')


@app.route('/reject_drive/<int:id>')
def reject_drive(id):
    drive = PlacementDrive.query.get(id)
    drive.is_approved = False
    drive.status = 'rejected'
    db.session.commit()
    return redirect('/manage_drives')

@app.route('/manage_users')
def manage_users():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')

    query = request.args.get('q')

    if query:
        users = User.query.filter(User.email.contains(query)).all()
    else:
        users = User.query.all()

    return render_template('manage_users.html', users=users)

@app.route('/toggle_user/<int:id>')
def toggle_user(id):
    user = User.query.get(id)
    user.is_active = not user.is_active
    db.session.commit()
    return redirect('/manage_users')

@app.route('/update_drive_status/<int:drive_id>/<status>')
def update_drive_status(drive_id, status):
    if 'user_id' not in session or session.get('role') != 'company':
        return redirect('/login')

    drive = PlacementDrive.query.get(drive_id)

    # Security check 
    if drive.company_id != session['user_id']:
        return "Unauthorized"

    drive.status = status
    db.session.commit()

    return redirect('/company_dashboard')

@app.route('/update_application_status/<int:app_id>/<status>')
def update_application_status(app_id, status):
    if 'user_id' not in session or session.get('role') != 'company':
        return redirect('/login')

    application = Application.query.get(app_id)

    # Security check
    drive = PlacementDrive.query.get(application.drive_id)
    if drive.company_id != session['user_id']:
        return "Unauthorized"
    allowed_status = ['shortlisted', 'interview', 'selected', 'rejected']

    if status not in allowed_status:
        return "Invalid status"
    
    application.status = status
    db.session.commit()
    notification = Notification(
    user_id=application.student_id,
    message=f"Your application status is now {status}"
    )
    db.session.add(notification)
    db.session.commit()
    return redirect(f'/view_applications/{application.drive_id}')

@app.route('/student_applications')
def student_applications():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')

    applications = Application.query.filter_by(student_id=session['user_id']).all()

    return render_template('student_applications.html', applications=applications)

@app.route('/upload_resume', methods=['GET', 'POST'])
def upload_resume():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')

    if request.method == 'POST':
        file = request.files['resume']

        if file:
            filename = secure_filename(file.filename)

            upload_folder = os.path.join(os.getcwd(), 'static', 'resumes')
            os.makedirs(upload_folder, exist_ok=True)

            filepath = os.path.join(upload_folder, filename)

            file.save(filepath)

            user = User.query.get(session['user_id'])
            user.resume = filename
            db.session.commit()

            return "Resume uploaded successfully"

    return render_template('upload_resume.html')

@app.route('/student_dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    search = request.args.get('search', '')

    query = PlacementDrive.query.filter_by(status='open')
    notifications = Notification.query.filter_by(user_id=session['user_id']).all()
    if search:
        query = query.join(User, PlacementDrive.company_id == User.id).filter(
            or_(
                PlacementDrive.title.ilike(f"%{search}%"),
                PlacementDrive.description.ilike(f"%{search}%"),
                PlacementDrive.skills.ilike(f"%{search}%"),
                User.name.ilike(f"%{search}%")   # company name
            )
        )
    drives = query.all()
    return render_template('student_dashboard.html', drives=drives,notifications=notifications)
    
@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        print("POST HIT:", request.form)

        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.skills = request.form.get('skills')
        user.education = request.form.get('education')

        db.session.commit()
        

        return redirect('/profile')
    return render_template('update_profile.html', user=user)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')

    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

if __name__ == "__main__":
    app.run(debug=True)