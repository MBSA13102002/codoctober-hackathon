from flask import Flask,render_template,request,session,g,url_for
import os

from flask.helpers import url_for
from werkzeug.utils import redirect

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route("/",methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        session.pop('user',None)

        uname = request.form.get("username")
        upass = request.form.get("password")
        if(upass=="pass"):
            session['user'] = uname
            return redirect(url_for('dashboard'))
    if 'user' in session:
        return redirect(url_for('dashboard'))

    return render_template("index.html")

@app.route('/dashboard')
def dashboard():
    if g.user:
        return render_template("dashboard.html",uname = session['user'])
    return redirect(url_for('index'))

@app.route("/drop",methods=['GET','POST'])
def drop():
    if request.method=='POST':
        session.pop('user')
        return redirect(url_for('index'))
@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

if __name__ =='__main__':
    app.run(debug=True)