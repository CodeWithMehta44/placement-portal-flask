from flask import Flask
from models import db
from models import *
from flask import session
from flask import render_template, request, redirect

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
        return render_template('student_dashboard.html')

    elif role == 'company':
        return render_template('company_dashboard.html')

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
        return "Your account is not approved by admin yet."

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']

        new_drive = PlacementDrive(
            company_id=session['user_id'],
            title=title,
            description=description,
            deadline=deadline,
            status='pending',
            is_approved=False
        )

        db.session.add(new_drive)
        db.session.commit()
        return "Drive Added Successfully"
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
        return "You have already applied"
    new_application = Application(
        student_id=session['user_id'],
        drive_id=drive_id
    )
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

if __name__ == "__main__":
    app.run(debug=True)