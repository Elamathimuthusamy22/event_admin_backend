from flask import Flask, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
import pymongo
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS
app.config.from_pyfile('config.py')
app.secret_key = 'xyz1234nbg789ty8inmcv2134'

client = MongoClient('mongodb://localhost:27017/')
db = client['user_login_system']
users_collection = db['users']
events_collection = db['events']
winner1_collection = db['winner1']
winner2_collection = db['winner2']
competition1_collection = db['competition1']
competition2_collection = db['competition2']
participants1_collection = db['participants1']
participants2_collection = db['participants2']

logging.basicConfig(level=logging.DEBUG)

def convert_objectid_to_str(doc):
    """Convert ObjectId to string in MongoDB documents."""
    if isinstance(doc, list):
        for item in doc:
            if '_id' in item and isinstance(item['_id'], ObjectId):
                item['_id'] = str(item['_id'])
    elif isinstance(doc, dict):
        if '_id' in doc and isinstance(doc['_id'], ObjectId):
            doc['_id'] = str(doc['_id'])
    return doc
users = [
    {'username': 'admin', 'password': 'admin', 'role': 'admin1'},
    {'username': 'admin1', 'password': 'admin1', 'role': 'admin2'}
]

@app.route('/')
def index():
    """Index route to verify API is working."""
    return jsonify({"message": "Welcome to the Flask API"})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Mock authentication logic (replace with actual database queries)
    for user in users:
        if user['username'] == username and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            return jsonify({"message": "Login successful", "role": user['role']}), 200

    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/CompetitionSelection')
def CompetitionSelection():
    """Route to check access to competition selection."""
    if 'username' in session:
        return jsonify({"message": "Access granted"}), 200
    else:
        return jsonify({"message": "Unauthorized"}), 401

@app.route('/competition1', methods=['GET', 'POST'])
def competition1():
    """Route for competition1 data and operations."""
    if 'role' in session and session['role'] != 'admin':
        return redirect(url_for('error'))

    if request.method == 'POST':
        try:
            data = request.get_json()
            for key, value in data.items():
                if key.startswith('attendance_'):
                    user_id = key.split('_')[1]
                    attendance = value  # value is expected to be a boolean
                    competition1_collection.update_one(
                        {'user_id': user_id},
                        {'$set': {'attendance': attendance}},
                        upsert=True
                    )
            return jsonify({"message": "Attendance updated successfully"}), 200
        except Exception as e:
            logging.error(f"An error occurred while updating attendance: {str(e)}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    else:
        try:
            if competition1_collection.count_documents({}) == 0:
                events_cursor = events_collection.find({'event_name': 'Competition 1'})
                for event_data in events_cursor:
                    user_id = event_data['_id']
                    username = event_data['username']
                    competition1_collection.insert_one({'user_id': user_id, 'username': username, 'attendance': False})

            competition1_participants_cursor = competition1_collection.find()
            competition1_participants = list(competition1_participants_cursor)
            competition1_participants = convert_objectid_to_str(competition1_participants)

            return jsonify({"participants": competition1_participants}), 200
        except PyMongoError as e:
            logging.error(f"An error occurred with MongoDB: {str(e)}")
            return jsonify({"error": f"An error occurred with MongoDB: {str(e)}"}), 500
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/competition2', methods=['GET', 'POST'])
def competition2():
    """Route for competition2 data and operations."""
    if 'role' in session and session['role'] != 'admin1':
        return redirect(url_for('error'))

    if request.method == 'POST':
        try:
            data = request.get_json()
            for key, value in data.items():
                if key.startswith('attendance_'):
                    user_id = key.split('_')[1]
                    attendance = value  # value is expected to be a boolean
                    competition2_collection.update_one(
                        {'user_id': user_id},
                        {'$set': {'attendance': attendance}},
                        upsert=True
                    )
            return jsonify({"message": "Attendance updated successfully"}), 200
        except Exception as e:
            logging.error(f"An error occurred while updating attendance: {str(e)}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    else:
        try:
            if competition2_collection.count_documents({}) == 0:
                events_cursor = events_collection.find({'event_name': 'Competition 2'})
                for event_data in events_cursor:
                    user_id = event_data['_id']
                    username = event_data['username']
                    competition2_collection.insert_one({'user_id': user_id, 'username': username, 'attendance': False})

            competition2_participants_cursor = competition2_collection.find()
            competition2_participants = list(competition2_participants_cursor)
            competition2_participants = convert_objectid_to_str(competition2_participants)

            return jsonify({"participants": competition2_participants}), 200
        except PyMongoError as e:
            logging.error(f"An error occurred with MongoDB: {str(e)}")
            return jsonify({"error": f"An error occurred with MongoDB: {str(e)}"}), 500
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/participants1', methods=['GET', 'POST'])
def participants1():
    """Route for participants1 data and operations."""
    if 'role' in session and session['role'] != 'admin':
        return redirect(url_for('error'))

    if request.method == 'POST':
        try:
            data = request.get_json()
            user_data = {}
            for key, value in data.items():
                if key.startswith('round1_') or key.startswith('round2_'):
                    user_id = key.split('_')[1]
                    round_number = key.split('_')[0][-1]
                    round_marks = int(value)
                    participant_info = competition1_collection.find_one({'user_id': user_id})
                    if participant_info:
                        username = participant_info.get('username', 'Unknown')
                    participants1_collection.update_one(
                        {'user_id': user_id},
                        {'$set': {f'round{round_number}_marks': round_marks, 'username': username}},
                        upsert=True
                    )
                    if user_id in user_data:
                        user_data[user_id]['total_marks'] += round_marks
                        user_data[user_id]['round_count'] += 1
                    else:
                        user_data[user_id] = {'username': username, 'total_marks': round_marks, 'round_count': 1}

            for user_id, data in user_data.items():
                average_marks = data['total_marks'] / data['round_count']
                winner1_collection.update_one(
                    {'user_id': user_id},
                    {'$set': {'username': data['username'], 'average_marks': average_marks}},
                    upsert=True
                )

            return jsonify({"message": "Marks updated successfully"}), 200
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    else:
        try:
            participants1_users = []
            for participant in competition1_collection.find({'attendance': True}):
                user_id = participant.get('user_id')
                username = participant.get('username', 'Unknown')
                participants1_users.append({'user_id': user_id, 'username': username})

            participants1_users = convert_objectid_to_str(participants1_users)
            return jsonify({"participants": participants1_users}), 200
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/participants2', methods=['GET', 'POST'])
def participants2():
    """Route for participants2 data and operations."""
    if 'role' in session and session['role'] != 'admin1':
        return redirect(url_for('error'))

    if request.method == 'POST':
        try:
            data = request.get_json()
            user_data = {}
            for key, value in data.items():
                if key.startswith('round1_') or key.startswith('round2_'):
                    user_id = key.split('_')[1]
                    round_number = key.split('_')[0][-1]
                    round_marks = int(value)
                    participant_info = competition2_collection.find_one({'user_id': user_id})
                    if participant_info:
                        username = participant_info.get('username', 'Unknown')
                    participants2_collection.update_one(
                        {'user_id': user_id},
                        {'$set': {f'round{round_number}_marks': round_marks, 'username': username}},
                        upsert=True
                    )
                    if user_id in user_data:
                        user_data[user_id]['total_marks'] += round_marks
                        user_data[user_id]['round_count'] += 1
                    else:
                        user_data[user_id] = {'username': username, 'total_marks': round_marks, 'round_count': 1}

            for user_id, data in user_data.items():
                average_marks = data['total_marks'] / data['round_count']
                winner2_collection.update_one(
                    {'user_id': user_id},
                    {'$set': {'username': data['username'], 'average_marks': average_marks}},
                    upsert=True
                )

            return jsonify({"message": "Marks updated successfully"}), 200
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    else:
        try:
            participants2_users = []
            for participant in competition2_collection.find({'attendance': True}):
                user_id = participant.get('user_id')
                username = participant.get('username', 'Unknown')
                participants2_users.append({'user_id': user_id, 'username': username})

            participants2_users = convert_objectid_to_str(participants2_users)
            return jsonify({"participants": participants2_users}), 200
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/winner1', methods=['GET'])
def get_winner1():
    """Route to get winners of competition1."""
    if 'role' in session and session['role'] != 'admin':
        return redirect(url_for('error'))

    try:
        winners_cursor = winner1_collection.find().sort('average_marks', pymongo.DESCENDING).limit(2)
        winners_list = list(winners_cursor)
        winners_list = convert_objectid_to_str(winners_list)
        return jsonify({"winners": winners_list}), 200
    except PyMongoError as e:
        logging.error(f"An error occurred with MongoDB: {str(e)}")
        return jsonify({"error": f"An error occurred with MongoDB: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/winner2', methods=['GET'])
def get_winner2():
    """Route to get winners of competition2."""
    if 'role' in session and session['role'] != 'admin1':
        return redirect(url_for('error'))

    try:
        winners_cursor = winner2_collection.find().sort('average_marks', pymongo.DESCENDING).limit(2)
        winners_list = list(winners_cursor)
        winners_list = convert_objectid_to_str(winners_list)
        return jsonify({"winners": winners_list}), 200
    except PyMongoError as e:
        logging.error(f"An error occurred with MongoDB: {str(e)}")
        return jsonify({"error": f"An error occurred with MongoDB: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/error')
def error():
    return jsonify({"error"}), 403

if __name__ == '__main__':
    app.run(debug=True)
