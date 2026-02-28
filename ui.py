
import tkinter as tk
from tkinter import messagebox
import random

from themes import LIGHT, DARK
from database import (init_db, login_user, register_user,
                      save_score, get_leaderboard,
                      get_profile, calculate_score)
from sudoku_engine import SudokuEngine


class SudokuApp:
    def __init__(self, root):
        self.root     = root
        self.root.title("Sudoku")
        self.root.resizable(False, False)

        self.is_dark  = False
        self.theme    = LIGHT
        self.user_id  = None
        self.username = None
        self.engine   = SudokuEngine()

        init_db()
        self._show_login()

    # ═══════════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════════

    def _clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _btn(self, parent, text, cmd, style="primary", **kwargs):
        t   = self.theme
        cfg = {
            "primary": (t["btn_primary"], t["btn_fg"]),
            "accent":  (t["btn_accent"],  "#ffffff"),
            "danger":  (t["btn_danger"],  "#ffffff"),
            "warn":    (t["btn_warn"],    "#ffffff"),
            "flat":    (t["card_bg"],     t["label_fg"]),
        }
        bg, fg = cfg.get(style, cfg["primary"])
        return tk.Button(parent, text=text, command=cmd,
                         font=("Helvetica", 11, "bold"),
                         bg=bg, fg=fg, relief="flat",
                         padx=12, pady=7, cursor="hand2",
                         activebackground=bg, activeforeground=fg,
                         bd=0, **kwargs)

    def _label(self, parent, text, size=11, bold=False, color_key="label_fg"):
        font = ("Helvetica", size, "bold") if bold else ("Helvetica", size)
        return tk.Label(parent, text=text, font=font,
                        bg=parent["bg"],
                        fg=self.theme[color_key])

    # ═══════════════════════════════════════════════════════════════════
    # LOGIN
    # ═══════════════════════════════════════════════════════════════════

    def _show_login(self):
        self._clear()
        self.root.unbind("<Return>")
        t = self.theme
        self.root.configure(bg=t["bg"])

        outer = tk.Frame(self.root, bg=t["bg"])
        outer.pack(expand=True, fill="both", padx=60, pady=40)

        tk.Label(outer, text="SUDOKU", font=("Helvetica", 32, "bold"),
                 bg=t["bg"], fg=t["header_bg"]).pack(pady=(0, 4))
        tk.Label(outer, text="Login to your account",
                 font=("Helvetica", 12),
                 bg=t["bg"], fg=t["status_fg"]).pack(pady=(0, 18))

        card = tk.Frame(outer, bg=t["card_bg"], padx=30, pady=28)
        card.pack(fill="x")

        tk.Label(card, text="Username", font=("Helvetica", 11, "bold"),
                 bg=t["card_bg"], fg=t["label_fg"]).pack(anchor="w")
        self.l_user = tk.Entry(card, font=("Helvetica", 12),
                                bg=t["input_bg"], fg=t["input_fg"],
                                insertbackground=t["input_fg"],
                                relief="flat", bd=4)
        self.l_user.pack(fill="x", pady=(2, 12))

        tk.Label(card, text="Password", font=("Helvetica", 11, "bold"),
                 bg=t["card_bg"], fg=t["label_fg"]).pack(anchor="w")
        self.l_pass = tk.Entry(card, font=("Helvetica", 12),
                                bg=t["input_bg"], fg=t["input_fg"],
                                insertbackground=t["input_fg"],
                                relief="flat", bd=4, show="●")
        self.l_pass.pack(fill="x", pady=(2, 14))

        self.l_err = tk.Label(card, text="", font=("Helvetica", 10),
                               bg=t["card_bg"], fg=t["error_fg"])
        self.l_err.pack()

        self._btn(card, "Login", self._do_login).pack(fill="x", pady=(8, 4))
        self._btn(card, "Create Account", self._show_signup,
                  style="accent").pack(fill="x")

        self.root.bind("<Return>", lambda e: self._do_login())
        self.l_user.focus()

    def _do_login(self):
        u = self.l_user.get().strip()
        p = self.l_pass.get().strip()
        if not u or not p:
            self.l_err.config(text="Please fill in both fields.")
            return
        ok, uid = login_user(u, p)
        if ok:
            self.user_id  = uid
            self.username = u
            self._show_game()
        else:
            self.l_err.config(text="Invalid username or password.")

    def _show_signup(self):
        self._clear()
        t = self.theme
        self.root.configure(bg=t["bg"])

        outer = tk.Frame(self.root, bg=t["bg"])
        outer.pack(expand=True, fill="both", padx=60, pady=40)

        tk.Label(outer, text="SUDOKU", font=("Helvetica", 32, "bold"),
                 bg=t["bg"], fg=t["header_bg"]).pack(pady=(0, 4))
        tk.Label(outer, text="Create a new account",
                 font=("Helvetica", 12),
                 bg=t["bg"], fg=t["status_fg"]).pack(pady=(0, 18))

        card = tk.Frame(outer, bg=t["card_bg"], padx=30, pady=28)
        card.pack(fill="x")

        fields = [("Username", False), ("Password", True),
                  ("Confirm Password", True)]
        self.su_entries = []
        for label, hide in fields:
            tk.Label(card, text=label, font=("Helvetica", 11, "bold"),
                     bg=t["card_bg"], fg=t["label_fg"]).pack(anchor="w")
            e = tk.Entry(card, font=("Helvetica", 12),
                         bg=t["input_bg"], fg=t["input_fg"],
                         insertbackground=t["input_fg"],
                         relief="flat", bd=4,
                         show="●" if hide else "")
            e.pack(fill="x", pady=(2, 12))
            self.su_entries.append(e)

        self.su_err = tk.Label(card, text="", font=("Helvetica", 10),
                                bg=t["card_bg"], fg=t["error_fg"])
        self.su_err.pack()

        self._btn(card, "Sign Up", self._do_signup).pack(fill="x", pady=(8, 4))
        self._btn(card, "← Back to Login", self._show_login,
                  style="flat").pack(fill="x")

        self.root.bind("<Return>", lambda e: self._do_signup())
        self.su_entries[0].focus()

    def _do_signup(self):
        u, p, c = [e.get().strip() for e in self.su_entries]
        if not u or not p or not c:
            self.su_err.config(text="All fields are required.")
            return
        if len(u) < 3:
            self.su_err.config(text="Username must be at least 3 characters.")
            return
        if len(p) < 4:
            self.su_err.config(text="Password must be at least 4 characters.")
            return
        if p != c:
            self.su_err.config(text="Passwords do not match.")
            return
        ok, msg = register_user(u, p)
        if ok:
            messagebox.showinfo("Success", f"Welcome, {u}! Please login.")
            self._show_login()
        else:
            self.su_err.config(text=msg)

    # ═══════════════════════════════════════════════════════════════════
    # GAME
    # ═══════════════════════════════════════════════════════════════════

    def _show_game(self):
        self._clear()
        self.root.unbind("<Return>")

        self.difficulty      = tk.StringVar(value="Medium")
        self.hints_used      = 0
        self.selected        = None
        self.elapsed         = 0
        self.timer_running   = False
        self.timer_id        = None
        self.countdown_active = False
        self.countdown_id    = None

        self.CELL = 56
        self.PAD  = 4

        self._build_game_ui()
        self.generate_puzzle()

    def _build_game_ui(self):
        t = self.theme

        # Header
        self.hdr = tk.Frame(self.root, bg=t["header_bg"], pady=12)
        self.hdr.pack(fill="x")
        tk.Label(self.hdr, text="SUDOKU",
                 font=("Helvetica", 24, "bold"),
                 bg=t["header_bg"], fg=t["header_fg"]).pack(side="left", padx=16)
        rh = tk.Frame(self.hdr, bg=t["header_bg"])
        rh.pack(side="right", padx=16)
        tk.Label(rh, text=f"👤 {self.username}",
                 font=("Helvetica", 11),
                 bg=t["header_bg"], fg=t["header_fg"]).pack(side="left", padx=8)
        self.timer_lbl = tk.Label(rh, text="00:00",
                                   font=("Courier", 18, "bold"),
                                   bg=t["header_bg"], fg=t["header_fg"])
        self.timer_lbl.pack(side="left", padx=8)

        # Difficulty
        self.diff_frm = tk.Frame(self.root, bg=t["bg"], pady=8)
        self.diff_frm.pack(fill="x")
        self._build_diff_bar()

        # Canvas
        self.cv_frm = tk.Frame(self.root, bg=t["bg"])
        self.cv_frm.pack(padx=15, pady=4)
        self._build_canvas()

        # Hints label
        self.hints_lbl = tk.Label(self.root,
                                   text="💡 Hints used: 0",
                                   font=("Helvetica", 10),
                                   bg=t["bg"], fg=t["status_fg"])
        self.hints_lbl.pack()

        # Action buttons
        self.btn_frm = tk.Frame(self.root, bg=t["bg"], pady=8)
        self.btn_frm.pack()
        self._build_action_buttons()

        # Nav buttons
        nav = tk.Frame(self.root, bg=t["bg"], pady=4)
        nav.pack()
        for txt, cmd in [("🏆 Leaderboard", self._show_leaderboard),
                          ("👤 My Profile",  self._show_profile),
                          ("🚪 Logout",       self._logout)]:
            self._btn(nav, txt, cmd, style="flat").pack(side="left", padx=5)

        # Status bar
        self.status_var = tk.StringVar(value="Welcome back!")
        self.status_lbl = tk.Label(self.root,
                                    textvariable=self.status_var,
                                    font=("Helvetica", 10),
                                    anchor="center", pady=5,
                                    bg=t["bg"], fg=t["status_fg"])
        self.status_lbl.pack(fill="x")

    def _build_diff_bar(self):
        t = self.theme
        for w in self.diff_frm.winfo_children():
            w.destroy()
        tk.Label(self.diff_frm, text="Difficulty:",
                 font=("Helvetica", 11, "bold"),
                 bg=t["bg"], fg=t["label_fg"]).pack(side="left", padx=(15, 5))
        for lvl in ("Easy", "Medium", "Hard", "Expert"):
            tk.Radiobutton(self.diff_frm, text=lvl,
                           variable=self.difficulty, value=lvl,
                           font=("Helvetica", 11),
                           bg=t["bg"], activebackground=t["bg"],
                           fg=t["clue_fg"], selectcolor=t["clue_bg"],
                           indicatoron=0, padx=10, pady=3,
                           relief="flat", cursor="hand2").pack(side="left", padx=3)

    def _build_action_buttons(self):
        t = self.theme
        for w in self.btn_frm.winfo_children():
            w.destroy()
        actions = [
            ("⟳ New Game",  self.generate_puzzle,   "primary"),
            ("✔ Check",     self.check_solution,    "accent"),
            ("⚡ Solve",    self.solve_puzzle,      "warn"),
            ("💡 Hint",     self.give_hint,         "accent"),
            ("✕ Clear",    self.clear_grid,        "danger"),
            ("☀/☾ Theme",  self.toggle_theme,      "primary"),
        ]
        for txt, cmd, style in actions:
            self._btn(self.btn_frm, txt, cmd,
                      style=style).pack(side="left", padx=4)

    def _build_canvas(self):
        CELL, PAD = self.CELL, self.PAD
        SIZE = 9 * CELL + 4 * PAD
        t    = self.theme

        self.canvas = tk.Canvas(self.cv_frm,
                                 width=SIZE, height=SIZE,
                                 highlightthickness=2,
                                 highlightbackground=t["box_border"],
                                 bg=t["grid_bg"])
        self.canvas.pack()

        self.rects = [[None]*9 for _ in range(9)]
        self.texts = [[None]*9 for _ in range(9)]

        for row in range(9):
            for col in range(9):
                x1, y1, x2, y2 = self._coords(row, col)
                r = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="white", outline=t["cell_border"], width=1)
                tx = self.canvas.create_text(
                    (x1+x2)//2, (y1+y2)//2,
                    text="", font=("Helvetica", 20, "bold"),
                    fill=t["clue_fg"])
                self.rects[row][col] = r
                self.texts[row][col] = tx

        for i in range(4):
            x = PAD + i * (3*CELL + PAD)
            y = PAD + i * (3*CELL + PAD)
            self.canvas.create_line(x, 0, x, SIZE, width=3,
                                     fill=t["box_border"], tags="box")
            self.canvas.create_line(0, y, SIZE, y, width=3,
                                     fill=t["box_border"], tags="box")

        # Countdown overlay
        self.cd_overlay = self.canvas.create_rectangle(
            0, 0, SIZE, SIZE,
            fill="#000000", stipple="gray25",
            state="hidden", tags="cd")
        self.cd_num = self.canvas.create_text(
            SIZE//2, SIZE//2,
            text="", font=("Helvetica", 90, "bold"),
            fill="#FFFFFF", state="hidden", tags="cd")
        self.cd_sub = self.canvas.create_text(
            SIZE//2, SIZE//2 + 88,
            text="", font=("Helvetica", 13),
            fill="#FFFFFF", state="hidden", tags="cd")

        self.canvas.bind("<Button-1>", self._on_click)
        self.root.bind("<Key>", self._on_key)

    def _coords(self, row, col):
        C, P  = self.CELL, self.PAD
        br, bc = row // 3, col // 3
        x1 = P + bc*(3*C + P) + (col % 3)*C
        y1 = P + br*(3*C + P) + (row % 3)*C
        return x1, y1, x1+C, y1+C

    # ── Theme ────────────────────────────────────────────────────────

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.theme   = DARK if self.is_dark else LIGHT
        t = self.theme
        self.root.configure(bg=t["bg"])
        self.hdr.configure(bg=t["header_bg"])
        for w in self.hdr.winfo_children():
            w.configure(bg=t["header_bg"], fg=t["header_fg"])
        self.diff_frm.configure(bg=t["bg"])
        self.cv_frm.configure(bg=t["bg"])
        self.btn_frm.configure(bg=t["bg"])
        self.hints_lbl.configure(bg=t["bg"], fg=t["status_fg"])
        self.status_lbl.configure(bg=t["bg"], fg=t["status_fg"])
        self.canvas.configure(bg=t["grid_bg"],
                               highlightbackground=t["box_border"])
        self.canvas.itemconfig("box", fill=t["box_border"])
        self._build_diff_bar()
        self._build_action_buttons()
        self._redraw()

    # ── Canvas interaction ───────────────────────────────────────────

    def _on_click(self, ev):
        if self.countdown_active:
            return
        for r in range(9):
            for c in range(9):
                x1, y1, x2, y2 = self._coords(r, c)
                if x1 <= ev.x <= x2 and y1 <= ev.y <= y2:
                    self._select(r, c)
                    return

    def _select(self, row, col):
        if self.selected:
            self._paint(*self.selected)
        self.selected = (row, col)
        self.canvas.itemconfig(self.rects[row][col],
                                fill=self.theme["select_bg"])

    def _on_key(self, ev):
        if self.countdown_active:
            return
        if not self.selected:
            return
        r, c = self.selected
        moves = {"Up":(-1,0),"Down":(1,0),"Left":(0,-1),"Right":(0,1)}
        if ev.keysym in moves:
            dr, dc = moves[ev.keysym]
            self._select((r+dr)%9, (c+dc)%9)
            return
        if self.engine.clues[r][c]:
            return
        if ev.char.isdigit() and ev.char != "0":
            self.engine.grid[r][c] = int(ev.char)
        elif ev.keysym in ("BackSpace", "Delete") or ev.char == "0":
            self.engine.grid[r][c] = 0
        self._paint(r, c)
        self.selected = (r, c)
        self.canvas.itemconfig(self.rects[r][c],
                                fill=self.theme["select_bg"])
        if self.engine.is_complete():
            self._on_win()

    def _paint(self, row, col, fill=None, fg=None):
        t   = self.theme
        val = self.engine.grid[row][col]
        if self.engine.clues[row][col]:
            f  = fill or t["clue_bg"]
            fg = fg   or t["clue_fg"]
            font = ("Helvetica", 20, "bold")
        else:
            f  = fill or t["user_bg"]
            fg = fg   or (t["user_fg"] if val else t["user_bg"])
            font = ("Helvetica", 20)
        self.canvas.itemconfig(self.rects[row][col],
                                fill=f, outline=t["cell_border"])
        self.canvas.itemconfig(self.texts[row][col],
                                text=str(val) if val else "",
                                fill=fg, font=font)

    def _redraw(self):
        for r in range(9):
            for c in range(9):
                self._paint(r, c)

    # ── Countdown ────────────────────────────────────────────────────

    def _start_countdown(self, count=15):
        self.countdown_active = True
        self.canvas.itemconfig("cd", state="normal")
        if count > 0:
            self.canvas.itemconfig(self.cd_num, text=str(count))
            self.canvas.itemconfig(self.cd_sub,
                                    text="Get ready... you cannot type yet!")
            self.status_var.set(f"⏳  Starting in {count} seconds...")
            self.countdown_id = self.root.after(
                1000, lambda: self._start_countdown(count - 1))
        else:
            self.canvas.itemconfig(self.cd_num, text="GO!")
            self.canvas.itemconfig(self.cd_sub, text="")
            self.status_var.set("▶  Go! Timer started.")
            self.countdown_id = self.root.after(700, self._end_countdown)

    def _end_countdown(self):
        self.countdown_active = False
        self.canvas.itemconfig("cd", state="hidden")
        self._start_timer()

    # ── Timer ────────────────────────────────────────────────────────

    def _start_timer(self):
        self._stop_timer()
        self.elapsed = 0
        self.timer_running = True
        self._tick()

    def _tick(self):
        if not self.timer_running:
            return
        m, s = divmod(self.elapsed, 60)
        self.timer_lbl.config(text=f"{m:02d}:{s:02d}")
        self.elapsed += 1
        self.timer_id = self.root.after(1000, self._tick)

    def _stop_timer(self):
        self.timer_running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    # ── Puzzle actions ───────────────────────────────────────────────

    def generate_puzzle(self):
        self._stop_timer()
        if self.countdown_id:
            self.root.after_cancel(self.countdown_id)
        self.countdown_active = False
        self.canvas.itemconfig("cd", state="hidden")
        self.selected   = None
        self.hints_used = 0
        self.hints_lbl.config(text="💡 Hints used: 0")
        self.engine.generate(self.difficulty.get())
        self._redraw()
        self._start_countdown(15)

    def check_solution(self):
        if not self.engine.is_valid():
            self.status_var.set("❌  Errors found — wrong cells highlighted.")
            t = self.theme
            for r in range(9):
                for c in range(9):
                    if (not self.engine.clues[r][c]
                            and self.engine.grid[r][c] != 0
                            and self.engine.grid[r][c] != self.engine.solution[r][c]):
                        self._paint(r, c,
                                    fill=t["error_bg"],
                                    fg=t["error_fg"])
        elif self.engine.is_complete():
            self._on_win()
        else:
            self.status_var.set("✅  No errors yet — keep going!")

    def solve_puzzle(self):
        for r in range(9):
            for c in range(9):
                if not self.engine.clues[r][c]:
                    self.engine.grid[r][c] = 0
        if self.engine.solve():
            self._redraw()
            self._stop_timer()
            self.status_var.set("⚡  Auto-solved! No score recorded.")
        else:
            messagebox.showerror("Error", "No solution found.")

    def give_hint(self):
        if self.countdown_active:
            return
        empties = [(r, c) for r in range(9) for c in range(9)
                   if self.engine.grid[r][c] == 0]
        if not empties:
            self.status_var.set("No empty cells left!")
            return
        r, c = random.choice(empties)
        self.engine.grid[r][c]  = self.engine.solution[r][c]
        self.engine.clues[r][c] = True
        self.hints_used += 1
        self.hints_lbl.config(text=f"💡 Hints used: {self.hints_used}")
        hf = "#E8F5E9" if not self.is_dark else "#1B3A1F"
        hg = "#2E7D32" if not self.is_dark else "#A5D6A7"
        self._paint(r, c, fill=hf, fg=hg)
        self.status_var.set(
            f"💡  Hint: row {r+1}, col {c+1} = {self.engine.solution[r][c]}")

    def clear_grid(self):
        for r in range(9):
            for c in range(9):
                if not self.engine.clues[r][c]:
                    self.engine.grid[r][c] = 0
        self._redraw()
        self.status_var.set("Cleared — original clues kept.")

    def _on_win(self):
        self._stop_timer()
        elapsed = max(self.elapsed - 1, 1)
        score   = calculate_score(self.difficulty.get(),
                                   elapsed, self.hints_used)
        save_score(self.user_id, self.difficulty.get(),
                   elapsed, self.hints_used, score)
        m, s = divmod(elapsed, 60)
        self.status_var.set(
            f"🎉  Solved in {m:02d}:{s:02d}!  Score: {score}")
        messagebox.showinfo("You solved it!",
                            f"Difficulty : {self.difficulty.get()}\n"
                            f"Time       : {m:02d}:{s:02d}\n"
                            f"Hints used : {self.hints_used}\n"
                            f"Score      : {score} pts 🎉")

    # ═══════════════════════════════════════════════════════════════════
    # LEADERBOARD
    # ═══════════════════════════════════════════════════════════════════

    def _show_leaderboard(self):
        self._clear()
        t = self.theme
        self.root.configure(bg=t["bg"])

        hdr = tk.Frame(self.root, bg=t["header_bg"], pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🏆  Leaderboard",
                 font=("Helvetica", 20, "bold"),
                 bg=t["header_bg"], fg=t["header_fg"]).pack(side="left", padx=16)
        self._btn(hdr, "← Back", self._show_game,
                  style="primary").pack(side="right", padx=16)

        frm = tk.Frame(self.root, bg=t["bg"], padx=20, pady=10)
        frm.pack(fill="both", expand=True)

        headers = ["Rank", "Username", "Difficulty", "Time", "Score", "Date"]
        widths  = [6, 14, 10, 8, 8, 12]
        for i, (h, w) in enumerate(zip(headers, widths)):
            tk.Label(frm, text=h, font=("Helvetica", 11, "bold"),
                     bg=t["card_bg"], fg=t["label_fg"],
                     width=w, anchor="center",
                     relief="flat", pady=6).grid(row=0, column=i,
                                                  padx=2, pady=2, sticky="ew")

        rows = get_leaderboard()
        if not rows:
            tk.Label(frm, text="No scores yet. Play a game!",
                     font=("Helvetica", 12),
                     bg=t["bg"], fg=t["status_fg"]).grid(
                         row=1, column=0, columnspan=6, pady=20)

        for i, (uname, diff, tsecs, score, date) in enumerate(rows):
            m, s    = divmod(tsecs, 60)
            rank    = ["🥇", "🥈", "🥉"][i] if i < 3 else str(i+1)
            vals    = [rank, uname, diff, f"{m:02d}:{s:02d}", str(score), date[:10]]
            bg_row  = t["card_bg"] if i % 2 == 0 else t["bg"]
            fg_row  = "#FFD700" if i == 0 else t["label_fg"]
            for j, (v, w) in enumerate(zip(vals, widths)):
                tk.Label(frm, text=v, font=("Helvetica", 11),
                         bg=bg_row, fg=fg_row,
                         width=w, anchor="center",
                         pady=5).grid(row=i+1, column=j,
                                       padx=2, pady=1, sticky="ew")

    # ═══════════════════════════════════════════════════════════════════
    # PROFILE
    # ═══════════════════════════════════════════════════════════════════

    def _show_profile(self):
        self._clear()
        t    = self.theme
        data = get_profile(self.user_id, self.username)
        self.root.configure(bg=t["bg"])

        hdr = tk.Frame(self.root, bg=t["header_bg"], pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"👤  {self.username}'s Profile",
                 font=("Helvetica", 20, "bold"),
                 bg=t["header_bg"], fg=t["header_fg"]).pack(side="left", padx=16)
        self._btn(hdr, "← Back", self._show_game,
                  style="primary").pack(side="right", padx=16)

        outer = tk.Frame(self.root, bg=t["bg"], padx=24, pady=14)
        outer.pack(fill="both", expand=True)

        # Summary cards
        cards_frm = tk.Frame(outer, bg=t["bg"])
        cards_frm.pack(fill="x", pady=(0, 14))
        for i, (lbl, val) in enumerate([
            ("Joined",       data["joined"]),
            ("Games Played", str(data["total"])),
            ("Best Score",   str(data["best_single"])),
            ("Total Score",  str(data["total_score"])),
        ]):
            card = tk.Frame(cards_frm, bg=t["card_bg"], padx=16, pady=12)
            card.grid(row=0, column=i, padx=6, sticky="ew")
            tk.Label(card, text=val,
                     font=("Helvetica", 18, "bold"),
                     bg=t["card_bg"], fg=t["label_fg"]).pack()
            tk.Label(card, text=lbl,
                     font=("Helvetica", 9),
                     bg=t["card_bg"], fg=t["status_fg"]).pack()

        tk.Label(outer, text="Performance by Difficulty",
                 font=("Helvetica", 13, "bold"),
                 bg=t["bg"], fg=t["label_fg"]).pack(anchor="w", pady=(8, 4))

        tbl = tk.Frame(outer, bg=t["bg"])
        tbl.pack(fill="x")
        for j, h in enumerate(["Difficulty", "Best Time", "Best Score"]):
            tk.Label(tbl, text=h, font=("Helvetica", 11, "bold"),
                     bg=t["card_bg"], fg=t["label_fg"],
                     width=14, anchor="center",
                     pady=6, relief="flat").grid(row=0, column=j,
                                                  padx=2, pady=2)
        for i, diff in enumerate(("Easy", "Medium", "Hard", "Expert")):
            rd   = data["by_diff"][diff]
            bt   = "—"
            bs   = "—"
            if rd and rd[0] is not None:
                m, s = divmod(rd[0], 60)
                bt   = f"{m:02d}:{s:02d}"
                bs   = str(rd[1])
            bg_r = t["card_bg"] if i % 2 == 0 else t["bg"]
            for j, v in enumerate([diff, bt, bs]):
                tk.Label(tbl, text=v, font=("Helvetica", 11),
                         bg=bg_r, fg=t["label_fg"],
                         width=14, anchor="center",
                         pady=5).grid(row=i+1, column=j,
                                       padx=2, pady=1)

    # ═══════════════════════════════════════════════════════════════════
    # LOGOUT
    # ═══════════════════════════════════════════════════════════════════

    def _logout(self):
        self._stop_timer()
        self.user_id  = None
        self.username = None
        self._show_login()