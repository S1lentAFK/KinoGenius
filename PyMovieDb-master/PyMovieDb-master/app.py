# login_gui.py
import tkinter as tk
from tkinter import messagebox
import requests

def login():
    username = entry_username.get()
    password = entry_password.get()

    # Send credentials to the server for verification
    response = requests.post("http://16.170.225.118/login", json={"username": username, "password": password})

    if response.status_code == 200:
        messagebox.showinfo("Login Successful", "Welcome, " + username)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

def register():
    username = entry_username.get()
    password = entry_password.get()

    # Send new user registration data to the server
    response = requests.post("http://16.170.225.118/register", json={"username": username, "password": password})

    if response.status_code == 200:
        messagebox.showinfo("Registration Successful", "You can now login.")
    else:
        messagebox.showerror("Registration Failed", "Username already exists or an error occurred")

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
