from flask import Flask, request, render_template, redirect, url_for, flash
import os
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size 16MB

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Allowed file extensions
ALLOWED_EXTENSIONS = {'xlsx'}

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for home page
@app.route('/')
def index():
    return render_template('upload-excel.html')  # Ensure this template is in 'templates/' folder

# Route to upload and process the Excel file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the Excel file using pandas
        try:
            df = pd.read_excel(file_path)

            # Assume questions are in a column named 'Question'
            if 'Question' not in df.columns:
                flash('Excel file must contain a "Question" column.')
                return redirect(url_for('index'))

            # Map questions to Bloom's Taxonomy categories
            df['Bloom_Category'] = df['Question'].apply(map_blooms_taxonomy)

            # Convert the DataFrame to an HTML table for rendering
            questions_table = df[['Question', 'Bloom_Category']].to_html(classes='table table-bordered', index=False)

            return render_template('upload-excel.html', table=questions_table)

        except Exception as e:
            flash(f"Error processing file: {str(e)}")
            return redirect(url_for('index'))

    flash('Allowed file type is .xlsx')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
