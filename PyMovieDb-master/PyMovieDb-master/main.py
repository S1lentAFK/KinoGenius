import requests
from bs4 import BeautifulSoup
import csv

exclude_list = ['Newsletter', '2024 Movie Release Calendar', 'What To Watch', 'Netflix', 'Horror', 'Echo',
                'The Golden Globes', 'New Trailers', 'Movie News', 'TV News', 'Marvel News', 'DC News',
                '☆ Christmas Movies', 'Action', 'Comedy', 'Fantasy', 'Horror', 'K-Dramas', 'Romance', 'Sci-Fi',
                'Westerns', 'What To Watch', 'Apple TV+', 'Criterion Collection', 'Disney+', 'Hulu', 'Max', 'Netflix',
                'Prime Video', 'Shudder', 'Tubi', 'Franchise Database', 'DC Movies', 'Indiana Jones',
                'James Bond Movies', 'Jurassic Park', 'Marvel Movies', 'Marvel TV Shows', 'Star Wars Movies',
                'Studio Ghibli', 'Videos', 'Movie Database By Year', '2023', '2024', 'Movie Trailers', 'Features',
                'Movie Lists', 'TV Lists', 'Interviews', 'Reviews', 'Join Our Team', 'Newsletter', 'Advertise with us',
                'Log in', 'Write For Us', 'Home', 'Contact Us', 'Terms', 'Privacy', 'Copyright', 'About Us',
                'Fact Checking Policy', 'Corrections Policy', 'Ethics Policy', 'Ownership Policy', '2021', '2022',
                '2023', '2024', '2025', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                'September', 'October', 'November', 'December', 'Unconfirmed Release Dates', '2017', '2018', '2019',
                '2020', 'Movie', '2016']

movies_all_years = []

for year in range(2018, 2024):
    url = f"https://movieweb.com/movies/{year}/"
    response = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})

    movies = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)

        for link in links:
            text = link.text.strip()
            href = link['href']


            if not any(word in text for word in exclude_list) and not any(word in href for word in exclude_list):
                if text != '':
                    movies.append({'Movie': text, 'Year': year})

        movies_all_years.extend(movies)

    else:
        print(f"Nema rezultata za {year}. Error:", response.status_code)


with open('movies_2018-2023.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Movie', 'Year']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for movie in movies_all_years:
        writer.writerow(movie)

print("Svi filmovi spremljeni movies_2018-2023.csv")
