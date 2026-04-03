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
        return render_template('admin_dashboard.html')

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

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']

        new_drive = PlacementDrive(
            company_id=session['user_id'],
            title=title,
            description=description,
            deadline=deadline,
            status='open'
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

    drives = PlacementDrive.query.all()
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

if __name__ == "__main__":
    app.run(debug=True)