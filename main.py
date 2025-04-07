import tkinter as tk

from editor.editor_app import ExifEditorApp

if __name__ == "__main__":
    root = tk.Tk()
    app = ExifEditorApp(root)
    root.mainloop()
