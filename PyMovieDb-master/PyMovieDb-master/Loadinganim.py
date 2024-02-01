from tkinter import *
from threading import *
from time import *
from PIL import Image, ImageTk

def dugi_proces(t):
    sleep(t)
    root.deiconify()
    loading.destroy()

def pokreni_thread():
    t = Thread(target=dugi_proces, args=(5,))
    t.start()

def close():
    root.destroy()

root = Tk()
root.title('Loading...')
frame = Frame(root)
frame.pack()
gumb = Button(frame, text='OK', command=close)
gumb.pack()
root.withdraw()
loading = Toplevel(root)
f = Frame(loading)
loading.title('Učitavanje')
f.pack()
img = Image.open(r'C:\Users\Admin\Downloads\Blocks-1s-500px.gif')
imag = ImageTk.PhotoImage(img)
l = Label(f, image=imag)
l.photo = imag
l.pack()
loading.after(100, pokreni_thread)
root.mainloop()
    
