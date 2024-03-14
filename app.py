from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)

# Define the directory where files are stored
UPLOAD_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB in bytes

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        folder_name = request.form['folderName']
        file = request.files['file']
        if folder_name and file:
            # Check if the file has an allowed extension
            if allowed_file(file.filename):
                # Check if the file size is within the allowed limit
                if request.content_length <= MAX_FILE_SIZE:
                    # Create a folder with the given folder name under 'data' directory
                    data_dir = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
                    folder_path = os.path.join(data_dir, folder_name)
                    os.makedirs(folder_path, exist_ok=True)
                    print(f"Folder created: {folder_path}")

                    # Generate timestamp
                    timestamp = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")

                    # Save the file in the folder with timestamp as part of filename
                    file_name = f"{timestamp}_{secure_filename(file.filename)}"
                    file_path = os.path.join(folder_path, file_name)

                    # Save the file
                    file.save(file_path)
                    print(f"File saved: {file_path}")

                    return render_template('upload_success.html')
                else:
                    return "File size exceeds the maximum limit of 20MB."
            else:
                return "Invalid file type. Please upload an image (jpg, jpeg, png, gif)."

    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    explicit = request.args.get('explicit', '').lower() == 'true'
    if query:
        # Search for folders containing the query string
        results = []
        for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
            for dir in dirs:
                if explicit:
                    if query == dir:
                        results.append(os.path.relpath(os.path.join(root, dir), app.config['UPLOAD_FOLDER']))
                else:
                    if query in dir:
                        results.append(os.path.relpath(os.path.join(root, dir), app.config['UPLOAD_FOLDER']))
        print(f"Search results for query '{query}': {results}")
        return render_template('search_results.html', query=query, results=results, get_images_in_folder=get_images_in_folder)
    else:
        print("Error: No search query provided.")
        return render_template('search.html')

@app.route('/file/<path:filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        print(f"Downloading file: {file_path}")
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    else:
        print(f"Error: File not found: {file_path}")
        return 'File not found.', 404

@app.route('/display_image/<folder>/<image>')
def display_image(folder, image):
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
    image_path = os.path.join(folder_path, image)
    if os.path.exists(image_path):
        return send_from_directory(folder_path, image)
    else:
        return 'Image not found.', 404

@app.route('/browse')
def browse():
    # List all folders in the 'data' directory
    folders = sorted([f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], f))])
    return render_template('browse.html', folders=folders)

def get_images_in_folder(folder):
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
    images = [file for file in os.listdir(folder_path) if file.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    return images

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
