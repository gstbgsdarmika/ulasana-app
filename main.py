from database import db
from config import Config
from model.userModel import User
from service.userService import UserService
from service.analysisService import AnalysisService
from flask import Flask, request, jsonify, render_template, flash, redirect, session, url_for
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app=Flask(__name__, static_folder='static')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + Config.DB_USER + ':' + Config.DB_PASS + '@' + Config.DB_HOST + ':' + Config.DB_PORT + '/' + Config.DB_NAME
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = Config.SECRET_KEY

db = db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Handle login form submission
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = UserService.login(email, password)
        if user is None:
            return render_template('login.html', error='email atau password salah')
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html') 

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        email = request.form['email']
        
        if password != password_confirm:
            return render_template('register.html', error='konfirmasi password tidak sesuai')
        
        # Instantiate UserService
        user_service = UserService()

        # Check if email is already registered
        user = user_service.getUser(email)
        if user is not None:
            return render_template('register.html', error='email sudah terdaftar')

        # Create new user
        user_service.createUser(name, password, email)
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/', methods=['GET'])
@login_required
def index():
    active_page = 'index'
    return render_template('index.html', active_page=active_page) 

@app.route('/analysis') 
def analysis():
    active_page = 'analysis'
    return render_template('analysis.html', active_page=active_page) 

@app.route('/analysis-text-input') 
def analysisInputText():
    active_page = 'analysis'
    return render_template('analysisInputText.html', active_page=active_page) 

@app.route('/result-text-input') 
def resultInputText():
    active_page = 'analysis'
    return render_template('resultInputText.html', active_page=active_page) 

@app.route('/history')
def history():
    active_page = 'history'
    return render_template('history.html', active_page=active_page) 

@app.route('/logout')
@login_required
def logout(): 
    logout_user()
    return redirect(url_for('login'))

app.run(debug=True)
