import sqlite3
import requests
import json
from flask import Flask, redirect, request
from dotenv import dotenv_values

# Constants
STREAMLABS_API_BASE = "https://www.streamlabs.com/api/v1.0"
socket_token = ""
app = Flask(__name__)
config = dotenv_values(".env")

# Connect to local database
con = sqlite3.connect('db.sqlite', check_same_thread=False)
cur = con.cursor()

@app.route('/')
def main():
    # Create a new table and store the token in there
    cur.execute("CREATE TABLE IF NOT EXISTS `streamlabs_auth` (`id` INTEGER PRIMARY KEY AUTOINCREMENT, `access_token` CHAR(50), `refresh_token` CHAR(50))")
    cur.execute("SELECT access_token FROM `streamlabs_auth`")
    row = cur.fetchone()

    # If row is not None
    if(row != None):
        response = requests.get(STREAMLABS_API_BASE + "/socket/token?access_token=" + row[0])
        if response.status_code == 200:
            return "Connection success! You can close off this window now."

    # If connection failed, request for new token
    client_id = config['CLIENT_ID']
    redirect_uri = config['REDIRECT_URI']
    response_type = "code"
    scope = "donations.read+donations.create+socket.token"
    authorize_url = STREAMLABS_API_BASE + "/authorize?client_id=" + client_id + "&redirect_uri=" + redirect_uri + "&response_type=" + response_type + "&scope=" + scope
    return '<a href="' + authorize_url + '">No valid token found! Please authorize with Streamlabs!</a>'

@app.route('/auth')
def auth():
    code = request.args.get('code')

    # Send request to Streamlabs API to get the token
    # Save the token as a json file inside data variable
    data = requests.post(STREAMLABS_API_BASE + "/token?", data={
        'grant_type': "authorization_code",
        'client_id': config['CLIENT_ID'],
        'client_secret': config['CLIENT_SECRET'],
        'redirect_uri':  config['REDIRECT_URI'],
        'code': code,
    }).json()

    # Console log for debug purposes
    print(json.dumps(data, indent=1))

    # Save and commit into database
    cur.execute("INSERT INTO `streamlabs_auth` (access_token, refresh_token) VALUES (?,?)",
        [data['access_token'], data['refresh_token']])
    con.commit()
    return redirect("/")

# Main function
if __name__ == '__main__':
    app.run(host='localhost', port=8080)
    print("Open the localhost site to start!")