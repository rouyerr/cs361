
import os
import glob
import json
import ndjson
import shutil
import requests
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


def get_chess_com_games(username=None, time_formats=None, save = False, mesg_label= None):
    
    with open(f".\\config.json", "r") as f:
        config = json.load(f)
        
    if username==None:
        username = config.get("chess_com_user")
    if time_formats == None:
        time_formats = config.get("time_formats")
    imported_dir = config.get("imported_dir")
    header = {'User-Agent': config.get("email")}
    api_url = f"https://api.chess.com/pub/player/{username}/games/archives"
    monthlyURLS = load_json_from_api(api_url, header)
    if monthlyURLS is None:
        return None
    
    monthlyURLS = monthlyURLS.get("archives")
    
    games = []

    for url in monthlyURLS:
        month = load_json_from_api(url, header)
        games.extend(month.get("games"))
        prints(f"{len(games)} ingested so far, Up to date {'/'.join(url.split('/')[-2:])}", mesg_label)

    games = list(filter(lambda g: g.get("rated") == True and g.get("time_class") in time_formats and g.get("initial_setup") == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", games))
    for g in games:
        g["variant"] = "standard" if g.get("rules") == "chess" else g.get("rules")
        g["time_control"]=g.pop("time_class")
        g["platform"] = "chess.com"
        g["player_color"] = "white" if g.get("white").get("username") == username else "black"
    

    if save:
        with open(f".\\{imported_dir}\\chess_com_{username}.json", "w") as f:
            json.dump(games,f)
    

    return games


def get_lichess_games(username=None, time_formats=None, save=False, mesg_label=None):
        
    with open(f".\\config.json", "r") as f:
        config = json.load(f)
        
    if username==None:
        username = config.get("lichess_user")
    if time_formats == None:
        time_formats = config.get("time_formats")
    imported_dir = config.get("imported_dir")
    header = {"Authorization": f"Bearer {config.get('lichess_token')}",
             "Accept": "application/x-ndjson"}

    if username==None:
        username = config.get('user')

    api_url = f"https://lichess.org/api/games/user/{username}"
    
    params = {
        "pgnInJson": True,
    }
    
    # params = {
    #     "since": since,
    #     "until": until,
    #     "max": max,
    #     "vs": vs,
    #     "rated": rated,
    #     "perfType": perf_type,
    #     "color": color,
    #     "analysed": analysed,
    #     "moves": moves,
    #     "pgnInJson": "true",
    #     "tags": tags,
    #     "clocks": clocks,
    #     "evals": evals,
    #     "opening": opening,
    #     "ongoing": ongoing,
    #     "finished": finished,
    #     "players": players,
    #     "sort": sort,
    #     "literate": literate,
    # }
    games = load_json_from_api(api_url,header=header, params = params, fmt = ndjson.Decoder)
    
    games = list(filter(lambda g: g.get("rated") == True and g.get("variant")== "standard" and g.get("perf") in time_formats, games))
    prints(len(games), mesg_label)
    for g in games:
        g["end_time"] = g.get("lastMoveAt")
        g["time_class"] = g.get("speed")
        g["winner"] = g.get("winner", "draw")
        players = g.pop("players", None)
        
        g["white"] = players.get("white")
        g["white"]["username"] = g.get("white").pop("user", None).get("id")
        g["black"] = players.get("black")
        g["black"]["username"] = g.get("black").pop("user", None).get("id")
        g["platform"] = "lichess"
        g["player_color"] = "white" if g.get("white").get("username") == username else "black"
        

    #white_games = list(filter(lambda g: g.get("player_color") == "white", games))
    #black_games = list(filter(lambda g: g.get("player_color") == "black", games))
    
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
    with open(f".\\{file_path}{'.pgn' if not file_path.endswith('.pgn') else''}", "r") as f:
        lines = f.readlines()
    games = []
    g = None
    pgn=""
    tag_start_flag = True
    for line in lines:
        pgn+=f"{line}\n"
        if line.startswith("[Event"):
            if g!= None:
                g["pgn"]=pgn
                games.append(g)
                pgn=""
            g=dict()
            tag_start_flag = True
        if line[0] == "[":
            tag = line[1:].split('"')
            tag[0]=tag[0].lower()
            g[tag[0]] = tag[1]
            if (tag[0] == "white" or tag[0] == "black") and tag[1] == username:
                g["player_color"] = tag[0]
            
        elif line.startswith("1."):
            g["moves"]=f"{g.get('moves','')}{line}\n"
    if g!= None:
        g["pgn"]=pgn
        games.append(g)
        pgn=""
    file_name = file_path.split("\\")[-1]
    if save:
        with open(f".\\{imported_dir}\\pgn_{file_name.split('.')[0]}_all_games.json", "w") as f:
            json.dump(games,f)
        
    return games

def ingest_pgns(pgn_files=None, username=None, mesg_label=None):
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
            games.extend(import_pgn_file(pgn_file, username))
            prints(f"Done ingesting {pgn_file}", mesg_label)
            if ingested_dir:
                if not os.path.exists(ingested_dir):
                    os.makedirs(ingested_dir)
                file_name = pgn_file.split('\\')[-1]
                move_file = f"{ingested_dir}\\{file_name}"
                prints(f"Moving to {move_file}", mesg_label)
                shutil.move(pgn_file, ingested_dir)
        
        return games
    if os.path.isfile(pgn_files) and pgn_files.lower().endswith(".pgn"):
        return import_pgn_file(pgn_files)
    
def prints(mesg, mesg_label=None):
    print(mesg)
    if mesg_label:
        mesg_label.config(text=mesg)


def import_all_games(file_name=None, chess_com_user=None, lichess_user=None, pgns_files=None, time_formats = None, append=True, mesg_label=None, sub_mesg_label=None):
    
    with open(f".\\config.json", "r") as f:
        config = json.load(f)
    imported_dir = config.get("imported_dir")
    if not os.path.exists(imported_dir):
        os.makedirs(imported_dir)
    if file_name == None:
        file_name = f"{config.get('name')}"
    if chess_com_user == None:
        chess_com_user = config.get("chess_com_user", False)
    if lichess_user == None:
        lichess_user = config.get("lichess_user", False)
    if pgns_files == None:
        pgns_files = config.get("ingest_dir", False)
    
    full_file_path = f"{imported_dir}\\{file_name}_all_games.json"
    if os.path.isfile(full_file_path) and append:
        prints(f"File {full_file_path} is already found so appending games", mesg_label)
        with open(full_file_path, "r") as f:
            games = json.load(f)
    else:
        games = []
    if chess_com_user:
        prints(f"Ingesting Chess.com Games from user {chess_com_user}", mesg_label)
        games.extend(get_chess_com_games(chess_com_user,time_formats,mesg_label=sub_mesg_label))
    if lichess_user:
        prints(f"Ingesting Lichess Games from user {lichess_user}", mesg_label)
        games.extend(get_lichess_games(lichess_user,time_formats,mesg_label=sub_mesg_label))
    if pgns_files:
        prints(f"Ingesting Pgns files {pgns_files}",mesg_label)
        games.extend(ingest_pgns(pgns_files,mesg_label=sub_mesg_label))  
    #print(games)
    white_games = list(filter(lambda g: g.get("player_color","") == "white", games))
    black_games = list(filter(lambda g: g.get("player_color","") == "black", games))
    
    prints("Saving Files",mesg_label)

    fp_all= f".\\{imported_dir}\\{file_name}_all_games.json"
    prints(f"Imported {len(games)} in total, saving to {fp_all}",sub_mesg_label)
    with open(fp_all, "w") as f:
        json.dump(games,f)
    prints(f"Saved to {fp_all}",sub_mesg_label)

    fp_white = f".\\{imported_dir}\\{file_name}_white_games.json"
    prints(f"Imported {len(white_games)} white games in total, saving to {fp_white}",sub_mesg_label)
    with open(fp_white, "w") as f:
        json.dump(white_games,f)
    prints(f"Saved to {fp_white}",sub_mesg_label)

    fp_black = f".\\{imported_dir}\\{file_name}_black_games.json"
    prints(f"Imported {len(black_games)} black games in total, saving to {fp_black}",sub_mesg_label)
    with open(fp_black, "w") as f:
        json.dump(black_games,f)
    prints(f"Saved to {fp_black}",sub_mesg_label)
    return games
    

if __name__ == "__main__":
    games = import_all_games()
    input()