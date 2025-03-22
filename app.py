from flask import Flask, render_template
from functions import validate_client_list
from variables import client_csv_file_path, un_sc_url, number_of_matches

app = Flask(__name__)

# Get the matched clients
matched_clients = validate_client_list(client_csv_file_path, un_sc_url, number_of_matches)

@app.route('/')
def index():
    return render_template('index.html', matched_clients=matched_clients)

if __name__ == '__main__':
    app.run(debug=True)
