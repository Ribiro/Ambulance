from flask import Flask, render_template, url_for, request, redirect, flash, session, g
from flask_sqlalchemy import SQLAlchemy
from config.config import Development, Production
from functools import wraps
import os
import time
from PIL import Image
import pygal


# this is the part to change in image uploading
UPLOAD_FOLDER = 'static/ambulance_images/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# create an instance of class Flask called app
app = Flask(__name__)
app.config.from_object(Development)
# app.config.from_object(Production)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# create an instance of sqlalchemy
db = SQLAlchemy(app)

from models.Admin import AdminModel
from models.Companies import CompaniesModel
from models.Branches import BranchesModel
from models.Ambulances import AmbulancesModel

# create tables in our database
@app.before_first_request
def create_tables():
    db.create_all()


@app.before_request
def setg():
    g.user = None
    try:
        if session:
            if session['username']:
                g.user = session['username']
            else:
                g.user = None
        else:
            g.user = None
    except:
        print('no worries')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# register
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        phone = request.form['phone']
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']
        confirm_passw = request.form['confirm_passw']
        hashed = AdminModel.generate_hash(passw)

        if passw == confirm_passw:
            if AdminModel.check_email(mail) and AdminModel.check_username(uname):
                flash("Username/Email already exists")
                return render_template("register.html")
            else:
                register = AdminModel(username=uname, email=mail, phone=phone, password=hashed)
                register.insert_records()

                return redirect(url_for("login"))
        else:
            flash("The two passwords do not match!")
            return render_template("register.html")
    return render_template('register.html')

# login
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]
        if AdminModel.fetch_by_username(uname):
            if AdminModel.check_password(uname, passw):
                session['username'] = uname
                session['uid'] = AdminModel.fetch_by_username(uname).id
                # session['role'] = 'admin'
                # print(session['role'])
                return redirect(url_for('home'))
        flash("Username does not Exist!")
    return render_template('login.html')


# logout route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('ambulance'))

# forgot password
@app.route('/forgot_password')
def forgot_password():
    return render_template('recover.html')


@app.route('/')
def ambulance():
    return render_template('landing.html')


@app.route('/about')
def about_us():
    return render_template('about us.html')


@app.route('/contacts')
def contact_us():
    return render_template('contact us.html')


@app.route('/home')
@login_required
def home():
    if session:
        companies = 0
        branches = 0
        ambulances = 0
        drivers = 0

        booked = 0
        unbooked = 0

        graph = ''
        graph2 = ''

        for each in CompaniesModel.fetch_all():
            companies += 1
        for each in BranchesModel.fetch_all():
            branches += 1
        for each in AmbulancesModel.fetch_all():
            ambulances += 1
            drivers += 1
            if each.status == 'booked':
                booked += 1
            else:
                unbooked += 1

        pie_chart = pygal.Pie()
        pie_chart.title = 'Resources distribution in %'
        pie_chart.add('Companies', companies)
        pie_chart.add('Branches', branches)
        pie_chart.add('Ambulances', ambulances)
        pie_chart.add('Drivers', drivers)
        graph = pie_chart.render_data_uri()
        # print(graph)

        pie_chart2 = pygal.Pie()
        pie_chart2.title = 'Booked V Unbooked ambulances'
        pie_chart2.add('Booked', booked)
        pie_chart2.add('Unbooked', unbooked)
        graph2 = pie_chart2.render_data_uri()
        # print(graph2)

        return render_template('home.html', companies=companies, branches=branches, ambulances=ambulances,
                               drivers=drivers, booked=booked, unbooked=unbooked, graph=graph, graph2=graph2)


@app.route('/companies')
@login_required
def companies():
    if session:
        admin = AdminModel.fetch_by_id(session['uid'])
        kampuni_zake = admin.companies
        print(type(companies))
        return render_template('companies.html', kampuni_zake=kampuni_zake)

# add a new company
@app.route('/new_company', methods=['POST'])
@login_required
def new_company():
    if session:
        if request.method == 'POST':
            company_name = request.form['company_name']
            phone = request.form['phone']
            email = request.form['email']
            admin_id = session['uid']

            if CompaniesModel.check_company(company_name):
                flash('Company Already Exists!')
                return redirect(url_for('companies'))
            new = CompaniesModel(company_name=company_name, phone=phone, email=email, admin_id=admin_id)
            new.insert_record()
            return redirect(url_for('companies'))

# update company information
@app.route('/update_company/<int:id>', methods=['POST'])
@login_required
def update_company(id):
    if request.method == "POST":
        company_name = request.form['company_name']
        phone = request.form['phone']
        email = request.form['email']

        CompaniesModel.update_company_by_id(id=id, company_name=company_name, phone=phone, email=email)

    return redirect(url_for('companies'))

# delete company
@app.route('/delete_company/<int:id>')
@login_required
def delete_company(id):
    CompaniesModel.delete_company_by_id(id)
    return redirect(url_for('companies'))


@app.route('/branches/<int:id>')
@login_required
def branches(id):
    if session:
        this_company = CompaniesModel.fetch_by_id(id)
        return render_template('branches.html', id=id, this_company=this_company)

# new branch
@app.route('/new_branch/<int:cid>', methods=['POST'])
def new_branch(cid):
    if request.method == 'POST':
        branch_name = request.form['branch_name']
        phone = request.form['phone']
        email = request.form['email']

        new = BranchesModel(branch_name=branch_name, phone=phone, email=email, company_id=cid)
        new.insert_record()

    return redirect(url_for('branches', id=cid))

# update branch information
@app.route('/update_branch/<int:id>', methods=['GET','POST'])
@login_required
def update_branch(id):
    if request.method == "POST":
        branch_name = request.form['branch_name']
        phone = request.form['phone']
        email = request.form['email']

        BranchesModel.update_branch_by_id(id=id, branch_name=branch_name, phone=phone, email=email)
        this_branch = BranchesModel.fetch_by_id(id)
        id = this_branch.company_id
    return redirect(url_for('branches', id=id))


# delete branch
@app.route('/delete_branch/<int:id>')
@login_required
def delete_branch(id):
    BranchesModel.delete_branch_by_id(id)
    return redirect(url_for('branches', id=id))


# create a function that check if an extension is valid, uploads a file and redirect user to url for image
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# create a function that uploads files
def upload_file(imageFile):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in imageFile:
            print('No file part')
            return None

        file = imageFile['file']

        # if user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            return None
        if file and allowed_file(file.filename):
            img = Image.open(file)
            new_width = 183
            new_height = 275
            size = (new_height,new_width)
            img = img.resize(size)
            stamped = int(time.time())
            print('all good')
            img.save(os.path.join(UPLOAD_FOLDER, str(stamped) + file.filename))
            print(os.path.join(UPLOAD_FOLDER, str(stamped) + file.filename))
            return '/static/ambulance_images/' + str(stamped) + file.filename
        else:
            return None


@app.route('/ambulances/<int:id>')
@login_required
def ambulances(id):
    if session:
        this_branch = BranchesModel.fetch_by_id(id)
        return render_template('ambulances.html', id=id, this_branch=this_branch)


# ambulance for selected constituency
@app.route('/searched_ambulances/<string:constituency>')
def searched_ambulances(constituency):
    this_constituency = BranchesModel.fetch_by_branch_name(constituency)
    return render_template('near_ambulances.html', id=id, this_constituency=this_constituency)

# search ambulances by constituency
@app.route('/search_ambulances', methods=['POST', 'GET'])
def search_ambulances():
    if request.method == 'POST':
        constituency = request.form['constituency']
    else:
        constituency = request.args.get("constituency")
    if BranchesModel.check_constituency(constituency):
        return redirect(url_for('searched_ambulances', constituency=constituency))
    else:
        flash('No such constituency! Please consider trying one that is near to you')
        return redirect(url_for('ambulance'))

# new branch
@app.route('/new_ambulance/<int:bid>', methods=['POST'])
def new_ambulance(bid):
    if request.method == 'POST':
        ambulances_type = request.form['ambulance_type']
        ambulance_plates = request.form['ambulance_plates']
        ambulance_image = upload_file(request.files)
        drivers_name = request.form['drivers_name']
        phone = request.form['phone']
        email = request.form['email']

        if AmbulancesModel.check_plates(ambulance_plates):
            flash('Ambulance with this plates already exists!')
            return redirect(url_for('ambulances', id=bid))
        drivers_name = drivers_name.strip()
        new = AmbulancesModel(ambulance_type=ambulances_type, ambulance_plates=ambulance_plates, ambulance_image=ambulance_image, driver_name=drivers_name, phone=phone, email=email, branch_id=bid)
        new.insert_record()

    return redirect(url_for('ambulances', id=bid))

# update branch information
@app.route('/update_ambulance/<int:id>', methods=['GET', 'POST'])
@login_required
def update_ambulance(id):
    if request.method == "POST":
        drivers_name = request.form['drivers_name']
        phone = request.form['phone']
        email = request.form['email']

        try:
            AmbulancesModel.update_ambulance_by_id(id=id, driver_name=drivers_name, phone=phone, email=email)
        except:
            print('could not update')
        this_ambulance = AmbulancesModel.fetch_by_id(id)
        id = this_ambulance.branch_id
    return redirect(url_for('ambulances', id=id))

# update ambulance status
@app.route('/update_status/<int:id>', methods=['GET', 'POST'])
def update_status(id):
    if request.method == 'POST':
        status = request.form['status']
        AmbulancesModel.update_status(id=id, status=status)

        this_ambulance = AmbulancesModel.fetch_by_id(id)
        driver_name = this_ambulance.driver_name

        return redirect(url_for('drivers', driver_name=driver_name))

# Login a driver
@app.route('/login_driver', methods=['POST', 'GET'])
def login_driver():
    if request.method == 'POST':
        driver_name = request.form['dname']
        phone = request.form['phone']

        if AmbulancesModel.fetch_by_driver_name(driver_name):
            this_driver = AmbulancesModel.fetch_by_driver_name(driver_name)
            if this_driver.phone == phone:
                return redirect(url_for('drivers', driver_name=driver_name))
            else:
                flash('Invalid credentials')
                return redirect(url_for('login_driver'))
    return render_template('login_driver.html')

# drivers portal
@app.route('/drivers/<driver_name>', methods=['POST', 'GET'])
def drivers(driver_name):
    this_ambulance = AmbulancesModel.fetch_by_driver_name(driver_name)
    return render_template('driver.html', this_ambulance=this_ambulance)

# delete branch
@app.route('/delete_ambulance/<int:id>')
@login_required
def delete_ambulance(id):
    AmbulancesModel.delete_ambulance_by_id(id)
    this_ambulance = AmbulancesModel.fetch_by_id(id)
    id = this_ambulance.branch_id
    return redirect(url_for('ambulances', id=id))


if __name__ == '__main__':
    app.run()
