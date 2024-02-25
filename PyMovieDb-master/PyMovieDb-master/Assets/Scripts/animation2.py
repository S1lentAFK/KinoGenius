import customtkinter
from PIL import Image, ImageSequence

root4 = customtkinter.CTk()
root4.title("Loading...")
root4.configure(fg_color="#212121")

gif_path = r"C:\Users\Admin\Downloads\Blocks-1s-500px.gif"
gif = Image.open(gif_path)

screen_width = root4.winfo_screenwidth()
screen_height = root4.winfo_screenheight()

x_position = (screen_width - gif.width) // 2
y_position = (screen_height - gif.height) // 2

gif_frames = [customtkinter.CTkImage(light_image=frame.convert("RGBA"), dark_image=frame.convert("RGBA"), size=(400, 400)) for frame in ImageSequence.Iterator(gif)]

gif_label = customtkinter.CTkLabel(root4, text="")
gif_label.pack()

genius_label = customtkinter.CTkLabel(root4, text="KinoGenius", font=("Roboto", 24), fg_color="#212121")
genius_label.pack(pady=12, padx=15)

def update_gif(frame_num=0):
    gif_label.configure(image=gif_frames[frame_num])
    root4.after(50, update_gif, (frame_num + 1) % len(gif_frames))

def update_loading_label(loading_sequence=0):
    if loading_sequence == 0:
        genius_label.configure(text="KinoGenius")

    elif loading_sequence == 1:
        genius_label.configure(text="KinoGenius .")

    elif loading_sequence == 2:
        genius_label.configure(text="KinoGenius . .")

    elif loading_sequence == 3:
        genius_label.configure(text="KinoGenius . . .")

    next_loading_sequence = (loading_sequence + 1) % 4

    root4.after(200, update_loading_label, next_loading_sequence)

root4.geometry(f"{gif.width}x{gif.height}+{x_position}+{y_position}")

update_gif()
update_loading_label()

root4.mainloop()
