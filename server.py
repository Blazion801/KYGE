from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Replace with your actual MongoDB URI
client = MongoClient("mongodb+srv://KYGE:T0v3sJE8NK3lzobh@cluster0.xvd3f.mongodb.net/?retryWrites=true&w=majority")

db = client["sensors"]
collection = db["sensorData"]

@app.route("/insert", methods=["POST"])
def insert_data():
    data = request.json
    result = collection.insert_one(data)
    return jsonify({"message": "Data inserted!", "id": str(result.inserted_id)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
