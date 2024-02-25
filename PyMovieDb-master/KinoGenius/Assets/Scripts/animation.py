import customtkinter as ctk
from PIL import Image, ImageTk
import ctypes

class LoadingAnimation(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Loading Animation")

        window_width, window_height = 300, 300
        self.geometry(f"{window_width}x{window_height}")
        self.resizable(False, False)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"+{x}+{y}")

        self.configure(bg="#242424")
        self.configure(fg_color="#242424")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.canvas = ctk.CTkCanvas(self, width=window_width, height=window_height, bg="#242424")
        self.canvas.pack()

        original_image = Image.open("loading.png")
        resized_image = original_image.resize((200, 200))

        self.loading_frames = [ctk.CTkImage(dark_image=resized_image.rotate(angle), size=(200, 200)) for angle in range(0, 360, 15)]

        self.loading_label = ctk.CTkLabel(self.canvas, text="", image=self.loading_frames[0], fg_color="#242424")
        self.loading_label.pack()

        self.text_label = ctk.CTkLabel(self.master, text="Loading", font=("Roboto", 30, "bold"), fg_color="#242424")
        self.text_label.pack(side="bottom", pady=12, padx=15)

        self.current_frame = 0
        self.current_text_index = 0
        self.animate()

    def animate(self):
        self.loading_label.configure(image=self.loading_frames[self.current_frame])
        self.current_frame = (self.current_frame + 1) % len(self.loading_frames)

        # Update Loading text in the sequence
        loading_texts = ["Učitavanje ", "Učitavanje . ", "Učitavanje . . ", "Učitavanje . . . "]
        self.text_label.configure(text=loading_texts[self.current_text_index], fg_color="#242424")
        self.current_text_index = (self.current_text_index + 1) % len(loading_texts)

        if self.current_frame == 0:
            self.after(1000, self.animate)
        else:
            self.after(50, self.animate)

if __name__ == "__main__":
    app = LoadingAnimation()
    app.mainloop()
