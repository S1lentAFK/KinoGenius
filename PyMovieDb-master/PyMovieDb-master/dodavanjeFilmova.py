from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
uri = "mongodb+srv://francesljas:<password>@cluster0.zadaprp.mongodb.net/"
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
            f = open(f'{dirPath}\\{f.name}')
            data = eval(f.read())
            f.close()
            dodaj_film(data)

dodaj_filmove('C:\\Programi')
