import os
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'replace-with-your-secret-key'

UPLOAD_FOLDER = 'uploads'
CLEANED_FOLDER = 'cleaned'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLEANED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_dataframe(df, strip=True, drop_duplicates=True, drop_empty=True):
    if drop_empty:
        df = df.dropna(how='all')
    if strip:
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    if drop_duplicates:
        df = df.drop_duplicates()
    return df

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'files' not in request.files:
            flash("No files uploaded")
            return redirect(request.url)
        files = request.files.getlist('files')
        cleaned_files = []

        strip = request.form.get('strip') == 'on'
        drop_duplicates_opt = request.form.get('drop_duplicates') == 'on'
        drop_empty_opt = request.form.get('drop_empty') == 'on'

        for file in files:
            if file.filename == '':
                continue
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)

                if filename.lower().endswith('.csv'):
                    df = pd.read_csv(file_path)
                    cleaned_name = "cleaned_" + filename
                    df = clean_dataframe(df, strip, drop_duplicates_opt, drop_empty_opt)
                    df.to_csv(os.path.join(CLEANED_FOLDER, cleaned_name), index=False)
                else:
                    df = pd.read_excel(file_path)
                    cleaned_name = "cleaned_" + filename
                    df = clean_dataframe(df, strip, drop_duplicates_opt, drop_empty_opt)
                    df.to_excel(os.path.join(CLEANED_FOLDER, cleaned_name), index=False)

                cleaned_files.append(cleaned_name)

        if not cleaned_files:
            flash("No valid files uploaded")
            return redirect(request.url)

        return render_template("index.html", cleaned_files=cleaned_files)

    return render_template("index.html")

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(CLEANED_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
