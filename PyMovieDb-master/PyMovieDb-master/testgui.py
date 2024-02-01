import customtkinter
import os
import threading
import time
import json

def load_json_file(file_path):
    # Add your code to load and handle the JSON file here
    if file_path == "+":  # Special case for the "+" button
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
    scale_factor = 1.3
    target_size = 130  # Adjust the target size as needed

    for i in range(button.winfo_width(), target_size + 1, 2):
        button.configure(width=i, height=i)
        root.update_idletasks()
        time.sleep(0.000001)

def shrink_button(button):
    target_size = 100  # Initial size of the button

    for i in range(button.winfo_width(), target_size - 1, -2):
        button.configure(width=i, height=i)
        root.update_idletasks()
        time.sleep(0.000001)

def create_button_for_json(file_path, column):
    font_style = ("Roboto", 30, "bold")  # Adjust the font size as needed

    if file_path == "+":  # Special case for the "+" button
        button = customtkinter.CTkButton(frame, text="+", font=font_style, width=100, height=100)
        button.grid(row=2, column=0, padx=10, pady=10)  # Place the "+" button at column 0
        label = customtkinter.CTkLabel(frame, text="")
        label.grid(row=3, column=0)  # Placed label below the button
        button.bind("<Enter>", lambda event, btn=button, lbl=label: on_hover(event, btn, lbl, ""))
        button.bind("<Leave>", lambda event, btn=button, lbl=label: on_leave(event, btn, lbl))
    else:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            username = data.get('username', 'Unknown')
            button = customtkinter.CTkButton(frame, text='👤', font=font_style, width=100, height=100)
            button.grid(row=2, column=column, padx=10, pady=10)
            label = customtkinter.CTkLabel(frame, text="")
            label.grid(row=3, column=column)  # Placed label below the button
            button.bind("<Enter>", lambda event, btn=button, lbl=label, usr=username: on_hover(event, btn, lbl, usr))
            button.bind("<Leave>", lambda event, btn=button, lbl=label: on_leave(event, btn, lbl))

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.title("Load JSON Files")
root.geometry("600x400")

customtkinter.CTkLabel(root, text="Koji profil Koristite?", font=("Roboto", 40)).pack(padx=8, pady=8)

frame = customtkinter.CTkScrollableFrame(root, orientation="horizontal")
frame.pack(pady=12, padx=15, fill="both", expand=True)


customtkinter.CTkLabel(frame, text="", font=("Roboto", 60)).grid(row=1, column=0)

json_directory = r"C:\Users\Admin\Downloads\PyMovieDb-master\PyMovieDb-master\accounts"

# List all JSON files in the directory
json_files = [f for f in os.listdir(json_directory) if f.endswith(".json")]

# Create a button with text "+"
create_button_for_json("+", 2)

# Create buttons for each JSON file
for i, json_file in enumerate(json_files):
    json_file_path = os.path.join(json_directory, json_file)
    create_button_for_json(json_file_path, i + 1)

root.mainloop()