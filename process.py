import pymongo
import json
from flask import Flask, request, jsonify

# Establish a connection to MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['python_gmail']
collection = db['gmail_data']

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_emails():
    # Load the rules from the JSON file
    with open('rules.json') as file:
        rules = json.load(file)

    # Retrieve emails from MongoDB
    emails = collection.find()

    for email in emails:
        email_data = {
            'from': email['from'],
            'subject': email['subject'],
            'message': email['message'],
            'received_date': email['received_date']
        }

        # Apply the rules to each email
        for rule in rules:
            conditions = rule['conditions']
            actions = rule['actions']
            predicate = rule['predicate']

            if check_conditions(email_data, conditions, predicate):
                perform_actions(actions, email['_id'])
                break

    return jsonify({'message': 'Email processing completed'})

def check_conditions(email_data, conditions, predicate):
    if predicate == 'All':
        return all(check_condition(email_data, condition) for condition in conditions)
    elif predicate == 'Any':
        return any(check_condition(email_data, condition) for condition in conditions)

def check_condition(email_data, condition):
    field_name = condition['field_name']
    predicate = condition['predicate']
    value = condition['value']

    if field_name == 'From':
        field_value = email_data['from']
    elif field_name == 'Subject':
        field_value = email_data['subject']
    elif field_name == 'Message':
        field_value = email_data['message']
    elif field_name == 'Received Date/Time':
        field_value = email_data['received_date']

    if predicate == 'Contains':
        return value.lower() in field_value.lower()
    elif predicate == 'Does not Contain':
        return value.lower() not in field_value.lower()
    elif predicate == 'Equals':
        return value.lower() == field_value.lower()
    elif predicate == 'Does not equal':
        return value.lower() != field_value.lower()
    # Additional handling for date-related predicates (e.g., less than, greater than) can be added here

    return False

def perform_actions(actions, email_id):
    for action in actions:
        if action.lower().startswith('mark as read'):
            mark_as_read(email_id)
        elif action.lower().startswith('mark as unread'):
            mark_as_unread(email_id)
        elif action.lower().startswith('move message'):
            folder = action.split(':')[1].strip()
            move_message(email_id, folder)

def mark_as_read(email_id):
    # Update the email's status to marked as read in MongoDB
    collection.update_one({'_id': email_id}, {'$set': {'read': True}})

def mark_as_unread(email_id):
    # Update the email's status to marked as unread in MongoDB
    collection.update_one({'_id': email_id}, {'$set': {'read': False}})

def move_message(email_id, folder):
    # Update the email's folder in MongoDB
    collection.update_one({'_id': email_id}, {'$set': {'folder': folder}})

# Call the process_emails function to process the emails and apply the rules
process_emails()

if __name__ == '__main__':
    app.run()
