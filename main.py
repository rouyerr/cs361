from ast import Pass
import os
import glob
import json
import import_games
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox

class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=self.controller.style.lookup('TFrame', 'background'))
        title_label = tk.Label(self, text="Settings", font=("Helvetica", 24))
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        ypadding=20
        self.configs = self.controller.configs

        
        chess_com_username_label = tk.Label(self, text="Chess.Com User Name:")
        chess_com_username_label.grid(row=1, column=0, sticky="w", padx=10, pady=ypadding)
        self.chess_com_username_entry = tk.Entry(self)
        self.chess_com_username_entry.grid(row=1, column=1, sticky="w", padx=10, pady=ypadding)
        self.chess_com_username_entry.insert(0, self.configs.get("chess_com_user"))

        chess_com_email_label = tk.Label(self, text="Chess.Com Email(require for Chess.com imports):")
        chess_com_email_label.grid(row=2, column=0, sticky="w", padx=10, pady=ypadding)
        self.chess_com_email_entry = tk.Entry(self)
        self.chess_com_email_entry.grid(row=2, column=1, sticky="w", padx=10, pady=ypadding)
        self.chess_com_email_entry.insert(0, self.configs.get("email"))

        lichess_username_label = tk.Label(self, text="Lichess User Name:")
        lichess_username_label.grid(row=3, column=0, sticky="w", padx=10, pady=ypadding)
        self.lichess_username_entry = tk.Entry(self)
        self.lichess_username_entry.grid(row=3, column=1, sticky="w", padx=10, pady=ypadding)
        self.lichess_username_entry.insert(0, self.configs.get("lichess_user"))

        lichess_token_label = tk.Label(self, text="Lichess Token:")
        lichess_token_label.grid(row=4, column=0, sticky="w", padx=10, pady=ypadding)
        self.lichess_token_entry = tk.Entry(self, show='*')
        self.lichess_token_entry.grid(row=4, column=1, sticky="w", padx=10, pady=ypadding)
        self.lichess_token_entry.insert(0, self.configs.get("lichess_token"))
        show_lichess_button = tk.Button(self, text="?", command=self.show_lichess_message)
        show_lichess_button.grid(row=4, column=2, pady=10)
        
        self.time_formats = ("rapid", "blitz", "bullet")
        self.time_format_bools = []
        time_format_checkboxes=[]
        for i, tf in enumerate(self.time_formats):

            self.time_format_bools.append(tk.BooleanVar())
            time_format_checkboxes.append( tk.Checkbutton(self, text=f"{tf}", variable=self.time_format_bools[i]))
            time_format_checkboxes[i].grid(row=5, column=i, sticky="w", padx=10, pady=ypadding)
            time_format_checkboxes[i].select()

        save_button = tk.Button(self, text="Save settings", command=self.save_config)
        save_button.grid(row=8, column=1, pady=10)
        apply_button = tk.Button(self, text="Apply settings", command=self.apply_config)
        apply_button.grid(row=8, column=2, pady=10)

        back_button = tk.Button(self, text="Back to Main Menu", command=lambda: controller.show_frame(MainMenu))
        back_button.grid(row=8, column=0, columnspan=2, pady=20)
    def show_lichess_message(self):
        messagebox.showinfo("Info", "Lichess imports are faster with a token you can get this token by going to https://lichess.org/account/oauth/token")
    def save_config(self):
        self.apply_config()
        with open(f".\\config.json", "w") as f:
            json.dump(self.configs,f)
    def apply_config(self):
        self.configs["chess_com_user"] = self.chess_com_username_entry.get()
        self.configs["email"] = self.chess_com_email_entry.get()
        self.configs["lichess_user"] = self.lichess_username_entry.get()
        self.configs["lichess_token"] = self.lichess_token_entry.get()
        self.configs["time_formats"] = [t for t,b in zip(self.time_formats, self.time_format_bools) if b.get()]

class ImportPage(tk.Frame):
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=self.controller.style.lookup('TFrame', 'background'))
        title_label = tk.Label(self, text="Import", font=("Helvetica", 24))
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        ypadding=20

        self.checkbox_chess_com = tk.BooleanVar()
        checkbox_chess_com = tk.Checkbutton(self, text="Import From Chess.Com", variable=self.checkbox_chess_com)
        checkbox_chess_com.grid(row=1, column=0, sticky="w", padx=10, pady=ypadding)

        chess_com_username_label = tk.Label(self, text="Chess.Com User Name:")
        chess_com_username_label.grid(row=1, column=1, sticky="w", padx=10, pady=ypadding)
        self.chess_com_username_entry = tk.Entry(self)
        self.chess_com_username_entry.grid(row=1, column=2, sticky="w", padx=10, pady=ypadding)

        self.checkbox_lichess = tk.BooleanVar()
        checkbox_lichess = tk.Checkbutton(self, text="Import From Lichess", variable=self.checkbox_lichess)
        checkbox_lichess.grid(row=2, column=0, sticky="w", padx=10, pady=ypadding)

        lichess_username_label = tk.Label(self, text="Lichess User Name:")
        lichess_username_label.grid(row=2, column=1, sticky="w", padx=10, pady=ypadding)
        self.lichess_username_entry = tk.Entry(self)
        self.lichess_username_entry.grid(row=2, column=2, sticky="w", padx=10, pady=ypadding)

        self.checkbox_pgn_files = tk.BooleanVar()
        checkbox_pgn_files = tk.Checkbutton(self, text="Import From Pgn Files", variable=self.checkbox_pgn_files)
        checkbox_pgn_files.grid(row=3, column=0, sticky="w", padx=10, pady=ypadding)

        pgn_files_label = tk.Label(self, text="Pgn Files or Directory:")
        pgn_files_label.grid(row=3, column=1, sticky="w", padx=10, pady=ypadding)
        self.pgn_files_entry = tk.Entry(self)
        self.pgn_files_entry.grid(row=3, column=2, sticky="w", padx=10, pady=ypadding)
        browse_button_ingest = tk.Button(self, text="Browse", command=lambda: self.browse_directory(self.pgn_files_entry))
        browse_button_ingest.grid(row=3, column=3, pady=10)

        label_pgn_ingest = tk.Label(self, text="Save_As:")
        label_pgn_ingest.grid(row=4, column=0, sticky="w", padx=10)
        self.save_as_file_path_entry = tk.Entry(self)
        self.save_as_file_path_entry.grid(row=4, column=1, sticky="w", padx=10)
        browse_button_save_path = tk.Button(self, text="Browse", command=lambda: self.browse_directory_save(self.save_as_file_path_entry))
        browse_button_save_path.grid(row=4, column=2, pady=10)

        self.time_formats = ("rapid", "blitz", "bullet")
        self.time_format_bools = []
        time_format_checkboxes=[]
        for i, tf in enumerate(self.time_formats):

            self.time_format_bools.append(tk.BooleanVar())
            time_format_checkboxes.append( tk.Checkbutton(self, text=f"{tf}", variable=self.time_format_bools[i]))
            time_format_checkboxes[i].grid(row=5, column=i, sticky="w", padx=10, pady=ypadding)
            time_format_checkboxes[i].select()

        self.message_label = tk.Label(self, text="", font=("Helvetica", 20))
        self.message_label.grid(row=6, column=0, columnspan=3, pady=10)
        self.sub_message_label = tk.Label(self, text="", font=("Helvetica", 16))
        self.sub_message_label.grid(row=7, column=0, columnspan=3, pady=10)

        import_button = tk.Button(self, text="Import Games", command=self.start_import_func)
        import_button.grid(row=8, column=0, columnspan=2, pady=20)

        import_button = tk.Button(self, text="Populate from config file", command=self.populate_entries)
        import_button.grid(row=9, column=0, columnspan=2, pady=20)

        back_button = tk.Button(self, text="Back to Main Menu", command=lambda: controller.show_frame(MainMenu))
        back_button.grid(row=10, column=0, columnspan=2, pady=20)

    def import_func(self):
        chess_com_user = self.chess_com_username_entry.get().strip() if self.checkbox_chess_com.get() else False
        lichess_user = self.lichess_username_entry.get().strip() if self.checkbox_lichess.get() else False
        pgns_files = self.pgn_files_entry.get().strip() if self.checkbox_pgn_files.get() else False
        time_formats = (t for t,b in zip(self.time_formats, self.time_format_bools) if b.get())
        file_name = self.save_as_file_path_entry.get().strip() if self.save_as_file_path_entry.get().strip() else None
        games = import_games.import_all_games(file_name=file_name, 
                                              chess_com_user=chess_com_user, 
                                              lichess_user=lichess_user, 
                                              pgns_files=pgns_files, 
                                              time_formats = time_formats, 
                                              append=True, 
                                              mesg_label=self.message_label, 
                                              sub_mesg_label=self.sub_message_label)
    def start_import_func(self):
        thread = threading.Thread(target=self.import_func)
        thread.start()
    def insert_in_entry(self, entry, txt):
        entry.delete(0, tk.END)
        entry.insert(0, txt)

    def populate_entries(self):
        with open(f".\\config.json", "r") as f:
            config = json.load(f)
        self.insert_in_entry(self.chess_com_username_entry,config.get("chess_com_user"))
        self.insert_in_entry(self.lichess_username_entry,config.get("lichess_user"))
        self.insert_in_entry(self.pgn_files_entry,config.get("ingest_dir"))
        self.insert_in_entry(self.pgn_files_entry,config.get("imported_dir"))
    
    def browse_directory(self, entry):
        directory = filedialog.askopenfilename()
        if directory:
            self.insert_in_entry(entry, directory)
        
    def browse_directory_save(self, entry):
        #initial_dir = entry.get().strip()
        #if not initial_dir:
        #    initial_dir = os.getcwd()
        #print(initial_dir)
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Json Files", "*.json"), ("All Files", "*.*")])
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path)
    
class MemorizationGame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=self.controller.style.lookup('TFrame', 'background'))
        self.title = "MemorizationGame"
        label = tk.Label(self, text="Memorization Game")
        label.pack(padx=10, pady=10)
        
        label = tk.Label(self, text="Coming soon")
        label.pack(padx=10, pady=10)

        back_button = tk.Button(self, text="Back to Main Menu", command=lambda: controller.show_frame(MainMenu))
        back_button.pack()
        
    def print_size(self):
        
        width = self.winfo_width()
        height = self.winfo_height()
        print(f"Frame '{self.title}' size: {width}x{height}")
        screen_width = self.controller.winfo_screenwidth()
        screen_height = self.controller.winfo_screenheight()
        print(f"{screen_width}x{screen_height}")

class MainMenu (tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=self.controller.style.lookup('TFrame', 'background'))
        label = tk.Label(self, text="Chess Learn Main Menu", font=("Helvetica", 36))
        label.pack(fill="x", pady=50)

        to_import_page = tk.Button(self, text="Go to Imports Page", command=lambda: controller.show_frame(ImportPage))
        to_import_page.pack(fill="x", pady = 40)

        to_memorize_page = tk.Button(self, text="Go to Memorization Game", command=lambda: controller.show_frame(MemorizationGame))
        to_memorize_page.pack(fill="x",pady = 40)

        to_memorize_page = tk.Button(self, text="Go to Settings", command=lambda: controller.show_frame(SettingsPage))
        to_memorize_page.pack(fill="x",pady = 40)

        exit_button = tk.Button(self, text="Exit", command=self.quit_application)
        exit_button.pack(fill="x",pady=40)

    def quit_application(self):
        self.controller.destroy()

class GUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open(f".\\config.json", "r") as f:
            self.configs = json.load(f)
        full_screen=False

        if full_screen:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            self.geometry(f"{screen_width}x{screen_height}")
        self.tk.eval("""
    set base_theme_dir ./awthemes-10.4.0/

    package ifneeded awthemes 10.4.0 \
        [list source [file join $base_theme_dir awthemes.tcl]]
    package ifneeded colorutils 4.8 \
        [list source [file join $base_theme_dir colorutils.tcl]]
    package ifneeded awdark 7.12 \
        [list source [file join $base_theme_dir awdark.tcl]]
    # ... (you can add the other themes from the package if you want
    """)
        self.tk.call("package", "require", 'awdark')
        self.style = ttk.Style(self)
        self.theme = self.configs.get("theme")
        self.update_theme()

        self.title("ChessLearn")
        self.iconbitmap("logo.png")
        container = tk.Frame(self, borderwidth=5, relief="ridge")
        container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (MainMenu, ImportPage, MemorizationGame, SettingsPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainMenu)

        
    def update_theme(self):
        self.style.theme_use(self.theme)
        #if self.configs.get("dark_mode"):
        #    self.configure(bg="black")  # Set the window background color to black in dark mode
        #    self.style.configure("TLabel", foreground="white", background="black")
        #    print("Welp")
        #else:
        #    self.configure(bg="white")  # Set the window background color to white in light mode
        #    self.style.configure("TLabel", foreground="black", background="white")


    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()

if __name__ == "__main__":
    app = GUI()
    app.mainloop()




def load_games(self, file_name):
        
        if file_name == None:
            file_name = f"{config.get('name')}_all_games.json"
        imported_dir = config.get("imported_dir")
        full_file_path = f"{imported_dir}\\{file_name}"
        if os.path.isfile(full_file_path):
            with open(full_file_path, "r") as f:
                games = json.load(f)
        return games

