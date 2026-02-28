Sudoku Game
A desktop Sudoku game built with Python and Tkinter, featuring user authentication, SQLite score tracking, global leaderboard, and per-user profile stats. Uses a randomised backtracking algorithm to generate a unique valid puzzle on every run.

Features
User Login & Signup with SHA-256 hashed passwords

Unique puzzle generation using randomised backtracking

15-second countdown before timer starts for fair scoring

Global leaderboard with top 20 scores

Per-user profile with stats by difficulty

Hint system with score penalty

Auto-solver using deterministic backtracking

Wrong cells highlighted in red on Check

Dark / Light theme toggle

Arrow key navigation across the grid

4 difficulty levels: Easy, Medium, Hard, Expert

Project Structure
text
Sudoku_Project/
├── trial.py            # Entry point — run this file
├── ui.py               # All screens: Login, Game, Leaderboard, Profile
├── sudoku_engine.py    # Puzzle generation and solving logic
├── database.py         # SQLite, authentication, scores, profile
└── themes.py           # Light and Dark colour palettes
Score Formula
text
Score = Base(difficulty) + max(0, 300 - time_seconds) - (hints_used x 20)
Difficulty	Base Score
Easy	100
Medium	200
Hard	350
Expert	500
Faster solve = higher time bonus (up to +300)

Each hint = -20 penalty

Using Auto-Solve records no score

Controls
Key / Action	Function
Click a cell	Select it
Type 1–9	Enter number
Backspace / Delete	Clear cell
Arrow keys	Navigate cells
New Game	Generate new puzzle
Check	Highlight wrong cells
Solve	Auto-fill solution
Hint	Reveal one empty cell
Clear	Erase user entries
Theme	Toggle Dark / Light
Getting Started
Requirements: Python 3.8 or above — no external libraries needed.

bash
cd Sudoku_Project
python trial.py
Verify setup:

bash
python -c "import tkinter, sqlite3, random, hashlib; print('All good!')"
Security
Passwords stored as SHA-256 hash — never plain text

Auto-solve does not save a score — prevents leaderboard abuse

