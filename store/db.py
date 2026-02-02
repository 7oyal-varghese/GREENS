from pymongo import MongoClient
from django.conf import settings

client = MongoClient(settings.MONGO_URI)
db = client["greens"]

products_collection = db["products"]
cart_collection = db["carts"]
orders_collection = db["orders"]