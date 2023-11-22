import import_games
from board import Board
import tree
import random as rand


class MemorizationGame:
    QUIT_COMMANDS = ("quit", 'q', "exit")
    HINT_COMMAND = ('h',"hint")
    ANSWER_COMMAND = ('a',"answer")

    def __init__ (self, study_trees):
        self.study_trees = study_trees
        self.visited_nodes=[]
        self.testing_nodes = []
        self.current_test_node = None
        self.current_subtitle = ""
        self.current_board = None
        self.valid_moves = None
        self.from_coords = []
        self.to_coords = []
        for study_tree in study_trees:
            self.testing_nodes.extend([(node,study_tree.name) for node in study_tree.get_test_nodes()])

    def run_game_cl(self):
        while True:
            self.next_random_node()
            print(self.current_subtitle)
            self.current_board.display(players_perspective=True)

            while True:
                user_input = input("Your move (or enter 'hint', 'answer', 'quit' to exit): ").strip().lower()
                
                if user_input in MemorizationGame.QUIT_COMMANDS:
                    print("Game ended. Goodbye!")
                    return
                elif user_input in MemorizationGame.HINT_COMMAND:
                    
                    print(self.get_hint())
                    continue
                elif user_input in MemorizationGame.ANSWER_COMMAND:
                    print(f"The correct move(s): {', '.join(self.valid_moves)}")
                    input("Press enter to get next")

                    break
                
                if user_input in self.valid_moves:
                    print("Correct!")
                    notes = "\n".join(self.current_test_node.notes)
                    print(f"Notes:\n{notes}")
                    if len(self.valid_moves)>1:
                        print(f"Also valid moves in study:{', '.join([move for move in self.valid_moves if move != user_input])}")
                    input("Press enter to get next")
                    break
                else:
                    print("Incorrect. Try again, or ask for a 'hint' or the 'answer'.")
            
    def get_answer(self):
        return f"The correct move(s): {', '.join(self.valid_moves)}"
    def get_notes(self):
        return "\n".join(self.current_test_node.notes)
    def check_answer(self, move):
        if move in self.valid_moves:
            if len(self.valid_moves)>1:
                return f"Correct! Also valid moves in study:{', '.join([move for move in self.valid_moves if move != move])}"
            return "Correct!"          
        return "Incorrect. Try again, or ask for a 'hint' or the 'answer'"
    def get_hint(self):
        return f"Hint: The move(s) starts with {', '.join([move[0] for move in self.valid_moves])}..."

    def return_to_last_node(self):
        self.current_test_node = self.visited_nodes[-2]
        self.current_subtitle = f"From {self.current_study_tree_name}: ({', '.join([s.get('event','') for s in self.current_test_node.studies])})"
        self.current_board =  Board(self.current_test_node.fen)
        self.valid_moves = [move for _, move in self.current_test_node.children]
        self.from_coords = [self.current_board.get_to_from_square_algebraic_move(move,return_bitboard=False)[0] for move in self.valid_moves]
        self.to_coords = [self.current_board.get_to_from_square_algebraic_move(move,return_bitboard=False)[1] for move in self.valid_moves]

    def next_random_node(self):
        
        self.current_test_node, self.current_study_tree_name = rand.choice(self.testing_nodes)
        self.visited_nodes.append(self.current_test_node)
        self.current_subtitle = f"From {self.current_study_tree_name}: ({', '.join([s.get('event','') for s in self.current_test_node.studies])})"
        self.current_board =  Board(self.current_test_node.fen)
        self.valid_moves = [move for _, move in self.current_test_node.children]
        self.from_coords = [self.current_board.get_to_from_square_algebraic_move(move,return_bitboard=False)[0] for move in self.valid_moves]
        self.to_coords = [self.current_board.get_to_from_square_algebraic_move(move,return_bitboard=False)[1] for move in self.valid_moves]
        return (self.current_test_node, self.current_study_tree_name)

        
if __name__ == "__main__":
    
    studies = import_games.load_games("Remy Rouyer's Study.json")
    st = tree.StudyTree("Remy Rouyer's Study", studies=studies)
    print("starting game")
    mg = MemorizationGame([st])
    mg.run_game_cl()