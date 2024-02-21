import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

uri = "mongodb+srv://francesljas:Fran2008.@cluster0.zadaprp.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))

def dodaj_film(json):
    db = client['DBMoovies']
    moovies = db['Moovies']
    moovie = moovies.insert_one(json)
    print(f'Film: {json["name"]}; ID: {moovie.inserted_id}')

def dodaj_filmove(dirPath):
    for f in os.scandir(dirPath):
        if not f.is_dir() and f.name[-4:] == 'json':
            print(f'{dirPath}\\{f.name}')
            with open(f'{dirPath}\\{f.name}', 'r') as file:
                data = json.load(file)
                # Replace 'null' with 'None'
                data = recursive_replace(data, 'null', None)
                dodaj_film(data)

def recursive_replace(data, target, replacement):
    if isinstance(data, dict):
        return {k: recursive_replace(v, target, replacement) for k, v in data.items()}
    elif isinstance(data, list):
        return [recursive_replace(item, target, replacement) for item in data]
    elif data == target:
        return replacement
    else:
        return data

dodaj_filmove(r'C:\Users\Admin\Documents\GitHub\MovieGenius\PyMovieDb-master\PyMovieDb-master\movies\2023')
