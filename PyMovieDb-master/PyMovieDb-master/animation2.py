import customtkinter
from PIL import Image, ImageSequence

# Create the main window
root4 = customtkinter.CTk()
root4.title("Loading...")
root4.configure(fg_color="#212121")

# Load the animated GIF
gif_path = r"C:\Users\Admin\Downloads\Blocks-1s-500px.gif"
gif = Image.open(gif_path)

# Get screen width and height
screen_width = root4.winfo_screenwidth()
screen_height = root4.winfo_screenheight()

# Calculate the position to center the window
x_position = (screen_width - gif.width) // 2
y_position = (screen_height - gif.height) // 2

# Create a list to store CustomTkinter image frames
gif_frames = [customtkinter.CTkImage(light_image=frame.convert("RGBA"), dark_image=frame.convert("RGBA"), size=(400, 400)) for frame in ImageSequence.Iterator(gif)]

# Create a label to display the GIF
gif_label = customtkinter.CTkLabel(root4, text="")
gif_label.pack()

# Create a label for the loading text
genius_label = customtkinter.CTkLabel(root4, text="KinoGenius", font=("Roboto", 24), fg_color="#212121")
genius_label.pack(pady=12, padx=15)

# Function to update the GIF
def update_gif(frame_num=0):
    gif_label.configure(image=gif_frames[frame_num])
    root4.after(50, update_gif, (frame_num + 1) % len(gif_frames))

# Function to update the loading label
def update_loading_label(loading_sequence=0):
    # Update the loading label based on the loading sequence
    if loading_sequence == 0:
        genius_label.configure(text="KinoGenius")

    elif loading_sequence == 1:
        genius_label.configure(text="KinoGenius .")

    elif loading_sequence == 2:
        genius_label.configure(text="KinoGenius . .")

    elif loading_sequence == 3:
        genius_label.configure(text="KinoGenius . . .")

    # Update loading sequence for the next iteration
    next_loading_sequence = (loading_sequence + 1) % 4

    root4.after(200, update_loading_label, next_loading_sequence)

# Set the window geometry to center it on the screen
root4.geometry(f"{gif.width}x{gif.height}+{x_position}+{y_position}")

# Start the GIF animation and loading label update
update_gif()
update_loading_label()

# Run the CustomTkinter event loop
root4.mainloop()
