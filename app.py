from flask import Flask, request, render_template, send_from_directory, g, jsonify, make_response,redirect, url_for
from werkzeug.utils import secure_filename
import os, sqlite3, uuid
from datetime import datetime
from PIL import Image, ExifTags
import zipfile
from io import BytesIO

app = Flask(__name__)

# Define the directory where files are stored
app.config['UPLOAD_FOLDER'] = 'data'
app.config['IMAGES_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'images')
app.config['DATABASE_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'database')
app.config['PREVIEW_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'preview')


# Create database, preview and images directory if it doesn't exist
os.makedirs(app.config['DATABASE_FOLDER'], exist_ok=True)
os.makedirs(app.config['IMAGES_FOLDER'], exist_ok=True)
os.makedirs(app.config['IMAGES_FOLDER'], exist_ok=True)

app.config['DATABASE'] = os.path.join(app.config['DATABASE_FOLDER'], 'main.db')

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
                            comment TEST,
                            uploader TEXT,
                            upload_timestamp TEXT
                        )''')
        db.commit()

# Initialize the database when the application starts
init_db()

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB in bytes

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        project_id = request.form['projectID']
        file = request.files['file']
        comment = request.form['comment']
        if project_id and file:
            # Check if the file has an allowed extension
            if allowed_file(file.filename):
                # Check if the file size is within the allowed limit
                if request.content_length <= MAX_FILE_SIZE:

                    # Save the file with a UUID as the filename
                    filename = str(uuid.uuid4()) + str("_") + secure_filename(file.filename)
                    file_path = os.path.join(app.config['IMAGES_FOLDER'], filename)
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
                    cursor.execute('''INSERT INTO images (project_id, filename, comment, upload_timestamp)
                                    VALUES (?, ?, ?, ?)''', (project_id, filename, comment, upload_timestamp))
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
            cursor.execute('''SELECT project_id FROM images WHERE project_id = ? GROUP BY project_id ''', (query,))
        else:
            # Search for partial matches
            cursor.execute('''SELECT project_id FROM images WHERE project_id LIKE ? GROUP BY project_id''', ('%' + query + '%',))

        results = cursor.fetchall()
        cursor.close()

        # Extract unique project IDs from the search results
        project_ids = [result[0] for result in results]

        print(f"Search results for query '{query}': {project_ids}")
        return render_template('search_results.html', query=query, results=project_ids, get_images_in_project=get_images_in_project, get_comment=get_comment)
    else:
        print("Error: No search query provided.")
        return render_template('search.html')

@app.route('/file/<image>')
def download_file(image):
    attached = request.args.get('attached', '').lower() == 'true'
    print("AT: ", request.args.get('attached', ''))
    file_path = os.path.join(app.config['IMAGES_FOLDER'], image)
    if os.path.exists(file_path):
        return send_from_directory(app.config['IMAGES_FOLDER'], image, as_attachment=attached)
    else:
        return 'Image not found.', 404

@app.route('/preview/<image>')
def preview_file(image):
    file_path = os.path.join(app.config['PREVIEW_FOLDER'], image)
    if os.path.exists(file_path):
        return send_from_directory(app.config['PREVIEW_FOLDER'], image)
    else:
        return 'Preview not found.', 404

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

# Returns the Comment for a given Image
def get_comment(image):
    print(image)
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''SELECT comment FROM images WHERE filename = ?''', (image[0],))
    comments = cursor.fetchall()
    cursor.close()
    print(comments[0])
    return comments[0][0]

# Function to delete an image from the database and filesystem
def delete_image_from_db_and_filesystem(filename):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''DELETE FROM images WHERE filename = ?''', (filename,))
        db.commit()
        print(f"Image '{filename}' deleted from the database.")

        # Delete image file from 'data' folder
        file_path = os.path.join(app.config['IMAGES_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Image file '{filename}' deleted from 'data' folder.")

        # Delete preview image file from 'data/preview' folder
        preview_file_path = os.path.join(app.config['PREVIEW_FOLDER'], filename)
        if os.path.exists(preview_file_path):
            os.remove(preview_file_path)
            print(f"Preview image file '{filename}' deleted from 'data/preview' folder.")

    except sqlite3.Error as e:
        print(f"Error deleting image '{filename}' from the database:", e)
    finally:
        cursor.close()

@app.route('/delete_image', methods=['POST'])
def delete_image():
    data = request.get_json()
    filename = data.get('filename', None)
    if filename:
        # Delete the image from the database and filesystem
        delete_image_from_db_and_filesystem(filename)
        return jsonify({'status': 'success', 'message': f'Image "{filename}" deleted from the database and filesystem.'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'No filename provided.'}), 400
    
import shutil

@app.route('/download_all_images', methods=['GET'])
def download_all_images():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''SELECT project_id, filename FROM images''')
        project_images = cursor.fetchall()

        # Check if there are any images in the database
        if not project_images:
            # Redirect to the empty_database route
            return redirect(url_for('empty_database'))

        # Create a BytesIO object to hold the ZIP file in memory
        zip_data = BytesIO()
        with zipfile.ZipFile(zip_data, mode='w') as zipf:
            for project_id, filename in project_images:
                folder_path = os.path.join('data', 'downloads', project_id)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                file_path = os.path.join(app.config['IMAGES_FOLDER'], filename)
                if os.path.exists(file_path):
                    zipf.write(file_path, os.path.join(project_id, filename))

        # Move to the beginning of the BytesIO object
        zip_data.seek(0)

        # Create a Flask response with the ZIP file
        response = make_response(zip_data.getvalue())
        response.headers['Content-Type'] = 'application/zip'
        response.headers['Content-Disposition'] = 'attachment; filename=all_images.zip'
        
        # Clear the 'downloads' folder after download
        downloads_folder = os.path.join('data', 'downloads')
        if os.path.exists(downloads_folder):
            shutil.rmtree(downloads_folder)
            os.makedirs(downloads_folder)

        return response

    except sqlite3.Error as e:
        print("Error downloading all images:", e)
        return jsonify({'status': 'error', 'message': 'Error downloading all images.'}), 500
    finally:
        cursor.close()

@app.route('/empty_database', methods=['GET'])
def empty_database():
    return render_template('empty_database.html')

# Route for editing comment
@app.route('/edit_comment', methods=['POST'])
def edit_comment():
    data = request.get_json()
    filename = data.get('filename')
    new_comment = data.get('comment')
    if filename and new_comment:
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''UPDATE images SET comment = ? WHERE filename = ?''', (new_comment, filename))
            db.commit()
            return jsonify({'status': 'success', 'message': 'Comment updated successfully.'}), 200
        except sqlite3.Error as e:
            print("Error updating comment:", e)
            return jsonify({'status': 'error', 'message': 'Error updating comment.'}), 500
        finally:
            cursor.close()
    else:
        return jsonify({'status': 'error', 'message': 'Missing filename or comment.'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
