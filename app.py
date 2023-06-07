from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import functions
import git
import tempfile
import config
from flask_babel import Babel, gettext
from flask import g 


# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

###SETUP BABEL###

app.config['BABEL_DEFAULT_LOCALE'] = 'ja'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['LANGUAGES'] = {
    'en': 'English',
    'ja': '日本語'
}

def get_locale():
    return session.get('lang', request.accept_languages.best_match(['ja', 'ja_JP', 'en']))

babel = Babel(app, locale_selector=get_locale)

###SWITCHING LANGUAGE###

@app.route('/set_language/<lang>')
def set_language(lang):
    session['lang'] = lang
    print(f"Language of website was set to: {session['lang']}")
    return redirect('/')

###PASSWORD PROTECTING###

# Create a users dictionary with usernames and hashed passwords
users = {
    config.entrance_id: generate_password_hash(config.entrance_password)
}

# Initialize HTTPBasicAuth
auth = HTTPBasicAuth()

# Retrieve the password hash of the user
@auth.get_password
def get_password(username):
    return users.get(username)

# Verify the user's password
@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        session['username'] = username
        return True
    return False

# Handle 401 error for unauthorized access
@app.errorhandler(401)
def unauthorized_handler(error):
    return 'Unauthorized access.', 401

###FOR SWITCHING LANGUAGE###

# creat g object for turning the order of audio language
@app.before_request
def before_request():
    g.locale = get_locale()



###SETUP LOUTES###

# Home route, requires login
@app.route("/")
@auth.login_required
def index():
    return render_template("index.html")

# Route for error message
@app.route('/error', methods=['GET', 'POST'])
def error():
    return render_template("error.html")


# Route for processing an audio file
# This function will be called when user clicked "Start" button
@app.route('/process', methods=['GET', 'POST'])
def process():
    file_path = session.get('file_path', None) # get the path of the file from session 
    language = session.get('language', None) # get the language the users selected from session
    print("Path of uploaded file was retrieved from session:", file_path)

    if file_path is not None: # if file is uploaded successfully
        try:
            result = functions.process(file_path, language) # transcribe the file by process function that is defined in functions.py

            # create a temporary text file that has transcription in "results" folder
            with tempfile.NamedTemporaryFile(dir='results', delete=False, mode='w', encoding='utf-8') as temp_result_file:
                temp_result_file.write(result)
                session['result_file'] = temp_result_file.name

            # remove temporary files from the folder    
            os.remove(file_path)
            print(f"Deleted file at: {file_path}")

            # return "{'success': True}" in JSON format if all processes are done successfully
            return jsonify(success=True)
        
        # If any problem happened, record the error in the log and return "{'success': False}"
        except Exception as e:
            print(f"Error in \"def process()\": {e}")
            return jsonify(success=False)
        
    # return "{'success': False}" if file is uploaded successfully  
    else:
        return jsonify(success=False)

# Route for showing loading page
@app.route('/loading', methods=['GET', 'POST'])
def loading():    
    if request.method == "POST":
        try:
            print("Uploaded file:", request.files['file_input'].filename) 
            print("Selected language of the file:", request.form['language'])

            if "file_input" in request.files: # if submitted file has the id of "file_input", which is defined in index.html

                file = request.files["file_input"] # get uploaded file
                filename = secure_filename(file.filename) # change file name to safer format

                # save the file in "uploads" folder and seve the path and language in session
                file_path = os.path.join('uploads', filename) 
                file.save(file_path)
                session['file_path'] = file_path
                print("Path of uploaded file was stored in session:", file_path)
                session['language'] = request.form.get('language')  
                print("Language of uploaded file was stored in session:", session['language'])

                # redirect to loading page if all processes above have been done successfully 
                return redirect(url_for('loading'))
            
        # If any problem happened, record the error in the log and return "{'success': False}"
        except Exception as e:
            print("Error:", e)
            return jsonify(success=False, error="Error processing file in \"def loading()\"."), 400
    
    else:
        # identify if the GET request came from /process or user put url down directly
        file_path = session.get('file_path', None)
        if file_path is None:
            # redirect to "error.html" if file_path is None
            return redirect(url_for('error'))
        
        # it it is GET request, display the announcement to start from top page
        return render_template('loading.html', file_path=session.get('file_path', '')) 

# Route for showing transcription results
@app.route('/results')
def results():
    result_file = session.get('result_file', None)

    # check if there is the temporary text file that has transcription in "results" folder
    if result_file is not None:
        with open(result_file, 'r', encoding='utf-8') as f: # open and read it
            result = f.read()

        # remove temprary file from "results" folder, result_file and file_path from session
        os.remove(result_file)
        session.pop('result_file', None)
        session.pop('file_path', None)
        print("File path and result was removed from session")

        # display results
        return render_template('results.html', result=result)
    
    # it it is GET request, display the announcement to start from top page    
    else:
        return redirect(url_for('error'))
    

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, threaded=True)