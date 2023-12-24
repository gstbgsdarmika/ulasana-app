from flask import Flask, render_template, redirect, url_for

app=Flask(__name__, static_folder='static')

@app.route('/login')
def login():
    return render_template('login.html') 

@app.route('/register')
def register():
    return render_template('register.html') 

@app.route('/')
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
def logout(): 
    return redirect(url_for('login'))

app.run(debug=True)
