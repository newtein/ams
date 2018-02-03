
from flask import Flask, render_template, request,redirect, url_for
from datetime import timedelta
from flask_pymongo import PyMongo
import ntplib,datetime

app = Flask(__name__)
app.config['MONGO_DBNAME']='admin'
app.config['MONGO_URI']='mongodb://admin:admin123@localhost:27017/admin'
mongo=PyMongo(app)

@app.route('/',methods=["GET","POST"])
def index():
    if request.method=="POST":
        print("POST2")
        attem_user=request.form['username']
        attem_pass=request.form['password']

        print(attem_pass,attem_user)

        l=mongo.db.users.find_one({"username":attem_user})
        print(l,attem_pass,attem_user)
        if(l['username']==attem_user):
                    if(l['password']==attem_pass):
                        print("hey--")
                        session["username"]=attem_user
                        session["type"]=l["type"]
                        return redirect(url_for('login'))
    return render_template('hello.html')


@app.route("/login")
def login():
    if "username" in session:
       save_att(session["username"])
       if session["type"]=="EMP":
               return render_template('dashboard.html', name=session["username"], type=session["type"])
       elif session["type"]=="HR":
               return render_template('dashboard.html',name=session["username"],type=session["type"])
    else:
      return render_template('hello.html')

def save_att(x):
    pass
@app.route('/newemployee')
def newemployee():
    return render_template('newemployee.html',name=session["username"],type=session["type"])


if __name__ == "__main__":
    session={}
    app.run(debug=True)