# Slitherlink Solver

A solver for the **Slitherlink** logic puzzle, written in **Python** as a group project for *Artificial Intelligence* at Instituto Superior Técnico (2025/26).

## Approach
- The puzzle is modelled as a **search problem** (`Problem` / `actions` / `result` / `goal_test`).
- **Constraint propagation** before and during search: static rules for 0/3 clues and corners, plus inference that fixes edges forced by cell and vertex constraints after every move.
- **Pruning** of states that close a loop prematurely or violate a clue.
- Solved with depth-first tree search; A*, greedy and RBFS (with a heuristic `h`) are also supported.

## Run
```bash
python3 slitherlink.py < boards/test01.txt
```
Output: for each cell, a 4-bit string with the state of its top, right, bottom and left edges.

`search.py` and `utils.py` are the course's search framework (based on AIMA); `slitherlink.py` is our solution.
