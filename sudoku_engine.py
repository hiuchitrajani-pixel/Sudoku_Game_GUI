import random


class SudokuEngine:
    def __init__(self):
        self.grid     = [[0]*9 for _ in range(9)]
        self.solution = [[0]*9 for _ in range(9)]
        self.clues    = [[False]*9 for _ in range(9)]

    def generate(self, difficulty):
        random.seed()
        self.grid  = [[0]*9 for _ in range(9)]
        self.clues = [[False]*9 for _ in range(9)]
        self._fill(0, 0)
        self.solution = [row[:] for row in self.grid]
        removes = {"Easy": 36, "Medium": 46, "Hard": 52, "Expert": 58}
        self._remove(removes.get(difficulty, 46))
        for r in range(9):
            for c in range(9):
                self.clues[r][c] = self.grid[r][c] != 0

    def _fill(self, row, col):
        if row == 9:
            return True
        if col == 9:
            return self._fill(row + 1, 0)
        if self.grid[row][col] != 0:
            return self._fill(row, col + 1)
        nums = list(range(1, 10))
        random.shuffle(nums)
        for n in nums:
            if self._safe(row, col, n):
                self.grid[row][col] = n
                if self._fill(row, col + 1):
                    return True
                self.grid[row][col] = 0
        return False

    def solve(self, row=0, col=0):
        if row == 9:
            return True
        if col == 9:
            return self.solve(row + 1, 0)
        if self.grid[row][col] != 0:
            return self.solve(row, col + 1)
        for n in range(1, 10):
            if self._safe(row, col, n):
                self.grid[row][col] = n
                if self.solve(row, col + 1):
                    return True
                self.grid[row][col] = 0
        return False

    def _safe(self, row, col, n):
        if n in self.grid[row]:
            return False
        if any(self.grid[r][col] == n for r in range(9)):
            return False
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if self.grid[r][c] == n:
                    return False
        return True

    def _remove(self, count):
        positions = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(positions)
        done = 0
        for r, c in positions:
            if done >= count:
                break
            if self.grid[r][c] != 0:
                self.grid[r][c] = 0
                done += 1

    def is_valid(self):
        def unique(lst):
            lst = [x for x in lst if x != 0]
            return len(lst) == len(set(lst))
        for i in range(9):
            if not unique(self.grid[i]):
                return False
            if not unique([self.grid[r][i] for r in range(9)]):
                return False
        for br in range(3):
            for bc in range(3):
                box = [self.grid[r][c]
                       for r in range(br*3, br*3+3)
                       for c in range(bc*3, bc*3+3)]
                if not unique(box):
                    return False
        return True

    def is_complete(self):
        return (
            all(self.grid[r][c] != 0 for r in range(9) for c in range(9))
            and self.is_valid()
        )
