<h1 align="center">PENAMBANGAN DATA TEKSTUAL</h1>

## Anggota Kelompok 
* Puspadevi Anggotra 2008561008
* Putu Ayu Novia Aryanti 2008561011
* Ni Luh Komang Indira Pramesti 2008561064
* I Nengah Oka Darmayasa 2008561070
* Yauw James Fang Dwiputra Harta 2008561078
* I Gusti Bagus Darmika Putra 2008561094

## Cara Settup Project
1. Install semua depedensi library yang digunakan (direkomendasikan menggunakan Python versi 3.10)
2. Buat file config.py di root project yang berisi class seperti config-example.py. Sesuaikan koneksi database anda.
3. Jalankan perintah berikut di terminal secara berurutan untuk melakukan migrasi database
    - `flask shell`
    - `from database import db`
    - `from model.userModel import User`
    - `from model.historyModel import History`
    - `db.create_all()`
4. Jalankan aplikasi dengan menjalankan perintah `flask run` atau `flask run --debug` untuk memasukin mode debuging.

## Link Video Presentasi 
https://youtu.be/s0H39wI7jk8?si=I1ylDk8ytmJPrX6D 

## Selamat aplikasi anda berjalan !
