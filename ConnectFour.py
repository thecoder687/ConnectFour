import math
import random

# TODO: maybe let players customize board size later? nah keep it standard for now
ROWS = 6
COLS = 7 

EMPTY = " "
P1 = "X"
P2 = "O"

def new_board():
    # making the grid
    b = []
    for i in range(ROWS):
        row = []
        for j in range(COLS):
            row.append(EMPTY)
        b.append(row)
    return b

def valid_moves(board):
    # just checking top row
    valid = []
    for c in range(COLS):
        if board[0][c] == EMPTY:
            valid.append(c)
    return valid

def drop(board, col, piece):
    # Drop a piece into a column. Returns the row it landed in.
    # start from the bottom and go up
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == EMPTY:
            board[r][col] = piece
            return r
    raise ValueError("Column is full!! how did this happen")

def undo(board, col):
    # undo move helper for minimax
    for r in range(ROWS):
        if board[r][col] != EMPTY:
            board[r][col] = EMPTY
            return

def winner(board):
    # Return the winning piece, or None.
    # checking all directions... kinda messy but it works lol
    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if p == EMPTY:
                continue
            
            # check right
            if c + 3 < COLS and board[r][c+1] == p and board[r][c+2] == p and board[r][c+3] == p:
                return p
            # check down
            if r + 3 < ROWS and board[r+1][c] == p and board[r+2][c] == p and board[r+3][c] == p:
                return p
            # check diagonal down-right
            if r + 3 < ROWS and c + 3 < COLS and board[r+1][c+1] == p and board[r+2][c+2] == p and board[r+3][c+3] == p:
                return p
            # check diagonal up-right
            if r - 3 >= 0 and c + 3 < COLS and board[r-1][c+1] == p and board[r-2][c+2] == p and board[r-3][c+3] == p:
                return p
                
    return None

def is_full(board):
    if len(valid_moves(board)) == 0:
        return True
    return False

def print_board(board):
    print("\n")
    print("  " + "   ".join(str(c + 1) for c in range(COLS)))
    for r in board:
        print("| " + " | ".join(r) + " |")
    print("+" + "---+" * COLS)
    print()


# ---------- AI stuff (minimax) ----------

def score_window(window, piece):
    # scoring heuristic windows
    if piece == P2:
        opp = P1
    else:
        opp = P2
        
    s = 0
    if window.count(piece) == 4:
        s += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        s += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        s += 2
        
    if window.count(opp) == 3 and window.count(EMPTY) == 1:
        s -= 4
        
    return s

def evaluate(board, piece):
    score = 0
    
    # prefer center column
    centre_column = []
    for r in range(ROWS):
        centre_column.append(board[r][COLS // 2])
    score += centre_column.count(piece) * 3
    
    for r in range(ROWS):
        for c in range(COLS):
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                er, ec = r + 3 * dr, c + 3 * dc
                if 0 <= er < ROWS and 0 <= ec < COLS:
                    window = []
                    for i in range(4):
                        window.append(board[r + i * dr][c + i * dc])
                    score += score_window(window, piece)
    return score

def minimax(board, depth, alpha, beta, maximizing, me):
    if me == P2:
        opp = P1
    else:
        opp = P2
        
    w = winner(board)
    if w == me:
        return None, 1000000 + depth
    if w == opp:
        return None, -1000000 - depth
    if is_full(board) or depth == 0:
        return None, evaluate(board, me)

    # Search centre columns first for better pruning.
    moves = sorted(valid_moves(board), key=lambda c: abs(c - COLS // 2))
    best_col = moves[0] # just pick something initially

    if maximizing:
        value = -math.inf
        for col in moves:
            drop(board, col, me)
            _, s = minimax(board, depth - 1, alpha, beta, False, me)
            undo(board, col)
            if s > value:
                value = s
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value
    else:
        value = math.inf
        for col in moves:
            drop(board, col, opp)
            _, s = minimax(board, depth - 1, alpha, beta, True, me)
            undo(board, col)
            if s < value:
                value = s
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value

def computer_move(board, piece, depth):
    col, score_val = minimax(board, depth, -math.inf, math.inf, True, piece)
    return col


# ---------- Game stuff ----------

def ask_column(board, name, piece):
    while True:
        raw = input(f"{name} ({piece}), choose a col (1-{COLS}) or 'q' to quit: ").strip().lower()
        if raw == 'q' or raw == 'quit':
            raise KeyboardInterrupt
            
        if not raw.isdigit():
            print("Dude, enter a valid number.")
            continue
            
        col = int(raw) - 1
        if col < 0 or col >= COLS:
            print(f"Out of bounds! Choose between 1 and {COLS}.")
            continue
            
        if col not in valid_moves(board):
            print("That column is full! Pick another one.")
            continue
            
        return col

def choose_mode():
    print("\n--- CONNECT 4 ---")
    print("1. 2 Players")
    print("2. vs Computer (Easy)")
    print("3. vs Computer (Med)")
    print("4. vs Computer (Hard)")
    
    while True:
        choice = input("Select mode (1-4): ").strip()
        if choice == "1":
            return None
        elif choice == "2":
            return 2 # depth 2
        elif choice == "3":
            return 4 # depth 4
        elif choice == "4":
            return 6 # depth 6 (maybe slow? lets see)
        else:
            print("Invalid choice, try again.")

def play():
    depth = choose_mode()
    board = new_board()
    
    p2_name = "Computer" if depth is not None else "Player 2"
    players = [(P1, "Player 1"), (P2, p2_name)]
    
    turn = 0 # 0 for P1, 1 for P2/CPU
    
    while True:
        print_board(board)
        piece, name = players[turn]

        if depth is not None and piece == P2:
            print("AI is thinking hard...")
            col = computer_move(board, piece, depth)
            print(f"AI drops piece in column {col + 1}")
        else:
            col = ask_column(board, name, piece)

        drop(board, col, piece)

        if winner(board) is not None:
            print_board(board)
            print(f"OMG! {name} ({piece}) won the game!! 🏆")
            return
            
        if is_full(board):
            print_board(board)
            print("Stalemate! It's a draw.")
            return
            
        # switch turn
        if turn == 0:
            turn = 1
        else:
            turn = 0

def main():
    try:
        while True:
            play()
            again = input("Play again? (y/n): ").strip().lower()
            if again != 'y':
                print("Bye bye!")
                break
    except (KeyboardInterrupt, EOFError):
        print("\nExiting game... See ya!")

if __name__ == "__main__":
    main()
