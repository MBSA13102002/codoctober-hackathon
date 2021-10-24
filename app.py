
from flask import Flask,render_template,request,session,g,url_for,redirect
import os
import json 
from firebase import Firebase
config = {
  "apiKey": "AIzaSyAU3FDUxBIHiIfo8szINjTds7oGZN1WPa0",
  "authDomain": "codoctober-hackathon.firebaseapp.com",
  "databaseURL": "https://codoctober-hackathon-default-rtdb.firebaseio.com",
  "projectId": "codoctober-hackathon",
  "storageBucket": "codoctober-hackathon.appspot.com",
  "messagingSenderId": "765466062931",
  "appId": "1:765466062931:web:4a5e0e96dc88300ef996a6",
  "measurementId": "G-QM19VJWCME"
}
firebase = Firebase(config)
db = firebase.database()
auth = firebase.auth()

app = Flask(__name__)
app.secret_key = os.urandom(24)
with open('config.json', 'r') as c:                                                                
    params = json.load(c)["params"]
def handle_catch(caller, on_exception):
    try:
         return caller()
    except:
         return on_exception
@app.route("/",methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        session.pop('user',None)
        uname = request.form.get("username")
        upass = request.form.get("password")
        try:
            user_ = auth.sign_in_with_email_and_password(uname ,upass)
            session['user'] = user_['localId']
            session['email'] = user_['email']
            g.user  = session['user']
            return redirect(url_for('dashboard'))
        except:
            return redirect(url_for('dashboard'))
    if 'user' in session:
        return redirect(url_for('dashboard'))

    return render_template("index.html")

@app.route('/dashboard')
def dashboard():
    if g.user:
        name = db.child("Users").child(g.user).child("name").get().val()
        data_LP_html = ""
        data=  ""
        try:
            data = db.child("Users").child(g.user).child("Tasks").child("-MmiB3RyCMnJ7cuoTB5s").get().val()['data']
            data_LP = db.child("Users").child(g.user).child("Learning_Paths").get()
            for item in data_LP.each():
                data_LP_html+=item.val()['html_data']
        except:
            pass

        return render_template("dashboard.html",username=name,handle_catch = handle_catch,data = data,data_LP = data_LP_html)
    return redirect(url_for('index'))

@app.route("/drop",methods=['GET','POST'])
def drop():
    if request.method=='POST':
        session.pop('user')
        return redirect(url_for('index'))

@app.route("/signup", methods = ['GET','POST'])
def signup():
    if request.method=='POST':
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            _user_ = auth.create_user_with_email_and_password(username ,password)
            auth.send_email_verification(_user_['idToken'])
            db.child("Users").child(_user_['localId']).set({
                "name":name
            })
            return render_template("success.html")
        except Exception as e:
            pass
            return render_template(url_for('index'))
    return render_template("signup.html")
@app.route('/passchange',methods = ['GET','POST'])
def passchange():
    if request.method == 'POST':
        email = request.form.get("pass_change_email")
        auth.send_password_reset_email(email)
        return render_template("passwordchange.html",val = "true")
    return render_template("passwordchange.html",val = "false")

@app.route("/LPC/<string:key>/",methods = ['GET','POST'])
def LPC(key):
    if (request.method=='POST'):
        temp_base64data = request.form.get("base64DATA")
        try:
            name  =  db.child("Users").child(g.user).child("Learning_Paths").child(key).child("title").get().val()
            db.child("Users").child(g.user).child("Learning_Paths").child(key).update({
                "base64_data":temp_base64data
            })
            return render_template("painter.html",name = name,key = key,base64 = temp_base64data)
        except:
            return render_template("doesnotexist.html")

    try:
        name  =  db.child("Users").child(g.user).child("Learning_Paths").child(key).child("title").get().val()
        base64data  =  db.child("Users").child(g.user).child("Learning_Paths").child(key).child("base64_data").get().val()
        return render_template("painter.html",name = name,key = key,base64 = base64data)
    except:
        return render_template("doesnotexist.html")

@app.route("/LPC/delete/<string:key>/",methods=['GET','POST'])
def remove_LP(key):
    if request.method== 'POST':
        db.child("Users").child(g.user).child("Learning_Paths").child(key).remove()
        return redirect(url_for('dashboard'))



@app.route('/todolist',methods = ['GET','POST'])
def add_task():
    if(request.method == 'POST' and g.user):
        html_data = request.form.get("html_todolist")
        db.child("Users").child(g.user).child("Tasks").child("-MmiB3RyCMnJ7cuoTB5s").update({
            "data":html_data
        })
        return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))
@app.route("/learningpath",methods = ['GET','POST'])
def add_LP():
    if(request.method=='POST' and g.user):
        title = request.form.get("LP_title")
        key = request.form.get("LP_UK")
        db.child("Users").child(g.user).child("Learning_Paths").child(key).set({
            'title':title,
            "key":key,
            "base64_data":""
        })
        html_card_data = request.form.get("LP_HTML")
        db.child("Users").child(g.user).child("Learning_Paths").child(key).update({
            'html_data':html_card_data
        })
        return redirect(url_for('LPC',key = key))

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

