import random

N = 9
CLUES = {"1": 40, "2": 32, "3": 26}

def candidates(grid, r, c):
    used = set(grid[r]) | {grid[i][c] for i in range(N)}
    br, bc = 3 * (r // 3), 3 * (c // 3)
    used |= {grid[i][j] for i in range(br, br + 3) for j in range(bc, bc + 3)}
    return [v for v in range(1, 10) if v not in used]

def find_empty(grid):
    """Pick the empty cell with the fewest candidates (fast solving)."""
    best, best_opts = None, None
    for r in range(N):
        for c in range(N):
            if grid[r][c] == 0:
                opts = candidates(grid, r, c)
                if best is None or len(opts) < len(best_opts):
                    best, best_opts = (r, c), opts
                    if len(opts) <= 1:
                        return best, best_opts
    return best, best_opts

def fill(grid):
    """Fill the grid with a random complete solution."""
    cell, opts = find_empty(grid)
    if cell is None:
        return True
    r, c = cell
    random.shuffle(opts)
    for v in opts:
        grid[r][c] = v
        if fill(grid):
            return True
    grid[r][c] = 0
    return False

def count_solutions(grid, limit=2):
    cell, opts = find_empty(grid)
    if cell is None:
        return 1
    r, c = cell
    total = 0
    for v in opts:
        grid[r][c] = v
        total += count_solutions(grid, limit - total)
        if total >= limit:
            break
    grid[r][c] = 0
    return total

def make_puzzle(clues):
    """Return (puzzle, solution) where the puzzle has exactly one solution."""
    solution = [[0] * N for _ in range(N)]
    fill(solution)
    puzzle = [row[:] for row in solution]
    cells = [(r, c) for r in range(N) for c in range(N)]
    random.shuffle(cells)
    filled = N * N
    for r, c in cells:
        if filled <= clues:
            break
        saved = puzzle[r][c]
        puzzle[r][c] = 0
        if count_solutions([row[:] for row in puzzle]) != 1:
            puzzle[r][c] = saved
        else:
            filled -= 1
    return puzzle, solution

def render(grid, given, conflicts=frozenset()):
    RESET, DIM, BOLD, RED = "\033[0m", "\033[2m", "\033[1m", "\033[31m"
    lines = ["", "     1 2 3   4 5 6   7 8 9", "   +-------+-------+-------+"]
    for r in range(N):
        parts = []
        for c in range(N):
            v = grid[r][c]
            if v == 0:
                s = f"{DIM}.{RESET}"
            elif (r, c) in conflicts:
                s = f"{RED}{v}{RESET}"
            elif given[r][c]:
                s = f"{BOLD}{v}{RESET}"
            else:
                s = str(v)
            parts.append(s)
        row = " | ".join(" ".join(parts[i:i + 3]) for i in range(0, 9, 3))
        lines.append(f" {r + 1} | {row} |")
        if r % 3 == 2:
            lines.append("   +-------+-------+-------+")
    print("\n".join(lines))
    print()

def find_conflicts(grid):
    """Cells that duplicate another value in their row, column or box."""
    bad = set()
    groups = []
    for i in range(N):
        groups.append([(i, j) for j in range(N)])
        groups.append([(j, i) for j in range(N)])
    for br in range(0, N, 3):
        for bc in range(0, N, 3):
            groups.append([(br + i, bc + j) for i in range(3) for j in range(3)])
    for g in groups:
        seen = {}
        for r, c in g:
            v = grid[r][c]
            if v:
                seen.setdefault(v, []).append((r, c))
        for cells in seen.values():
            if len(cells) > 1:
                bad.update(cells)
    return bad

def is_complete(grid):
    return all(v for row in grid for v in row) and not find_conflicts(grid)

HELP = """Commands:
  <row> <col> <value>   place a number, e.g.  3 5 7   (rows/cols/values 1-9)
  c <row> <col>         clear a cell you filled in
  h                     reveal one correct cell (hint)
  check                 highlight mistakes (cells that break the rules)
  s                     give up and show the solution
  help                  show this message
  q                     quit
"""

def choose_difficulty():
    print("=== SUDOKU ===")
    print("1) Easy\n2) Medium\n3) Hard")
    while True:
        choice = input("Select difficulty [1-3]: ").strip()
        if choice in CLUES:
            return CLUES[choice]

def play():
    puzzle, solution = make_puzzle(choose_difficulty())
    given = [[v != 0 for v in row] for row in puzzle]
    grid = [row[:] for row in puzzle]
    hints = 0
    print(HELP)

    while True:
        render(grid, given)
        raw = input("> ").strip().lower().split()
        if not raw:
            continue
        cmd = raw[0]

        if cmd in ("q", "quit"):
            raise KeyboardInterrupt
        if cmd == "help":
            print(HELP)
        elif cmd == "check":
            bad = find_conflicts(grid)
            wrong = {(r, c) for r in range(N) for c in range(N)
                     if grid[r][c] and not given[r][c] and grid[r][c] != solution[r][c]}
            render(grid, given, bad | wrong)
            print("No mistakes so far!" if not (bad or wrong)
                  else "Cells in red are wrong or break the rules.")
        elif cmd == "h":
            empties = [(r, c) for r in range(N) for c in range(N) if grid[r][c] == 0]
            if not empties:
                print("No empty cells left.")
                continue
            r, c = random.choice(empties)
            grid[r][c] = solution[r][c]
            given[r][c] = True
            hints += 1
            print(f"Hint: row {r + 1}, column {c + 1} is {solution[r][c]}.")
        elif cmd == "s":
            render(solution, given)
            print("Solution shown. Better luck next time!")
            return
        elif cmd == "c" and len(raw) == 3 and all(x.isdigit() for x in raw[1:]):
            r, c = int(raw[1]) - 1, int(raw[2]) - 1
            if not (0 <= r < N and 0 <= c < N):
                print("Row and column must be 1-9.")
            elif given[r][c]:
                print("That cell is part of the puzzle and can't be cleared.")
            else:
                grid[r][c] = 0
        elif len(raw) == 3 and all(x.isdigit() for x in raw):
            r, c, v = int(raw[0]) - 1, int(raw[1]) - 1, int(raw[2])
            if not (0 <= r < N and 0 <= c < N and 1 <= v <= 9):
                print("Row, column and value must each be 1-9.")
            elif given[r][c]:
                print("That cell is part of the puzzle and can't be changed.")
            else:
                grid[r][c] = v
                if is_complete(grid):
                    render(grid, given)
                    extra = f" using {hints} hint(s)" if hints else " with no hints"
                    print(f"🎉 Solved{extra}!")
                    return
        else:
            print("Unknown command. Type 'help' to see the options.")

def main():
    try:
        while True:
            play()
            if input("Play again? [y/N]: ").strip().lower() != "y":
                break
    except (KeyboardInterrupt, EOFError):
        print("\nThanks for playing!")

if __name__ == "__main__":
    main()
