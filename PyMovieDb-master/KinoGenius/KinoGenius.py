import re
import tkinter as tk
from tkinter import messagebox, ttk
import PIL
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
from openai import OpenAI
from pymongo import MongoClient
import webbrowser
import datetime
from fuzzywuzzy import fuzz
from tkinter import filedialog

prikaz = False

username_user = ""
ct = 0

#MongoDB baza podataka s filmovima
client = MongoClient("#")
db = client['DBMoovies']
moovies = db['Moovies']

#Lokalni fileovi s filmovima
base_path = r'movies'
years = ['2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014',
         '2015','2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023']
directories = [os.path.join(base_path, year) for year in years]

#Korištenje OpenAI api-a
client = OpenAI(api_key='#')

selected_genres = []
genre_buttons = {}
recommended = []


def destroy_all_windows_and_exit():
    for window in root.winfo_children():
        if isinstance(window, tk.Toplevel):
            window.destroy()
    root.destroy()
    root.quit()

#spremljanje korisnika
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

#Prijava
def login():
    global username_user
    username = entry_username.get()
    password = entry_password.get()

    username_user = username

    response = requests.post("http://16.170.246.163/login", json={"username": username, "password": password})

    if response.status_code == 200:
        try:
            user_data = response.json()
            user_id = user_data.get('user_id')
            genres = user_data.get('genres')
            if user_id and genres:
                #messagebox.showinfo("Login Successful", f"Dobordošao, User ID: {user_id}, Žanrovi: {genres}")
                loginreg.withdraw()
                recommend_movies(genres)
                more_button = customtkinter.CTkButton(movie_frame, text="Učitaj još",
                                                      command=lambda: recommend_more_movies(genres))
                more_button.pack(pady=10, padx=10, side="bottom")
                select_and_send_genres(user_id, genres)
                save_user_info(username, password, genres)
            else:
                messagebox.showerror("Login Failed", "Neispravan odgovor servera!")
        except json.JSONDecodeError:
            messagebox.showerror("Login Failed", "Neispravan JSON odgovor servera!")
    else:
        messagebox.showerror("Login Failed", "Neispravno korisničko ime ili lozinka!")

#Također prijava
def poslogin():
    global username_user
    root3.withdraw()
    username = entry_username2.get()
    password = entry_password2.get()

    username_user = username

    response = requests.post("http://16.170.246.163/login", json={"username": username, "password": password})

    if response.status_code == 200:
        try:
            user_data = response.json()
            user_id = user_data.get('user_id')
            genres = user_data.get('genres')
            if user_id and genres:
                #messagebox.showinfo("Login Successful", f"Dobordošao, User ID: {user_id}, Žanrovi: {genres}")
                recommend_movies(genres)
                more_button = customtkinter.CTkButton(movie_frame, text="Učitaj još",
                                                      command=lambda: recommend_more_movies(genres))
                more_button.pack(pady=10, padx=10, side="bottom")
                select_and_send_genres(user_id, genres)
            else:
                messagebox.showerror("Login Failed", "Neispravan odgovor servera!")
        except json.JSONDecodeError:
            messagebox.showerror("Login Failed", "Neispravan JSON odgovor servera!")
    else:
        messagebox.showerror("Login Failed", "Neispravno korisničko ime ili lozinka!")
    loginreg.withdraw()

def preregister():
    frmlog.pack_forget()
    frmreg.pack()

#Registracija
def register():
    global username_user
    frmlog.pack_forget()
    frmreg.pack()

    username = entry_username2.get()
    password = entry_password2.get()

    username_user = username

    loginreg.withdraw()


    selected_genres = select_genres()


    save_user_info(username, password, selected_genres)


    response = requests.post("http://16.170.246.163/register", json={"username": username, "password": password, "genres": selected_genres})

    if response.status_code == 200:
        #messagebox.showinfo("Registration Successful", "Sada se možete ulogirati.")
        poslogin()
        root3.deiconify()
    else:
        messagebox.showerror("Registration Failed", "Korisničko ime već postoji ili je došlo do pogreške!")



from PIL import Image, ImageTk
import customtkinter

#Glavni dio ovoga projekta, class koji prikazuje sveukupni prijedlog
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
        try:
            poster_image = Image.open(BytesIO(response.content))
        except PIL.UnidentifiedImageError:
            if movie_name == "12 Angry Men":
                poster_image = Image.open("Assets/Images/Miscellaneous/12 Angry Men.jpg")
            elif movie_name == "Skyfall":
                poster_image = Image.open("Assets/Images/Miscellaneous/Skyfall.jpg")
            elif movie_name == "The Lord of the Rings: The Fellowship of the Ring":
                poster_image = Image.open("Assets/Images/Miscellaneous/Lord-of-the-rings.jpg")
            elif movie_name == "Top Gun: Maverick":
                poster_image = Image.open("Assets/Images/Miscellaneous/Top Gun Maverick.jpg")
            else:
                poster_image = Image.open("Assets/Images/Miscellaneous/unknown.png")

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
            if movie_description == "Unknown":
                description_textbox.insert("0.0", get_description(movie_name))
            else:
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
                try:
                    poster_img = Image.open(BytesIO(response_m.content))
                    poster_img = self.round_corners(poster_img, radius=60)
                    pos_image = customtkinter.CTkImage(light_image=poster_img, size=(100, 150))
                    img = customtkinter.CTkLabel(recommend_frame, text="", image=pos_image)
                    img.grid(row=0, column=temp_col_mov, padx=5, pady=5)
                except PIL.UnidentifiedImageError:
                    pass
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

        #Korištenje OpenAI-a za dobivanje opisa
        def get_description(movie_name):
            description_prompt = f"Opiši mi navedeni film na hrvatskom jeziku i u dvije rečenice: {movie_name}"

            description_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        'role': 'user',
                        'content': f'{description_prompt}'
                    }
                ]
            )

            description = description_response.choices[0].message.content
            return description

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
        customtkinter.CTkLabel(info_frame, text="Ocjena:", font=("Roboto", 24)).pack(side="left", pady=5, padx=5)
        progressbar = customtkinter.CTkProgressBar(info_frame)
        progressbar.pack(side="left", pady=5, padx=5)
        info_frame.columnconfigure(0, weight=1)
        progressbar.set(movie_rating)
        customtkinter.CTkLabel(info_frame, text=f"{int(round(movie_rating*100, 2))}%/100%", font=("Roboto", 24)).pack(side="left", pady=5, padx=5)
        button = customtkinter.CTkButton(recommendation_frame, text="Pogledaj\nviše", command=show_details)
        button.pack(side="right", fill="y", padx=10, pady=10)

        recommended.append(movie_name)


    #uređivanje slika
    def round_corners(self, image, radius):
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, image.width, image.height), radius, fill=255)
        result = Image.new("RGBA", image.size)
        result.paste(image, (0, 0), mask)
        return result

#prikazivanje prijedloga
def recommend_movies_and_display(user_genres, offset=0, count=5):
    all_movies = load_movies()
    matching_movies = [movie for movie in all_movies if any(genre in movie["genre"] for genre in user_genres)]
    sorted_movies = sorted(matching_movies, key=lambda x: x["rating"]["ratingValue"] if x["rating"]["ratingValue"] is not None else 0, reverse=True)
    top_movies = sorted_movies[offset:offset+count]

    for movie in top_movies:
        if movie["name"] in recommended:
            pass
        else:
            movie_recommendations_widget = MovieRecommendationsWidget(movie_frame, movie)
            movie_recommendations_widget.pack(fill="both", expand=True, pady=12, padx=15)

#funkcija služi za pozivanje prošle i za sakrivanje glavnog prozora
def recommend_movies(user_genres):
    recommend_movies_and_display(user_genres)
    root3.deiconify()

offset = 0

#funkicja za tipku koja daje još prijedloga
def recommend_more_movies(genres):
    global offset
    offset += 5
    recommend_movies_and_display(genres, offset=offset)

#pretraživanje baze podataka
def search_movies(query):
    results = moovies.find({"name": {"$regex": query, "$options": "i"}})
    return list(results)

#prikazivanje rezultata u ttk.treeview-u
search_treeview = None
def display_search_results(results):
    global search_treeview

    if search_treeview is not None:
        search_treeview.destroy()

    search_treeview = ttk.Treeview(search_frame, columns=("Naslov", "Redatelj", "Ocjena"), show="headings", height=10)
    search_treeview.pack(fill="both", expand=True, padx=10, pady=10)

    style = ttk.Style()
    style.configure("Custom.Treeview", background="#212121", foreground="white", anchor="center")

    search_treeview["style"] = "Custom.Treeview"

    search_treeview.heading("Naslov", text="Naslov")
    search_treeview.heading("Redatelj", text="Redatelj")
    search_treeview.heading("Ocjena", text="Ocjena")

    def on_double_click(event):
        item = search_treeview.selection()[0]
        movie_index = int(search_treeview.item(item, "text"))
        if 0 <= movie_index < len(results):
            show_movie_details(results[movie_index])
        else:
            pass

    for index, movie in enumerate(results):
        name = movie.get("name", "")
        director = ", ".join(d["name"] for d in movie.get("director", []))
        rating = movie.get("rating", {}).get("ratingValue", "")
        search_treeview.insert("", "end", text=str(index), values=(name, director, rating))

    search_treeview.bind("<Double-1>", on_double_click)


search_results = []

#funkicja koja prikazuje rezultate i sortira ih
def perform_search(query):
    results = search_movies(query)

    for widget in search_frame.winfo_children():
        widget.destroy()

    if results:
        results.sort(key=lambda x: x.get("rating", {}).get("ratingValue", 0), reverse=True)
        display_search_results(results)
    else:
        no_results_label = customtkinter.CTkLabel(search_frame, text="Odgovarajući rezultati nisu pronađeni.", font=("Roboto", 14))
        no_results_label.pack(pady=10)


#pozivanje funkcije za pretraživanje
def on_search(event=None):
    query = entry_search.get().strip()

    if not query:
        for widget in search_frame.winfo_children():
            widget.destroy()
        return

    if hasattr(search_frame, "tree_frame"):
        search_frame.tree_frame.destroy()

    search_frame.tree_frame = tk.Frame(search_frame, bg="#212121")
    search_frame.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

    search_frame.tree = ttk.Treeview(search_frame.tree_frame, columns=("Name", "Director", "Rating"), show="headings", height=10)
    search_frame.tree.pack(fill="both", expand=True)

    search_frame.tree.configure(style="Custom.Treeview")

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Custom.Treeview", background="#212121", foreground="#212121",
                    fieldbackground="#212121", anchor=tk.CENTER)
    style.configure("Custom.Treeview.Heading", background="#212121",
                    foreground="white", anchor=tk.CENTER)
    style.map("Custom.Treeview", background=[("selected", "#007ACC")])
    search_frame.tree.heading("Name", text="Naslov", anchor=tk.CENTER)
    search_frame.tree.heading("Director", text="Redatelj", anchor=tk.CENTER)
    search_frame.tree.heading("Rating", text="Ocjena", anchor=tk.CENTER)

    loading_label = customtkinter.CTkLabel(search_frame.tree_frame, text="Pretraživanje...", font=("Roboto", 14))
    loading_label.pack(pady=10)

    def update_loading_label(loading_sequence=0):
        if loading_sequence == 0:
            loading_label.configure(text="Pretraživanje")

        elif loading_sequence == 1:
            loading_label.configure(text="Pretraživanje .")

        elif loading_sequence == 2:
            loading_label.configure(text="Pretraživanje . .")

        elif loading_sequence == 3:
            loading_label.configure(text="Pretraživanje . . .")

        next_loading_sequence = (loading_sequence + 1) % 4

        search_frame.tree_frame.after(200, update_loading_label, next_loading_sequence)


    if hasattr(on_search, "_after_id"):
        root.after_cancel(on_search._after_id)
        update_loading_label(0)

    on_search._after_id = root.after(3000, lambda: perform_search(query))


#obnavljanje widget-a ttk.treeview
def update_search_results():
    for widget in search_frame.winfo_children():
        widget.destroy()

    display_search_results(search_results)

#prikazivanje detalja za filmove unutar ttk.treeview-a
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
    try:
        poster_image = Image.open(BytesIO(response.content))
    except PIL.UnidentifiedImageError:
        if movie_name == "12 Angry Men":
            poster_image = Image.open("Assets/Images/Miscellaneous/12 Angry Men.jpg")
        elif movie_name == "Skyfall":
            poster_image = Image.open("Assets/Images/Miscellaneous/Skyfall.jpg")
        elif movie_name == "The Lord of the Rings: The Fellowship of the Ring":
            poster_image = Image.open("Assets/Images/Miscellaneous/Lord-of-the-rings.jpg")
        elif movie_name == "Top Gun: Maverick":
            poster_image = Image.open("Assets/Images/Miscellaneous/Top Gun Maverick.jpg")
        else:
            poster_image = Image.open("Assets/Images/Miscellaneous/unknown.png")
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
    if movie_description == "Unknown":
        description_textbox.insert("0.0", get_description(movie_name))
    else:
        description_textbox.insert("0.0", translator.translate(movie_description, src="en", dest="hr").text)
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


def get_description(movie_name):
    description_prompt = f"Opiši mi navedeni film na hrvatskom jeziku i u dvije rečenice: {movie_name}"

    description_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                'role': 'user',
                'content': f'{description_prompt}'
            }
        ]
    )

    description = description_response.choices[0].message.content
    return description

def round_corners(image, radius):
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, image.width, image.height), radius, fill=255)
    result = Image.new("RGBA", image.size)
    result.paste(image, (0, 0), mask)
    return result

#dio funkcija koje služe za postavljanje profila
def select_and_send_genres(user_id, genres):
    response = requests.post("http://16.170.246.163/update_genres", json={"user_id": user_id, "genres": genres})

    try:
        response_data = response.json()
        if response_data.get("user_id") and response_data.get("genres"):
            pass
            #messagebox.showinfo("Genres Updated", f"Žanrovi uspješno obnovljeni. User ID: {response_data['user_id']}, Žanrovi: {response_data['genres']}")
        else:
            messagebox.showerror("Update Failed", "Neispravan odgovor servera!")
    except json.JSONDecodeError:
        messagebox.showerror("Update Failed", "Neispravan JSON odgovor servera!")

#sveukupno biranje žanrova za korisnika
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


    genres = [
        "Fantasy", "Animation", "Sport", "Romance", "Comedy", "Thriller", "Musical",
        "Adventure", "War", "Documentary", "Horror", "Drama", "Action", "Sci-Fi",
        "Mystery", "Crime", "Family", "Short", "Western", "Biography", "Music", "History"
    ]
    for genre in genres:
        genre_buttons[genre] = customtkinter.CTkButton(gen, text=genre, font=(("Roboto", 16, "bold")), command=lambda g=genre: on_genre_button_click(g))
        genre_buttons[genre].grid(row=0, column=genres.index(genre), padx=5)
    for genre in genres:
        pass

    picked_gen = customtkinter.CTkScrollableFrame(pick)
    picked_gen.pack(pady=12, padx=12, fill="both", expand=True)


    submit_button = customtkinter.CTkButton(pick, text="Potvrdi", font=(("Roboto", 20, "bold")), command=submit_genres)
    submit_button.pack(side="bottom", fill="both", padx=10, pady=12)


    selected_genres = []


    pick.wait_window(pick)
    return selected_genres


#učitavanje filmova kako bi program mogao davati prijedloge
def load_movies():
    base_path = r'movies'
    years = ['2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012',
             '2013', '2014',
             '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023']
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

#prikaz passworda
def hide():
    if check.get() == "on":
        entry_password.configure(show="")
    else:
        entry_password.configure(show="*")

#prikaz passworda
def hide2():
    if check.get() == "on":
        entry_password2.configure(show="")
    else:
        entry_password2.configure(show="*")

#Glavni GUI

root = customtkinter.CTk()
root.title("KinoGenius")
root.withdraw()
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
customtkinter.deactivate_automatic_dpi_awareness()
root.protocol("WM_DELETE_WINDOW", destroy_all_windows_and_exit)

loginreg = customtkinter.CTkToplevel(root)
loginreg.title("login/registracija")
frmlog = customtkinter.CTkFrame(loginreg)
frmreg = customtkinter.CTkFrame(loginreg)

frmlog.pack()
loginreg.withdraw()

loginreg.protocol("WM_DELETE_WINDOW", destroy_all_windows_and_exit)

#prijava i registracija
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

#prikazivanje dostupnih profila
def load_json_file(file_path):

    if file_path == "+":
        pass
    else:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            username = data.get('username', 'Unknown')


#animacije za tipke
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

#prikazivanje dostupnih korisnika
def create_button_for_json(file_path, column):
    font_style = ("Roboto", 30, "bold")

    if file_path == "+":
        button = customtkinter.CTkButton(frame, text="+", font=font_style, width=100, height=100, command=plus)
        button.grid(row=2, column=0, padx=10, pady=10)
        label = customtkinter.CTkLabel(frame, text="")
        label.grid(row=3, column=0)
        button.bind("<Enter>", lambda event, btn=button, lbl=label: on_hover(event, btn, lbl, ""))
        button.bind("<Leave>", lambda event, btn=button, lbl=label: on_leave(event, btn, lbl))
    else:
        with open(file_path, 'r') as json_file:
            global username_user
            data = json.load(json_file)
            username = data.get('username', 'Unknown')
            username_user = username
            #ulogiravanje izabranog korisnika
            def login_user():
                login_with_credentials(username, data.get('password', ''))

            button = customtkinter.CTkButton(frame, text='👤', font=font_style, width=100, height=100, command=login_user)
            button.grid(row=2, column=column, padx=10, pady=10)
            label = customtkinter.CTkLabel(frame, text="")
            label.grid(row=3, column=column)
            button.bind("<Enter>", lambda event, btn=button, lbl=label, usr=username: on_hover(event, btn, lbl, usr))
            button.bind("<Leave>", lambda event, btn=button, lbl=label: on_leave(event, btn, lbl))


#ulogiravanje izabranog korisnika
def login_with_credentials(username, password):

    root2.withdraw()
    response = requests.post("http://16.170.246.163/login", json={"username": username, "password": password})

    if response.status_code == 200:
        try:
            user_data = response.json()
            user_id = user_data.get('user_id')
            genres = user_data.get('genres')
            if user_id and genres:
                #messagebox.showinfo("Login Successful", f"Dobrodošao, User ID: {user_id}, Žanrovi: {genres}")
                recommend_movies(genres)
                more_button = customtkinter.CTkButton(movie_frame, text="Učitaj još",
                                                      command=lambda: recommend_more_movies(genres))
                more_button.pack(pady=10, padx=10, side="bottom")
                select_and_send_genres(user_id, genres)
                save_user_info(username, password, genres)
            else:
                messagebox.showerror("Login Failed", "Neispravan odgovor servera!")
        except json.JSONDecodeError:
            messagebox.showerror("Login Failed", "Neispravan JSON odgovor servera!")
    else:
        messagebox.showerror("Login Failed", "Neispravno koriničko ime ili lozinka!")

#Učitavanje postavaka
with open("Assets/Settings/settings.json", "r") as file:
    data = json.load(file)
theme = data["theme"]
with open("Assets/Settings/settings2.json", "r") as file:
    data2 = json.load(file)
color_theme = data2["color_theme"]

#prikazivanje korisnika i postavaka
def show_profile_details():
    global theme
    global color_theme
    root3.withdraw()
    def save_settings(settings_data):
        with open("Assets/Settings/settings.json", "w") as file:
            json.dump(settings_data, file)

    def save_settings_color(settings_data):
        with open("Assets/Settings/settings2.json", "w") as file:
            json.dump(settings_data, file)

    def set_theme(theme_name, button_states):
        customtkinter.set_appearance_mode(theme_name)
        save_settings({"theme": theme_name})
        for button, state in button_states.items():
            button.configure(state=state)

    def set_color_theme(color_theme, button_states):
        save_settings_color({"color_theme": color_theme})
        for button, state in button_states.items():
            button.configure(state=state)
        messagebox.showinfo("Promjena", "Vaša boja će se promjeniti nakon ponovnog pokretanja programa!")

    def set_dark_theme():
        set_theme("dark", {
            dark_theme_button: "disabled",
            light_theme_button: "normal",
            system_theme_button: "normal"
        })

    def set_light_theme():
        set_theme("light", {
            light_theme_button: "disabled",
            dark_theme_button: "normal",
            system_theme_button: "normal"
        })

    def set_system_theme():
        set_theme("system", {
            system_theme_button: "disabled",
            dark_theme_button: "normal",
            light_theme_button: "normal"
        })

    def set_darkblue_theme():
        set_color_theme("dark-blue", {
            darkblue_theme_button: "disabled",
            blue_theme_button: "normal",
            green_theme_button: "normal"
        })

    def set_blue_theme():
        set_color_theme("blue", {
            blue_theme_button: "disabled",
            darkblue_theme_button: "normal",
            green_theme_button: "normal"
        })

    def set_green_theme():
        set_color_theme("green", {
            green_theme_button: "disabled",
            darkblue_theme_button: "normal",
            blue_theme_button: "normal"
        })

    dark_image = customtkinter.CTkImage(light_image=round_corners(Image.open(r"Assets/Images/Themes/Dark.png"), radius=20),
                                        dark_image=round_corners(Image.open(r"Assets/Images/Themes/Dark.png"), radius=20),
                                        size=(20, 20))
    light_image = customtkinter.CTkImage(light_image=round_corners(Image.open(r"Assets/Images/Themes/Light.png"), radius=20),
                                         dark_image=round_corners(Image.open(r"Assets/Images/Themes/Light.png"), radius=20),
                                         size=(20, 20))
    darkblue_image = customtkinter.CTkImage(light_image=round_corners(Image.open(r"Assets/Images/Themes/Dark-Blue.png"), radius=20),
                                            dark_image=round_corners(Image.open(r"Assets/Images/Themes/Dark-Blue.png"), radius=20),
                                            size=(20, 20))
    blue_image = customtkinter.CTkImage(light_image=round_corners(Image.open(r"Assets/Images/Themes/Blue.png"), radius=20),
                                        dark_image=round_corners(Image.open(r"Assets/Images/Themes/Blue.png"), radius=20),
                                        size=(20, 20))
    green_image = customtkinter.CTkImage(light_image=round_corners(Image.open(r"Assets/Images/Themes/Green.png"), radius=20),
                                         dark_image=round_corners(Image.open(r"Assets/Images/Themes/Green.png"), radius=20),
                                         size=(20, 20))
    current_time = datetime.datetime.now()
    system_theme = customtkinter.get_appearance_mode()
    if system_theme == "Dark":
        img = dark_image
    else:
        img = light_image
    hour = current_time.hour
    if 5 <= hour < 12:
        lbl_text = "Dobro jutro,"
    elif 12 <= hour < 17:
        lbl_text = "Dobar dan,"
    elif 17 <= hour < 20:
        lbl_text = "Dobra večer,"
    else:
        lbl_text = "Dobro večer,"
    toplevel = customtkinter.CTkToplevel(root3)
    toplevel.title("Postavke")
    toplevel.geometry("525x400")
    pozdrav_label = customtkinter.CTkLabel(toplevel, text=f"{lbl_text} {username_user}!", font=("Roboto", 26, "bold"))
    pozdrav_label.pack(pady=12, padx=15)
    setting_frame = customtkinter.CTkFrame(toplevel)
    setting_frame.pack(fill="both", expand=True, pady=12, padx=15)
    setting_label = customtkinter.CTkLabel(setting_frame, text="Postavke", font=("Roboto", 24, "bold"))
    setting_label.grid(row=0, columnspan=3, pady=12, padx=12)
    customtkinter.CTkLabel(setting_frame, text="", font=("Roboto", 24, "bold")).grid(row=1, columnspan=3, pady=12, padx=12)
    dark_theme_button = customtkinter.CTkButton(setting_frame, text="Tamno", font=("Roboto", 16), anchor="w",
                                                image=dark_image, command=set_dark_theme)
    dark_theme_button.grid(row=2, column=0, pady=12, padx=12)
    light_theme_button = customtkinter.CTkButton(setting_frame, text="Svijetlo", font=("Roboto", 16), anchor="w",
                                                 image=light_image, command=set_light_theme)
    light_theme_button.grid(row=2, column=1, pady=12, padx=12)
    system_theme_button = customtkinter.CTkButton(setting_frame, text="Tema sistema", font=("Roboto", 16), anchor="w",
                                                  image=img, command=set_system_theme)
    system_theme_button.grid(row=2, column=2, pady=12, padx=12)
    if theme == "dark":
        dark_theme_button.configure(state="disabled")
    elif theme == "light":
        light_theme_button.configure(state="disabled")
    else:
        system_theme_button.configure(state="disabled")

    darkblue_theme_button = customtkinter.CTkButton(setting_frame, text="Tamno plava", font=("Roboto", 16), anchor="w",
                                                image=darkblue_image, command=set_darkblue_theme)
    darkblue_theme_button.grid(row=3, column=0, pady=12, padx=12)
    blue_theme_button = customtkinter.CTkButton(setting_frame, text="Plava", font=("Roboto", 16), anchor="w",
                                                 image=blue_image, command=set_blue_theme)
    blue_theme_button.grid(row=3, column=1, pady=12, padx=12)
    green_theme_button = customtkinter.CTkButton(setting_frame, text="Zelena", font=("Roboto", 16), anchor="w",
                                                  image=green_image, command=set_green_theme)
    green_theme_button.grid(row=3, column=2, pady=12, padx=12)
    if color_theme == "dark-blue":
        darkblue_theme_button.configure(state="disabled")
    elif color_theme == "blue":
        blue_theme_button.configure(state="disabled")
    else:
        green_theme_button.configure(state="disabled")

    def check():
        if toplevel.winfo_exists():
            root3.after(1000, check)
        else:
            root3.deiconify()

    check()

customtkinter.set_appearance_mode(theme)
customtkinter.set_default_color_theme(color_theme)

#prozor za biranje profila
root2 = customtkinter.CTkToplevel(root)
root2.title("Biranje Profila")
root2.geometry("600x400")
root2.resizable(False, False)
root2.protocol("WM_DELETE_WINDOW", destroy_all_windows_and_exit)


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

#glavni prozor
root3 = customtkinter.CTkToplevel(root)
root3.title("KinoGenius")
root3.geometry("1000x800")
root3.withdraw()
root3.protocol("WM_DELETE_WINDOW", destroy_all_windows_and_exit)

#tabview koji prikazuje 3 tab-a
tabview = customtkinter.CTkTabview(root3)
tabview.pack(fill="both", expand=True, pady=12, padx=15)

tab_1 = tabview.add("Za vas")
tab_2 = tabview.add("Pretraživanje")
tab_3 = tabview.add("Popularne franšize")

movie_frame = customtkinter.CTkScrollableFrame(tab_1)
movie_frame.pack(fill="both", expand=True, pady=12, padx=15)
account_button1 = customtkinter.CTkButton(tab_1, text="👤", font=("Roboto", 32, "bold"), width=32, height=32,
                                          command=show_profile_details, bg_color="transparent")
account_button1.place(x=0, y=0)

search_label = customtkinter.CTkLabel(tab_2, text="Pretraži filmove:", font=("Roboto", 16, "bold"))
search_label.pack(pady=10)

entry_search = customtkinter.CTkEntry(tab_2, font=("Roboto", 14))
entry_search.pack(pady=10, fill="x", padx=50)
entry_search.bind("<KeyRelease>", on_search)

search_frame = customtkinter.CTkFrame(tab_2)
search_frame.pack(fill="both", expand=True, pady=12, padx=15)
account_button2 = customtkinter.CTkButton(tab_2, text="👤", font=("Roboto", 32, "bold"), width=32, height=32,
                                          command=show_profile_details, bg_color="transparent")
account_button2.place(x=0, y=0)

francises = customtkinter.CTkScrollableFrame(tab_3)
francises.pack(fill="both", expand=True, pady=12, padx=15)
account_button3 = customtkinter.CTkButton(tab_3, text="👤", font=("Roboto", 32, "bold"), width=32, height=32,
                                          command=show_profile_details, bg_color="transparent")
account_button3.place(x=0, y=0)

#svi filmovi "popularnih žanrova"
SCI_FI_label = customtkinter.CTkLabel(francises, text="SCI-FI", font=("Roboto", 29, "bold"))
SCI_FI_label.pack(pady=25, padx=25)

customtkinter.CTkLabel(francises, text="Marvel", font=("Roboto", 24, "bold")).pack(pady=2, padx=2)
marvel_img = Image.open("Assets/Images/Banners/Marvel_Studios_logo.png")
marvel_img = round_corners(marvel_img, radius=60)
marvel_movies = [{'name': 'Spider-Man 2'},
                 {'name': 'X-Men: Days of Future Past'},
                 {'name': 'Iron Man'},
                 {'name': 'Ant-Man'},
                 {'name': 'Black Panther'},
                 {'name': 'Guardians of the Galaxy Vol. 3'},
                 {'name': 'Deadpool 2'},
                 {'name': 'Morbius'},
                 {'name': 'Thor: Love and Thunder'},
                 {'name': 'Avengers: Infinity War'},
                 {'name': 'Spider-Man: Homecoming'},
                 {'name': 'Avengers: Endgame'}]
ctk_marvel_img = customtkinter.CTkImage(light_image=marvel_img, dark_image=marvel_img, size=(int(1725*0.5), int(450*0.5)))
marvel_button = customtkinter.CTkButton(francises, text="", image=ctk_marvel_img,
                                       fg_color="transparent", hover_color="#1A1A1A")
marvel_button.pack(pady=12, padx=10)

customtkinter.CTkLabel(francises, text="Star Wars", font=("Roboto", 24, "bold")).pack(pady=2, padx=2)
star_wars_img = Image.open("Assets/Images/Banners/Star_wars_banner.jpg")
star_wars_img = round_corners(star_wars_img, radius=60)
star_wars_movies = [{'name': 'Star Wars: Episode I - The Phantom Menace'},
                    {'name': 'Star Wars: Episode II - Attack of the Clones'},
                    {'name': 'Star Wars: The Clone Wars'},
                    {'name': 'Star Wars: Episode III - Revenge of the Sith'},
                    {'name': 'Rogue One: A Star Wars Story'},
                    {'name': 'Solo: A Star Wars Story'},
                    {'name': 'Star Wars: Episode VII - The Force Awakens'},
                    {'name': 'Star Wars: Episode VIII - The Last Jedi'},
                    {'name': 'Star Wars: Episode IX - The Rise of Skywalker'}]
ctk_star_wars_img = customtkinter.CTkImage(light_image=star_wars_img, dark_image=star_wars_img, size=(int(1725*0.5), int(450*0.5)))
star_wars_button = customtkinter.CTkButton(francises, text="", image=ctk_star_wars_img,
                                       fg_color="transparent", hover_color="#1A1A1A")
star_wars_button.pack(pady=12, padx=10)

action_label = customtkinter.CTkLabel(francises, text="Akcija", font=("Roboto", 29, "bold"))
action_label.pack(pady=25, padx=25)

customtkinter.CTkLabel(francises, text="The Fast and The Furious", font=("Roboto", 24, "bold")).pack(pady=2, padx=2)
fast_img = Image.open("Assets/Images/Banners/fastandfurious-banner.png")
fast_img = round_corners(fast_img, radius=60)
fast_movies = [{'name': 'The Fast and the Furious'},
               {'name': '2 Fast 2 Furious'},
               {'name': 'The Fast and the Furious: Tokyo Drift'},
               {'name': 'Furious 7: Talking Fast'},
               {'name': 'The Fate of the Furious: Extended Fight Scenes'},
               {'name': 'Fast X'}]
ctk_fast_img = customtkinter.CTkImage(light_image=fast_img, dark_image=fast_img, size=(int(1725*0.5), int(450*0.5)))
fast_button = customtkinter.CTkButton(francises, text="", image=ctk_fast_img,
                                       fg_color="transparent", hover_color="#1A1A1A")
fast_button.pack(pady=12, padx=10)

customtkinter.CTkLabel(francises, text="James Bond", font=("Roboto", 24, "bold")).pack(pady=2, padx=2)
james_img = Image.open("Assets/Images/Banners/james_bond_banner.png")
james_img = round_corners(james_img, radius=60)
james_movies = [{'name': 'Casino Royale'},
                {'name': 'Quantum of Solace'},
                {'name': 'Skyfall'},
                {'name': 'Spectre'},
                {'name': 'No Time to Die'}]
ctk_james_img = customtkinter.CTkImage(light_image=james_img, dark_image=james_img, size=(int(1725*0.5), int(450*0.5)))
james_button = customtkinter.CTkButton(francises, text="", image=ctk_james_img,
                                       fg_color="transparent", hover_color="#1A1A1A")
james_button.pack(pady=12, padx=10)

customtkinter.CTkLabel(francises, text="Mission: Impossible", font=("Roboto", 24, "bold")).pack(pady=2, padx=2)
mission_img = Image.open("Assets/Images/Banners/mission-impossible-banner.png")
mission_img = round_corners(mission_img, radius=60)
mission_movies = [{'name': 'Mission: Impossible'},
                  {'name': 'Mission: Impossible II'},
                  {'name': 'Mission: Impossible III'},
                  {'name': 'Mission: Impossible - Ghost Protocol'},
                  {'name': 'Mission: Impossible - Rogue Nation'},
                  {'name': 'Mission: Impossible - Fallout'},
                  {'name': 'Mission: Impossible - Dead Reckoning Part One'},
                  {'name': 'Mission: Impossible - Dead Reckoning Part Two'}]
ctk_mission_img = customtkinter.CTkImage(light_image=mission_img, dark_image=mission_img, size=(int(1725*0.5), int(450*0.5)))
mission_button = customtkinter.CTkButton(francises, text="", image=ctk_mission_img,
                                       fg_color="transparent", hover_color="#1A1A1A")
mission_button.pack(pady=12, padx=10)

drama_label = customtkinter.CTkLabel(francises, text="Drama", font=("Roboto", 29, "bold"))
drama_label.pack(pady=25, padx=25)

customtkinter.CTkLabel(francises, text="Lord of the rings", font=("Roboto", 24, "bold")).pack(pady=2, padx=2)
lord_img = Image.open("Assets/Images/Banners/lord-of-the-rings-banner.png")
lord_img = round_corners(lord_img, radius=60)
lord_movies = [{'name': 'The Lord of the Rings: The Fellowship of the Ring'},
               {'name': 'The Lord of the Rings: The Two Towers'},
               {'name': 'The Lord of the Rings: The Return of the King'}]
ctk_lord_img = customtkinter.CTkImage(light_image=lord_img, dark_image=lord_img, size=(int(1725*0.5), int(450*0.5)))
lord_button = customtkinter.CTkButton(francises, text="", image=ctk_lord_img,
                                       fg_color="transparent", hover_color="#1A1A1A")
lord_button.pack(pady=12, padx=10)

customtkinter.CTkLabel(francises, text="Harry Potter", font=("Roboto", 24, "bold")).pack(pady=2, padx=2)
harry_img = Image.open("Assets/Images/Banners/harry_potter_banner.png")
harry_img = round_corners(harry_img, radius=60)
harry_movies = [{'name': "Harry Potter and the Sorcerer's Stone"},
                {'name': 'Harry Potter and the Chamber of Secrets'},
                {'name': 'Harry Potter and the Prisoner of Azkaban'},
                {'name': 'Harry Potter and the Goblet of Fire'},
                {'name': 'Harry Potter and the Order of the Phoenix'},
                {'name': 'Harry Potter and the Half-Blood Prince'},
                {'name': 'Harry Potter and the Deathly Hallows - Part 1'},
                {'name': 'Harry Potter and the Deathly Hallows - Part 2'}]
ctk_harry_img = customtkinter.CTkImage(light_image=harry_img, dark_image=harry_img, size=(int(1725*0.5), int(450*0.5)))
harry_button = customtkinter.CTkButton(francises, text="", image=ctk_harry_img,
                                       fg_color="transparent", hover_color="#1A1A1A")
harry_button.pack(pady=12, padx=10)

romance_label = customtkinter.CTkLabel(francises, text="Romance", font=("Roboto", 29, "bold"))
romance_label.pack(pady=25, padx=25)

customtkinter.CTkLabel(francises, text="Fifty Shades", font=("Roboto", 24, "bold")).pack(pady=2, padx=2)
fifty_img = Image.open("Assets/Images/Banners/Fifty_Shades_Banner.png")
fifty_img = round_corners(fifty_img, radius=60)
fifty_movies = [{'name': 'Fifty Shades of Grey'},
                {'name': 'Fifty Shades Darker'},
                {'name': 'Fifty Shades Freed'}]
ctk_fifty_img = customtkinter.CTkImage(light_image=fifty_img, dark_image=fifty_img, size=(int(1725*0.5), int(450*0.5)))
fifty_button = customtkinter.CTkButton(francises, text="", image=ctk_fifty_img,
                                       fg_color="transparent", hover_color="#1A1A1A")
fifty_button.pack(pady=12, padx=10)

horror_label = customtkinter.CTkLabel(francises, text="Horror", font=("Roboto", 29, "bold"))
horror_label.pack(pady=25, padx=25)

customtkinter.CTkLabel(francises, text="The Conjuring", font=("Roboto", 24, "bold")).pack(pady=2, padx=2)
conjuring_img = Image.open("Assets/Images/Banners/Theconjuringuniverse-banner.png")
conjuring_img = round_corners(conjuring_img, radius=60)
conjuring_movies = [{'name': 'The Conjuring'},
                    {'name': 'The Conjuring 2'},
                    {'name': 'Annabelle: Creation'},
                    {'name': 'The Nun'},
                    {'name': 'Annabelle Comes Home'},
                    {'name': 'The Conjuring: The Devil Made Me Do It'},
                    {'name': 'The Nun II'}]
ctk_conjuring_img = customtkinter.CTkImage(light_image=conjuring_img, dark_image=conjuring_img, size=(int(1725*0.5), int(450*0.6)))
conjuring_button = customtkinter.CTkButton(francises, text="", image=ctk_conjuring_img,
                                       fg_color="transparent", hover_color="#1A1A1A")
conjuring_button.pack(pady=12, padx=10)
francises2 = customtkinter.CTkScrollableFrame(tab_3)
prefrancises2 = customtkinter.CTkFrame(tab_3)
gif_path = r"Assets/Images/Animation-gif/Loading.gif"
gif = Image.open(gif_path)

gif_frames = [customtkinter.CTkImage(light_image=frame.convert("RGBA"), dark_image=frame.convert("RGBA"), size=(400, 400)) for frame in ImageSequence.Iterator(gif)]

gif_label = customtkinter.CTkLabel(prefrancises2, text="")
gif_label.pack()
loading_label = customtkinter.CTkLabel(prefrancises2, text="Učitavanje. . .", font=("Roboto", 29, "bold"))
loading_label.pack()
#animacija učitavanja
def update_gif(frame_num=0):
    gif_label.configure(image=gif_frames[frame_num])
    prefrancises2.after(50, update_gif, (frame_num + 1) % len(gif_frames))
def update_loading_label(loading_sequence=0):
    if loading_sequence == 0:
        loading_label.configure(text="Učitavanje")

    elif loading_sequence == 1:
        loading_label.configure(text="Učitavanje .")

    elif loading_sequence == 2:
        loading_label.configure(text="Učitavanje . .")

    elif loading_sequence == 3:
        loading_label.configure(text="Učitavanje . . .")

    next_loading_sequence = (loading_sequence + 1) % 4

    prefrancises2.after(200, update_loading_label, next_loading_sequence)

def delete_all(frame2, frame1):
    frame2.pack_forget()
    for widget in frame2.winfo_children():
        widget.destroy()
    frame1.pack(fill="both", expand=True, pady=12, padx=15)
    account_button3.place(x=0, y=0)


#prikazivanje filmova za "popularne franšize"
def francisescom(movies):
    account_button3.place_forget()
    francises.pack_forget()

    prefrancises2.pack(fill="both", expand=True, pady=12, padx=15)
    for movie in movies:
        francise_recommendations_widget = MovieRecommendationsWidget(francises2, movie)
        francise_recommendations_widget.pack(fill="both", expand=True, pady=12, padx=15)
    prefrancises2.pack_forget()
    button_back = customtkinter.CTkButton(francises2, text="<", font=("Roboto", 24),
                                          command=lambda: delete_all(francises2, francises))
    button_back.place(x=25, y=5)
    francises2.pack(fill="both", expand=True, pady=12, padx=15)


def start_loading():
    loading_thread = threading.Thread(target=update_gif, args=(0,))
    loading_screen_thread = threading.Thread(target=update_loading_label, args=(0,))
    loading_thread.start()
    loading_screen_thread.start()

def start(movies):
    start_loading()
    francisescom_thread = threading.Thread(target=lambda: francisescom(movies))
    francisescom_thread.start()

marvel_button.configure(command=lambda : start(marvel_movies))
star_wars_button.configure(command=lambda : start(star_wars_movies))
fast_button.configure(command=lambda : start(fast_movies))
james_button.configure(command=lambda : start(james_movies))
mission_button.configure(command=lambda : start(mission_movies))
lord_button.configure(command=lambda : start(lord_movies))
harry_button.configure(command=lambda : start(harry_movies))
fifty_button.configure(command=lambda : start(fifty_movies))
conjuring_button.configure(command=lambda : start(conjuring_movies))


root.mainloop()