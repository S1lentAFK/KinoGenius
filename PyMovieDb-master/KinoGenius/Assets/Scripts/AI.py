import os
import json
import tkinter as tk
from tkinter import ttk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


def get_genre_recommendations(user_genres, num_recommendations=50):
    user_genre = ', '.join(user_genres)

    genre_indices = [i for i, movie_genre in enumerate(corpus) if
                     any(gen.lower() in movie_genre.lower() for gen in user_genres)]

    if not genre_indices:
        return []

    avg_sim_scores = [(sum(cosine_sim[i]) / len(cosine_sim[i]), ratings[i], i) for i in genre_indices]

    sorted_indices = sorted(avg_sim_scores, key=lambda x: x[1], reverse=True)

    top_indices = [i for _, _, i in sorted_indices[:num_recommendations]]

    recommendations = [(titles[i], ratings[i], movie_data[i].get("genre", [])) for i in top_indices]

    return recommendations

base_path = r'../../movies'
years = ['2018', '2019', '2020', '2021', '2022', '2023']
directories = [os.path.join(base_path, year) for year in years]

movie_data = []

for directory in directories:
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                movie_info = json.load(file)
                movie_data.append(movie_info)

corpus = []
titles = []
ratings = []

for movie in movie_data:
    genres = ', '.join(movie.get("genre", []))
    director = str(movie.get("director", ""))
    actors = ', '.join(actor["name"] for actor in movie.get("actor", [])) if movie.get("actor") else ""
    features = ' '.join([
        str(movie.get("type", "")),
        genres,
        director,
        actors,
        str(movie.get("description", ""))
    ])
    corpus.append(features)
    titles.append(movie.get("name", ""))
    rating_value = movie.get("rating", {}).get("ratingValue", None)
    ratings.append(float(rating_value) if rating_value is not None else 0.0)

vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(corpus)

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

class MovieRecommendationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Recommendation System")

        self.selected_genres = []

        # Create a frame for genre selection at the top
        self.genre_frame = tk.Frame(root)
        self.genre_frame.pack(fill=tk.X, pady=10)

        tk.Label(self.genre_frame, text="Select genres:").pack(side=tk.LEFT)

        # Create a separate frame for genre buttons with a canvas and scrollbar
        self.genre_button_frame = tk.Frame(root)
        self.genre_button_frame.pack(fill=tk.X)

        self.genre_canvas = tk.Canvas(self.genre_button_frame)
        self.genre_canvas.pack(side=tk.LEFT, fill=tk.X)

        scroll_x = tk.Scrollbar(self.genre_button_frame, orient=tk.HORIZONTAL, command=self.genre_canvas.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.genre_canvas.configure(xscrollcommand=scroll_x.set)

        # Create buttons for each unique genre
        for genre in unique_genres:
            genre_button = tk.Button(self.genre_canvas, text=genre, command=lambda g=genre: self.toggle_genre(g))
            genre_button.pack(side=tk.LEFT)

        tk.Button(root, text="Confirm", command=self.show_recommendations).pack(pady=10)

        self.tree = ttk.Treeview(root, columns=("Title", "Rating", "Genres"), show="headings", height=20)
        self.tree.heading("Title", text="Title")
        self.tree.heading("Rating", text="Rating")
        self.tree.heading("Genres", text="Genres")
        self.tree.pack(pady=10)

    def toggle_genre(self, genre):
        if genre in self.selected_genres:
            self.selected_genres.remove(genre)
        else:
            self.selected_genres.append(genre)

    def show_recommendations(self):
        recommendations = get_genre_recommendations(self.selected_genres, num_recommendations=50)

        # Clear existing items in the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not recommendations:
            self.tree.insert("", "end", values=("No recommendations found", "", ""))
        else:
            for i, (title, rating, genres) in enumerate(recommendations):
                self.tree.insert("", "end", values=(title, rating, ', '.join(genres)))


if __name__ == "__main__":
    # Get the unique genres
    unique_genres = set()
    for movie in movie_data:
        unique_genres.update(movie.get("genre", []))

    root = tk.Tk()
    app = MovieRecommendationGUI(root)

    # Pack the genre_button_frame onto the root
    app.genre_button_frame.pack(fill=tk.X)

    root.mainloop()
