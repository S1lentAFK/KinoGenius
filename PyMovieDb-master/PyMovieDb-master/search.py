import os
import json
from fuzzywuzzy import fuzz
import tkinter as tk
from tkinter import ttk

class FileSearchApp:
    def __init__(self, master):
        self.master = master
        master.title("Pretraživač datoteka")

        self.create_widgets()
        self.perform_search()

    def create_widgets(self):
        self.label = tk.Label(self.master, text="Unesite upit za pretraživanje:")
        self.label.pack(pady=10)

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(self.master, width=50, textvariable=self.entry_var)
        self.entry.pack(pady=10)

        self.result_tree = ttk.Treeview(self.master, columns=("Naziv datoteke", "Redatelj"), show="headings")
        self.result_tree.heading("Naziv datoteke", text="Naziv datoteke")
        self.result_tree.heading("Redatelj", text="Redatelj")
        self.result_tree.pack(pady=20)

        self.entry_var.trace_add("write", self.perform_search)

    def perform_search(self, *args):
        input_query = self.entry_var.get().strip(".json")
        base_path = r'C:\Users\Admin\Downloads\PyMovieDb-master\PyMovieDb-master\movies'
        years = ['2018', '2019', '2020', '2021', '2022', '2023']
        directories = [os.path.join(base_path, year) for year in years]

        results = self.search_files(input_query, directories)

        self.update_results_tree(results)

    def search_files(self, search_input, directories):
        found_files = []

        for directory in directories:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file_name in files:
                        if search_input == "" or self.is_match(search_input, file_name):
                            full_path = os.path.join(root, file_name)
                            director = self.extract_director_info(full_path)
                            similarity = self.calculate_similarity(search_input, file_name)
                            found_files.append((full_path, director, similarity))

        found_files.sort(key=lambda x: x[2], reverse=True)
        return found_files[:15] if search_input else found_files[:1673]

    def is_match(self, search_input, file_name):
        return search_input.lower() in file_name.lower()

    def calculate_similarity(self, search_input, file_name):
        return fuzz.partial_ratio(search_input.lower(), file_name.lower())

    def extract_director_info(self, full_path):
        try:

            with open(full_path, 'r', encoding='utf-8') as file:
                try:
                    movie_data = json.load(file)
                except json.JSONDecodeError:

                    return full_path

                if isinstance(movie_data, dict):
                    directors = movie_data.get("director", [])
                    if isinstance(directors, list) and directors:
                        # Assuming there can be multiple directors, join their names
                        return ", ".join(director["name"] for director in directors)
                    else:

                        return full_path
                else:

                    return full_path
        except FileNotFoundError:

            return full_path

    def update_results_tree(self, results):
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        for i, result in enumerate(results):
            file_name = os.path.basename(result[0])
            self.result_tree.insert("", "end", values=(file_name.strip(".json"), result[1]))


def main():
    root = tk.Tk()
    app = FileSearchApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
