from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import tensorflow as tf
from transformers import pipeline
from utils.s3_utils import upload_to_s3, download_from_s3
from utils.preprocess import preprocess_image
from utils.db_utils import save_result, get_results
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load AI models
image_model = tf.keras.models.load_model('models/image_model.h5')
text_model = pipeline('text-classification', model='models/text_model')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)  # Save file temporarily

        # Upload to S3
        s3_url = upload_to_s3(file_path, os.getenv('S3_BUCKET_NAME'), filename)
        os.remove(file_path)  # Delete the temporary file

        # Call the appropriate detection function
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            result = detect_image_deepfake(s3_url)
        elif filename.endswith('.txt'):
            result = detect_text_deepfake(s3_url)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        # Save result to MongoDB
        save_result(filename, filename.split('.')[-1], result)

        return jsonify({'result': result, 's3_url': s3_url})

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/results', methods=['GET'])
def get_all_results():
    results = get_results()
    return jsonify(results)

def detect_image_deepfake(s3_url):
    local_path = 'temp_image.jpg'
    download_from_s3(os.getenv('S3_BUCKET_NAME'), s3_url.split('/')[-1], local_path)
    image = preprocess_image(local_path)
    prediction = image_model.predict(image)
    os.remove(local_path)
    return "Fake" if prediction > 0.5 else "Real"

def detect_text_deepfake(s3_url):
    local_path = 'temp_text.txt'
    download_from_s3(os.getenv('S3_BUCKET_NAME'), s3_url.split('/')[-1], local_path)
    with open(local_path, 'r') as file:
        text = file.read()
    result = text_model(text)
    os.remove(local_path)
    return result[0]['label']

if __name__ == '__main__':
    app.run(debug=True)