from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
from app import app, db
from models import User, File
from utils import generate_secure_url

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password, user_type='client')
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    access_token = create_access_token(identity={'username': user.username, 'user_type': user.user_type})
    return jsonify(access_token=access_token), 200

@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    current_user = get_jwt_identity()
    if current_user['user_type'] != 'ops':
        return jsonify({'message': 'Permission denied'}), 403
    file = request.files['file']
    if file and file.filename.split('.')[-1] in ['pptx', 'docx', 'xlsx']:
        unique_filename = str(uuid.uuid4()) + "_" + file.filename
        file.save(os.path.join('uploads', unique_filename))
        new_file = File(filename=unique_filename, user_id=current_user['id'])
        db.session.add(new_file)
        db.session.commit()
        return jsonify({'message': 'File uploaded successfully'}), 201
    return jsonify({'message': 'Invalid file type'}), 400

@app.route('/download/<file_id>', methods=['GET'])
@jwt_required()
def download_file(file_id):
    current_user = get_jwt_identity()
    if current_user['user_type'] != 'client':
        return jsonify({'message': 'Permission denied'}), 403
    file = File.query.get(file_id)
    if not file:
        return jsonify({'message': 'File not found'}), 404
    download_link = generate_secure_url(file.filename)
    return jsonify({'download-link': download_link, 'message': 'success'}), 200

@app.route('/files', methods=['GET'])
@jwt_required()
def list_files():
    current_user = get_jwt_identity()
    if current_user['user_type'] != 'client':
        return jsonify({'message': 'Permission denied'}), 403
    files = File.query.all()
    return jsonify([{'id': file.id, 'filename': file.filename} for file in files]), 200