import os
import json
import tkinter as tk
from tkinter import ttk

base_path = r'C:\Users\Admin\Downloads\PyMovieDb-master\PyMovieDb-master\movies'
years = ['2018', '2019', '2020', '2021', '2022', '2023']
directories = [os.path.join(base_path, year) for year in years]


def load_movies(directory):
    movies = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                movie_data = json.load(file)
                movies.append(movie_data)
    return movies


def generate_id(selected_genres):
    return hash(','.join(selected_genres))


def recommend_movies(selected_genres):
    selected_movies = [movie for movie in all_movies if any(genre in movie['genre'] for genre in selected_genres)]

    # Exclude movies without a rating
    selected_movies = [movie for movie in selected_movies if 'rating' in movie and 'ratingValue' in movie['rating']]

    if not selected_movies:
        return [("No movies found in the selected genres.", "", "")]
    else:
        # Handle movies without a rating by providing a default value
        selected_movies.sort(
            key=lambda x: x['rating'].get('ratingValue', 0) if x['rating'].get('ratingValue') is not None else 0,
            reverse=True)

        recommendations = []
        for movie in selected_movies[:150]:  # Displaying the top 150 recommendations
            rating_value = movie['rating'].get('ratingValue', 'N/A') if movie['rating'].get(
                'ratingValue') is not None else 'N/A'
            recommendations.append((
                movie['name'],
                ', '.join(movie['genre']),
                f"Rating: {rating_value}\nDescription: {movie['description']}"
            ))
        return recommendations


def on_genre_button_click(genre):
    if genre in selected_genres:
        selected_genres.remove(genre)
        genre_buttons[genre].configure(style='TButton')
    else:
        selected_genres.append(genre)
        genre_buttons[genre].configure(style='Selected.TButton')
    update_selected_genres()


def update_selected_genres():
    selected_genres_label.config(text=f"Selected Genres: {', '.join(selected_genres)}")


def on_confirm():
    recommendations = recommend_movies(selected_genres)

    # Clear existing items in Treeview
    for item in recommendations_tree.get_children():
        recommendations_tree.delete(item)

    # Insert new recommendations into Treeview
    for idx, recommendation in enumerate(recommendations, 1):
        recommendations_tree.insert("", "end", values=(idx, *recommendation))


# Main GUI window
root = tk.Tk()
root.title("Movie Recommender")
root.geometry("800x400")

# Style configuration
style = ttk.Style()
style.configure('Selected.TButton', background='#555555', foreground='white')

# Frame for genre buttons with scroll bar
genre_frame = ttk.Frame(root)
genre_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")

canvas = tk.Canvas(genre_frame, highlightthickness=0)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

scrollbar = ttk.Scrollbar(genre_frame, orient=tk.HORIZONTAL, command=canvas.xview)
scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

canvas.configure(xscrollcommand=scrollbar.set)

# Frame inside the canvas to hold genre buttons
genre_buttons_frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=genre_buttons_frame, anchor=tk.NW)

# Selected Genres label
selected_genres_label = ttk.Label(genre_frame, text="Selected Genres:")
selected_genres_label.pack(pady=5)

# Confirm button
confirm_button = ttk.Button(genre_frame, text="Confirm", command=on_confirm)
confirm_button.pack(pady=10)

# Genre buttons
selected_genres = []
genre_buttons = {}

genres = [
    "History", "Biography", "Thriller", "Romance", "Crime", "Fantasy", "Family",
    "Adventure", "Music", "Horror", "Action", "War", "Comedy", "Drama", "Western",
    "Mystery", "Sci-Fi", "Musical", "Sport", "Animation", "Documentary", "Short"
]

for genre in genres:
    genre_buttons[genre] = ttk.Button(genre_buttons_frame, text=genre, command=lambda g=genre: on_genre_button_click(g))
    genre_buttons[genre].grid(row=0, column=genres.index(genre), padx=5)

# Update the scroll region of the canvas
genre_buttons_frame.update_idletasks()
canvas.config(scrollregion=canvas.bbox(tk.ALL))

# Frame for Treeview
treeview_frame = ttk.Frame(root)
treeview_frame.grid(row=0, column=1, sticky="nsew")

# Recommendations display in Treeview
recommendations_tree = ttk.Treeview(treeview_frame, columns=("Index", "Title", "Genres", "Details"), show="headings")
recommendations_tree.heading("Index", text="Index")
recommendations_tree.heading("Title", text="Title")
recommendations_tree.heading("Genres", text="Genres")
recommendations_tree.heading("Details", text="Details")
recommendations_tree.column("Index", width=50, anchor=tk.CENTER)
recommendations_tree.column("Title", width=150, anchor=tk.W)
recommendations_tree.column("Genres", width=150, anchor=tk.W)
recommendations_tree.column("Details", width=400, anchor=tk.W)
recommendations_tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=1)

# Initialize movie data
all_movies = []
for directory in directories:
    all_movies.extend(load_movies(directory))

# Set weight for resizing columns
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)

root.mainloop()
