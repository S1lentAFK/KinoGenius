import os
import json

base_path = r'C:\Users\Admin\Downloads\PyMovieDb-master\PyMovieDb-master\movies'
years = ['2018', '2019', '2020', '2021', '2022', '2023']
directories = [os.path.join(base_path, year) for year in years]

unique_genres = set()

for directory in directories:
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)

            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if 'genre' in data:
                    unique_genres.update(data['genre'])

print("Unique Genres:")
for genre in unique_genres:
    print(genre)
