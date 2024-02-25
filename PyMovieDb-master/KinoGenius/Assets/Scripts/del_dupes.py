from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb+srv://francesljas:Fran2008.@cluster0.zadaprp.mongodb.net/?retryWrites=true&w=majority")
db = client['DBMoovies']
moovies = db['Moovies']

# Aggregate to find duplicates by 'name' field
pipeline = [
    {"$group": {"_id": "$name", "count": {"$sum": 1}}},
    {"$match": {"count": {"$gt": 1}}}
]

# Execute aggregation pipeline
duplicates = list(moovies.aggregate(pipeline))

# Delete duplicates
for duplicate in duplicates:
    name = duplicate['_id']
    # Find all duplicates for this name
    duplicate_movies = moovies.find({"name": name})
    # Delete all duplicates except one
    delete_ids = [movie['_id'] for movie in duplicate_movies[1:]]  # Exclude the first one
    moovies.delete_many({"_id": {"$in": delete_ids}})

print("Duplicates removed successfully.")
