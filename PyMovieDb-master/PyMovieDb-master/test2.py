import tkinter as tk
from tkinter import messagebox
import requests
import json
import os
import customtkinter


selected_genres = []
genre_buttons = {}

def login():
    username = entry_username.get()
    password = entry_password.get()

    # Send credentials to the server for verification
    response = requests.post("http://16.171.25.101/login", json={"username": username, "password": password})

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

def poslogin():
    username = entry_username2.get()
    password = entry_password2.get()

    # Send credentials to the server for verification
    response = requests.post("http://16.171.25.101/login", json={"username": username, "password": password})

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

def preregister():
    frmlog.pack_forget()
    frmreg.pack()
def register():
    frmlog.pack_forget()
    frmreg.pack()

    username = entry_username2.get()
    password = entry_password2.get()

    # Let the user pick genres
    selected_genres = select_genres()

    # Send new user registration data and genres to the server
    response = requests.post("http://16.171.25.101/register", json={"username": username, "password": password, "genres": selected_genres})

    if response.status_code == 200:
        messagebox.showinfo("Registration Successful", "You can now login.")
        poslogin()
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
    response = requests.post("http://16.171.25.101/update_genres", json={"user_id": user_id, "genres": genres})

    try:
        response_data = response.json()
        if response_data.get("user_id") and response_data.get("genres"):
            messagebox.showinfo("Genres Updated", f"Genres updated successfully. User ID: {response_data['user_id']}, Genres: {response_data['genres']}")
        else:
            messagebox.showerror("Update Failed", "Invalid response from the server")
    except json.JSONDecodeError:
        messagebox.showerror("Update Failed", "Invalid JSON response from the server")

def select_genres():
    def submit_genres():
        pick.destroy()  # Close the genre selection window

    def update_selected_genres():
        # Update the picked_gen frame with selected genres as disabled buttons
        for widget in picked_gen.winfo_children():
            widget.destroy()  # Clear existing buttons
        for selected_genre in selected_genres:
            selected_button = customtkinter.CTkButton(picked_gen, text=selected_genre, font=(("Roboto", 16, "bold")), state="disabled")
            selected_button.pack(padx=5, pady=5, fill="x")

    def on_genre_button_click(genre):
        if genre in selected_genres:
            selected_genres.remove(genre)
            genre_buttons[genre].configure(fg_color=("#3a7ebf", "#1f538d"))
        else:
            selected_genres.append(genre)
            genre_buttons[genre].configure(fg_color=("#325882", "#14375e"))
        update_selected_genres()

    pick = customtkinter.CTkToplevel(root)
    pick.title("Postavljane profila")
    pick.geometry("700x500")
    customtkinter.CTkLabel(pick, text=f"Pozdrav, {entry_username2.get()}. Kako bismo mogli postaviti vaš profil", font=(("Roboto", 20))).pack()
    customtkinter.CTkLabel(pick, text="Recite nam kakvu vrstu filmova volite:", font=(("Roboto", 20))).pack(pady=5, padx=5)
    gen_height = 40  # Adjust the height as needed
    gen = customtkinter.CTkScrollableFrame(pick, orientation="horizontal")
    gen.pack(side="top", fill="x", expand=False, pady=15, padx=12)
    gen.configure(height=gen_height)
    # Genre buttons

    print("Available Genres:")
    genres = [
        "Fantasy", "Animation", "Sport", "Romance", "Comedy", "Thriller", "Musical",
        "Adventure", "War", "Documentary", "Horror", "Drama", "Action", "Sci-Fi",
        "Mystery", "Crime", "Family", "Short", "Western", "Biography", "Music", "History"
    ]
    for genre in genres:
        genre_buttons[genre] = customtkinter.CTkButton(gen, text=genre, font=(("Roboto", 16, "bold")), command=lambda g=genre: on_genre_button_click(g))
        genre_buttons[genre].grid(row=0, column=genres.index(genre), padx=5)
    for genre in genres:
        print(genre)

    picked_gen = customtkinter.CTkScrollableFrame(pick)
    picked_gen.pack(pady=12, padx=12, fill="both", expand=True)

    # Add a Submit button to finalize genre selection
    submit_button = customtkinter.CTkButton(pick, text="Submit", font=(("Roboto", 20, "bold")), command=submit_genres)
    submit_button.pack(side="bottom", fill="both", padx=10, pady=12)

    # Initialize selected genres
    selected_genres = []

    # Wait for the user to interact with the GUI and then return the selected genres
    pick.wait_window(pick)
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

def hide():
    if check.get() == "on":
        entry_password.configure(show="")
    else:
        entry_password.configure(show="*")

def hide2():
    if check.get() == "on":
        entry_password2.configure(show="")
    else:
        entry_password2.configure(show="*")

# GUI Setup
root = customtkinter.CTk()
root.title("KinoGenius")
root.withdraw()
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
customtkinter.deactivate_automatic_dpi_awareness()

loginreg = customtkinter.CTkToplevel(root)
loginreg.title("login/registracija")
frmlog = customtkinter.CTkFrame(loginreg)
frmreg = customtkinter.CTkFrame(loginreg)

frmlog.pack()





label_username = customtkinter.CTkLabel(frmlog, text="Username:")
label_password = customtkinter.CTkLabel(frmlog, text="Password:")
entry_username = customtkinter.CTkEntry(frmlog)
entry_password = customtkinter.CTkEntry(frmlog, show="*")

check = customtkinter.StringVar(value="off")
chck = customtkinter.CTkCheckBox(frmlog, text="Prikaži lozinku?", command=hide, onvalue="on", offvalue="off", variable=check)
ost = customtkinter.CTkCheckBox(frmlog, text="Ostanite prijavljeni?")

button_login = customtkinter.CTkButton(frmlog, text="Login", command=login)
button_register = customtkinter.CTkButton(frmlog, text="Registracija", command=preregister)

label_username.grid(row=0, column=0, pady=10, padx = 12)
label_password.grid(row=1, column=0, pady=10, padx = 12)
entry_username.grid(row=0, column=1, pady=10, padx = 12)
entry_password.grid(row=1, column=1, pady=10, padx = 12)
ost.grid(row=0, column=2, pady=10, padx = 12)
chck.grid(row=1, column=2, pady=10, padx = 12)
button_login.grid(row=2, column=1, pady=10, padx = 12)
button_register.grid(row=3, column=1, pady=10, padx = 12)

#registracija
label_username2 = customtkinter.CTkLabel(frmreg, text="Username:")
label_password2 = customtkinter.CTkLabel(frmreg, text="Password:")
entry_username2 = customtkinter.CTkEntry(frmreg)
entry_password2 = customtkinter.CTkEntry(frmreg, show="*")

check2 = customtkinter.StringVar(value="off")
chck2 = customtkinter.CTkCheckBox(frmreg, text="Prikaži lozinku?", command=hide2, onvalue="on", offvalue="off", variable=check)
ost2 = customtkinter.CTkCheckBox(frmreg, text="Ostanite prijavljeni?")

button_login2 = customtkinter.CTkButton(frmreg, text="Login", command=login)
button_register2 = customtkinter.CTkButton(frmreg, text="Registracija", command=register)

label_username2.grid(row=0, column=0, pady=10, padx = 12)
label_password2.grid(row=1, column=0, pady=10, padx = 12)
entry_username2.grid(row=0, column=1, pady=10, padx = 12)
entry_password2.grid(row=1, column=1, pady=10, padx = 12)
ost2.grid(row=0, column=2, pady=10, padx = 12)
chck2.grid(row=1, column=2, pady=10, padx = 12)
button_register2.grid(row=2, column=1, pady=10, padx = 12)

root.mainloop()
