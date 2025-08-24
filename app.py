from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from tesseract import extract_aadhaar_info, extract_consumer_name_from_pdf

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/crop_recommendation')
def crop():
    return render_template('crop.html')  # or crop_recommendation.html


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/verify', methods=['POST'])
def verify_documents():
    if 'aadhaar' not in request.files or 'land' not in request.files or 'bill' not in request.files:
        return jsonify({'error': 'Missing required files'}), 400

    aadhaar_file = request.files['aadhaar']
    land_file = request.files['land']
    bill_file = request.files['bill']

    if not all([aadhaar_file.filename, land_file.filename, bill_file.filename]):
        return jsonify({'error': 'No selected file'}), 400

    if not all([allowed_file(f.filename) for f in [aadhaar_file, land_file, bill_file]]):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        # Save files temporarily
        aadhaar_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(aadhaar_file.filename))
        land_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(land_file.filename))
        bill_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(bill_file.filename))

        aadhaar_file.save(aadhaar_path)
        land_file.save(land_path)
        bill_file.save(bill_path)

        # Extract Aadhaar information
        aadhaar_result = extract_aadhaar_info(aadhaar_path)
        aadhaar_name = aadhaar_result['name']
        aadhaar_last_4 = aadhaar_result['aadhaar_last_4']

        # Verify against land ownership document
        land_name, land_aadhaar_match = extract_consumer_name_from_pdf(land_path, aadhaar_name, aadhaar_last_4)

        # Verify against electricity bill
        bill_name, bill_aadhaar_match = extract_consumer_name_from_pdf(bill_path, aadhaar_name, aadhaar_last_4)

        # Clean up temporary files
        os.remove(aadhaar_path)
        os.remove(land_path)
        os.remove(bill_path)

        # Prepare response
        result = {
            'aadhaar_info': {
                'name': aadhaar_name,
                'last_4_digits': aadhaar_last_4
            },
            'land_verification': {
                'name_match': land_name == aadhaar_name,
                'aadhaar_match': land_aadhaar_match
            },
            'bill_verification': {
                'name_match': bill_name == aadhaar_name,
                'aadhaar_match': bill_aadhaar_match
            },
            'all_match': (land_name == aadhaar_name and 
                         bill_name == aadhaar_name and 
                         land_aadhaar_match and 
                         bill_aadhaar_match)
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 