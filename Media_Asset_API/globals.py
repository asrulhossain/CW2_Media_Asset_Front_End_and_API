from pymongo import MongoClient

secret_key = 'mysecret'

# Mongo connection
client = MongoClient("mongodb://localhost:27017")
db = client.damDB
users = db.users
projects = db.projects
assets = db.assets
tags = db.tags
blacklist = db.blacklist
