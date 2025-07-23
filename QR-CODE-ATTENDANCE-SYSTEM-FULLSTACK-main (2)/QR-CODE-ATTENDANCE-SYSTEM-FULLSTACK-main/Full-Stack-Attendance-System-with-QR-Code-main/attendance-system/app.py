# Required: pip install flask pymongo qrcode pillow pyzbar

from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash, jsonify
from pymongo import MongoClient
import qrcode
import base64
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode
import datetime
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# MongoDB connection
MONGO_URI = 'mongodb+srv://gnana1313:Gnana1212@dbs.8wngtib.mongodb.net/?retryWrites=true&w=majority&appName=DBs'
DB_NAME = 'attendance_system'

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
signup_requests = db['signup_requests']
students = db['students']
qr_codes = db['qr_codes']
attendance = db['attendance']

# ========== ROUTES ==========

@app.route('/')
def home():
    return render_template('home.html', year=datetime.datetime.now().year)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = None
    if request.method == 'POST':
        rollno = request.form['rollno']
        name = request.form['name']
        class_ = request.form['class']
        branch = request.form['branch']
        mobile = request.form['mobile']
        password = request.form['password']
        if signup_requests.find_one({'rollno': rollno}) or students.find_one({'rollno': rollno}):
            message = 'Signup request or account already exists.'
        else:
            signup_requests.insert_one({
                'rollno': rollno,
                'name': name,
                'class': class_,
                'branch': branch,
                'mobile': mobile,
                'password': password
            })
            message = 'Signup request sent. Wait for admin approval.'
    return render_template('signup.html', message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        login_type = request.form.get('login_type')
        if login_type == 'student':
            rollno = request.form['rollno']
            password = request.form['password']
            student = students.find_one({'rollno': rollno, 'password': password})
            if student:
                session['user'] = rollno
                session['role'] = 'student'
                return redirect(url_for('dashboard'))
            else:
                message = 'Invalid credentials or not approved.'
        elif login_type == 'admin':
            username = request.form['username']
            password = request.form['password']
            if username == 'admin' and password == '123456':
                session['user'] = 'admin'
                session['role'] = 'admin'
                return redirect(url_for('admin_dashboard'))
            else:
                message = 'Invalid admin credentials.'
    return render_template('login.html', message=message)

# ========== PROTECT STUDENT ROUTES ==========

def login_required_student(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/dashboard')
@login_required_student
def dashboard():
    rollno = session['user']
    student = students.find_one({'rollno': rollno})
    return render_template('dashboard.html', student_name=student['name'])

@app.route('/dashboard/profile')
@login_required_student
def profile():
    student = students.find_one({'rollno': session['user']})
    return render_template('profile.html', student=student)

@app.route('/dashboard/download_qr')
@login_required_student
def download_qr():
    rollno = session['user']
    qr_doc = qr_codes.find_one({'rollno': rollno})
    if qr_doc:
        qr_base64 = qr_doc['qr_base64']
    else:
        qr_img = qrcode.make(rollno)
        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        qr_codes.insert_one({'rollno': rollno, 'qr_base64': qr_base64})
    student = students.find_one({'rollno': rollno})
    return render_template('download_qr.html', qr_base64=qr_base64, student=student)

@app.route('/dashboard/mark_attendance', methods=['GET', 'POST'])
@login_required_student
def mark_attendance():
    message = None
    success = False
    rollno = session['user']
    now = datetime.datetime.now()
    slot = None
    slot_enabled = False

    if datetime.time(8, 0) <= now.time() <= datetime.time(10, 0):
        slot = 'Morning'
        slot_enabled = True
    elif datetime.time(21, 0) <= now.time() <= datetime.time(22, 30):
        slot = 'Afternoon'
        slot_enabled = True

    if request.method == 'POST':
        if not slot_enabled:
            message = 'Attendance only allowed during the valid time slots.'
        elif 'qr_image' not in request.files:
            message = 'No file uploaded.'
        else:
            file = request.files['qr_image']
            try:
                img = Image.open(file.stream)
                decoded = decode(img)
                if not decoded:
                    message = 'No QR code detected.'
                else:
                    qr_data = decoded[0].data.decode()
                    if qr_data != rollno:
                        message = 'QR does not match your Roll No.'
                    else:
                        today = now.strftime('%Y-%m-%d')
                        if attendance.find_one({'rollno': rollno, 'date': today, 'slot': slot}):
                            message = 'Already marked for this slot.'
                        else:
                            attendance.insert_one({'rollno': rollno, 'date': today, 'slot': slot})
                            success = True
                            message = 'Attendance marked successfully.'
            except:
                message = 'Error decoding QR.'

    return render_template('mark_attendance.html', message=message, success=success, slot_enabled=slot_enabled)

@app.route('/dashboard/attendance_directory')
@login_required_student
def attendance_directory():
    rollno = session['user']
    records = attendance.find({'rollno': rollno}).sort('date', -1)
    return render_template('attendance_directory.html', attendance_records=list(records))


# ========== ADMIN ROUTES ==========

def login_required_admin(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/admin_dashboard')
@login_required_admin
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/requests', methods=['GET', 'POST'])
@login_required_admin
def admin_requests():
    message = None
    if request.method == 'POST':
        rollno = request.form['rollno']
        action = request.form['action']
        req = signup_requests.find_one({'rollno': rollno})
        if req:
            if action == 'approve':
                students.insert_one(req)
                signup_requests.delete_one({'rollno': rollno})
                message = f"Approved {rollno}."
            elif action == 'reject':
                signup_requests.delete_one({'rollno': rollno})
                message = f"Rejected {rollno}."
    return render_template('admin_requests.html', requests=list(signup_requests.find()), message=message)

@app.route('/admin/attendance')
@login_required_admin
def admin_attendance():
    filter_rollno = request.args.get('rollno', '').strip()
    filter_date = request.args.get('date', '').strip()
    now = datetime.datetime.now()
    total_sessions = 2 if filter_date else now.day * 2
    query = {'date': filter_date} if filter_date else {}

    table = []
    for student in students.find():
        if filter_rollno and student['rollno'] != filter_rollno:
            continue
        attended = attendance.count_documents({'rollno': student['rollno'], **query})
        percent = round((attended / total_sessions) * 100, 2) if total_sessions else 0
        table.append({
            'rollno': student['rollno'],
            'name': student['name'],
            'total_sessions': total_sessions,
            'sessions_attended': attended,
            'attendance_percent': percent
        })
    return render_template('admin_attendance.html', attendance_table=table,
                           filter_rollno=filter_rollno, filter_date=filter_date)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ========== START APP ==========
if __name__ == '__main__':
    app.run(debug=True)
