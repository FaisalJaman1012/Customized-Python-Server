from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

SHARED_FOLDER = os.path.abspath("C:\\Users\\4n0nym0u$~1012\\Downloads\\ARI")

USER_DB = "users.json"
PENDING_USERS_DB = "pending_users.json"
ACTIVITY_LOG = "activity_log.json"
LOGIN_ACTIVITY_LOG = "login_activity_log.json"

# Ensure shared folder and user databases exist
try:
    if not os.path.exists(SHARED_FOLDER):
        os.makedirs(SHARED_FOLDER)
except OSError as e:
    print(f"Error creating shared folder: {e}")

try:
    if not os.path.exists(USER_DB):
        with open(USER_DB, "w") as f:
            json.dump({}, f)
except IOError as e:
    print(f"Error creating user database: {e}")

try:
    if not os.path.exists(PENDING_USERS_DB):
        with open(PENDING_USERS_DB, "w") as f:
            json.dump({}, f)
except IOError as e:
    print(f"Error creating pending users database: {e}")

try:
    if not os.path.exists(ACTIVITY_LOG):
        with open(ACTIVITY_LOG, "w") as f:
            json.dump([], f)
except IOError as e:
    print(f"Error creating activity log: {e}")

try:
    if not os.path.exists(LOGIN_ACTIVITY_LOG):
        with open(LOGIN_ACTIVITY_LOG, "w") as f:
            json.dump([], f)
except IOError as e:
    print(f"Error creating login activity log: {e}")

def load_users():
    try:
        with open(USER_DB, "r") as f:
            return json.load(f)
    except IOError as e:
        print(f"Error loading user database: {e}")
        return {}

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)

def load_pending_users():
    try:
        with open(PENDING_USERS_DB, "r") as f:
            return json.load(f)
    except IOError as e:
        print(f"Error loading pending users database: {e}")
        return {}

def save_pending_users(users):
    with open(PENDING_USERS_DB, "w") as f:
        json.dump(users, f, indent=4)

def log_activity(username, action, path):
    try:
        with open(ACTIVITY_LOG, "r") as f:
            activities = json.load(f)
    except IOError as e:
        print(f"Error loading activity log: {e}")
        activities = []

    activities.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "username": username,
        "action": action,
        "path": path
    })

    with open(ACTIVITY_LOG, "w") as f:
        json.dump(activities, f, indent=4)

def log_login_activity(username, action):
    try:
        with open(LOGIN_ACTIVITY_LOG, "r") as f:
            activities = json.load(f)
    except IOError as e:
        print(f"Error loading login activity log: {e}")
        activities = []

    activities.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "username": username,
        "action": action
    })

    with open(LOGIN_ACTIVITY_LOG, "w") as f:
        json.dump(activities, f, indent=4)

def load_activities():
    try:
        with open(ACTIVITY_LOG, "r") as f:
            return json.load(f)
    except IOError as e:
        print(f"Error loading activity log: {e}")
        return []

def load_login_activities():
    try:
        with open(LOGIN_ACTIVITY_LOG, "r") as f:
            return json.load(f)
    except IOError as e:
        print(f"Error loading login activity log: {e}")
        return []

@app.route('/')
def home():
    if 'username' in session:
        return render_template('loader.html')  # Shows loader before redirecting
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username in users and isinstance(users[username], dict) and users[username].get('password') == password:
            session['username'] = username
            log_login_activity(username, 'login')
            return redirect(url_for('home'))
        return "Invalid credentials, try again!"
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        pending_users = load_pending_users()
        users = load_users()
        if username in users or username in pending_users:
            return "User already exists!"
        pending_users[username] = {'password': password}
        save_pending_users(pending_users)
        return "Signup successful! Please wait for admin approval."
    return render_template('signup.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        log_login_activity(session['username'], 'logout')
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/files/', defaults={'path': ''})
@app.route('/files/<path:path>')
def list_files(path):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    full_path = os.path.join(SHARED_FOLDER, path)
    
    if not os.path.exists(full_path):
        return "Invalid path!", 404

    items = os.listdir(full_path)
    files = []
    folders = []

    for item in items:
        item_path = os.path.join(full_path, item)
        if os.path.isdir(item_path):
            folders.append(item)
        else:
            files.append(item)

    log_activity(session['username'], 'view', path)
    return render_template('files.html', path=path, files=files, folders=folders)

@app.route('/download/<path:path>')
def download_file(path):
    if 'username' not in session:
        return redirect(url_for('login'))
    directory = os.path.dirname(path)
    filename = os.path.basename(path)
    log_activity(session['username'], 'download', path)
    return send_from_directory(os.path.join(SHARED_FOLDER, directory), filename, as_attachment=True)

@app.route('/preview/<path:path>')
def preview_file(path):
    if 'username' not in session:
        return redirect(url_for('login'))
    directory = os.path.dirname(path)
    filename = os.path.basename(path)
    log_activity(session['username'], 'preview', path)
    return send_from_directory(os.path.join(SHARED_FOLDER, directory), filename)

@app.route('/upload/', defaults={'path': ''}, methods=['POST'])
@app.route('/upload/<path:path>', methods=['POST'])
def upload_file(path):
    if 'username' not in session:
        return redirect(url_for('login'))
    if 'file' not in request.files:
        return "No file selected"
    
    file = request.files['file']
    if file.filename == '':
        return "No file selected"
    
    upload_path = os.path.join(SHARED_FOLDER, path)
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)

    file.save(os.path.join(upload_path, file.filename))
    log_activity(session['username'], 'upload', os.path.join(path, file.filename))
    return redirect(url_for('list_files', path=path))

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        return "Invalid admin credentials, try again!"
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    pending_users = load_pending_users()
    users = load_users()
    user_activities = load_activities()
    login_activities = load_login_activities()
    return render_template('admin_dashboard.html', pending_users=pending_users, users=users, user_activities=user_activities, login_activities=login_activities)

@app.route('/admin/approve/<username>')
def approve_user(username):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    pending_users = load_pending_users()
    users = load_users()
    if username in pending_users:
        users[username] = pending_users.pop(username)
        save_users(users)
        save_pending_users(pending_users)
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/<username>')
def reject_user(username):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    pending_users = load_pending_users()
    if username in pending_users:
        pending_users.pop(username)
        save_pending_users(pending_users)
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
