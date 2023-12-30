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

# Inisialisasi aplikasi Flask
app = Flask(__name__, static_folder='static')

# Konfigurasi database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + Config.DB_USER + ':' + Config.DB_PASS + '@' + Config.DB_HOST + ':' + Config.DB_PORT + '/' + Config.DB_NAME
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Inisialisasi database dan login manager
db = db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route untuk halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Menangani pengiriman formulir login
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = UserService.login(email, password)
        if user is None:
            return render_template('login.html', error='Email atau password salah')
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html') 

# Route untuk halaman registrasi
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        email = request.form['email']
        
        if password != password_confirm:
            return render_template('register.html', error='Konfirmasi password tidak sesuai')
        
        # Instansiasi UserService
        user_service = UserService()

        # Periksa apakah email sudah terdaftar
        user = user_service.getUser(email)
        if user is not None:
            return render_template('register.html', error='Email sudah terdaftar')

        # Buat pengguna baru
        user_service.createUser(name, password, email)
        return redirect(url_for('login'))

    return render_template('register.html')

# Route untuk halaman utama setelah login
@app.route('/', methods=['GET'])
@login_required
def index():
    active_page = 'index'
    return render_template('index.html', active_page=active_page) 

# Route untuk halaman analisis
@app.route('/analysis', methods=['GET', 'POST'])
@login_required
def analysis():
    active_page = 'analysis'

    if request.method == 'POST':
        # Periksa apakah 'file' ada dalam request.files
        if 'file' not in request.files:
            return render_template('analysis.html', error='File tidak ditemukan')
        file = request.files['file']
        if file.filename == '':
            return render_template('analysis.html', error='File tidak valid')
        try:
            # Baca file CSV menggunakan Pandas
            csv_data = pd.read_csv(file) 
            df_preprocessed2 = pd.DataFrame()
            df_preprocessed2["preprocessed"] = csv_data['content'].apply(preprocess)
            df_preprocessed2["sentiment"] = csv_data["score"].apply(returnSentiment)
            
            file_path = './model/machine/best_tfidf_vocabulary_SVM.pkl'
            file_path1 = './model/machine/svm_tfidf_model.pkl'

            with open(file_path, 'rb') as file:
                best_vocabulary_SVM = pickle.load(file)
                
            with open(file_path1, 'rb') as file:
                model_tfidf_SVM = pickle.load(file)
                
            tfidf_vectorizer_svm = TfidfVectorizer(vocabulary=best_vocabulary_SVM)
            X_TFIDF_SVM = tfidf_vectorizer_svm.fit_transform(df_preprocessed2["preprocessed"]).toarray()

            y = csv_data["score"].apply(returnSentiment)

            result = model_tfidf_SVM.score(X_TFIDF_SVM, y)
            rounded_accuracy = round(result * 100, 1)
            print('accuracy: ', rounded_accuracy)
            
            y_pred = model_tfidf_SVM.predict(X_TFIDF_SVM)
            results_df = pd.DataFrame({'Actual': y, 'Predicted': y_pred})
            results_df
            
            results_df['Actual'] = results_df['Actual'].map({'negative': 0, 'positive': 1})
            results_df['Predicted'] = results_df['Predicted'].map({'negative': 0, 'positive': 1})

            actual_counts = results_df['Actual'].value_counts()
            predicted_counts = results_df['Predicted'].value_counts()

            plot_data = pd.DataFrame({'Actual': actual_counts, 'Predicted': predicted_counts})

            # Plot diagram batang
            colors = ['#1E7559', '#0A905D']
            plot_data.plot(kind='bar', rot=0, color=colors)
            plt.xlabel('Sentimen')
            plt.ylabel('Jumlah')
            plt.title('Aktual vs. Prediksi Sentimen')
            plt.xticks([0, 1], ['Negatif', 'Positif'])
            
            # Simpan gambar diagram batang
            plt.savefig('./static/images/result.png')
            
            # Buat diagram pie 
            plt.figure(figsize=(6, 6))
            colors_pie = ['#1E7559', '#0A905D']
            plt.pie(predicted_counts, labels=['Negatif', 'Positif'], autopct='%1.1f%%', startangle=90, colors=colors_pie)
            plt.title('Persentase Prediksi Sentimen')
            
            # Simpan gambar diagram pie
            plt.savefig('./static/images/pie_chart.png')
            
            # Kirim hasil analisis ke template
            return render_template('resultFile.html', active_page=active_page, result=rounded_accuracy)

        except pd.errors.EmptyDataError:
            return render_template('analysis.html', error='Data tidak ditemukan')
        except pd.errors.ParserError:
            return render_template('analysis.html', error='Data tidak ditemukan')

    return render_template('analysis.html', active_page=active_page)

# Route untuk halaman analisis dengan input teks
@app.route('/analysis-text-input') 
def analysisInputText():
    active_page = 'analysis'
    return render_template('analysisInputText.html', active_page=active_page) 

# Route untuk halaman hasil analisis dengan file
@app.route('/result-file') 
def resultFile():
    active_page = 'analysis'
    return render_template('resultFile.html', active_page=active_page) 

# Route untuk halaman hasil analisis dengan input teks
@app.route('/result-text-input') 
def resultInputText():
    active_page = 'analysis'
    return render_template('resultInputText.html', active_page=active_page) 

# Route untuk halaman riwayat
@app.route('/history')
def history():
    active_page = 'history'
    return render_template('history.html', active_page=active_page) 

# Route untuk logout
@app.route('/logout')
@login_required
def logout(): 
    logout_user()
    return redirect(url_for('login'))

# Menjalankan aplikasi dalam mode debug
if __name__ == "__main__":
    app.run(debug=True)
