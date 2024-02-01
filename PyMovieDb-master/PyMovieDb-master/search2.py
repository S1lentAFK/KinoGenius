import os
import json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import random

# Set a higher limit for Image.MAX_IMAGE_PIXELS
Image.MAX_IMAGE_PIXELS = 1000000000  # Adjust the limit based on your needs

def display_movie_info(movie_data):
    # Create a top-level window for detailed movie information
    detail_window = tk.Toplevel(root)
    detail_window.title(movie_data.get("name", "Movie Details"))

    # Create a frame inside the window
    frame = ttk.Frame(detail_window)
    frame.pack(padx=10, pady=10, fill='both', expand=True)

    # Display detailed movie information
    for i, label_text in enumerate(labels):
        ttk.Label(frame, text=label_text + ":").grid(row=i, column=0, sticky='w')
        ttk.Label(frame, text=movie_data.get(label_text, "N/A")).grid(row=i, column=1, sticky='w')

    # Display the movie poster image in the detailed window
    poster_url = movie_data.get("poster", "N/A")
    if poster_url != "N/A":
        response = requests.get(poster_url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img = ImageTk.PhotoImage(img)
        ttk.Label(frame, image=img).grid(row=0, column=2, rowspan=len(labels), padx=10)
        ttk.Label(frame, image=img).img = img  # Keep a reference to the image to prevent garbage collection

# Create the main window
root = tk.Tk()
root.title("Movie Info Viewer")

# Create a canvas with a scrollbar
canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Create a frame for the movie cards
frame = ttk.Frame(scrollable_frame)
frame.pack(padx=10, pady=10)

# Define labels for movie attributes
labels = ["Movie Name", "Description", "Director", "Poster URL", "IMDb URL", "Rating",
          "Content Rating", "Genres", "Date Published", "Keywords", "Duration", "Actors"]

# Load and display 50 movies
limit = 50
base_path = r'C:\Users\Admin\Downloads\PyMovieDb-master\PyMovieDb-master\movies'
years = ['2018', '2019', '2020', '2021', '2022', '2023']
directories = [os.path.join(base_path, year) for year in years]

random_movies = []

for directory in directories:
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Check if the file is a JSON file
        if filename.endswith('.json'):
            # Load JSON data from the file
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Get movie poster image
            poster_url = data.get("poster", "N/A")
            if poster_url != "N/A":
                random_movies.append(data)
                limit -= 1

                if limit == 0:
                    break

    if limit == 0:
        break

# Shuffle the randomly picked movies
random.shuffle(random_movies)

# Display movie cards as buttons with images
for movie_data in random_movies:
    # Get movie poster image
    poster_url = movie_data.get("poster", "N/A")
    if poster_url != "N/A":
        response = requests.get(poster_url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img.thumbnail((150, 200))
        img = ImageTk.PhotoImage(img)

        # Create a button with the movie poster image
        button = tk.Button(frame, image=img, text=movie_data.get("name", "N/A"),
                           compound=tk.TOP, command=lambda data=movie_data: display_movie_info(data))
        button.img = img  # Keep a reference to the image to prevent garbage collection
        button.grid(row=len(random_movies), column=random_movies.index(movie_data), padx=10, pady=10)

# Pack the widgets
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Start the main loop
root.mainloop()
