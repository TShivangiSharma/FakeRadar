from pymongo import MongoClient  ## used to connect the backend and the ront end with mongoDB
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv('MONGO_URL'))
db = client.deepfake_db
results_collection = db.results

def save_result(file_name, file_type, result):
    document = {
        "file_name": file_name,
        "file_type": file_type,
        "result": result
    }
    results_collection.insert_one(document)

def get_results():
    return list(results_collection.find({}, {'_id': 0}))