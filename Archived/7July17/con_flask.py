from flask import Flask
from flask_pymongo import PyMongo
app = Flask(__name__)

app.config['MONGO_DBNAME']='admin'
app.config['MONGO_URI']='mongodb://admin:admin123@localhost:27017/admin'

mongo=PyMongo(app)

@app.route('/add')
def add():
    user=mongo.db.users
    #print(type(user))
    f=user.find_one({"username":"pooja"})
    print(f)
    return str(f)

if __name__=='__main__':
    app.run(debug=True)



