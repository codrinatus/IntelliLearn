import json
import os

from flask import Flask, request, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flasgger import Swagger, swag_from
from functools import wraps
import datetime

from werkzeug.utils import secure_filename

import database
import logging

from llama import generator
from pdf_extractor import extract_text_and_images

JWT_SECRET_KEY = 'meow'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# cursor.execute('SELECT * FROM questions')
#
# column_names = cursor.description
#
# for column in column_names:
#     print(column[0])

def verify_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if request.path not in ['/login', '/register']:
            try:
                jwt_required()(f)(*args, **kwargs)
            except:
                return jsonify(error='Unauthorized - Invalid token'), 401
        else:
            return f(*args, **kwargs)

    return decorator

app = Flask(__name__, static_folder='../frontend/build')

@app.route('/login', methods=['POST'])
def auth():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    conn = database.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify(error='Invalid credentials'), 401

    identity = {
        'username': username,
        'admin': user.admin
    }
    print('User admin: %s' % user.admin)

    token = create_access_token(identity=identity, expires_delta=datetime.timedelta(hours=12))
    stats = user.stats if user.stats else '[]'

    conn.close()
    return jsonify(token=token, stats=stats)


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        conn.close()
        return jsonify(error='Username already exists'), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

    return jsonify(message='User registered successfully'), 201


@app.route('/quiz/<level>', methods=['GET'])
@jwt_required()
def get_questions(level):
    logging.info(f"Fetching questions for level: {level}")
    logging.basicConfig(level=logging.DEBUG)
    conn = database.connect()
    cursor = conn.cursor()
    query = f"SELECT * FROM {level}"
    cursor.execute(query)
    questions = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    question_list = [dict(zip(columns, question)) for question in questions]
    print(question_list)
    conn.close()
    return jsonify(question_list)


@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        return jsonify(error='No file part'), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify(error='No selected file'), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        full_text = extract_text_and_images(file_path)

        result = generator(full_text)

        return jsonify(result), 200

    return jsonify(error='File type not allowed'), 400


@app.route('/insert-questions', methods=['POST'])
@jwt_required()
def insert_questions():
    data = request.get_json()
    questions = data
    table_name = 'SD'

    try:
        database.insert_questions(questions, table_name)
        return jsonify(message='Questions inserted successfully'), 200
    except Exception as e:
        logging.error(f"Error inserting questions: {e}")
        return jsonify(error='Failed to insert questions'), 500


@app.route('/updatestats', methods=['POST'])
@jwt_required()
def update_question_stats():
    data = request.get_json()
    question_stats_update = data.get('question_stats')
    print(question_stats_update)
    username = get_jwt_identity()['username']

    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT stats FROM Users WHERE username = ?", (username,))
    user = cursor.fetchone()
    existing_question_stats = json.loads(user.stats) if user.stats else []

    question_stats_dict = {stat['question_id']: stat for stat in existing_question_stats}
    for stat in question_stats_update:
        question_stats_dict[stat['question_id']] = stat

    updated_question_stats = list(question_stats_dict.values())
    print("Updated question stats:", updated_question_stats)

    cursor.execute("UPDATE Users SET stats = ? WHERE username = ?",
                   (json.dumps(updated_question_stats), username))
    conn.commit()
    conn.close()

    return jsonify(message='Question stats updated successfully'), 200


@app.route('/account', methods=['GET'])
@jwt_required()
def account():
    username = get_jwt_identity()['username']

    conn = database.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT stats FROM Users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user:
        user_dict = dict(zip([desc[0] for desc in cursor.description], user))
        if user_dict['stats']:
            user_stats = json.loads(user_dict['stats'])
        else:
            user_stats = []
    else:
        user_stats = []

    question_ids_with_status = [stat['question_id'] for stat in user_stats if stat['status'] > 0]

    if question_ids_with_status:
        # Get details for questions with status > 0
        format_strings = ','.join(['?'] * len(question_ids_with_status))
        print(format_strings)
        query = f" SELECT * FROM SD WHERE question_id IN ({format_strings})"
        cursor.execute(query, tuple(question_ids_with_status))
        questions = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        # Convert fetched questions to a dictionary
        questions_dict = {
            question[columns.index('question_id')]: {
                'question_id': question[columns.index('question_id')],
                'question': question[columns.index('question')],
                'difficulty': question[columns.index('difficulty')],
                'correct_response': question[columns.index(f'choice{question[columns.index("correctchoiceletter")]}')]
            }
            for question in questions
        }
    else:
        questions_dict = {}

    last_question_id = cursor.execute("SELECT MAX(question_id) FROM SD").fetchone()[0]

    response = {
        'questions': questions_dict,
        'user_stats': user_stats,
        'last_question_id': last_question_id
    }

    conn.close()
    return jsonify(response)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

port = int(os.environ.get('PORT', 3001))
app.run(host='0.0.0.0', port=port)
