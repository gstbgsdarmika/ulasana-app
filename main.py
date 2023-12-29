from database import db
import pickle
import matplotlib.pyplot as plt
import pandas as pd
from utils.preprocessing import preprocess, returnSentiment
from sklearn.feature_extraction.text import TfidfVectorizer
from config import Config
from model.userModel import User
from service.userService import UserService
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

@app.route('/analysis', methods=['GET', 'POST'])
@login_required
def analysis():
    active_page = 'analysis'

    if request.method == 'POST':
        # Check if 'file' is in request.files
        if 'file' not in request.files:
            return render_template('analysis.html', error='File tidak ditemukan')

        file = request.files['file']

        if file.filename == '':
            return render_template('analysis.html', error='File tidak valid')

        try:
            # Read the CSV file using Pandas
            csv_data = pd.read_csv(file)
            # Assuming `document` is a global variable or defined outside this function
            # document = pd.concat([document, csv_data], ignore_index=True)

            df_preprocessed2 = pd.DataFrame()
            # Extract text data from the CSV or perform any necessary text analysis here
            df_preprocessed2["preprocessed"] = csv_data['content'].apply(preprocess)
            df_preprocessed2["sentiment"] = csv_data["score"].apply(returnSentiment)
            
            file_path = './model/machine/best_tfidf_vocabulary_SVM.pkl'

            with open(file_path, 'rb') as file:
                best_vocabulary_SVM = pickle.load(file)
                
            file_path1 = './model/machine/svm_tfidf_model.pkl'

            with open(file_path1, 'rb') as file:
                model_tfidf_SVM = pickle.load(file)
                
            tfidf_vectorizer_svm = TfidfVectorizer(vocabulary=best_vocabulary_SVM)  # You can adjust the max_features parameter
            X_TFIDF_SVM = tfidf_vectorizer_svm.fit_transform(df_preprocessed2["preprocessed"]).toarray()

            y = csv_data["score"].apply(returnSentiment)

            result = model_tfidf_SVM.score(X_TFIDF_SVM, y)
            print('accuracy: ', result)
            
            y_pred = model_tfidf_SVM.predict(X_TFIDF_SVM)
            results_df = pd.DataFrame({'Actual': y, 'Predicted': y_pred})
            results_df
            
            # Assuming 'Actual' and 'Predicted' are columns in your DataFrame
            results_df['Actual'] = results_df['Actual'].map({'negative': 0, 'positive': 1})
            results_df['Predicted'] = results_df['Predicted'].map({'negative': 0, 'positive': 1})

            # Count the occurrences of each value in 'Actual' and 'Predicted'
            actual_counts = results_df['Actual'].value_counts()
            predicted_counts = results_df['Predicted'].value_counts()

            # Create a DataFrame for plotting
            plot_data = pd.DataFrame({'Actual': actual_counts, 'Predicted': predicted_counts})

            # Plot the bar chart
            plot_data.plot(kind='bar', rot=0)
            plt.xlabel('Sentiment')
            plt.ylabel('Count')
            plt.title('Actual vs. Predicted Sentiment')
            plt.xticks([0, 1], ['Negative', 'Positive'])
            
            # Save the figure
            plt.savefig('./static/images/result.png')
            
            # Pass the analysis results to the template
            return render_template('analysis.html', active_page=active_page, result=result)

        except pd.errors.EmptyDataError:
            return render_template('analysis.html', error='Data tidak ditemukan')
        except pd.errors.ParserError:
            return render_template('analysis.html', error='Data tidak ditemukan')

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
