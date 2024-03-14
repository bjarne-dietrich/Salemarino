from flask import Flask, request, render_template, send_from_directory, g
from werkzeug.utils import secure_filename
import os, sqlite3, uuid
from datetime import datetime
from PIL import Image, ExifTags

app = Flask(__name__)

app.config['DATABASE'] = 'main.db'

# Function to get the SQLite connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

# Function to close the SQLite connection at the end of the request
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Create a table to store image metadata
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS images (
                            id INTEGER PRIMARY KEY,
                            project_id TEXT,
                            filename TEXT,
                            uploader TEXT,
                            upload_timestamp TEXT
                        )''')
        db.commit()

# Initialize the database when the application starts
init_db()


# Define the directory where files are stored
app.config['UPLOAD_FOLDER'] = 'data'

# Create 'data' directory if it doesn't exist
data_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'preview')
os.makedirs(data_dir, exist_ok=True)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB in bytes

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        project_id = request.form['projectID']
        file = request.files['file']
        if project_id and file:
            # Check if the file has an allowed extension
            if allowed_file(file.filename):
                # Check if the file size is within the allowed limit
                if request.content_length <= MAX_FILE_SIZE:

                    # Save the file with a UUID as the filename
                    filename = str(uuid.uuid4()) + str("_") + secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    print(f"File saved: {file_path}")

                    # Open the original image
                    with Image.open(file_path) as img:
                        if hasattr(img, '_getexif') and img._getexif() is not None:
                            exif_data = img._getexif()
                            for tag, value in exif_data.items():
                                if tag in ExifTags.TAGS.keys() and ExifTags.TAGS[tag] == 'Orientation':
                                    if value == 3:
                                        img = img.rotate(180, expand=True)
                                    elif value == 6:
                                        img = img.rotate(270, expand=True)
                                    elif value == 8:
                                        img = img.rotate(90, expand=True)

                        
                        # Resize the image to the square size without preserving aspect ratio
                        img = img.resize((1024, 1024))

                        # Save the scaled-down image under data/preview with the same filename
                        preview_file_path = os.path.join('data', 'preview', filename)
                        img.save(preview_file_path)
                        print(f"Preview image saved: {preview_file_path}")

                    upload_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    db = get_db()
                    cursor = db.cursor()
                    cursor.execute('''INSERT INTO images (project_id, filename, upload_timestamp)
                                    VALUES (?, ?, ?)''', (project_id, filename, upload_timestamp))
                    db.commit()


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
        # Search for images based on uploader or project_id
        db = get_db()
        cursor = db.cursor()
        
        if explicit:
            # Search for exact matches
            cursor.execute('''SELECT project_id FROM images WHERE project_id = ?''', (query,))
        else:
            # Search for partial matches
            cursor.execute('''SELECT project_id FROM images WHERE project_id LIKE ? GROUP BY project_id''', ('%' + query + '%',))

        results = cursor.fetchall()
        cursor.close()

        # Extract unique project IDs from the search results
        project_ids = [result[0] for result in results]

        print(f"Search results for query '{query}': {project_ids}")
        return render_template('search_results.html', query=query, results=project_ids, get_images_in_project=get_images_in_project)
    else:
        print("Error: No search query provided.")
        return render_template('search.html')

@app.route('/file/<image>')
def download_file(image):
    attached = request.args.get('attached', '').lower() == 'true'
    print("AT: ", request.args.get('attached', ''))
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], image)
    if os.path.exists(file_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], image, as_attachment=attached)
    else:
        return 'Image not found.', 404
    
@app.route('/preview/<image>')
def preview_file(image):
    print("AT: ", request.args.get('attached', ''))
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'preview', image)
    if os.path.exists(file_path):
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'preview'), image)
    else:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], image)
        if os.path.exists(file_path):
            return send_from_directory(app.config['UPLOAD_FOLDER'], image)
        else:
            return 'Image not found.', 404

@app.route('/browse')
def browse():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''SELECT DISTINCT project_id FROM images''')
    projects = cursor.fetchall()
    print(projects)
    return render_template('browse.html', projects=projects)

def get_images_in_project(project_id):
    print(project_id)
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''SELECT filename, upload_timestamp FROM images WHERE project_id = ?''', (project_id,))
    images_data = cursor.fetchall()
    cursor.close()

    images = []
    for data in images_data:
        print(data)
        images.append((data[0],data[1]))

    return images


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
