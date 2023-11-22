
from multiprocessing import Value
import os
import glob
import json
import webbrowser
import import_games
import threading
import tkinter as tk
import board
import tree
from memorization_game import MemorizationGame
from tkinter import ttk
from tkinter import filedialog, messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk

class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=self.controller.style.lookup('TFrame', 'background'))
        title_label = tk.Label(self, text="Settings", font=("Helvetica", 24))
        title_label.grid(row=0, column=0, columnspan=3, pady=20)
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

        lichess_token_label = tk.Label(self, text="Lichess Token(require for lichess imports):")
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
        messagebox.showinfo("Info", "Lichess imports are require a token you can get this free and inserting it into the settings page. Get the token by going to https://lichess.org/account/oauth/token")
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
        self.columnconfigure(1, weight=1)
        title_label = tk.Label(self, text="Import", font=("Helvetica", 24))
        title_label.grid(row=0, column=0, columnspan=3, pady=20)
        
        self.CHESS_EMAIL_WARNING = "Chess.com requires an email registered to an account to import games. \nPlease go to the settings and save your email. (Press yes to go directly to settings)"
        self.LICHESS_TOKEN_WARNING = "Lichess imports are around 3 times faster if you input a lichess tocken into the settings page. You can get a token by going to by going to https://lichess.org/account/oauth/token \n (Press yes to go directly to settings or no to continue)"
        ypadding=20

        self.checkbox_chess_com = tk.BooleanVar()
        checkbox_chess_com = tk.Checkbutton(self, text="Import From Chess.Com", variable=self.checkbox_chess_com)
        checkbox_chess_com.grid(row=1, column=0, sticky="w", padx=10, pady=ypadding)

        chess_com_username_label = tk.Label(self, text="Chess.Com User Name:")
        chess_com_username_label.grid(row=1, column=1, sticky="w", padx=10, pady=ypadding)
        self.chess_com_username_entry = tk.Entry(self)
        self.chess_com_username_entry.grid(row=1, column=2, sticky="w", padx=10, pady=ypadding)
        
        ##add warning
        #if self.controller.configs.get("email",False):

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

        self.show_advanced = tk.BooleanVar(value=False)  
        self.toggle_advanced_btn = tk.Checkbutton(self, text="Show Advanced Options", var=self.show_advanced, command=self.toggle_advanced_options)
        self.toggle_advanced_btn.grid(row=5, column=0, columnspan=2, pady=10)

        self.advanced_frame = tk.Frame(self)


        self.time_formats = ("rapid", "blitz", "bullet")
        self.time_format_bools = []
        time_format_checkboxes=[]
        for i, tf in enumerate(self.time_formats):

            self.time_format_bools.append(tk.BooleanVar(value= tf in controller.configs.get("time_formats")))
            time_format_checkboxes.append( tk.Checkbutton(self.advanced_frame, text=f"{tf}", variable=self.time_format_bools[i]))
            time_format_checkboxes[i].grid(row=0, column=i, sticky="w", padx=10, pady=ypadding)
            if tf in self.controller.configs.get("time_formats"):
                time_format_checkboxes[i].select()
        
        self.from_date_bool = tk.BooleanVar(value=False)
        self.from_date_checkbox = tk.Checkbutton(self.advanced_frame,text="From Date:",variable=self.from_date_bool)
        self.from_date_checkbox.grid(row=1, column=0, sticky="w", padx=10, pady=ypadding)
        
        self.from_date_entry = DateEntry(self.advanced_frame, date_pattern='yyyy-mm-dd')
        self.from_date_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=ypadding)

        self.to_date_bool = tk.BooleanVar(value=False)
        self.to_date_checkbox = tk.Checkbutton(self.advanced_frame,text="To Date:",variable=self.to_date_bool)
        self.to_date_checkbox.grid(row=2, column=0, sticky="w", padx=10, pady=ypadding)

        self.to_date_entry = DateEntry(self.advanced_frame, date_pattern='yyyy-mm-dd')
        self.to_date_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=ypadding)

        self.message_label = tk.Label(self, text="", font=("Helvetica", 20))
        self.message_label.grid(row=7, column=0, columnspan=3, pady=10)
        self.sub_message_label = tk.Label(self, text="", font=("Helvetica", 16))
        self.sub_message_label.grid(row=8, column=0, columnspan=3, pady=10)

        self.import_button = tk.Button(self, text="Import Games", command=self.start_import_func)
        self.import_button.grid(row=9, column=2, columnspan=2, sticky="ew", padx=10, pady=20)

        populate_button = tk.Button(self, text="Populate from config file", command=self.populate_entries)
        populate_button.grid(row=9, column=1, columnspan=1, padx=10, pady=20)

        back_button = tk.Button(self, text="Back to Main Menu", command=lambda: controller.show_frame(MainMenu))
        back_button.grid(row=9, column=0, columnspan=1,sticky="ew", padx=10, pady=20)

    def import_func(self):
        chess_com_user = self.chess_com_username_entry.get().strip() if self.checkbox_chess_com.get() else False
        if chess_com_user and not self.controller.configs.get("email",False):
            
            if self.show_warning_question(self.CHESS_EMAIL_WARNING) == "yes":
                self.controller.show_frame(SettingsPage)
            return
        lichess_user = self.lichess_username_entry.get().strip() if self.checkbox_lichess.get() else False
        if lichess_user and not self.controller.configs.get("lichess_token",False):
            if self.show_warning_question(self.LICHESS_TOKEN_WARNING) == "yes":
                self.controller.show_frame(SettingsPage)
                return

        pgns_files = self.pgn_files_entry.get().strip() if self.checkbox_pgn_files.get() else False
        time_formats = [t for t,b in zip(self.time_formats, self.time_format_bools) if b.get()]
        file_name = self.save_as_file_path_entry.get().strip() if self.save_as_file_path_entry.get().strip() else None
        from_date = self.from_date_entry.get().strip() if self.from_date_bool.get() else None
        to_date = self.from_date_entry.get().strip() if self.to_date_bool.get() else None
        games = import_games.import_all_games(file_name=file_name, 
                                              chess_com_user=chess_com_user, 
                                              lichess_user=lichess_user, 
                                              pgns_files=pgns_files, 
                                              time_formats = time_formats, 
                                              append=True, 
                                              from_date = from_date,
                                              to_date= to_date,
                                              mesg_label=self.message_label, 
                                              sub_mesg_label=self.sub_message_label)

        #self.import_button.config(text="Start Import", command=self.start_import_func)
    
    def show_warning_question(self, mesg):
        return messagebox.askquestion("Warning", mesg)
    
    def toggle_advanced_options(self):
        if self.show_advanced.get():
            self.advanced_frame.grid(row=6, column=0, columnspan=3, sticky="ew")
        else:
            self.advanced_frame.grid_forget()
    def start_import_func(self):
        self.import_thread = threading.Thread(target=self.import_func)
        self.import_thread.start()
    #    self.import_button.config(text="Start Import", command=lambda:self.show_warning_question("Import already started"))
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
        directory = filedialog.askopenfilename(initialdir=f"{os.getcwd()}\\{self.controller.configs.get('ingest_dir','')}")
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
 


class MemorizationPage(tk.Frame):
    
    

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg=self.controller.style.lookup('TFrame', 'background'))
        self.title = "Memorization Game"
        self.images = []
        self.controller = controller
        self.memorization_game = None
        self.board = board.Board()
        self.flip_board = False
        self.piece_images = {}
        self.squares = {}


        self.paned_window = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.main_content_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.main_content_frame)

        self.side_panel = ttk.Frame(self.paned_window, width=200)
        self.paned_window.add(self.side_panel)

        self.notebook = ttk.Notebook(self.side_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.dir_tab_frame = ttk.Frame(self.notebook)
        
        self.file_listbox = tk.Listbox(self.dir_tab_frame, selectmode=tk.EXTENDED)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)

        self.notebook.add(self.dir_tab_frame, text="Study file select")

        

        # Game layout
        self.board_frame = tk.Frame(self.main_content_frame)
        self.board_frame.pack(pady=10)
        self.create_board()

        self.load_piece_images()
        self.update_board()
        self.control_frame = tk.Frame(self.main_content_frame)
        self.control_frame.pack(fill=tk.BOTH, expand=True)
        for i in range(5):
            self.control_frame.columnconfigure(i, weight=1)
            self.control_frame.rowconfigure(i, weight=1)
        self.input_move = tk.Entry(self.control_frame)
        self.input_move.grid(row=0, column=0, columnspan=3, pady=10)

        self.submit_button = tk.Button(self.control_frame, text="Submit", command=self.check_move)
        self.submit_button.grid(row=0, column=3, padx=5,pady=10)

        self.hint_button = tk.Button(self.control_frame, text="Hint", command=self.show_hint)
        self.hint_button.grid(row=0, column=4, padx=5,pady=10)

        self.last_puzzle_button = tk.Button(self.control_frame, text="Return to last puzzle", command=self.last_puzzle)
        self.last_puzzle_button.grid(row=1, column=1, padx=5, pady=10)

        self.flip_button = tk.Button(self.control_frame, text="Flip Board", command=self.flip_perspective)
        self.flip_button.grid(row=1, column=2, padx=5, pady=10)
        self.answer_button = tk.Button(self.control_frame, text="Show Answer", command=self.show_answer)
        self.answer_button.grid(row=1, column=3,padx=5, pady=10)

        self.next_button = tk.Button(self.control_frame, text="Next", command=self.next_puzzle)
        self.next_button.grid(row=1, column=4, padx=5, pady=10)
        

        self.message_label = tk.Label(self.control_frame, text="", font=("Helvetica", 12))
        self.message_label.grid(row=2, columnspan=4, pady=10)
        self.study_label = tk.Label(self.control_frame, text="", font=("Helvetica", 12))
        self.message_label.grid(row=3, columnspan=4, pady=10)
        self.notes_label = tk.Label(self.control_frame, text="", font=("Helvetica", 12))
        self.message_label.grid(row=4, columnspan=4, pady=10)
        self.back_button = tk.Button(self.control_frame, text="Back to Main Menu", command=lambda: self.controller.show_frame(MainMenu))
        self.back_button.grid(row=5, column=0, pady=10)

        
        

        # Populate the listbox with files
        self.populate_file_listbox(controller.configs.get("study_dir"))

        # Button to toggle the side panel
        self.toggle_button = tk.Button(self.main_content_frame, text="Toggle Side Panel", command=self.toggle_side_panel)
        self.toggle_button.pack()

        self.load_button = tk.Button(self.dir_tab_frame, text="Load Studies", command=self.start_memory_game)
        self.load_button.pack()

        

    def flip_perspective(self):
        self.flip_board = not self.flip_board
        self.update_board()
    def load_piece_images(self):
        
        pieces = ('K', 'k', 'Q', 'q', 'R', 'r', 'B', 'b', 'N', 'n', 'P', 'p')
        theme = self.controller.configs.get("piece_theme","merida")
        piece_to_file_name = {'K':"wK", 'k':"bK", 'Q':"wQ",'q':"bQ", 'R':"wR",'r':"bR",'B':"wB",'b':"bB", 'N':"wN",'n':"bN",'P':"wP",'p':"bP"}
        for piece in pieces:
            path = f"piece_images/{theme}/{piece_to_file_name.get(piece)}.png" 
            image = Image.open(path)
            image = image.resize((50, 50), Image.LANCZOS)
            self.piece_images[f"{piece}_pil"] = image
            image = ImageTk.PhotoImage(image)
            self.piece_images[piece] = image
        annotations = ('.',)
        annotations_to_file_name = {'.':"blank"}
        for annotation in annotations:
            path = f"piece_images/annotations/{annotations_to_file_name.get(annotation)}.png" 
            image = Image.open(path)
            image = image.resize((50, 50), Image.LANCZOS)  
            self.piece_images[f"{annotation}_pil"] = image
            image = ImageTk.PhotoImage(image)
            self.piece_images[annotation] = image

    def create_board(self):

        for row in range(8):
            for col in range(8):
                square_color = "white" if (row + col) % 2 == 0 else "gray"
                square = tk.Label(self.board_frame, bg=square_color)
                square.grid(row=row, column=col)
                self.squares[( col,row)] = square

    

    def update_board(self):
        # Clear the current board
        
        for square in self.squares.values():
            square.config(image='', text='', bg=square.cget("bg"))

        for row in range(8):
            for col in range(8):
                piece = self.board.piece_at((row,col),letter_rep = True , flipped = self.flip_board)
                if piece:
                    image = self.piece_images.get(piece, None)
                    if image:
                        self.squares[(row, 7-col)].config(image=image)
                        self.squares[(row, 7-col)].image = image
                        self.squares[(row, 7-col)].piece = piece
                    

    def check_move(self):
        user_move = self.input_move.get().strip()
        response = self.memorization_game.check_answer(user_move)
        self.message_label.config(text=response)
        if response[0] == 'C':
            self.notes_label.config(text=self.memorization_game.get_notes())

    def show_hint(self):
        if self.memorization_game:
            for row,col in self.memorization_game.from_coords:
                if self.flip_board:
                    self.highlight_square((7-row,col))
                else:
                    self.highlight_square((row,7-col))
                

    def show_answer(self):
        if self.memorization_game:
            self.message_label.config(text=self.memorization_game.get_answer())
            self.notes_label.config(text=self.memorization_game.get_notes())

    def next_puzzle(self):
        if self.memorization_game:
            self.memorization_game.next_random_node()
            self.board = self.memorization_game.current_board
            self.flip_board = not self.board.whites_move
            self.update_board()
            self.message_label.config(text="")
            self.notes_label.config(text="")
        else:
            
            pass
    def last_puzzle(self):
        if self.memorization_game:
            self.memorization_game.return_to_last_node()
            self.board = self.memorization_game.current_board
            self.flip_board = not self.board.whites_move
            self.update_board()
            self.message_label.config(text="")
            self.notes_label.config(text="")
        else:
            
            pass    
    def populate_file_listbox(self, directory):
        
        self.file_listbox.delete(0, tk.END)

        for file in os.listdir(directory):
            if file.endswith(".json"):
                self.file_listbox.insert(tk.END, file)

    def toggle_side_panel(self):
        
        if self.side_panel.winfo_ismapped():
            self.paned_window.remove(self.side_panel)
        else:
            self.paned_window.add(self.side_panel)
    
    def highlight_square(self, coord, color = None):
        
        if color == None:
            color = (255,0,0,200)
        
        piece_pil_image = self.piece_images.get(f"{self.squares[coord].piece}_pil", None).convert('RGBA')
        highlight =  Image.new(mode = "RGBA", size = (50, 50), color = color)
        highlight.paste(piece_pil_image, (0, 0), piece_pil_image)
        update_image = ImageTk.PhotoImage(highlight)
        self.squares[coord].config(image=update_image)
        self.squares[coord].image = update_image
 

    def create_studies_tab(self):
        
        self.study_tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.study_tab_frame, text="Chapter select color")
        
        self.radio_var = tk.StringVar()
        self.study_colors = [tk.StringVar(value=study.get("study_as")) for study in self.studies]
        for i, study in enumerate(self.studies):
            radio_frame = ttk.Frame(self.study_tab_frame)
            radio_frame.pack(fill=tk.X, padx=5, pady=5)

            tk.Radiobutton(radio_frame, text="White", variable=self.study_colors[i], value=f"w").pack(side=tk.LEFT)
            tk.Radiobutton(radio_frame, text="Black", variable=self.study_colors[i], value=f"b").pack(side=tk.LEFT)
            tk.Label(radio_frame, text=study.get("name")).pack(side=tk.LEFT)

        self.update_study_button = tk.Button(self.study_tab_frame, text="Update Color Studies", command=self.update_studies)
        self.update_study_button.pack()
    
    def update_studies(self):
        for i, study in enumerate(self.studies):
            if study.get("study_as") != self.study_colors[i].get():
                study["study_as"] = self.study_colors[i].get()
                import_games.dump_study(study,study.get("name"))

        thread = threading.Thread(target=self.load_memory_game)
        thread.start()

    def load_memory_game(self):

        study_trees=[]
        for study in self.studies:
            study_trees.append(tree.StudyTree(study))
            
        self.memorization_game = MemorizationGame(study_trees)
        self.next_puzzle()

    def start_memory_game(self):
        
        self.studies = self.load_selected_studies()

        if len(self.notebook.tabs()) > 1:
            self.notebook.forget(1)

        self.create_studies_tab()

        self.notebook.select(1)
        thread = threading.Thread(target=self.load_memory_game)
        thread.start()
        
        
        print("made game")
    

        
    def load_selected_studies(self):

        selected_files = [self.file_listbox.get(i) for i in self.file_listbox.curselection()]
        
        print("Selected Files:", selected_files)
        studies=[]
        for file in selected_files:
            study = import_games.load_study(file)
            studies.append(study)
            
        return studies
        

class AboutPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        #self.configure(bg=self.controller.style.lookup('TFrame', 'background'))
        self.title = "About"
        label = tk.Label(self, text="About")
        label.pack(padx=10, pady=10)

        self.text="""Chess Learn is an app that helps you memorize your opening lines, better prepare against opponents, and see where your openings are weak.
        
        The import games page allows you to import your chess games from both lichess and chess.com as well as local pgn files. These are then stored locally in a collective file that is later used by the program in memorization game and opening analysis.
        You can prepopulate the imports page from the defaults that you can change from the settings menu, you can further change advance settings at editing the config.json file directly. 
        
        In order to import games from chess.com, you need to insert a chess.com user email into the settings page.
        In order to import games from lichess, you need to insert a lichess token into the settings page. 
        
        """

        text_widget = tk.Text(self, wrap=tk.WORD)
        text_widget.insert("1.0", self.text)
        text_widget.configure(state="disabled")
        text_widget.pack(fill=tk.BOTH, expand=True)
        tutorial_link = tk.Label(self, text="Tutorial", fg="blue", cursor="hand2")
        tutorial_link.pack()
        tutorial_link.bind("<Button-1>", lambda e: self.callback("https://youtu.be/J7NBmdtpX4o"))

        github_link = tk.Label(self, text="Github", fg="blue", cursor="hand2")
        github_link.pack()
        github_link.bind("<Button-1>", lambda e: self.callback("https://github.com/rouyerr/cs361"))

        label.pack(padx=10, pady=10)

        back_button = tk.Button(self, text="Back to Main Menu", command=lambda: controller.show_frame(MainMenu))
        back_button.pack()
    def callback(self,url):
        webbrowser.open_new(url)
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

        to_memorize_page = tk.Button(self, text="Go to Memorization Game", command=lambda: controller.show_frame(MemorizationPage))
        to_memorize_page.pack(fill="x",pady = 40)

        to_settings_page = tk.Button(self, text="Go to Settings", command=lambda: controller.show_frame(SettingsPage))
        to_settings_page.pack(fill="x",pady = 40)

        to_about_page = tk.Button(self, text="Go to About", command=lambda: controller.show_frame(AboutPage))
        to_about_page.pack(fill="x",pady = 40)

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
        for F in (MainMenu, ImportPage, MemorizationPage, SettingsPage,AboutPage):
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

