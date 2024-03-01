from flask import Flask,render_template,redirect,request,url_for,jsonify,flash

app = Flask(__name__)
users = [
    {'username': 'testuser', 'password': 12345}
]
@app.route('/',methods=['GET','POST'])
@app.route('/login',methods=['GET','POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('usr')
        password =int(request.form.get('psw'))

        # Check if the user exists and credentials match
        user = user = next((user for user in users if user['username'] == username and user['password'] == password), None)
        if user:
            # If credentials match, redirect to chat
            return redirect(url_for('main'))
        else:
            # If credentials are invalid, flash an error message
            flash('Invalid credentials. Please try again.', 'error')

            return render_template("login.html")
    else:
         return render_template("login.html")
@app.route('/chat')
def main():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
