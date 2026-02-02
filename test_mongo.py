from pymongo import MongoClient

MONGO_URI = "mongodb+srv://joyal:joyal@cluster0.fdhyiob.mongodb.net/?appName=cluster0"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()   # Forces connection
    print("✅ MongoDB Atlas connected successfully")
except Exception as e:
    print("❌ MongoDB Atlas connection failed")
    print(e)
