import sys
from cx_Freeze import setup, Executable

# Dependencies to be included
build_exe_options = {
    "packages": [
        "tkinter", "requests", "json", "os", "customtkinter", "threading", "time",
        "PIL", "PIL.Image", "PIL.ImageTk", "PIL.ImageFilter", "PIL.ImageSequence",
        "requests", "io", "fuzzywuzzy", "tkinter.filedialog"
    ],
    "includes": ["fuzzywuzzy.fuzz"],
    "include_files": [
        ("accounts", "accounts"),
        ("movies", "movies"),
    ]
}

# Executable definition
executables = [Executable("KinoGenius.py", base="Win32GUI" if sys.platform == "win32" else None)]

setup(
    name="KinoGenius",
    version="0.1",
    description="KinoGenius",
    options={"build_exe": build_exe_options},
    executables=executables
)
