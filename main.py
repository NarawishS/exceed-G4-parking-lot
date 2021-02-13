import datetime
import math
import time

from flask import Flask, request
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://exceed_user:1q2w3e4r@158.108.182.0:2277/exceed_backend'
mongo = PyMongo(app)

myCollection = mongo.db.g4


@app.route('/find', methods=['GET'])
def find():
    query = myCollection.find()
    output = []
    for d in query:
        output.append({"slot": d['slot'],
                       "not_empty": d["not_empty"],
                       "park_history": d["park_history"],
                       "car_parked": d["car_parked"]}
                      )
    return {'result': output}


@app.route('/init', methods=['POST'])
def init_db():
    hard = ['ldr1', 'ldr2', 'ldr3', 'ldr4']
    for l in hard:
        add_in = {"slot": l,
                  "not_empty": 0,
                  "park_history": [],
                  "car_parked": 0}
        myCollection.insert_one(add_in)
    return {'result': 'Created successfully'}


@app.route('/update', methods=['POST'])
def update_all():
    now = datetime.datetime.now()
    data = request.json
    hard = data.keys()
    for i in hard:
        my_query = {"slot": i}
        query = myCollection.find(my_query)
        for d in query:
            if d["not_empty"] and not data[i]:
                p_hist = d["park_history"]
                cost = math.ceil((now - p_hist[-1]["in"]).total_seconds() / 60) * 20
                p_hist[-1]["out"] = now
                p_hist[-1]["fee"] = cost
                new_values = {"$set": {"park_history": p_hist}}
                myCollection.update_one(my_query, new_values)
            elif not d["not_empty"] and data[i]:
                p_hist = d["park_history"]
                p_hist.append({"in": now,
                               "out": None,
                               "fee": 0
                               })
                new_values = {"$set": {"park_history": p_hist}}
                myCollection.update_one(my_query, new_values)
            new_values = {"$set": {"car_parked": len(d["park_history"])}}
            myCollection.update_one(my_query, new_values)
        new_values = {"$set": {"not_empty": data[i]}}
        myCollection.update_one(my_query, new_values)
    return {'result': 'Updated successfully'}


@app.route('/reset', methods=['DELETE'])
def delete_one():
    myCollection.delete_many({})
    return {'result': 'Deleted successfully'}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3000', debug=True)
