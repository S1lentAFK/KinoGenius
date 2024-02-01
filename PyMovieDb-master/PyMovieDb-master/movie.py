import os
import json
import csv
from PyMovieDb import IMDB


imdb = IMDB()


csv_file_path = 'movies2018_2023.csv'
fieldnames = ['Movie', 'Year']

with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile, fieldnames=fieldnames)


    next(reader, None)

    for row in reader:
        movie_name = row['Movie']
        movie_year = row['Year']

        try:

            res = imdb.get_by_name(movie_name, tv=False)


            movie_name = movie_name.replace(':', '')


            base_folder = 'movies'
            year_folder = os.path.join(base_folder, movie_year)
            os.makedirs(year_folder, exist_ok=True)


            file_path = os.path.join(year_folder, f'{movie_name}.json')
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(res, json_file, ensure_ascii=False, indent=4)
                print(res)
                print(f"Spremljeno {movie_name}.json u {year_folder}")

        except Exception as e:
            print(f"Pogreška pri dohvaćanju podataka za {movie_name}: {str(e)}")
