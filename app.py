from flask import Flask, render_template, request
import json
import requests

app = Flask(__name__)

# Define your routes and views
@app.route('/')
def index():
    # Render the template for the index page
    return render_template('/page.html')

@app.route('/process', methods=['POST'])
def process():
    # Retrieve the selected constraints from the form data
    rules = []
    rule_index = 1
    while True:
        field = request.form.get(f'field{rule_index}')
        predicate = request.form.get(f'predicate{rule_index}')
        value = request.form.get(f'value{rule_index}')
        if field and predicate and value:
            rule = {
                'fieldName': field,
                'predicate': predicate.lower(),
                'value': value
            }
            rules.append(rule)
            rule_index += 1
        else:
            break

    # Retrieve the selected predicate from the form data
    predicate = request.form.get('predicate')

    # Retrieve the selected actions from the form data
    actions = []
    action_index = 1
    while True:
        action = request.form.get(f'action{action_index}')
        if action:
            folder = request.form.get(f'folder{action_index}')
            if action.lower() == 'move message' and folder:
                actions.append(f'{action}:{folder}')
            else:
                actions.append(action.lower())
            action_index += 1
        else:
            break

    # Create the data dictionary to be sent in the request
    data = {
        'rules': rules,
        'predicate': predicate,
        'actions': actions
    }

    # Make a request to the process endpoint of the process.py script
    response = requests.post('http://localhost:3233/process', json=data)

    if response.status_code == 200:
        # Return a success message to the user
        return 'Actions performed successfully'
    else:
        # Return an error message to the user
        return 'Error processing actions'

if __name__ == '__main__':
    app.run(debug=True)
