from data_structures.Stack import Stack
from data_structures.DynamicArray import DynamicArray
from data_structures.ChainHashMap import ChainHashMap
from data_structures.DoubleList import DoubleList
from data_structures.Tree import Tree, TreeNode
from data_structures.HeapPriorityQueue import HeapPriorityQueue
import time, random

EMPTY, WHITE, BLACK = 0, 1, -1
BOARD_SIZE = 8
ALLOWED_TIME = 2.5
INF = 10**9
PIECE_DICT = {
    WHITE: 'W',
    BLACK: 'B',
    EMPTY: '.'
}
DIRECTION = {WHITE: +1, BLACK: -1}

class Square(object):
    def __init__(self, piece=EMPTY):
        self.piece = piece
    def __str__(self):
        return PIECE_DICT[self.piece]

class Zobrist(object):
    def __init__(self, n=BOARD_SIZE):
        random.seed(1)
        self.n = n
        self.key_table = [[[random.getrandbits(64) for _ in range(3)] for _ in range(n)] for _ in range(n)]
        self.side_key = random.getrandbits(64)
        self.hash = 0
    def update_square(self, row, col, piece):
        self.hash ^= self.key_table[row][col][piece]
    def update_side(self):
        self.hash ^= self.side_key
    def get_hash(self):
        return self.hash
    
class State(object):
    def __init__(self, n=BOARD_SIZE):
        self.n = n
        self.board = DynamicArray(n)
        for row in range(n):
            self.board[row] = DynamicArray(n)
            for col in range(n):
                self.board[row][col] = Square()
        self.to_move = WHITE
        self.history = Stack()
        self.white_list = DoubleList()
        self.black_list = DoubleList()
        self.zobrist = Zobrist()
    def set_piece(self, row, col, piece):
        old = self.board[row][col].piece
        if old:
            self.zobrist.update_square(row, col, old)
        self.board[row][col].piece = piece
        if piece:
            self.zobrist.update_square(row, col, piece)
        if old == WHITE:
            self.white_list.remove((row, col))
        if old == BLACK:
            self.black_list.remove((row, col))
        if piece == WHITE:
            self.white_list.add((row, col))
        if piece == BLACK:
            self.black_list.add((row, col))
    def set_start_position(self):
        for col in range(self.n):
            self.set_piece(0, col, WHITE) 
            self.set_piece(1, col, WHITE)
        for col in range(self.n):
            self.set_piece(self.n-2, col, BLACK)
            self.set_piece(self.n-1, col, BLACK)
    def print_board(self):
        print("\n   " + " ".join(chr(ord('a')+col) for col in range(self.n)))
        print("  " + "--" * self.n)
        for row in range(self.n-1, -1, -1):
            row_str = []
            for col in range(self.n):
                piece = self.board[row][col].piece
                if piece == WHITE:
                    row_str.append("W")
                elif piece == BLACK:
                    row_str.append("B")
                else:
                    if (row+col) % 2 == 0:
                        row_str.append("*")
                    else:
                        row_str.append("■")
            print(f"{row+1:2} " + " ".join(row_str))                    
        print("\n To move: ", "WHITE" if self.to_move == WHITE else "BLACK", "\n")
    def generate_moves(self, player):
        moves = []
        direction = DIRECTION[player]
        pieces = self.white_list if player == WHITE else self.black_list
        for (row, col) in pieces:
            new_row = row + direction
            if 0 <= new_row < self.n and self.board[new_row][col].piece == EMPTY:
                moves.append((row, col, new_row, col))
            for new_col in (col-1, col+1):
                if 0 <= new_col < self.n and self.board[new_row][new_col].piece != player:
                    moves.append((row, col, new_row, new_col))
        return moves
    def make_move(self, move):
        row1, col1, row2, col2 = move
        player = self.board[row1][col1].piece
        captured = self.board[row2][col2].piece
        self.history.push((move, captured, self.to_move, self.zobrist.get_hash()))
        self.set_piece(row1, col1, EMPTY)
        self.set_piece(row2, col2, player)
        self.zobrist.update_side()
        self.to_move = WHITE if self.to_move == BLACK else BLACK
    def undo_move(self):
        move, captured, prev_player, prev_hash = self.history.pop()
        row1, col1, row2, col2 = move
        player = self.board[row2][col2].piece
        self.zobrist.update_side()
        self.to_move = prev_player
        self.set_piece(row2, col2, captured)
        self.set_piece(row1, col1, player)
        self.zobrist.hash = prev_hash
    def winner(self):
        for col in range(self.n):
            if self.board[self.n-1][col].piece == WHITE:
                return WHITE
            if self.board[0][col].piece == BLACK:
                return BLACK
            if len(self.generate_moves(self.to_move)) == 0:
                return WHITE if self.to_move == BLACK else BLACK
        return None

class Heuristic(object):
    def __init__(self, n=8):
        self.n = n
        self.W_EAT = INF
        self.W_ADVANCE = 200
        self.W_MOBILITY = 40
        self.W_MATERIAL = 50
        self.W_OPP_THREAT = 80
        self.W_WINNING_NEXT = 100000
        self.W_PASSED = 400
        self.W_BLOCKED = 50
        self.W_CHAIN = 30
        self.W_TEMPO = 150
        self.W_CENTRAL = 10

    def calculate_score(self, board, player):
        score = 0
        score += self.W_ADVANCE * self.advance(board, player)
        score += self.W_MOBILITY * self.mobility_simple(board, player)
        score -= self.W_OPP_THREAT * self.opponent_threat(board, player)
        score += self.W_MATERIAL * self.material(board, player)
        if self.eat(board, player):
            score += self.W_EAT
        if self.winning_next(board, player):
            score += self.W_WINNING_NEXT
        score += self.W_PASSED * self.passed_pawns(board, player)
        score -= self.W_BLOCKED * self.blocked_pawns(board, player)
        score += self.W_CHAIN * self.pawn_chain(board, player)
        score += self.W_TEMPO * self.tempo(board, player)
        score += self.W_CENTRAL * self.center_proximity(board, player)
        return score

    def advance(self, board, player):
        progress = 0
        for r in range(self.n):
            for c in range(self.n):
                if board[r][c] == player:
                    if player == WHITE:
                        progress += r
                    else:
                        progress += (self.n - 1 - r)
        return progress
    def mobility_simple(self, board, player):
        moves = 0
        dirs = [(DIRECTION[player], 0), (DIRECTION[player], -1), (DIRECTION[player], 1)]
        for r in range(self.n):
            for c in range(self.n):
                if board[r][c] == player:
                    for dr, dc in dirs:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.n and 0 <= nc < self.n and board[nr][nc] != player:
                            moves += 1
        return moves
    def eat(self, board, player):
        opponent = WHITE if player == BLACK else BLACK
        for r in range(self.n):
            for c in range(self.n):
                if board[r][c] == player:
                    for dc in (1, -1):
                        if 0 <= c+dc < self.n and board[r+DIRECTION[player]][c+dc] != player:
                            if opponent == WHITE:
                                if 0 <= c+dc < self.n and board[r+DIRECTION[player]][c+dc] == WHITE:
                                    return False
                            if opponent == BLACK:
                                if 0 <= c+dc < self.n and board[r+DIRECTION[player]][c+dc] == BLACK:
                                    return False
        return True
    def material(self, board, player):
        return sum(1 for r in range(self.n) for c in range(self.n) if board[r][c] == player)
    def opponent_threat(self, board, player):
        opponent = WHITE if player == BLACK else BLACK
        threat = 0
        for r in range(self.n):
            for c in range(self.n):
                if board[r][c] == opponent:
                    if player == WHITE:
                        threat += (self.n - 1 - r)
                    else:
                        threat += r
        return threat
    def winning_next(self, board, player):
        for c in range(self.n):
            if player == WHITE and board[self.n-2][c] == WHITE and board[self.n-1][c] == EMPTY:
                return True
            if player == BLACK and board[1][c] == BLACK and board[0][c] == EMPTY:
                return True
        return False
    def passed_pawns(self, board, player):
        count = 0
        for r in range(self.n):
            for c in range(self.n):
                if board[r][c] == player:
                    cols = [c]
                    if c > 0: cols.append(c-1)
                    if c < self.n-1: cols.append(c+1)
                    if player == WHITE:
                        if all(board[rr][cc] != BLACK for rr in range(0, r) for cc in cols if 0 <= cc < self.n):
                            count += 1
                    else:
                        if all(board[rr][cc] != WHITE for rr in range(r+1, self.n) for cc in cols if 0 <= cc < self.n):
                            count += 1
        return count
    def blocked_pawns(self, board, player):
        blocked = 0
        dr = DIRECTION[player]
        for r in range(self.n):
            for c in range(self.n):
                if board[r][c] == player:
                    moves = 0
                    for dc in (-1, 0, 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.n and 0 <= nc < self.n and board[nr][nc] != player:
                            moves += 1
                    if moves == 0:
                        blocked += 1
        return blocked
    def pawn_chain(self, board, player):
        chains = 0
        dr = DIRECTION[player]
        for r in range(self.n):
            for c in range(self.n):
                if board[r][c] == player:
                    for dc in (-1, 1):
                        nr, nc = r - dr, c + dc
                        if 0 <= nr < self.n and 0 <= nc < self.n and board[nr][nc] == player:
                            chains += 1
        return chains
    def tempo(self, board, player):
        best_white = min((r for r in range(self.n) for c in range(self.n) if board[r][c] == WHITE), default=self.n)
        best_black = min((self.n-1-r for r in range(self.n) for c in range(self.n) if board[r][c] == BLACK), default=self.n)
        if best_white < best_black:
            return 1 if player == WHITE else -1
        elif best_black < best_white:
            return 1 if player == BLACK else -1
        return 0
    def center_proximity(self, board, player):
        mid = self.n//2
        center = [(mid-1, mid-1), (mid-1, mid), (mid, mid-1), (mid, mid)] if self.n % 2 == 0 else [(mid, mid)]
        total = 0
        for r in range(self.n):
            for c in range(self.n):
                if board[r][c] == player:
                    dist = min(abs(r-cr)+abs(c-cc) for cr, cc in center)
                    total += (self.n - dist)
        return total

class Search(object):
    def __init__(self, state, heuristic, allowed_time=ALLOWED_TIME, max_depth=10):
        self.s = state
        self.h = heuristic
        self.allowed_time = allowed_time
        self.max_depth = max_depth
        self.start = 0.0
        self.tt = ChainHashMap()
        self.nodes = 0
        self.tree = Tree()
    def time_exceeded(self):
        return (time.time()-self.start) >= self.allowed_time
    def minimax(self, depth, alpha, beta, player, node=None):
        self.nodes +=1
        if node is None:
            node = TreeNode(element="ROOT")
            self.tree.root = node
        if self.time_exceeded():
            board_pieces = [[self.s.board[r][c].piece for c in range(self.s.n)] for r in range(self.s.n)]
            node.score = self.h.calculate_score(board_pieces, player)
            return node.score, node
        cached = self.tt.get(self.s.zobrist.get_hash())
        if cached is not None:
            cached_eval, cached_depth = cached
            if cached_depth >= depth:
                return cached_eval, node
        winner = self.s.winner()
        if winner is not None:
            val = INF if winner == player else -INF
            node.score = val    
            return val, node
        if depth == 0:
            board_pieces = [[self.s.board[r][c].piece for c in range(self.s.n)] for r in range(self.s.n)]
            val = self.h.calculate_score(board_pieces, self.s.to_move)
            node.score = val
            return val, node
        moves = self.s.generate_moves(self.s.to_move)
        pq = HeapPriorityQueue()
        for move in moves:
            self.s.make_move(move)
            board_pieces = [[self.s.board[r][c].piece for c in range(self.s.n)] for r in range (self.s.n)]
            score = self.h.calculate_score(board_pieces, player)
            self.s.undo_move()
            pq.add(-score, move)
        sorted_moves = []
        while not pq.is_empty():
            _, move = pq.remove_min()
            sorted_moves.append(move)
        best_move = None
        if self.s.to_move == player:
            val = -INF
            for move in sorted_moves:
                self.s.make_move(move)
                child = TreeNode(element=move, parent=node)
                node.children.append(child)
                v, _ = self.minimax(depth-1, alpha, beta, player)
                self.s.undo_move()
                if v > val:
                    val, best_move = v, move
                alpha = max(alpha, val)
                if alpha >= beta:
                    break
        else:
            val = INF
            for move in sorted_moves:
                self.s.make_move(move)
                child = TreeNode(element=move, parent=node)
                node.children.append(child)
                v, _ = self.minimax(depth-1, alpha, beta, player)
                self.s.undo_move()
                if v < val:
                    val, best_move = v, move
                beta = min(beta, val)
                if alpha >= beta:
                    break
        node.score = val
        self.tt.set(self.s.zobrist.get_hash(), val, depth)
        return val, best_move
    def choose_move(self, player):
        self.start = time.time()
        best_move = None
        for depth in range(1, self.max_depth+1):
            if self.time_exceeded():
                break
            val, move = self.minimax(depth, -INF, INF, player)
            if move is not None:
                best_move = move
            if self.time_exceeded():
                break
        return best_move

def coord_to_str(r, c): 
    return f"{chr(ord('a')+c)}{r+1}"

def parse_coord(s, n=BOARD_SIZE):
    s = s.lower(); c = ord(s[0])-97; r = int(s[1:])-1
    return (r, c) if 0 <= c < n and 0 <= r < n else None

def game(human_white):
    s = State()
    h = Heuristic(n=BOARD_SIZE)
    s.set_start_position()
    p = Search(s, h, ALLOWED_TIME, 6)
    s.print_board()
    while True:
        win = s.winner()
        if win:
            print("Winner: ", "WHITE" if win == WHITE else "BLACK")
            break
        if (s.to_move == WHITE and human_white == True) or (s.to_move == BLACK and human_white == False):
            moves = s.generate_moves(s.to_move)
            cols = 4
            for i, m in enumerate(moves):
                move_str = f"{i+1}. {coord_to_str(m[0],m[1])}->{coord_to_str(m[2],m[3])}"
                print(f"{move_str:15}", end="")
                if (i+1) % cols == 0:
                    print()
                    print()
            if len(moves) % cols != 0:
                print()
                print()
            k = input("Choose move: ")
            if k.isdigit():
                k = int(k)-1
            else:
                print("Invalid move input.")
                return
            if k < len(moves)+1: 
                s.make_move(moves[k]); 
            else:
                print("Invalid move, try again!")
                continue
            s.print_board()
        else:
            print("AI is thinking...")
            move = p.choose_move(s.to_move)
            print("AI:", coord_to_str(move[0], move[1]), "->", coord_to_str(move[2], move[3]))
            s.make_move(move)
            s.print_board()

def main():
    while True:
        print("\n===== BREAKTHROUGH ======\n")
        print("="*20)
        print("1. START GAME")
        print("x. EXIT APPLICATION")
        choice = input("Enter your choice: ").strip().lower()
        if choice in ['1', 'x']:
            if choice == '1':
                print("Which side do you want to play?")
                print("1. WHITE")
                print("2. BLACK")
                side_choice = input("Enter your choice: ").strip()
                play_white = True if side_choice == '1' else False
                game(play_white)
            if choice == 'x':
                break
        else:
            print("Invalid option!")
            continue

if __name__ == "__main__":
    main()
