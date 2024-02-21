import re
import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import os
import customtkinter
import threading
import time
from PIL import Image, ImageTk, ImageFilter, ImageSequence
import requests
from io import BytesIO
from googletrans import Translator
from PIL import ImageDraw

from pymongo import MongoClient
import webbrowser

from fuzzywuzzy import fuzz
from tkinter import filedialog
prikaz = False

ct = 0

client = MongoClient("mongodb+srv://francesljas:Fran2008.@cluster0.zadaprp.mongodb.net/?retryWrites=true&w=majority")
db = client['DBMoovies']
moovies = db['Moovies']

base_path = r'movies'
years = ['2018', '2019', '2020', '2021', '2022', '2023']
directories = [os.path.join(base_path, year) for year in years]

selected_genres = []
genre_buttons = {}


def destroy_all_windows_and_exit():
    for window in root.winfo_children():
        if isinstance(window, tk.Toplevel):
            window.destroy()
    root.destroy()
    root.quit()

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


    response = requests.post("http://16.170.246.163/login", json={"username": username, "password": password})

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
                more_button = customtkinter.CTkButton(movie_frame, text="Učitaj još",
                                                      command=lambda: recommend_more_movies(genres))
                more_button.pack(pady=10, padx=10, side="bottom")
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


    response = requests.post("http://16.170.246.163/login", json={"username": username, "password": password})

    if response.status_code == 200:
        try:
            user_data = response.json()
            user_id = user_data.get('user_id')
            genres = user_data.get('genres')
            if user_id and genres:
                messagebox.showinfo("Login Successful", f"Welcome, User ID: {user_id}, Genres: {genres}")
                print("2")
                recommend_movies(genres)
                more_button = customtkinter.CTkButton(movie_frame, text="Učitaj još",
                                                      command=lambda: recommend_more_movies(genres))
                more_button.pack(pady=10, padx=10, side="bottom")
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


    response = requests.post("http://16.170.246.163/register", json={"username": username, "password": password, "genres": selected_genres})

    if response.status_code == 200:
        messagebox.showinfo("Registration Successful", "You can now login.")
        print("3")
        poslogin()
    else:
        messagebox.showerror("Registration Failed", "Username already exists or an error occurred")



from PIL import Image, ImageTk
import customtkinter


class MovieRecommendationsWidget(customtkinter.CTkFrame):
    def __init__(self, master, movie):
        super().__init__(master)

        translator = Translator()
        button_width = 200
        button_height = 250

        movie_name = movie["name"]
        movie_document = moovies.find_one({"name": movie_name})
        movie_poster_url = movie_document.get("poster")
        movie_rating = float(movie_document.get("rating", {}).get("ratingValue")) / 10
        movie_directors = ", ".join(director["name"] for director in movie_document.get("director", []))
        movie_directors_urls = ", ".join(director["url"] for director in movie_document.get("director", []))
        movie_actors = ", ".join(actor["name"] for actor in movie_document.get("actor", []))
        movie_actors_urls = ", ".join(actor["url"] for actor in movie_document.get("actor", []))
        movie_creators = ", ".join(creator["name"] for creator in movie_document.get("creator", []))
        movie_creators_urls = ", ".join(creator["url"] for creator in movie_document.get("creator", []))
        movie_genres = ", ".join(movie_document.get("genre", []))
        movie_duration = movie_document.get("duration")
        movie_date = movie_document.get("datePublished")
        movie_description = movie_document.get("description")
        movie_content_rating = movie_document.get("contentRating")
        more_rec_movies = moovies.aggregate([{ '$sample': { 'size': 4 }}])
        '''
        movie_rating = float(movie["rating"]["ratingValue"])
        movie_directors = ", ".join(director["name"] for director in movie["director"])
        movie_actors = ", ".join(actor["name"] for actor in movie["actor"])
        movie_genres = ", ".join(movie["genre"])
        movie_poster_url = movie["poster"]
        '''
        urls_directors = movie_directors_urls.split(", ")
        urls_actors = movie_actors_urls.split(", ")
        urls_creators = movie_creators_urls.split(", ")

        hour_regex = re.compile(r'(\d+)H')
        minute_regex = re.compile(r'(\d+)M')
        hours_match = hour_regex.search(movie_duration)
        minutes_match = minute_regex.search(movie_duration)
        hours = int(hours_match.group(1)) if hours_match else 0
        minutes = int(minutes_match.group(1)) if minutes_match else 0

        movie_cont_rating = 0
        warnings = ""

        warnings_dict = {
            "Not Rated": (12, "Nije ocijenjeno - Prikladno za osobe starije od 12 godina"),
            "12A": (12, "12A - Prikladno za osobe starije od 12 godina uz pratnju odrasle osobe"),
            "R": (18, "R - Restriktivno - Prikladno za osobe starije od 18 godina"),
            "TV-14": (14, "TV-14 - Preporučeno za osobe starije od 14 godina"),
            "6+": (6, "6+ - Prikladno za osobe starije od 6 godina"),
            "X": (18, "X - Eksplicitan sadržaj - Prikladno za osobe starije od 18 godina"),
            "18+": (18, "18+ - Eksplicitan sadržaj - Prikladno samo za punoljetne osobe"),
            "Unrated": (13, "Nepročitano - Prikladno za osobe starije od 13 godina"),
            "TV-G": (1, "TV-G - Opća publika - Prikladno za sve uzraste"),
            "Teen": (13, "Teen - Preporučeno za tinejdžere"),
            "A": (10, "A - Prikladno samo za odrasle"),
            "U": (1, "U - Univerzalno - Prikladno za sve uzraste"),
            "PG-13": (13, "PG-13 - Preporučeno za osobe starije od 13 godina uz roditeljski nadzor"),
            "PG": (13, "PG - Preporučeno uz roditeljski nadzor"),
            "Approved": (13, "Odobreno - Prikladno uz roditeljski nadzor"),
            "TV-MA": (17, "TV-MA - Zreloj publici - Prikladno samo za odrasle"),
            "TV-PG": (15, "TV-PG - Preporučeno uz roditeljski nadzor"),
            "AA": (14, "AA - Prikladno za sve uzraste"),
            "9+": (9, "9+ - Prikladno za osobe starije od 9 godina")
        }

        try:
            if movie_content_rating is not None:
                movie_cont_rating = int(movie_content_rating)
            else:
                movie_cont_rating = 12
                warnings = "Odobreno - Prikladno uz roditeljski nadzor"

            if movie_cont_rating in warnings_dict:
                movie_cont_rating, warnings = warnings_dict[movie_cont_rating]
            elif movie_content_rating == 15:
                warnings = "TV-PG - Preporučeno uz roditeljski nadzor"
            elif movie_content_rating == 16:
                warnings = "TV-MA - Zreloj publici - Prikladno samo za odrasle"
        except ValueError:
            movie_cont_rating, warnings = warnings_dict.get(movie_content_rating, (None, ""))

        if movie_date is not None:
            year, month, day = movie_date.split('-')
            year = int(year)
            month = int(month)
            day = int(day)
        else:
            year = 2022
            month = 3
            day = 16


        Image.MAX_IMAGE_PIXELS = 200000000000

        response = requests.get(movie_poster_url)
        poster_image = Image.open(BytesIO(response.content))

        poster_image = self.round_corners(poster_image, radius=60)

        poster_image = poster_image.resize((int(button_width * 0.8), int(button_height * 0.8)))

        tk_image = customtkinter.CTkImage(light_image=poster_image, size=(button_width, button_height))

        def show_details():
            root3.withdraw()
            toplevel = customtkinter.CTkToplevel(self.master)
            toplevel.title(movie_name)
            toplevel.geometry("500x800")

            main_frame = customtkinter.CTkFrame(toplevel)
            main_frame.pack(padx=15, pady=15, fill="x", expand=False)
            movie_label = customtkinter.CTkLabel(main_frame, text=movie_name, font=("Roboto", 24, "bold"))
            movie_label.pack(padx=10, pady=5)
            image_label = customtkinter.CTkLabel(main_frame, image=tk_image, text="")
            image_label.pack(padx=10, pady=5, side="left")

            secondary_frame = customtkinter.CTkScrollableFrame(main_frame)
            secondary_frame.pack(padx=10, pady=5, side="right", fill="both")

            customtkinter.CTkLabel(secondary_frame, text="Generalni detalji", font=("Roboto", 24, "bold")).pack(padx=5,
                                                                                                                pady=5)
            customtkinter.CTkLabel(secondary_frame, text=f"Trajanje: {hours*60+minutes} minuta", font=("Roboto", 12, "bold")).pack(
                padx=1, pady=1)
            customtkinter.CTkLabel(secondary_frame, text=f"Datum izdanja: {day}.{month}.{year}.", font=("Roboto", 12, "bold")).pack(padx=1, pady=1)
            customtkinter.CTkLabel(secondary_frame, text=f"Redatelji:", font=("Roboto", 12, "bold")).pack(
                padx=1, pady=1)

            for dir, url in zip(movie_directors.split(", "), urls_directors):
                dir_label = customtkinter.CTkLabel(secondary_frame, text=dir, font=("Roboto", 12), text_color="#1F538D")
                dir_label.pack()
                dir_label.bind("<Button-1>", lambda event, link=url: webbrowser.open_new(link))

            customtkinter.CTkLabel(secondary_frame, text="Glumci:", font=("Roboto", 12, "bold")).pack(padx=1, pady=1)

            # Iterate through each actor and create a label with a link
            for actor, url in zip(movie_actors.split(", "), urls_actors):
                actor_label = customtkinter.CTkLabel(secondary_frame, text=actor, font=("Roboto", 12), text_color="#1F538D")
                actor_label.pack()
                actor_label.bind("<Button-1>", lambda event, link=url: webbrowser.open_new(link))

            details_frame = customtkinter.CTkScrollableFrame(toplevel)
            details_frame.pack(padx=15, pady=15, fill="both", expand=True)
            recommend_frame = customtkinter.CTkScrollableFrame(details_frame, orientation="horizontal",
                                                               fg_color="#1A1A1A")
            recommend_frame.pack(padx=15, pady=15, fill="both", expand=True, side="bottom")
            customtkinter.CTkLabel(details_frame, text="Također preporučujemo:",
                                   font=("Roboto", 16, "bold")).pack(side="bottom")
            full_frame = customtkinter.CTkFrame(details_frame, fg_color="#1A1A1A")
            full_frame.pack(padx=15, pady=15, fill="both", expand=True)

            customtkinter.CTkLabel(full_frame, text=movie_name,font=("Roboto", 16, "bold")).pack(padx=15, pady=15)
            customtkinter.CTkLabel(full_frame, text="Opis:", font=("Roboto", 14, "bold")).pack(padx=5, pady=5)
            description_textbox = customtkinter.CTkTextbox(full_frame, font=("Roboto", 14), height=80, wrap="word")
            description_textbox.pack(padx=15, pady=5, fill="x")
            description_textbox.insert("0.0", translator.translate(movie_description, src="en", dest="hr").text)
            description_textbox.configure(state="disabled")
            secondary_full_frame = customtkinter.CTkFrame(full_frame)
            secondary_full_frame.pack(padx=15, pady=15, fill="x")
            customtkinter.CTkLabel(secondary_full_frame, text="Ocjena:", font=("Roboto", 14, "bold")).pack(padx=5, pady=5)
            customtkinter.CTkLabel(secondary_full_frame, text="                       ").pack(padx=5, pady=5, side="left")
            progressbar = customtkinter.CTkProgressBar(secondary_full_frame)
            progressbar.pack(pady=5, padx=5, side="left")
            customtkinter.CTkLabel(secondary_full_frame, text=f"{int(round(movie_rating * 100, 2))}%/100%").pack(padx=5, pady=5, side="left")
            progressbar.set(movie_rating)
            trd_full_frame = customtkinter.CTkFrame(full_frame)
            trd_full_frame.pack(padx=15, pady=15, fill="x")
            customtkinter.CTkLabel(trd_full_frame, text="Primjerenost sadržaja:",
                                   font=("Roboto", 14, "bold")).pack(padx=5, pady=5)
            contentbar = customtkinter.CTkProgressBar(trd_full_frame)
            contentbar.pack(pady=5, padx=5)
            contentbar.set(movie_cont_rating/18)
            if movie_cont_rating <= 10:
                contentbar.configure(progress_color="#138808")
            elif movie_cont_rating > 10 and movie_cont_rating <= 15:
                contentbar.configure(progress_color="#8FD400")
            elif movie_cont_rating > 16 and movie_cont_rating <= 18:
                contentbar.configure(progress_color="red")
            else:
                contentbar.configure(progress_color="red")
            customtkinter.CTkLabel(trd_full_frame, text=f"Objašnjenje:",
                                   font=("Roboto", 14, "bold")).pack(padx=3, pady=3)
            customtkinter.CTkLabel(trd_full_frame, text=f"{warnings}",
                                   font=("Roboto", 12)).pack(padx=3, pady=3)
            frame_det = customtkinter.CTkFrame(full_frame)
            frame_det.pack(padx=15, pady=5, fill="x")
            customtkinter.CTkLabel(frame_det, text=f"Trajanje: {hours * 60 + minutes} minuta",
                                   font=("Roboto", 12, "bold")).pack(pady=15, padx=15, side="left")
            customtkinter.CTkLabel(frame_det, text=f"Datum izdanja: {day}.{month}.{year}.",
                                   font=("Roboto", 12, "bold")).pack(pady=5, padx=5, side="right")
            frame_details = customtkinter.CTkFrame(full_frame)
            frame_details.pack(padx=15, pady=5, fill="x")
            customtkinter.CTkLabel(frame_details, text=f"Redatelji:",
                                   font=("Roboto", 12, "bold")).grid(row=0, column=0, pady=5, padx=5)
            temp_row_dir = 1
            for dir, url in zip(movie_directors.split(", "), urls_directors):
                dir_label = customtkinter.CTkLabel(frame_details, text=dir, font=("Roboto", 12), text_color="#1F538D")
                dir_label.grid(row=temp_row_dir, column=0, pady=1, padx=10)
                dir_label.bind("<Button-1>", lambda event, link=url: webbrowser.open_new(link))
                temp_row_dir += 1

            customtkinter.CTkLabel(frame_details, text="Glumci:",
                                   font=("Roboto", 12, "bold")).grid(row=0, column=1, pady=5, padx=5)

            temp_row_act = 1
            for actor, url in zip(movie_actors.split(", "), urls_actors):
                actor_label = customtkinter.CTkLabel(frame_details, text=actor, font=("Roboto", 12),
                                                     text_color="#1F538D")
                actor_label.grid(row=temp_row_act, column=1, pady=1, padx=10)
                actor_label.bind("<Button-1>", lambda event, link=url: webbrowser.open_new(link))
                temp_row_act += 1

            customtkinter.CTkLabel(frame_details, text="Kreatori:",
                                   font=("Roboto", 12, "bold")).grid(row=0, column=2, pady=5, padx=5)

            temp_row_crt = 1
            for creator, url in zip(movie_creators.split(", "), urls_creators):
                creator_label = customtkinter.CTkLabel(frame_details, text=creator, font=("Roboto", 12),
                                                     text_color="#1F538D")
                creator_label.grid(row=temp_row_crt, column=2, pady=1, padx=10)
                creator_label.bind("<Button-1>", lambda event, link=url: webbrowser.open_new(link))
                temp_row_crt += 1
            temp_col_mov = 0
            for movie in more_rec_movies:
                poster = movie.get("poster")
                nm = movie.get("name")
                response_m = requests.get(poster)
                poster_img = Image.open(BytesIO(response_m.content))

                poster_img = self.round_corners(poster_img, radius=60)

                pos_image = customtkinter.CTkImage(light_image=poster_img, size=(100, 150))
                img = customtkinter.CTkLabel(recommend_frame, text="", image=pos_image)
                img.grid(row=0, column=temp_col_mov, padx=5, pady=5)
                nme = customtkinter.CTkLabel(recommend_frame, text=nm)
                nme.grid(row=1, column=temp_col_mov, padx=5, pady=5)
                temp_col_mov += 1

            def open_link():
                webbrowser.open()

            def on_label_click(event):
                open_link()

            def check():
                if toplevel.winfo_exists():
                    root3.after(1000, check)
                else:
                    root3.deiconify()

            check()



        ct = 1
        recommendation_label = customtkinter.CTkLabel(self, text=movie_name, font=("Roboto", 24, "bold"))
        recommendation_label.pack(padx=10, pady=5)
        recommendation_frame = customtkinter.CTkFrame(self)
        recommendation_frame.pack(fill="both", expand=True, padx=10, pady=5)
        image_label = customtkinter.CTkLabel(recommendation_frame, image=tk_image, text="")
        image_label.pack(side="left", padx=10, pady=10)
        info_frame = customtkinter.CTkScrollableFrame(recommendation_frame, orientation="horizontal")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        customtkinter.CTkLabel(info_frame, text="Redatelj:", font=("Roboto", 24, "bold")).pack(pady=5)
        director_label = customtkinter.CTkLabel(info_frame, text=movie_directors, font=("Roboto", 24))
        director_label.pack(pady=5, padx=5)
        customtkinter.CTkLabel(info_frame, text="Žanrovi:", font=("Roboto", 24, "bold")).pack(pady=5)
        genre_label = customtkinter.CTkLabel(info_frame, text=movie_genres, font=("Roboto", 24))
        genre_label.pack(pady=5, padx=5)
        # Assuming you want the progress bar width to be 200 pixels
        customtkinter.CTkLabel(info_frame, text="Ocjena:", font=("Roboto", 24)).pack(side="left", pady=5, padx=5)
        progressbar = customtkinter.CTkProgressBar(info_frame)
        progressbar.pack(side="left", pady=5, padx=5)
        info_frame.columnconfigure(0, weight=1)  # Make the first column expand to fill the available space
        progressbar.set(movie_rating)
        customtkinter.CTkLabel(info_frame, text=f"{int(round(movie_rating*100, 2))}%/100%", font=("Roboto", 24)).pack(side="left", pady=5, padx=5)

        #customtkinter.CTkLabel(info_frame, text="Istaknuti glumci:", font=("Roboto", 24, "bold")).grid(row=1, column=0, padx=5, pady=5)
        #for actor in movie_actors.split(", "):
            #customtkinter.CTkLabel(info_frame, text=actor, font=("Roboto", 18)).grid(row=ct, column=1, padx=5, pady=5)
            #ct += 1
        button = customtkinter.CTkButton(recommendation_frame, text="Pogledaj\nviše", command=show_details)
        button.pack(side="right", fill="y", padx=10, pady=10)

        self.right_click_menu = tk.Menu(recommendation_frame, tearoff=0)
        self.right_click_menu.add_command(label="Show Another Recommendation", command=lambda: self.show_another_recommendation(movie_genres))

        self.bind("<Button-3>", self.show_right_click_menu)



    def round_corners(self, image, radius):
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, image.width, image.height), radius, fill=255)
        result = Image.new("RGBA", image.size)
        result.paste(image, (0, 0), mask)
        return result

    def show_another_recommendation(self, genres):
        # Call the recommend_more_movies function with the genres argument
        recommend_more_movies(genres)
        print("Showing another recommendation...")

    def show_right_click_menu(self, event):
        self.right_click_menu.post(event.x_root, event.y_root)

    offset = 0

    def recommend_more_movies(genres):
        global offset
        offset += 5
        recommend_movies_and_display(genres, offset=offset)




def recommend_movies_and_display(user_genres, offset=0, count=5):
    all_movies = load_movies()
    matching_movies = [movie for movie in all_movies if any(genre in movie["genre"] for genre in user_genres)]
    sorted_movies = sorted(matching_movies, key=lambda x: x["rating"]["ratingValue"] if x["rating"]["ratingValue"] is not None else 0, reverse=True)
    top_movies = sorted_movies[offset:offset+count]

    for movie in top_movies:
        movie_recommendations_widget = MovieRecommendationsWidget(movie_frame, movie)
        movie_recommendations_widget.pack(fill="both", expand=True, pady=12, padx=15)

def recommend_movies(user_genres):
    recommend_movies_and_display(user_genres)
    root3.deiconify()

offset = 0

def recommend_more_movies(genres):
    global offset
    offset += 5
    recommend_movies_and_display(genres, offset=offset)

def search_movies(query):
    results = moovies.find({"name": {"$regex": query, "$options": "i"}})
    return list(results)


def display_search_results(results):
    # Destroy any existing widgets in the search frame
    for widget in search_frame.winfo_children():
        widget.destroy()

    # Create a Treeview widget to display search results
    tree = ttk.Treeview(search_frame, columns=("Name", "Director", "Rating"), show="headings", height=10)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Create a custom style to set the background color
    style = ttk.Style()
    style.configure("Custom.Treeview", background="#212121", foreground="white", anchor="center")  # Set text color to white

    # Apply the custom style to the Treeview
    tree["style"] = "Custom.Treeview"

    # Define column headings
    tree.heading("Name", text="Name")
    tree.heading("Director", text="Director")
    tree.heading("Rating", text="Rating")

    def on_double_click(event):
        item = tree.selection()[0]
        movie_index = int(tree.item(item, "text"))
        print("Selected movie index:", movie_index)
        if 0 <= movie_index < len(search_results):
            show_movie_details(search_results[movie_index])
        else:
            print("Invalid movie index")

    # Add search results to the Treeview
    for index, movie in enumerate(results):
        name = movie.get("name", "")
        director = ", ".join(d["name"] for d in movie.get("director", []))
        rating = movie.get("rating", {}).get("ratingValue", "")
        tree.insert("", "end", text=str(index), values=(name, director, rating))

    # Bind double-click event to the on_double_click function
    tree.bind("<Double-1>", on_double_click)

    search_results.clear()
    search_results.extend(results)

search_results = []


def perform_search(query):
    results = search_movies(query)

    for widget in search_frame.winfo_children():
        widget.destroy()

    if results:
        display_search_results(results)
    else:
        no_results_label = customtkinter.CTkLabel(search_frame, text="No results found.", font=("Roboto", 14))
        no_results_label.pack(pady=10)


def on_search(event=None):
    query = entry_search.get().strip()

    if not query:
        for widget in search_frame.winfo_children():
            widget.destroy()
        return

    # Destroy previous search results if any
    if hasattr(search_frame, "tree_frame"):
        search_frame.tree_frame.destroy()

    # Create frame to contain Treeview widget
    search_frame.tree_frame = tk.Frame(search_frame, bg="#212121")
    search_frame.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Create Treeview widget for search results
    search_frame.tree = ttk.Treeview(search_frame.tree_frame, columns=("Name", "Director", "Rating"), show="headings", height=10)
    search_frame.tree.pack(fill="both", expand=True)

    # Set background color for Treeview widget
    search_frame.tree.configure(style="Custom.Treeview")

    # Create custom style for Treeview
    style = ttk.Style()
    style.theme_use("default")  # Use default theme
    style.configure("Custom.Treeview", background="#212121", foreground="#212121",
                    fieldbackground="#212121", anchor=tk.CENTER)  # Set row style
    style.configure("Custom.Treeview.Heading", background="#212121",
                    foreground="white", anchor=tk.CENTER)  # Set header style
    style.map("Custom.Treeview", background=[("selected", "#007ACC")])  # Set background color for selected items

    # Define column headings
    search_frame.tree.heading("Name", text="Name", anchor=tk.CENTER)
    search_frame.tree.heading("Director", text="Director", anchor=tk.CENTER)
    search_frame.tree.heading("Rating", text="Rating", anchor=tk.CENTER)

    # Display "Searching..." label
    loading_label = customtkinter.CTkLabel(search_frame.tree_frame, text="Searching...", font=("Roboto", 14))
    loading_label.pack(pady=10)

    # Cancel previous search after delay
    if hasattr(on_search, "_after_id"):
        root.after_cancel(on_search._after_id)

    # Perform search after delay
    on_search._after_id = root.after(3000, lambda: perform_search(query))

# Call this function to perform search
# on_search()



def update_search_results():
    for widget in search_frame.winfo_children():
        widget.destroy()

    display_search_results(search_results)


def show_movie_details(movie):
    root3.withdraw()
    translator = Translator()
    button_width = 200
    button_height = 250


    movie_name = movie.get("name", "")
    movie_poster_url = movie.get("poster")
    movie_rating = float(movie.get("rating", {}).get("ratingValue")) / 10
    movie_directors = ", ".join(director["name"] for director in movie.get("director", []))
    movie_directors_urls = ", ".join(director["url"] for director in movie.get("director", []))
    movie_actors = ", ".join(actor["name"] for actor in movie.get("actor", []))
    movie_actors_urls = ", ".join(actor["url"] for actor in movie.get("actor", []))
    movie_creators = ", ".join(creator["name"] for creator in movie.get("creator", []))
    movie_creators_urls = ", ".join(creator["url"] for creator in movie.get("creator", []))
    movie_genres = ", ".join(movie.get("genre", []))
    movie_duration = movie.get("duration")
    movie_date = movie.get("datePublished")
    movie_description = movie.get("description")
    movie_content_rating = movie.get("contentRating")
    more_rec_movies = moovies.aggregate([{'$sample': {'size': 4}}])

    urls_directors = movie_directors_urls.split(", ")
    urls_actors = movie_actors_urls.split(", ")
    urls_creators = movie_creators_urls.split(", ")

    hour_regex = re.compile(r'(\d+)H')
    minute_regex = re.compile(r'(\d+)M')
    hours_match = hour_regex.search(movie_duration)
    minutes_match = minute_regex.search(movie_duration)
    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0

    movie_cont_rating = 0
    warnings = ""

    warnings_dict = {
        "Not Rated": (12, "Nije ocijenjeno - Prikladno za osobe starije od 12 godina"),
        "12A": (12, "12A - Prikladno za osobe starije od 12 godina uz pratnju odrasle osobe"),
        "R": (18, "R - Restriktivno - Prikladno za osobe starije od 18 godina"),
        "TV-14": (14, "TV-14 - Preporučeno za osobe starije od 14 godina"),
        "6+": (6, "6+ - Prikladno za osobe starije od 6 godina"),
        "X": (18, "X - Eksplicitan sadržaj - Prikladno za osobe starije od 18 godina"),
        "18+": (18, "18+ - Eksplicitan sadržaj - Prikladno samo za punoljetne osobe"),
        "Unrated": (13, "Nepročitano - Prikladno za osobe starije od 13 godina"),
        "TV-G": (1, "TV-G - Opća publika - Prikladno za sve uzraste"),
        "Teen": (13, "Teen - Preporučeno za tinejdžere"),
        "A": (10, "A - Prikladno samo za odrasle"),
        "U": (1, "U - Univerzalno - Prikladno za sve uzraste"),
        "PG-13": (13, "PG-13 - Preporučeno za osobe starije od 13 godina uz roditeljski nadzor"),
        "PG": (13, "PG - Preporučeno uz roditeljski nadzor"),
        "Approved": (13, "Odobreno - Prikladno uz roditeljski nadzor"),
        "TV-MA": (17, "TV-MA - Zreloj publici - Prikladno samo za odrasle"),
        "TV-PG": (15, "TV-PG - Preporučeno uz roditeljski nadzor"),
        "AA": (14, "AA - Prikladno za sve uzraste"),
        "9+": (9, "9+ - Prikladno za osobe starije od 9 godina")
    }

    try:
        if movie_content_rating is not None:
            movie_cont_rating = int(movie_content_rating)
        else:
            movie_cont_rating = 12
            warnings = "Odobreno - Prikladno uz roditeljski nadzor"

        if movie_cont_rating in warnings_dict:
            movie_cont_rating, warnings = warnings_dict[movie_cont_rating]
        elif movie_content_rating == 15:
            warnings = "TV-PG - Preporučeno uz roditeljski nadzor"
        elif movie_content_rating == 16:
            warnings = "TV-MA - Zreloj publici - Prikladno samo za odrasle"
    except ValueError:
        movie_cont_rating, warnings = warnings_dict.get(movie_content_rating, (None, "TV-PG - Preporučeno uz roditeljski nadzor"))

    if movie_date is not None:
        year, month, day = movie_date.split('-')
        year = int(year)
        month = int(month)
        day = int(day)
    else:
        year = 2022
        month = 3
        day = 16

    Image.MAX_IMAGE_PIXELS = 200000000000

    response = requests.get(movie_poster_url)
    poster_image = Image.open(BytesIO(response.content))

    poster_image = round_corners(poster_image, radius=60)

    poster_image = poster_image.resize((int(button_width * 0.8), int(button_height * 0.8)))

    tk_image = customtkinter.CTkImage(light_image=poster_image, size=(button_width, button_height))

    toplevel = customtkinter.CTkToplevel(root3)
    toplevel.title(movie_name)
    toplevel.geometry("500x800")

    main_frame = customtkinter.CTkFrame(toplevel)
    main_frame.pack(padx=15, pady=15, fill="x", expand=False)
    movie_label = customtkinter.CTkLabel(main_frame, text=movie_name, font=("Roboto", 24, "bold"))
    movie_label.pack(padx=10, pady=5)
    image_label = customtkinter.CTkLabel(main_frame, image=tk_image, text="")
    image_label.pack(padx=10, pady=5, side="left")

    secondary_frame = customtkinter.CTkScrollableFrame(main_frame)
    secondary_frame.pack(padx=10, pady=5, side="right", fill="both")

    customtkinter.CTkLabel(secondary_frame, text="Generalni detalji", font=("Roboto", 24, "bold")).pack(padx=5,
                                                                                                        pady=5)
    customtkinter.CTkLabel(secondary_frame, text=f"Trajanje: {hours * 60 + minutes} minuta",
                           font=("Roboto", 12, "bold")).pack(
        padx=1, pady=1)
    customtkinter.CTkLabel(secondary_frame, text=f"Datum izdanja: {day}.{month}.{year}.",
                           font=("Roboto", 12, "bold")).pack(padx=1, pady=1)
    customtkinter.CTkLabel(secondary_frame, text=f"Redatelji:", font=("Roboto", 12, "bold")).pack(
        padx=1, pady=1)

    for dir, url in zip(movie_directors.split(", "), urls_directors):
        dir_label = customtkinter.CTkLabel(secondary_frame, text=dir, font=("Roboto", 12), text_color="#1F538D")
        dir_label.pack()
        dir_label.bind("<Button-1>", lambda event, link=url: webbrowser.open_new(link))

    customtkinter.CTkLabel(secondary_frame, text="Glumci:", font=("Roboto", 12, "bold")).pack(padx=1, pady=1)

    # Iterate through each actor and create a label with a link
    for actor, url in zip(movie_actors.split(", "), urls_actors):
        actor_label = customtkinter.CTkLabel(secondary_frame, text=actor, font=("Roboto", 12), text_color="#1F538D")
        actor_label.pack()
        actor_label.bind("<Button-1>", lambda event, link=url: webbrowser.open_new(link))

    details_frame = customtkinter.CTkScrollableFrame(toplevel)
    details_frame.pack(padx=15, pady=15, fill="both", expand=True)
    full_frame = customtkinter.CTkFrame(details_frame, fg_color="#1A1A1A")
    full_frame.pack(padx=15, pady=15, fill="both", expand=True)

    customtkinter.CTkLabel(full_frame, text=movie_name, font=("Roboto", 16, "bold")).pack(padx=15, pady=15)
    customtkinter.CTkLabel(full_frame, text="Opis:", font=("Roboto", 14, "bold")).pack(padx=5, pady=5)
    description_textbox = customtkinter.CTkTextbox(full_frame, font=("Roboto", 14), height=80, wrap="word")
    description_textbox.pack(padx=15, pady=5, fill="x")
    try:
        description_textbox.insert("0.0", translator.translate(movie_description, src="en", dest="hr").text)
    except TypeError:
        description_textbox.insert("0.0", "Opis je trenutno nepoznat!")
    description_textbox.configure(state="disabled")
    secondary_full_frame = customtkinter.CTkFrame(full_frame)
    secondary_full_frame.pack(padx=15, pady=15, fill="x")
    customtkinter.CTkLabel(secondary_full_frame, text="Ocjena:", font=("Roboto", 14, "bold")).pack(padx=5, pady=5)
    customtkinter.CTkLabel(secondary_full_frame, text="                       ").pack(padx=5, pady=5, side="left")
    progressbar = customtkinter.CTkProgressBar(secondary_full_frame)
    progressbar.pack(pady=5, padx=5, side="left")
    customtkinter.CTkLabel(secondary_full_frame, text=f"{int(round(movie_rating * 100, 2))}%/100%").pack(padx=5, pady=5,
                                                                                                         side="left")
    progressbar.set(movie_rating)
    trd_full_frame = customtkinter.CTkFrame(full_frame)
    trd_full_frame.pack(padx=15, pady=15, fill="x")
    customtkinter.CTkLabel(trd_full_frame, text="Primjerenost sadržaja:",
                           font=("Roboto", 14, "bold")).pack(padx=5, pady=5)
    contentbar = customtkinter.CTkProgressBar(trd_full_frame)
    contentbar.pack(pady=5, padx=5)
    contentbar.set(movie_cont_rating / 18)
    if movie_cont_rating <= 10:
        contentbar.configure(progress_color="#138808")
    elif movie_cont_rating > 10 and movie_cont_rating <= 15:
        contentbar.configure(progress_color="#8FD400")
    elif movie_cont_rating > 16 and movie_cont_rating <= 18:
        contentbar.configure(progress_color="red")
    else:
        contentbar.configure(progress_color="red")
    customtkinter.CTkLabel(trd_full_frame, text=f"Objašnjenje:",
                           font=("Roboto", 14, "bold")).pack(padx=3, pady=3)
    customtkinter.CTkLabel(trd_full_frame, text=f"{warnings}",
                           font=("Roboto", 12)).pack(padx=3, pady=3)
    frame_det = customtkinter.CTkFrame(full_frame)
    frame_det.pack(padx=15, pady=5, fill="x")
    customtkinter.CTkLabel(frame_det, text=f"Trajanje: {hours * 60 + minutes} minuta",
                           font=("Roboto", 12, "bold")).pack(pady=15, padx=15, side="left")
    customtkinter.CTkLabel(frame_det, text=f"Datum izdanja: {day}.{month}.{year}.",
                           font=("Roboto", 12, "bold")).pack(pady=5, padx=5, side="right")
    frame_details = customtkinter.CTkFrame(full_frame)
    frame_details.pack(padx=15, pady=5, fill="x")
    customtkinter.CTkLabel(frame_details, text=f"Redatelji:",
                           font=("Roboto", 12, "bold")).grid(row=0, column=0, pady=5, padx=5)
    temp_row_dir = 1
    for dir, url in zip(movie_directors.split(", "), urls_directors):
        dir_label = customtkinter.CTkLabel(frame_details, text=dir, font=("Roboto", 12), text_color="#1F538D")
        dir_label.grid(row=temp_row_dir, column=0, pady=1, padx=10)
        dir_label.bind("<Button-1>", lambda event, link=url: webbrowser.open_new(link))
        temp_row_dir += 1

    customtkinter.CTkLabel(frame_details, text="Glumci:",
                           font=("Roboto", 12, "bold")).grid(row=0, column=1, pady=5, padx=5)

    temp_row_act = 1
    for actor, url in zip(movie_actors.split(", "), urls_actors):
        actor_label = customtkinter.CTkLabel(frame_details, text=actor, font=("Roboto", 12),
                                             text_color="#1F538D")
        actor_label.grid(row=temp_row_act, column=1, pady=1, padx=10)
        actor_label.bind("<Button-1>", lambda event, link=url: webbrowser.open_new(link))
        temp_row_act += 1

    customtkinter.CTkLabel(frame_details, text="Kreatori:",
                           font=("Roboto", 12, "bold")).grid(row=0, column=2, pady=5, padx=5)

    temp_row_crt = 1
    for creator, url in zip(movie_creators.split(", "), urls_creators):
        creator_label = customtkinter.CTkLabel(frame_details, text=creator, font=("Roboto", 12),
                                               text_color="#1F538D")
        creator_label.grid(row=temp_row_crt, column=2, pady=1, padx=10)
        creator_label.bind("<Button-1>", lambda event, link=url: webbrowser.open_new(link))
        temp_row_crt += 1

    def open_link():
        webbrowser.open()

    def on_label_click(event):
        open_link()

    def check():
        if toplevel.winfo_exists():
            root3.after(1000, check)
        else:
            root3.deiconify()

    check()


def round_corners(image, radius):
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, image.width, image.height), radius, fill=255)
    result = Image.new("RGBA", image.size)
    result.paste(image, (0, 0), mask)
    return result


def select_and_send_genres(user_id, genres):
    response = requests.post("http://16.170.246.163/update_genres", json={"user_id": user_id, "genres": genres})

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
root.protocol("WM_DELETE_WINDOW", destroy_all_windows_and_exit)  # Add this line

loginreg = customtkinter.CTkToplevel(root)
loginreg.title("login/registracija")
frmlog = customtkinter.CTkFrame(loginreg)
frmreg = customtkinter.CTkFrame(loginreg)

frmlog.pack()
loginreg.withdraw()

loginreg.protocol("WM_DELETE_WINDOW", destroy_all_windows_and_exit)




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
    response = requests.post("http://16.170.246.163/login", json={"username": username, "password": password})

    if response.status_code == 200:
        try:
            user_data = response.json()
            user_id = user_data.get('user_id')
            genres = user_data.get('genres')
            if user_id and genres:
                messagebox.showinfo("Login Successful", f"Welcome, User ID: {user_id}, Genres: {genres}")
                print("5")

                recommend_movies(genres)
                more_button = customtkinter.CTkButton(movie_frame, text="Učitaj još",
                                                      command=lambda: recommend_more_movies(genres))
                more_button.pack(pady=10, padx=10, side="bottom")
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
root2.protocol("WM_DELETE_WINDOW", destroy_all_windows_and_exit)  # Add this line


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
root3.protocol("WM_DELETE_WINDOW", destroy_all_windows_and_exit)  # Add this line


tabview = customtkinter.CTkTabview(root3)
tabview.pack(fill="both", expand=True, pady=12, padx=15)

tab_1 = tabview.add("Za vas")
tab_2 = tabview.add("Pretraživanje")
tab_3 = tabview.add("Popularne franšize")

movie_frame = customtkinter.CTkScrollableFrame(tab_1)
movie_frame.pack(fill="both", expand=True, pady=12, padx=15)

search_label = customtkinter.CTkLabel(tab_2, text="Search Movies:", font=("Roboto", 16, "bold"))
search_label.pack(pady=10)

entry_search = customtkinter.CTkEntry(tab_2, font=("Roboto", 14))
entry_search.pack(pady=10, fill="x", padx=50)
entry_search.bind("<KeyRelease>", on_search)

search_frame = customtkinter.CTkFrame(tab_2)
search_frame.pack(fill="both", expand=True, pady=12, padx=15)



#search_button = customtkinter.CTkButton(tab_2, text="Search", font=("Roboto", 16, "bold"), command=on_search)
#search_button.pack(pady=10)




root.mainloop()