from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb+srv://francesljas:Fran2008.@cluster0.zadaprp.mongodb.net/?retryWrites=true&w=majority")
db = client['DBMoovies']
moovies = db['Moovies']

# Find and delete documents with null genre
null_genre_movies = moovies.find({"genre": {"$in": [None, "null", ""]}})
for movie in null_genre_movies:
    print(f"Deleting movie: {movie['name']}")
    moovies.delete_one({"_id": movie["_id"]})

print("Deletion process completed.")
