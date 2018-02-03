import pymongo

conn = pymongo.MongoClient()

db = conn.test

coll = db.coll_name

coll.insert({'vasu': 'Gaur'})