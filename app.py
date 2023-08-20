from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
import uuid
import threading
import asyncio
from script.save_html import save_web_pages, read_web_pages
from script.save_images import image_uploader

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = "scrapped"
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

async def process_file(filename):
    # Simulate asynchronous processing (replace with your actual processing logic)

    folder_path = save_web_pages(file_name=filename)
    print(f"Saved all HTML file in : {folder_path}")

    filename = read_web_pages(folder_path=folder_path)
    print(f"Saved processed Excel File : {filename}")

async def handle_images(sellerId, filename):
    # Simulate asynchronous processing (replace with your actual processing logic)
    image_uploader(sellerId, filename)

def async_process(filename):
    asyncio.run(process_file(filename))

def async_image_process(sellerId, filename):
    asyncio.run(handle_images(sellerId, filename))

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"

        file = request.files['file']

        if file.filename == '':
            return "No selected file"

        if file and allowed_file(file.filename):
            unique_filename = str(uuid.uuid4()) + '_' + file.filename
            filename = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filename)

            # Start asynchronous processing in a separate thread
            t = threading.Thread(target=async_process, args=(filename,))
            t.start()

            return redirect(url_for('success', filename=unique_filename))
        else:
            return "Invalid file format"

    return render_template('upload.html')

@app.route('/image-upload', methods=['GET', 'POST'])
def upload_processed_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"

        file = request.files['file']

        if file.filename == '':
            return "No selected file"

        sellerId = request.form.get('sellerId')  # Get user-inputted filename

        if file and allowed_file(file.filename):
            unique_filename = str(uuid.uuid4()) + '_' + file.filename
            filename = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filename)

            # Start asynchronous processing in a separate thread
            t = threading.Thread(target=async_image_process, args=(sellerId, filename,))
            t.start()

            return redirect(url_for('success', filename=unique_filename))
        else:
            return "Invalid file format"

    return render_template('image-uploader.html')


@app.route('/success/<filename>')
def success(filename):
    return f"File '{filename}' uploaded successfully!"

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        return f'<p>Download the scrapped file: <a href="{url_for("download_file_path", filename=filename)}" download>{filename}</a></p>'
    else:
        return f'File "{filename}" not found.'

@app.route('/download_path/<filename>')
def download_file_path(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
