from tkinterdnd2 import TkinterDnD

from editor.editor_app import ExifEditorApp

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = ExifEditorApp(root)
    root.mainloop()
