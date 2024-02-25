from pymongo import MongoClient

# Connect to the MongoDB server
client = MongoClient("mongodb+srv://francesljas:Fran2008.@cluster0.zadaprp.mongodb.net/?retryWrites=true&w=majority")
db = client['DBMoovies']
moovies = db['Moovies']

# Fetch documents from the collection
cursor = moovies.find()

# Iterate over the documents
for movie_document in cursor:
    # Replace None rating value with 0
    movie_rating = float(movie_document.get("rating", {}).get("ratingValue")) if movie_document.get("rating", {}).get(
        "ratingValue") is not None else 0

    # Replace None directors with "Nicolas Sterwart" and "google.com"
    movie_directors = ", ".join(
        director["name"] for director in movie_document.get("director", [])) if movie_document.get("director",
                                                                                                   []) else "Nicolas Sterwart"
    movie_directors_urls = ", ".join(
        director["url"] for director in movie_document.get("director", [])) if movie_document.get("director",
                                                                                                  []) else "google.com"

    # Replace None actors with "Jonny Sins" and "youtube.com"
    movie_actors = ", ".join(actor["name"] for actor in movie_document.get("actor", [])) if movie_document.get("actor",
                                                                                                               []) else "Jonny Sins"
    movie_actors_urls = ", ".join(actor["url"] for actor in movie_document.get("actor", [])) if movie_document.get(
        "actor", []) else "youtube.com"

    # Replace None creators with "Johnny Johnson" and "imdb.com"
    movie_creators = ", ".join(creator["name"] for creator in movie_document.get("creator", [])) if movie_document.get(
        "creator", []) else "Johnny Johnson"
    movie_creators_urls = ", ".join(
        creator["url"] for creator in movie_document.get("creator", [])) if movie_document.get("creator",
                                                                                               []) else "imdb.com"

    # Replace None duration with "PT1H30M"
    movie_duration = movie_document.get("duration") if movie_document.get("duration") else "PT1H30M"

    # Replace None datePublished with "2001-09-11"
    movie_date = movie_document.get("datePublished") if movie_document.get("datePublished") else "2001-09-11"

    # Replace None description with "Unknown"
    movie_description = movie_document.get("description") if movie_document.get("description") else "Unknown"

    # Replace None contentRating with "15"
    movie_content_rating = movie_document.get("contentRating") if movie_document.get("contentRating") else "15"

    # Update the document in the collection
    moovies.update_one({'_id': movie_document['_id']}, {'$set': {
        "rating.ratingValue": movie_rating,
        "director": [{"name": movie_directors, "url": movie_directors_urls}],
        "actor": [{"name": movie_actors, "url": movie_actors_urls}],
        "creator": [{"name": movie_creators, "url": movie_creators_urls}],
        "duration": movie_duration,
        "datePublished": movie_date,
        "description": movie_description,
        "contentRating": movie_content_rating
    }})

    print(f"Updated movie '{movie_document.get('title')}'")

print("All updates completed.")

# Close the connection to the MongoDB server
client.close()
