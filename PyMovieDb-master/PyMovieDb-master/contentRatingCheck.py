import os
import json

base_path = r'movies'
years = ['2018', '2019', '2020', '2021', '2022', '2023']
directories = [os.path.join(base_path, year) for year in years]

unique_content_ratings = set()

for directory in directories:
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    content_rating = data.get('contentRating')
                    if content_rating:
                        unique_content_ratings.add(content_rating)

print("Unique Content Ratings:")
for rating in unique_content_ratings:
    print(rating)
