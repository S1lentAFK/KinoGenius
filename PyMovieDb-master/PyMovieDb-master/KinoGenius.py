import tkinter as tk
from tkinter import messagebox
import requests
import json
import os
import customtkinter
import threading
import time
from PIL import Image, ImageTk, ImageFilter, ImageSequence
import requests
from io import BytesIO
from fuzzywuzzy import fuzz
from tkinter import filedialog
prikaz = False

ct = 0

base_path = r'movies'
years = ['2018', '2019', '2020', '2021', '2022', '2023']
directories = [os.path.join(base_path, year) for year in years]

selected_genres = []
genre_buttons = {}



def save_user_info(username, password, genres):
    account_folder = "accounts"


    if not os.path.exists(account_folder):
        os.makedirs(account_folder)

    user_info = {
        "username": username,
        "password": password,
        "genres": genres
    }


    user_file_path = os.path.join(account_folder, f"{username}.json")
    with open(user_file_path, 'w', encoding='utf-8') as user_file:
        json.dump(user_info, user_file)

def login():
    username = entry_username.get()
    password = entry_password.get()


    response = requests.post("http://13.53.101.41/login", json={"username": username, "password": password})

    if response.status_code == 200:
        try:
            user_data = response.json()
            user_id = user_data.get('user_id')
            genres = user_data.get('genres')
            if user_id and genres:
                messagebox.showinfo("Login Successful", f"Welcome, User ID: {user_id}, Genres: {genres}")
                loginreg.withdraw()
                print("1")
                recommend_movies(genres)
                select_and_send_genres(user_id, genres)
                save_user_info(username, password, genres)
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


    response = requests.post("http://13.53.101.41/login", json={"username": username, "password": password})

    if response.status_code == 200:
        try:
            user_data = response.json()
            user_id = user_data.get('user_id')
            genres = user_data.get('genres')
            if user_id and genres:
                messagebox.showinfo("Login Successful", f"Welcome, User ID: {user_id}, Genres: {genres}")
                print("2")
                recommend_movies(genres)
                select_and_send_genres(user_id, genres)
            else:
                messagebox.showerror("Login Failed", "Invalid response from the server")
        except json.JSONDecodeError:
            messagebox.showerror("Login Failed", "Invalid JSON response from the server")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")
        print(response.content)
    loginreg.withdraw()

def preregister():
    frmlog.pack_forget()
    frmreg.pack()
def register():
    frmlog.pack_forget()
    frmreg.pack()

    username = entry_username2.get()
    password = entry_password2.get()

    loginreg.withdraw()


    selected_genres = select_genres()


    save_user_info(username, password, selected_genres)


    response = requests.post("http://13.53.101.41/register", json={"username": username, "password": password, "genres": selected_genres})

    if response.status_code == 200:
        messagebox.showinfo("Registration Successful", "You can now login.")
        print("3")
        poslogin()
    else:
        messagebox.showerror("Registration Failed", "Username already exists or an error occurred")



class MovieRecommendationsWidget(customtkinter.CTkFrame):
    def __init__(self, master, movies):
        super().__init__(master)


        button_width = 200
        button_height = 250


        for i, movie in enumerate(movies):

            row = i // 3
            col = i % 3

            self.display_movie(movie, row, col, button_width, button_height)


        self.grid(row=0, column=0, sticky="nsew")
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

    def display_movie(self, movie, row, col, button_width, button_height):



        movie_name = movie["name"]
        movie_rating = movie["rating"]["ratingValue"]
        movie_genres = ", ".join(movie["genre"])
        movie_poster_url = movie["poster"]
        movie_json = json.dumps(movie, indent=2)

        Image.MAX_IMAGE_PIXELS = 200000000000




        response = requests.get(movie_poster_url)
        poster_image = Image.open(BytesIO(response.content))
        poster_image = poster_image.resize((int(button_width * 0.8), int(button_height * 0.8)))



        tk_image = customtkinter.CTkImage(light_image=poster_image, size=(button_width, button_height))


        def show_details():

            toplevel = customtkinter.CTkToplevel(self.master)
            toplevel.title(movie_name)


            image_label = customtkinter.CTkLabel(toplevel, image=tk_image, text="")
            image_label.pack(padx=10, pady=5)


            details_label = customtkinter.CTkLabel(toplevel, text=f"{movie_name} - Rating: {movie_rating} - Genres: {movie_genres}")
            details_label.pack(pady=5, anchor="w")


            json_label = customtkinter.CTkLabel(toplevel, text=movie_json, wraplength=400, justify="left", anchor="w")
            json_label.pack(pady=5, padx=10, anchor="w")


        button = customtkinter.CTkButton(self, image=tk_image, text=movie_name, compound=tk.TOP, command=show_details)
        button.configure(width=button_width, height=button_height)
        button.grid(row=row, column=col, padx=10, pady=5)

def recommend_movies_and_display(user_genres):


    all_movies = load_movies()


    matching_movies = [movie for movie in all_movies if any(genre in movie["genre"] for genre in user_genres)]


    sorted_movies = sorted(matching_movies, key=lambda x: x["rating"]["ratingValue"] if x["rating"]["ratingValue"] is not None else 0, reverse=True)


    top_movies = sorted_movies[:10]


    movie_recommendations_widget = MovieRecommendationsWidget(movie_frame, top_movies)
    movie_recommendations_widget.pack(fill="both", expand=True, pady=12, padx=15)



def recommend_movies(user_genres):


    recommend_movies_and_display(user_genres)
    root3.deiconify()





def search_movies(query):
    results = []
    for directory in directories:
        results.extend(search_movies_in_directory(directory, query))
    return results

def search_movies_in_directory(directory, query):
    movies = load_movies_from_directory(directory)
    matching_movies = [movie for movie in movies if query.lower() in movie["name"].lower()]
    return matching_movies

def display_search_results(results):
    for widget in search_frame.winfo_children():
        widget.destroy()

    for i, movie in enumerate(results):
        button = customtkinter.CTkButton(search_frame, text=movie["name"], font=("Roboto", 16, "bold"), command=lambda m=movie: show_movie_details(m))
        button.pack(pady=10)



search_results = []


def perform_search(query):
    results = search_movies(query)

    for widget in search_frame.winfo_children():
        widget.destroy()

    if results:
        for i, movie in enumerate(results):
            button = customtkinter.CTkButton(search_frame, text=movie["name"], font=("Roboto", 16, "bold"),
                                             command=lambda m=movie: show_movie_details(m))
            button.pack(pady=10)
    else:
        no_results_label = customtkinter.CTkLabel(search_frame, text="No results found.", font=("Roboto", 14))
        no_results_label.pack(pady=10)


def on_search(event=None):
    query = entry_search.get().strip()

    if not query:
        for widget in search_frame.winfo_children():
            widget.destroy()
        return

    loading_label = customtkinter.CTkLabel(search_frame, text="Searching...", font=("Roboto", 14))
    loading_label.pack(pady=10)

    if hasattr(on_search, "_after_id"):
        root.after_cancel(on_search._after_id)

    on_search._after_id = root.after(3000, lambda: perform_search(query))


def update_search_results():
    for widget in search_frame.winfo_children():
        widget.destroy()

    display_search_results(search_results)


def show_movie_details(movie):
    print(f"Movie Details: {movie}")


def select_and_send_genres(user_id, genres):
    response = requests.post("http://13.53.101.41/update_genres", json={"user_id": user_id, "genres": genres})

    try:
        response_data = response.json()
        if response_data.get("user_id") and response_data.get("genres"):
            messagebox.showinfo("Genres Updated", f"Genres updated successfully. User ID: {response_data['user_id']}, Genres: {response_data['genres']}")
            print("4")
        else:
            messagebox.showerror("Update Failed", "Invalid response from the server")
    except json.JSONDecodeError:
        messagebox.showerror("Update Failed", "Invalid JSON response from the server")

def select_genres():
    def submit_genres():
        pick.destroy()
        root3.deiconify()

    def update_selected_genres():

        for widget in picked_gen.winfo_children():
            widget.destroy()
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
    gen_height = 40
    gen = customtkinter.CTkScrollableFrame(pick, orientation="horizontal")
    gen.pack(side="top", fill="x", expand=False, pady=15, padx=12)
    gen.configure(height=gen_height)


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


    submit_button = customtkinter.CTkButton(pick, text="Submit", font=(("Roboto", 20, "bold")), command=submit_genres)
    submit_button.pack(side="bottom", fill="both", padx=10, pady=12)


    selected_genres = []


    pick.wait_window(pick)
    return selected_genres



def load_movies():

    base_path = r'movies'
    years = ['2018', '2019', '2020', '2021', '2022', '2023']
    directories = [os.path.join(base_path, year) for year in years]


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
loginreg.withdraw()




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

def load_json_file(file_path):

    if file_path == "+":
        print("Special case for the '+' button")
    else:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            username = data.get('username', 'Unknown')
            print(f"Loading JSON file: {file_path}, Username: {username}")



def on_hover(event, button, label, username):
    threading.Thread(target=lambda: grow_button(button)).start()
    label.configure(text=username)

def on_leave(event, button, label):
    threading.Thread(target=lambda: shrink_button(button)).start()
    label.configure(text="")

def grow_button(button):
    scale_factor = 1.15
    target_size = 115

    for i in range(button.winfo_width(), target_size + 4, 2):
        button.configure(width=i, height=i)
        root.update_idletasks()
        time.sleep(0.000001)

def shrink_button(button):
    target_size = 100

    for i in range(button.winfo_width(), target_size - 1, -2):
        button.configure(width=i, height=i)
        root.update_idletasks()
        time.sleep(0.000001)

def disable_window_move(event):
    return "break"

def plus():
    root2.withdraw()
    loginreg.deiconify()

def create_button_for_json(file_path, column):
    font_style = ("Roboto", 30, "bold")

    if file_path == "+":  # Special case for the "+" button
        button = customtkinter.CTkButton(frame, text="+", font=font_style, width=100, height=100, command=plus)
        button.grid(row=2, column=0, padx=10, pady=10)
        label = customtkinter.CTkLabel(frame, text="")
        label.grid(row=3, column=0)
        button.bind("<Enter>", lambda event, btn=button, lbl=label: on_hover(event, btn, lbl, ""))
        button.bind("<Leave>", lambda event, btn=button, lbl=label: on_leave(event, btn, lbl))
    else:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            username = data.get('username', 'Unknown')

            def login_user():
                login_with_credentials(username, data.get('password', ''))

            button = customtkinter.CTkButton(frame, text='👤', font=font_style, width=100, height=100, command=login_user)
            button.grid(row=2, column=column, padx=10, pady=10)
            label = customtkinter.CTkLabel(frame, text="")
            label.grid(row=3, column=column)
            button.bind("<Enter>", lambda event, btn=button, lbl=label, usr=username: on_hover(event, btn, lbl, usr))
            button.bind("<Leave>", lambda event, btn=button, lbl=label: on_leave(event, btn, lbl))

def login_with_credentials(username, password):

    root2.withdraw()
    response = requests.post("http://13.53.101.41/login", json={"username": username, "password": password})

    if response.status_code == 200:
        try:
            user_data = response.json()
            user_id = user_data.get('user_id')
            genres = user_data.get('genres')
            if user_id and genres:
                messagebox.showinfo("Login Successful", f"Welcome, User ID: {user_id}, Genres: {genres}")
                print("5")

                recommend_movies(genres)
                select_and_send_genres(user_id, genres)
                save_user_info(username, password, genres)
            else:
                messagebox.showerror("Login Failed", "Invalid response from the server")
        except json.JSONDecodeError:
            messagebox.showerror("Login Failed", "Invalid JSON response from the server")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")
        print(response.content)



customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root2 = customtkinter.CTkToplevel(root)
root2.title("Load JSON Files")
root2.geometry("600x400")
root2.resizable(False, False)
root2.protocol("WM_DELETE_WINDOW", root2.destroy)

screen_width = root2.winfo_screenwidth()
screen_height = root2.winfo_screenheight()
window_width = 600
window_height = 400
x_coordinate = (screen_width - window_width) // 2
y_coordinate = (screen_height - window_height) // 2
root2.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

root2.bind("<B1-Motion>", disable_window_move)

customtkinter.CTkLabel(root2, text="Koji profil Koristite?", font=("Roboto", 40)).pack(padx=8, pady=8)

frame = customtkinter.CTkScrollableFrame(root2, orientation="horizontal")
frame.pack(pady=12, padx=15, fill="both", expand=True)


customtkinter.CTkLabel(frame, text="", font=("Roboto", 60)).grid(row=1, column=0)

json_directory = r"accounts"

json_files = [f for f in os.listdir(json_directory) if f.endswith(".json")]

create_button_for_json("+", 2)

for i, json_file in enumerate(json_files):
    json_file_path = os.path.join(json_directory, json_file)
    create_button_for_json(json_file_path, i + 1)

root3 = customtkinter.CTkToplevel(root)
root3.title("KinoGenius")
root3.geometry("1000x800")
root3.withdraw()

tabview = customtkinter.CTkTabview(root3)
tabview.pack(fill="both", expand=True, pady=12, padx=15)

tab_1 = tabview.add("Za vas")
tab_2 = tabview.add("Pretraživanje")
tab_3 = tabview.add("Popularne franšize")

movie_frame = customtkinter.CTkScrollableFrame(tab_1)
movie_frame.pack(fill="both", expand=True, pady=12, padx=15)

search_frame = customtkinter.CTkScrollableFrame(tab_2)
search_frame.pack(fill="both", expand=True, pady=12, padx=15)

search_label = customtkinter.CTkLabel(tab_2, text="Search Movies:", font=("Roboto", 16, "bold"))
search_label.pack(pady=10)

entry_search = customtkinter.CTkEntry(tab_2, font=("Roboto", 14))
entry_search.pack(pady=10)
entry_search.bind("<KeyRelease>", on_search)

#search_button = customtkinter.CTkButton(tab_2, text="Search", font=("Roboto", 16, "bold"), command=on_search)
#search_button.pack(pady=10)




root.mainloop()