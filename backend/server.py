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

def find_static_folder():
    for root, dirs, files in os.walk('/tmp'):
        if 'static' in dirs:
            return os.path.join(root, 'static')
    return None

STATIC_FOLDER = './'

app = Flask(__name__, static_folder=STATIC_FOLDER)
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:80"}})

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')
    
@app.route('/debug-files')
def debug_files():
    directory = app.static_folder

    def get_file_structure(path):
        structure = []
        for root, dirs, files in os.walk(path):
            relative_root = os.path.relpath(root, directory)
            if relative_root == '.':
                relative_root = ''
            for dir_name in dirs:
                structure.append(f"Directory: {os.path.join(relative_root, dir_name)}")
            for file_name in files:
                structure.append(f"File: {os.path.join(relative_root, file_name)}")
        return structure

    file_structure = get_file_structure(directory)
    return jsonify(file_structure)
    return jsonify(files_and_dirs)
    
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


def select_questions_based_on_score(cursor, level, user_stats, score):
    if score == 0:
        # First quiz(new user/topic)
        difficulty_weights = {'easy': 1, 'medium': 1, 'hard': 1}
    elif score < 60:  # Beginner
        difficulty_weights = {'easy': 2, 'medium': 1, 'hard': 0}
    elif score < 150:  # Intermediate
        difficulty_weights = {'easy': 1, 'medium': 2, 'hard': 1}
    elif score < 240:  # Advanced
        difficulty_weights = {'easy': 0, 'medium': 2, 'hard': 2}
    else:  # Master
        difficulty_weights = {'easy': 0, 'medium': 1, 'hard': 3}

    answered_questions = [stat['question_id'] for stat in user_stats if stat['status'] == 2]
    if answered_questions:
        placeholders = ','.join(['?'] * len(answered_questions))
        query = f"SELECT * FROM {level} WHERE question_id NOT IN ({placeholders})"
        cursor.execute(query, answered_questions)
    else:
        query = f"SELECT * FROM {level}"
        cursor.execute(query)

    questions = cursor.fetchall()
    columns = [column[0] for column in cursor.description]

    easy_questions = [dict(zip(columns, q)) for q in questions if q[columns.index('difficulty')] == 'easy']
    medium_questions = [dict(zip(columns, q)) for q in questions if q[columns.index('difficulty')] == 'medium']
    hard_questions = [dict(zip(columns, q)) for q in questions if q[columns.index('difficulty')] == 'hard']

    selected_questions = []
    total_weight = sum(difficulty_weights.values())
    num_questions = 10

    while len(selected_questions) < num_questions and total_weight > 0:
        if not easy_questions:
            difficulty_weights['easy'] = 0
        if not medium_questions:
            difficulty_weights['medium'] = 0
        if not hard_questions:
            difficulty_weights['hard'] = 0

        total_weight = sum(difficulty_weights.values())
        if total_weight == 0:
            break

        choice = random.choices(
            population=['easy', 'medium', 'hard'],
            weights=[difficulty_weights['easy'], difficulty_weights['medium'], difficulty_weights['hard']],
            k=1
        )[0]

        if choice == 'easy' and easy_questions:
            selected_questions.append(easy_questions.pop())
        elif choice == 'medium' and medium_questions:
            selected_questions.append(medium_questions.pop())
        elif choice == 'hard' and hard_questions:
            selected_questions.append(hard_questions.pop())

        if len(selected_questions) < num_questions:
            remaining_questions = easy_questions + medium_questions + hard_questions
            selected_questions.extend(random.sample(remaining_questions, min(num_questions - len(selected_questions),
                                                                             len(remaining_questions))))

    return selected_questions


@app.route('/quiz/<level>', methods=['GET'])
@jwt_required()
def get_questions(level):
    logging.info(f"Fetching questions for level: {level}")
    logging.basicConfig(level=logging.DEBUG)
    username = get_jwt_identity()['username']

    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT stats, score FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    user_stats = json.loads(user[0]) if user[0] else []
    score = user[1] if user[1] else 0

    questions = select_questions_based_on_score(cursor, level, user_stats, score)

    conn.close()

    return jsonify(questions)


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
    cursor.execute("SELECT stats, score FROM Users WHERE username = ?", (username,))
    user = cursor.fetchone()
    existing_question_stats = json.loads(user[0]) if user[0] else []
    current_score = user[1] if user[1] else 0

    question_stats_dict = {stat['question_id']: stat for stat in existing_question_stats}
    for stat in question_stats_update:
        question_stats_dict[stat['question_id']] = stat
        print(stat)

    updated_question_stats = list(question_stats_dict.values())
    print("Updated question stats:", updated_question_stats)

    new_score = current_score
    points = {'easy': 2, 'medium': 4, 'hard': 8}

    for stat in question_stats_update:
        if stat['status'] == 2:
            new_score += points[stat['difficulty']]


    cursor.execute("UPDATE users SET stats = ?, score = ? WHERE username = ?",
                   (json.dumps(updated_question_stats), new_score, username))
    conn.commit()
    conn.close()

    return jsonify(message='Question stats updated successfully'), 200


@app.route('/account', methods=['GET'])
@jwt_required()
def account():
    username = get_jwt_identity()['username']

    conn = database.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT stats,score FROM Users WHERE username = ?", (username,))
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
        format_strings = ','.join(['?'] * len(question_ids_with_status))
        print(format_strings)
        query = f" SELECT * FROM SD WHERE question_id IN ({format_strings})"
        cursor.execute(query, tuple(question_ids_with_status))
        questions = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

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
        'username': username,
        'score': user_dict['score'],
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

port = int(os.environ.get('PORT', 8080))
app.run(host='0.0.0.0', port=port)
