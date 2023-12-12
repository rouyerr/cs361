import os
from datetime import datetime
import time
import glob
import json
import ndjson
import shutil
import requests
import re
from board import Board

ANNOTATION_NAGS = {
    0: "null annotation",
    1: "good move [!] see also Nunn Convention for alternate meanings",
    2: "poor move or mistake [?] ",
    3: "very good or brilliant move (!!)",
    4: "very poor move or blunder (??)",
    5: "speculative or interesting move [!?]",
    6: "questionable or dubious move [?!]",
    7: "forced move (all others lose quickly) or only move",
    8: "singular move (no reasonable alternatives)",
    9: "worst move",
    10: "drawish position or even",
    11: "equal chances, quiet position",
    12: "equal chances, active position",
    13: "unclear position",
    14: "White has a slight advantage",
    15: "Black has a slight advantage",
    16: "White has a moderate advantage",
    17: "Black has a moderate advantage",
    18: "White has a decisive advantage",
    19: "Black has a decisive advantage",
    20: "White has a crushing advantage (Black should resign)",
    21: "Black has a crushing advantage (White should resign)",
    22: "White is in zugzwang",
    23: "Black is in zugzwang",
    24: "White has a slight space advantage",
    25: "Black has a slight space advantage",
    26: "White has a moderate space advantage",
    27: "Black has a moderate space advantage",
    28: "White has a decisive space advantage",
    29: "Black has a decisive space advantage",
    30: "White has a slight time (development) advantage",
    31: "Black has a slight time (development) advantage",
    32: "White has a moderate time (development) advantage",
    33: "Black has a moderate time (development) advantage",
    34: "White has a decisive time (development) advantage",
    35: "Black has a decisive time (development) advantage",
    36: "White has the initiative",
    37: "Black has the initiative",
    38: "White has a lasting initiative",
    39: "Black has a lasting initiative",
    40: "White has the attack",
    41: "Black has the attack",
    42: "White has insufficient compensation for material deficit",
    43: "Black has insufficient compensation for material deficit",
    44: "White has sufficient compensation for material deficit",
    45: "Black has sufficient compensation for material deficit",
    46: "White has more than adequate compensation for material deficit",
    47: "Black has more than adequate compensation for material deficit",
    48: "White has a slight center control advantage",
    49: "Black has a slight center control advantage",
    50: "White has a moderate center control advantage",
    51: "Black has a moderate center control advantage",
    52: "White has a decisive center control advantage",
    53: "Black has a decisive center control advantage",
    54: "White has a slight kingside control advantage",
    55: "Black has a slight kingside control advantage",
    56: "White has a moderate kingside control advantage",
    57: "Black has a moderate kingside control advantage",
    58: "White has a decisive kingside control advantage",
    59: "Black has a decisive kingside control advantage",
    60: "White has a slight queenside control advantage",
    61: "Black has a slight queenside control advantage",
    62: "White has a moderate queenside control advantage",
    63: "Black has a moderate queenside control advantage",
    64: "White has a decisive queenside control advantage",
    65: "Black has a decisive queenside control advantage",
    66: "White has a vulnerable first rank",
    67: "Black has a vulnerable first rank",
    68: "White has a well-protected first rank",
    69: "Black has a well-protected first rank",
    70: "White has a poorly protected king",
    71: "Black has a poorly protected king",
    72: "White has a well-protected king",
    73: "Black has a well-protected king",
    74: "White has a poorly placed king",
    75: "Black has a poorly placed king",
    76: "White has a well-placed king",
    77: "Black has a well-placed king",
    78: "White has a very weak pawn structure",
    79: "Black has a very weak pawn structure",
    80: "White has a moderately weak pawn structure",
    81: "Black has a moderately weak pawn structure",
    82: "White has a moderately strong pawn structure",
    83: "Black has a moderately strong pawn structure",
    84: "White has a very strong pawn structure",
    85: "Black has a very strong pawn structure",
    86: "White has poor knight placement",
    87: "Black has poor knight placement",
    88: "White has good knight placement",
    89: "Black has good knight placement",
    90: "White has poor bishop placement",
    91: "Black has poor bishop placement",
    92: "White has good bishop placement",
    93: "Black has good bishop placement",
    94: "White has poor rook placement",
    95: "Black has poor rook placement",
    96: "White has good rook placement",
    97: "Black has good rook placement",
    98: "White has poor queen placement",
    99: "Black has poor queen placement",
    100: "White has good queen placement",
    101: "Black has good queen placement",
    102: "White has poor piece coordination",
    103: "Black has poor piece coordination",
    104: "White has good piece coordination",
    105: "Black has good piece coordination",
    106: "White has played the opening very poorly",
    107: "Black has played the opening very poorly",
    108: "White has played the opening poorly",
    109: "Black has played the opening poorly",
    110: "White has played the opening well",
    111: "Black has played the opening well",
    112: "White has played the opening very well",
    113: "Black has played the opening very well",
    114: "White has played the middlegame very poorly",
    115: "Black has played the middlegame very poorly",
    116: "White has played the middlegame poorly",
    117: "Black has played the middlegame poorly",
    118: "White has played the middlegame well",
    119: "Black has played the middlegame well",
    120: "White has played the middlegame very well",
    121: "Black has played the middlegame very well",
    122: "White has played the ending very poorly",
    123: "Black has played the ending very poorly",
    124: "White has played the ending poorly",
    125: "Black has played the ending poorly",
    126: "White has played the ending well",
    127: "Black has played the ending well",
    128: "White has played the ending very well",
    129: "Black has played the ending very well",
    130: "White has slight counterplay",
    131: "Black has slight counterplay",
    132: "White has moderate counterplay",
    133: "Black has moderate counterplay",
    134: "White has decisive counterplay",
    135: "Black has decisive counterplay",
    136: "White has moderate time control pressure",
    137: "Black has moderate time control pressure",
    138: "White has severe time control pressure",
    139: "Black has severe time control pressure"
}

def load_json_from_api(url, header=None, params = None, fmt = None):
    response = requests.get(url, headers=header, params=params)
    print(url)
    if response.status_code == 200:
        
        #return response
        if fmt == None:
            json_data = response.json()
        else:
            json_data = response.json(cls=fmt)
        return json_data
    else:
        print(f"Error: Failed to retrieve data from the API. Status Code {response.status_code}")
        return None

def date_to_epoch(date_string):
    if date_string:
        date_object = datetime.strptime(date_string, "%Y-%m-%d")
        epoch_time = int(time.mktime(date_object.timetuple()))
        return epoch_time
    return None

def get_chess_com_games(username=None, time_formats=None, rated=True, from_date=None, to_date=None, save = False, mesg_label= None):
    
    with open(f".\\config.json", "r") as f:
        config = json.load(f)
        
    if username==None:
        username = config.get("chess_com_user")
    if time_formats == None:
        time_formats = config.get("time_formats")
    if from_date:
        from_year, from_month, _ = [int(d) for d in from_date.split('-')]
        from_epoch = date_to_epoch(from_date)
    if to_date:
        to_year, to_month, _ = [int(d) for d in to_date.split('-')]
        to_epoch = date_to_epoch(to_date)

    imported_dir = config.get("imported_dir")
    header = {'User-Agent': config.get("email")}
    api_url = f"https://api.chess.com/pub/player/{username}/games/archives"
    monthlyURLS = load_json_from_api(api_url, header)
    if monthlyURLS is None:
        return None
    
    monthlyURLS = monthlyURLS.get("archives")
    
    games = []

    for url in monthlyURLS:
        year, month = url.split('/')[-2:]

        if (not from_date or (int(year) > from_year or (int(year) == from_year and int(month) >= from_month))) and \
           (not to_date or (int(year) < to_year or (int(year) == to_year and int(month) <= to_month))):
            monthGames = load_json_from_api(url, header)
            games.extend(monthGames.get("games"))
            prints(f"{len(games)} ingested so far, Up to date {'/'.join(url.split('/')[-2:])}", mesg_label)
    if rated:
        games = list(filter(lambda g: g.get("rated") == True and g.get("time_class") in time_formats and g.get("rules") == "chess" and g.get("initial_setup") == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", games))
    else:
        games = list(filter(lambda g: g.get("time_class") in time_formats and g.get("rules") == "chess" and g.get("initial_setup") == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", games))

    lower_username=username.lower()
    for g in games:
        g["variant"] = "standard" if g.get("rules") == "chess" else g.get("rules")
        g["time_control"]=g.pop("time_class")
        g["end_fen"]=g.pop("fen")
        g["id"] = g.pop("uuid")
        g["platform"] = "chess.com"
        g["player_color"] = "white" if g.get("white").get("username").lower() == lower_username else "black"
    
    if save:
        with open(f".\\{imported_dir}\\chess_com_{username}.json", "w") as f:
            json.dump(games,f)
    
    return games

def load_games (file_name, filtered_games = None):
    with open(".\\config.json", "r") as f:
        config = json.load(f)

    imported_dir = config.get("imported_dir")

    if file_name.endswith(".json"):
        full_file_path = f"{imported_dir}\\{file_name}"
        with open(full_file_path, "r") as f:
            games_dict = json.load(f)
        if filtered_games:
            return games_dict.get(filtered_games,[])
        games = games_dict.get("white_games",[])
        games.extend(games_dict.get("black_games",[]))
        games.extend(games_dict.get("other_games",[]))
        return games

def load_study (file_name):
    with open(".\\config.json", "r") as f:
        config = json.load(f)

    imported_dir = config.get("study_dir")

    if file_name.endswith(".json"):
        full_file_path = f"{imported_dir}\\{file_name}"
        with open(full_file_path, "r") as f:
            return json.load(f)
        

def sanitize_png_moves(games, mesg_label=None, sub_mesg_label=None):

    prints(f"Santizing the moves of {len(games)} games", mesg_label)
    if not isinstance(games,list):
        games = [games]
    for i,g in enumerate(games):
        if i %500 == 0:
            prints(f"Santized {i}/{len(games)} games", sub_mesg_label)
        pgn = g["pgn"]
        tags_and_move_numbers = re.compile(r"\[[^\]]+\]|\{[^\}]*\}|\d+\.+")
        clean_png = re.sub(tags_and_move_numbers, '', pgn).strip()
        moves = [i for i in clean_png.split(" ") if i]
        if moves and moves[-1] == "1/2-1/2" or moves[-1] == "1-0" or moves[-1] == "0-1" or moves[-1] == '*':
            g["result"] = moves.pop(-1)
        g["clean_moves"] = moves
    

def add_fen_list(games, mesg_label=None, sub_mesg_label=None):
    prints("Adding FENs to each position in every game (Used for building trees and analysis later)",mesg_label)
    num_games = len(games)
    for i,g in enumerate(games):
        if i%500 == 0:
            prints(f"Adding FENs for {i}/{num_games}",sub_mesg_label)
        b = Board()
        moves = g.get("clean_moves",None)
        
        if moves:
            g["move_fen_list"] = [(move, b.make_algebraic_move(move)) for move in moves]
       

def get_lichess_games(username=None, time_formats=None, rated = True, from_epoch = None, to_epoch=None, save=False, mesg_label=None, sub_mesg_label=None):
        
    with open(f".\\config.json", "r") as f:
        config = json.load(f)
    if username==None:
        username = config.get("lichess_user")
    if time_formats == None:
        time_formats = config.get("time_formats")
    imported_dir = config.get("imported_dir")
    if config.get("lichess_token",""):
        header = {"Authorization": f"Bearer {config.get('lichess_token')}",
             "Accept": "application/x-ndjson"}
    else:
        header = {"Accept": "application/x-ndjson"}

    if username==None:
        username = config.get('user')

    api_url = f"https://lichess.org/api/games/user/{username}"
    
    params = {
        "pgnInJson": True,
        "lastFen":True,
        "perfType":",".join(time_formats)
    }
    if from_epoch:
        params["since"] = from_epoch
    if to_epoch:
        params["until"] = to_epoch
    if rated:
        params["rated"] = rated
     
    prints("This may take a few minutes...\nApproximately 60 games/sec if you inputted a token or 20 games/ sec otherwise", mesg_label)
    games = load_json_from_api(api_url,header=header, params = params, fmt = ndjson.Decoder)
    
    lower_username=username.lower()
    for g in games:
        g["end_time"] = g.get("lastMoveAt")//1000
        g["time_class"] = g.get("speed")
        g["winner"] = g.get("winner", "draw")
        players = g.pop("players", None)
        
        g["white"] = players.get("white")
        g["white"]["username"] = g.get("white").pop("user", {}).get("id","GUEST")
        g["black"] = players.get("black")
        g["black"]["username"] = g.get("black").pop("user", {}).get("id","GUEST")
        g["platform"] = "lichess"
        g["player_color"] = "white" if g.get("white").get("username").lower() == lower_username else "black"
        
    
    if save: 
        with open(f".\\{imported_dir}\\lc_{username}_all_games.json", "w") as f:
            json.dump(games,f)
   
    return games


def import_pgn_file(file_path, username=None, save = False):
    
    with open(f".\\config.json", "r") as f:
        config = json.load(f)
    if username==None:
        username = config.get('name')
    imported_dir = config.get("imported_dir")
    file_path = os.path.normpath(file_path)
    with open(f"{file_path}{'.pgn' if not file_path.endswith('.pgn') else''}", "r") as f:
        lines = f.readlines()
    games = []
    g = None
    pgn=""
    for line in lines:
        pgn+=f"{line}\n"
        if line.startswith("[Event"):
            if g!= None:
                g["pgn"]=pgn
                g["moves"] = g.get('moves','').strip()
                games.append(g)
                pgn=""
            g=dict()
        if line[0] == "[":
            tag = line[1:].split('"')
            tag[0]=tag[0].lower()
            g[tag[0]] = tag[1]
            if (tag[0] == "white" or tag[0] == "black") and tag[1] == username:
                g["player_color"] = tag[0]
        else:
            g["moves"]=f"{g.get('moves','')}{line}\n"
    if g!= None:
        g["pgn"]=pgn
        g["moves"] = g.get('moves','').strip()
        games.append(g)
        
    file_name = file_path.split("\\")[-1]
    if save:
        with open(f".\\{imported_dir}\\pgn_{file_name.split('.')[0]}_all_games.json", "w") as f:
            json.dump(games,f)
        
    return games


def ingest_pgns(pgn_files=None, username=None, mesg_label=None, move_file = True, seperate = False, study=False):
    with open(f".\\config.json", "r") as f:
        config = json.load(f)
    if pgn_files == None:
        pgn_files = config.get("ingest_dir")
    ingested_dir = config.get("ingested_dir", None)
    games = []

    if os.path.isdir(pgn_files):
        pgn_files = glob.glob(os.path.join(pgn_files, "*.pgn"))
        if not pgn_files:
            prints(f"{pgn_files} is empty or contains no .pgn files", mesg_label)
        for pgn_file in pgn_files:
            prints(f"Ingesting {pgn_file}", mesg_label)
            if seperate:
                games.append((pgn_file.split("\\")[-1][:-4],import_pgn_file(pgn_file, username)))
            else:
                games.extend(import_pgn_file(pgn_file, username))
            prints(f"Done ingesting {pgn_file}", mesg_label)
            if move_file and ingested_dir:
                if not os.path.exists(ingested_dir):
                    os.makedirs(ingested_dir)
                file_name = pgn_file.split('\\')[-1]
                move_file = f"{ingested_dir}\\{file_name}"
                prints(f"Moving to {move_file}", mesg_label)
                shutil.move(pgn_file, ingested_dir)
        
        
    elif os.path.isfile(pgn_files) and pgn_files.lower().endswith(".pgn"):
        prints(f"Ingesting {pgn_files}", mesg_label)
        
        if study: 
            games = [(pgn_files.split("\\")[-1][:-4],import_pgn_file(pgn_files))]
        else:
            games = [import_pgn_file(pgn_files)]
        prints(f"Done ingesting {pgn_files}", mesg_label)

        if move_file and ingested_dir:
            if not os.path.exists(ingested_dir):
                os.makedirs(ingested_dir)
            file_name = pgn_files.split('\\')[-1]
            move_file = f"{ingested_dir}\\{file_name}"
            prints(f"Moving to {move_file}", mesg_label)
            shutil.move(pgn_files, ingested_dir)
    

    return games
    
def prints(mesg, mesg_label=None):
    print(mesg)
    if mesg_label:
        mesg_label.config(text=mesg)

def update_imported(file_name, add_fens=True):
    with open(f".\\config.json", "r") as f:
        config = json.load(f)
    imported_dir = config.get("imported_dir")
    full_file_path = f"{imported_dir}\\{file_name}.json"
    if os.path.isfile(full_file_path):
        with open(full_file_path, "r") as f:
            games_dict = json.load(f)
        games = games_dict.get("white_games")
        games.extend(games_dict.get("black_games"))
        games.extend(games_dict.get("other_games"))

    if add_fens:
        add_fen_list(games)

    dump_games(games, file_name=file_name)

def dump_games(games, file_name=None,  mesg_label=None, sub_mesg_label=None, filter_games = True):

    with open(f".\\config.json", "r") as f:
        config = json.load(f)
    imported_dir = config.get("imported_dir")
    if not os.path.exists(imported_dir):
        os.makedirs(imported_dir)

    white_games = list(filter(lambda g: g.get("player_color","") == "white", games))
    black_games = list(filter(lambda g: g.get("player_color","") == "black", games))
    other_games = list(filter(lambda g: g.get("player_color","") == "", games))
    
    prints("Saving Files",mesg_label)
    games_json = {"white_games":white_games,"black_games":black_games, "other_games":other_games}
    fp= f".\\{imported_dir}\\{file_name}.json"
    prints(f"Imported {len(games)} in total, saving to {fp}",sub_mesg_label)
    with open(fp, "w") as f:
        json.dump(games_json,f)
    prints(f"Saved to {fp}",sub_mesg_label)

def dump_study(study, file_name=None,  mesg_label=None, sub_mesg_label=None):
    with open(f".\\config.json", "r") as f:
        config = json.load(f)

    imported_dir = config.get("study_dir")
    if not os.path.exists(imported_dir):
        os.makedirs(imported_dir)
    
    prints("Saving Files",mesg_label)
    
    fp= f".\\{imported_dir}\\{file_name}" if file_name.endswith(".json") else f".\\{imported_dir}\\{file_name}.json"
    prints(f"Imported to {fp}",sub_mesg_label)
    with open(fp, "w") as f:
        json.dump(study,f)
    prints(f"Saved to {fp}",sub_mesg_label)

def import_all_games(file_name=None, chess_com_user=None, lichess_user=None, pgns_files=None, time_formats = None, append=True, rated=True, from_date=None, to_date=None, mesg_label=None, sub_mesg_label=None):
    with open(f".\\config.json", "r") as f:
        config = json.load(f)
    
    if file_name == None:
        file_name = f"{config.get('name')}"
    if chess_com_user == None:
        chess_com_user = config.get("chess_com_user", False)
    if lichess_user == None:
        lichess_user = config.get("lichess_user", False)
    if pgns_files == None or pgns_files == "":
        pgns_files = config.get("ingest_dir", False)
    
    imported_dir = config.get("imported_dir")
    full_file_path = f"{imported_dir}\\{file_name}.json"
    if os.path.isfile(full_file_path) and append:
        prints(f"File {full_file_path} is already found so appending games", mesg_label)
        with open(full_file_path, "r") as f:
            games_dict = json.load(f)
            games = games_dict.get("white_games")
            games.extend(games_dict.get("black_games",[]))
            games.extend(games_dict.get("other_games",[]))
    else:
        games = []

    if chess_com_user:
        prints(f"Ingesting Chess.com Games from user {chess_com_user}", mesg_label)
        games.extend(get_chess_com_games(chess_com_user,time_formats = time_formats, rated=rated, from_date=from_date, to_date=to_date, mesg_label=sub_mesg_label))
    if lichess_user:
        prints(f"Ingesting Lichess Games from user {lichess_user}", mesg_label)
        from_epoch = date_to_epoch(from_date)
        to_epoch = date_to_epoch(to_date)

        games.extend(get_lichess_games(lichess_user,time_formats = time_formats, rated=rated, from_epoch=from_epoch, to_epoch=to_epoch, mesg_label=sub_mesg_label))
    if pgns_files:
        prints(f"Ingesting Pgns files {pgns_files}",mesg_label)
        games.extend(ingest_pgns(pgns_files,mesg_label=sub_mesg_label))  
    
    sanitize_png_moves(games,mesg_label=mesg_label, sub_mesg_label=sub_mesg_label)
    add_fen_list(games,mesg_label=mesg_label, sub_mesg_label=sub_mesg_label)

    dump_games(games, file_name=file_name,  mesg_label=mesg_label, sub_mesg_label=sub_mesg_label)
    
    return games

def import_studies(file_name=None, study_as='w', seperate=True, pgns_files=None, mesg_label=None, sub_mesg_label=None):
    with open(f".\\config.json", "r") as f:
        config = json.load(f)
    
    if pgns_files == None or pgns_files == "":
        pgns_files = config.get("ingest_study_dir", False)

    if pgns_files:
        prints(f"Ingesting Pgns files {pgns_files}",mesg_label)
        for name, study in ingest_pgns(pgns_files, mesg_label=sub_mesg_label, seperate=seperate, study=True):
            study = {"name":name, "study_as":study_as, "studies":study}
            sanitize_png_moves(study.get("studies"))
            if file_name:
                name = file_name
            dump_study(study, file_name=name,  mesg_label=mesg_label, sub_mesg_label=sub_mesg_label)

    return study
    

if __name__ == "__main__":
    #games = import_all_games()
    #import_studies()
    print()
    games = get_lichess_games()
    print("Done")