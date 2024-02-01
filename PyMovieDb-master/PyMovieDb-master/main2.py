import csv
from selenium import webdriver
from bs4 import BeautifulSoup

def scrape_movies_for_year(year, last_movie, writer):
    url = f"https://en.wikipedia.org/wiki/List_of_American_films_of_{year}"


    driver = webdriver.Chrome()
    driver.get(url)


    driver.implicitly_wait(10)


    page_source = driver.page_source


    driver.quit()


    soup = BeautifulSoup(page_source, 'html.parser')


    similar_elements = soup.find_all('i')


    unique_movie_names = set()

    for element in similar_elements:
        link = element.find('a', href=True)
        text = link.text.strip() if link else element.text.strip()
        href = link['href'] if link else None


        if text not in unique_movie_names:

            print(f"{text}")


            writer.writerow({'Movie': text, 'Year': year})


            if text == last_movie:
                break

            unique_movie_names.add(text)


csv_file_path = 'movies2018_2023.csv'
fieldnames = ['Movie', 'Year']

with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()


    for year, last_movie in zip(range(2018, 2024), ['Destroyer', 'Clemency', 'Pieces of a Woman', 'Memoria', 'Alice, Darling', 'Good Grief']):
        scrape_movies_for_year(year, last_movie, writer)
