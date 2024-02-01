import tkinter as tk
from tkinter import messagebox
import requests
import json
import os

def login():
    username = entry_username.get()
    password = entry_password.get()

    # Send credentials to the server for verification
    response = requests.post("http://16.170.225.118/login", json={"username": username, "password": password})

    if response.status_code == 200:
        try:
            user_data = response.json()
            user_id = user_data.get('user_id')
            genres = user_data.get('genres')
            if user_id and genres:
                messagebox.showinfo("Login Successful", f"Welcome, User ID: {user_id}, Genres: {genres}")
                recommend_movies(genres)
                select_and_send_genres(user_id, genres)
            else:
                messagebox.showerror("Login Failed", "Invalid response from the server")
        except json.JSONDecodeError:
            messagebox.showerror("Login Failed", "Invalid JSON response from the server")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")
        print(response.content)

def register():
    username = entry_username.get()
    password = entry_password.get()

    # Let the user pick genres
    selected_genres = select_genres()

    # Send new user registration data and genres to the server
    response = requests.post("http://16.170.225.118/register", json={"username": username, "password": password, "genres": selected_genres})

    if response.status_code == 200:
        messagebox.showinfo("Registration Successful", "You can now login.")
    else:
        messagebox.showerror("Registration Failed", "Username already exists or an error occurred")

def recommend_movies(user_genres):
    # Get all movies
    all_movies = load_movies()

    # Filter movies based on user's selected genres
    matching_movies = [movie for movie in all_movies if any(genre in movie["genre"] for genre in user_genres)]

    # Sort movies by rating in descending order, excluding movies with None rating
    sorted_movies = sorted(matching_movies, key=lambda x: x["rating"]["ratingValue"] if x["rating"]["ratingValue"] is not None else 0, reverse=True)

    # Display the top 150 movies with name, rating, and genres
    top_movies = sorted_movies[:150]
    print("Recommended Movies:")
    for movie in top_movies:
        genres_str = ", ".join(movie["genre"])
        print(f"{movie['name']} - Rating: {movie['rating']['ratingValue']} - Genres: {genres_str}")




def select_and_send_genres(user_id, genres):
    # Send user ID and selected genres to the server
    response = requests.post("http://16.170.225.118/update_genres", json={"user_id": user_id, "genres": genres})

    try:
        response_data = response.json()
        if response_data.get("user_id") and response_data.get("genres"):
            messagebox.showinfo("Genres Updated", f"Genres updated successfully. User ID: {response_data['user_id']}, Genres: {response_data['genres']}")
        else:
            messagebox.showerror("Update Failed", "Invalid response from the server")
    except json.JSONDecodeError:
        messagebox.showerror("Update Failed", "Invalid JSON response from the server")

def select_genres():
    selected_genres = []
    print("Available Genres:")
    genres = [
        "Fantasy", "Animation", "Sport", "Romance", "Comedy", "Thriller", "Musical",
        "Adventure", "War", "Documentary", "Horror", "Drama", "Action", "Sci-Fi",
        "Mystery", "Crime", "Family", "Short", "Western", "Biography", "Music", "History"
    ]
    for genre in genres:
        print(genre)
    while True:
        user_genre = input("Enter the genre you like (or 'done' to finish): ").capitalize()
        if user_genre == 'Done':
            break
        elif user_genre in genres:
            selected_genres.append(user_genre)
        else:
            print("Invalid genre. Please enter a valid genre.")
    return selected_genres

def load_movies():
    # Specify the base path and years
    base_path = r'C:\Users\Admin\Downloads\PyMovieDb-master\PyMovieDb-master\movies'
    years = ['2018', '2019', '2020', '2021', '2022', '2023']
    directories = [os.path.join(base_path, year) for year in years]

    # Load all movies from directories
    movies = []
    for directory in directories:
        movies.extend(load_movies_from_directory(directory))
    return movies

def load_movies_from_directory(directory):
    movies = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                movie_data = json.load(file)
                movies.append(movie_data)
    return movies

# GUI Setup
root = tk.Tk()
root.title("Login System")

label_username = tk.Label(root, text="Username:")
label_password = tk.Label(root, text="Password:")
entry_username = tk.Entry(root)
entry_password = tk.Entry(root, show="*")

button_login = tk.Button(root, text="Login", command=login)
button_register = tk.Button(root, text="Register", command=register)

label_username.grid(row=0, column=0)
label_password.grid(row=1, column=0)
entry_username.grid(row=0, column=1)
entry_password.grid(row=1, column=1)
button_login.grid(row=2, column=0, columnspan=2, pady=10)
button_register.grid(row=3, column=0, columnspan=2)

root.mainloop()
