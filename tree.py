import import_games
from study_board import Board

class Node:
    def __init__(self, fen, from_move = None, parent = None):
        self.fen = fen
        self.parents = [parent]
        self.from_moves = [from_move]
        self.children = []
        self.games = []
        self.results = []
        self.times = []

    def add_child(self, fen, move, game):
        child = Node(fen, from_move = move, parent = self)
        child.add_game(game)
        self.children.append((child, move))
        return child

    def add_game(self, game):
        self.games.append(game)
        player_color = game.get("player_color","")
        result = game.get("result","0-0")
        if result[0:3] == "1/2":
            self.results.append(.5)
        elif player_color == "black" and len(result)==3:
            self.results.append(int(result.split("-")[-1]))
        else:
            self.results.append(int(result.split("-")[0]))
        self.times.append(game.get("end_time"))

    def sort_children(self, count=True):
        if count:
            self.children.sort(key=lambda c: len(c[0].games), reverse=True)
        else:
            self.children.sort(key=lambda c: sorted(c[0].times,reverse=True)[0], reverse=True)

    def win_rates(self):
        return [self.results.count(1)/len(self.games),self.results.count(.5)/len(self.games),self.results.count(0)/len(self.games)]

    def win_rates_str(self):
        win_rates = self.win_rates()
        return f"{win_rates[0]*100:.2f}% wins,  {win_rates[1]*100:.2f}% draws, {win_rates[2]*100:.2f}% losses"

    def __str__(self):
        strs = [f"{self.fen}\nReached {len(self.games)} times, ({self.win_rates_str()})"]
        for child,move in self.children:
            strs.append(f"   {move} : ({len(child.games)}) {child.win_rates_str()}")
        return "\n".join(strs)
        
class StudyNode:
    def __init__(self, fen, test = True, parent=None, from_move = None):
        self.fen = fen
        fen_split = fen.split(" ")
        if parent:
            self.parents_and_moves = [(parent,from_move)]
        self.studies = []
        self.children = []
        self.notes = []
        self.eval = None
        self.players_turn = fen_split[1]
        self.move_number = fen_split[5]
        self.test = test
        
        
    def add_child(self, fen, move, study, test = True):
        child = StudyNode(fen, test = test, parent=self, from_move = move)
        child.studies.append(study)
        self.children.append((child, move))
        return child
    
    def __str__(self):
        strs = [f"{self.fen}\n "]
        for _,move in self.children:
            strs.append(f"   {move} Testing:{self.test}")
        if self.notes:
            notes = '\n'.join(self.notes)
            strs.append(f"\nNotes\n{notes}")
        return "\n".join(strs)

class OpeningTree:
    def __init__(self, is_white=True, open_fen = None, games = None):
        if not open_fen:
            open_fen = Board.STARTING_FEN
        self.root = Node(open_fen)
        self.nodes = {open_fen:self.root}
        self.is_white=is_white
        if games:
            for game in games:
                self.add_game(game)

    def add_game(self, game):
        current_node = self.root
        current_node.add_game(game)

        fen_list = game.get("move_fen_list",None)
        if fen_list:
            for move,fen in fen_list:
                child = self.nodes.get(fen,None)
                if child:
                    if current_node not in child.parents:
                        child.parents.append(current_node)
                        child.from_moves.append(move)
                    child.add_game(game)
                else:
                   child = current_node.add_child(fen, move, game)
                   self.nodes[fen] = child
                current_node = child
        
    def sort_children_nodes(self, count=True):
        for node in self.nodes.values():
            node.sort_children(count)


class StudyTree:
    def __init__(self, study = None, open_fen = None):
        if not open_fen:
            open_fen = Board.STARTING_FEN
        self.name = study.get("name")
        self.root = StudyNode(open_fen)
        self.nodes = {open_fen:self.root}
        self.is_white = study.get("study_as") == 'w' 
        self.color = study.get("study_as")
        self.studies = []
        if study.get("studies"):
            
            for study in study.get("studies"):
                self.add_study(study)
            

    def add_study(self, study):
        if study in self.studies:
            print("study already in")
            return 
        self.studies.append(study)
        current_node = self.root
        moves = study.get("moves","").split(" ")

        current_board = Board(self.root.fen)
        last_fen = self.root.fen
        variation_stack = []
        open_comment = False
        comment = ""
        pop_count = 0
        ply = 0
        if moves:
            for i, move in enumerate(moves[:-1]):
                
                if open_comment or move[0] == '$':
                    if move[0] == "}" or move[0] == '$':
                        pop_count = move.count(')')
                        
                        while pop_count > 0:
                            current_board,current_node = variation_stack.pop()
                            last_fen = current_board.last_fen
                            pop_count -=1
                            move = move[:-1]
                        current_node.notes.append(f"{comment}{import_games.ANNOTATION_NAGS.get(f'{move[1:]}','')}")
                        open_comment = False
                        comment = ''
                        
                    elif comment:
                        comment = f"{comment}{move}"
                    else:
                        comment = move

                elif move == "{":
                    open_comment = True

                elif move[0] == '(':
                    if move.endswith("..."):
                        ply = 2*int(move[1:-3])
                    else:
                        ply = 2*int(move[1:-1]) -1
                    variation_stack.append ((current_board, current_node))
                    current_board = Board(last_fen)
                    current_node = self.nodes.get(last_fen)

                
                elif move[0].isdigit():
                    if move.endswith("..."):
                        ply = 2*int(move[:-3])
                    else:
                        ply = 2*int(move[:-1]) -1

                else:
                    pop_count = move.count(')')
                    if pop_count:
                        move= move[:-pop_count]
                    

                    while move[-1] == '!' or move[-1] == '?':
                        comment=f"{move[-1]}{comment}"
                        move = move[:-1]

                    last_fen = current_node.fen
                    current_fen = current_board.make_algebraic_move(move)
                    test = current_fen.split(" ")[1] == self.color
                    child = self.nodes.get(current_fen, None)
                    if child:
                        if (current_node, move) not in child.parents_and_moves:
                            child.parents_and_moves.append((current_node, move))
                    else:
                        child = current_node.add_child(current_fen,move,study, test = test)
                        self.nodes[current_fen] = child
                    current_node = child
                    if comment:
                        current_node.notes.append(comment)
                        comment=""
                    while pop_count > 0:
                        current_board,current_node = variation_stack.pop()

                        last_fen = current_board.last_fen
                        pop_count -=1
                    ply += 1

    def get_test_nodes(self):
        return [n for n in self.nodes.values() if n.test and n.children]
    


def run_through_game(game):
    b=Board()
    moves = game.get("clean_moves",None)
    if moves:
        for i,m in enumerate(moves):
            
            made = b.make_algebraic_move(m)
            if made == -1:
                input("AHHHHHHHHHH")
            #b.display()
        end_fen = b.export_fen()
        correct_end_fen =  game.get("end_fen", False)
        #print(f"{end_fen}\n{correct_end_fen}")
        if correct_end_fen and correct_end_fen[:min(len(correct_end_fen),len(correct_end_fen))] != end_fen[:min(len(correct_end_fen),len(correct_end_fen))]:
            print("AHHHHHHHH")
            print(game.get("url"))
            print(f"{end_fen[:min(len(correct_end_fen),len(end_fen))]}\n{correct_end_fen[:min(len(correct_end_fen),len(end_fen))]}")
            
    



if __name__ == "__main__":
    #st = StudyTree(import_games.load_study("lichess_study_urusov-gambit_by_remyrouyer_2020.11.21.json"))

    op = OpeningTree()
    games = import_games.load_games("Remy Rouyer.json")
    import_games.sanitize_png_moves(games)
    import_games.add_fen_list(games)
    for g in games:
        op.add_game(g)

