import random
import tkinter as tk
from tkinter import messagebox

MAX_SIZE = 8
CELL_SIZE = 54

def empty_grid(m, n):
    return [[0 for _ in range(n)] for _ in range(m)]

def clone_grid(grid):
    return [row[:] for row in grid]

def is_solved(grid):
    return all(value == 0 for row in grid for value in row)

def flatten(grid):
    return [value for row in grid for value in row]

def unflatten(vector, m, n):
    return [vector[i * n:(i + 1) * n] for i in range(m)]

def toggle_move(grid, row, col):
    m = len(grid)
    n = len(grid[0])
    new_grid = clone_grid(grid)

    for j in range(n):
        new_grid[row][j] ^= 1

    for i in range(m):
        if i != row:
            new_grid[i][col] ^= 1

    return new_grid

def build_move_matrix(m, n):
    size = m * n
    matrix = [[0 for _ in range(size)] for _ in range(size)]

    for p in range(size):
        i, j = divmod(p, n)

        for q in range(size):
            u, v = divmod(q, n)

            if i == u or j == v:
                matrix[p][q] = 1

    return matrix

def solve_gf2(matrix, rhs):
    rows = len(matrix)
    cols = len(matrix[0])
    aug = [matrix[i][:] + [rhs[i]] for i in range(rows)]

    pivot_cols = []
    r = 0

    for c in range(cols):
        if r >= rows:
            break

        pivot = None
        for i in range(r, rows):
            if aug[i][c] == 1:
                pivot = i
                break

        if pivot is None:
            continue

        aug[r], aug[pivot] = aug[pivot], aug[r]

        for i in range(rows):
            if i != r and aug[i][c] == 1:
                for k in range(c, cols + 1):
                    aug[i][k] ^= aug[r][k]

        pivot_cols.append(c)
        r += 1

    for i in range(rows):
        if all(aug[i][c] == 0 for c in range(cols)) and aug[i][cols] == 1:
            return None

    x = [0 for _ in range(cols)]

    for i, col in enumerate(pivot_cols):
        x[col] = aug[i][cols]

    return x

def random_solvable_grid(m, n):
    grid = empty_grid(m, n)

    for i in range(m):
        for j in range(n):
            if random.random() < 0.45:
                grid = toggle_move(grid, i, j)

    if is_solved(grid):
        i = random.randrange(m)
        j = random.randrange(n)
        grid = toggle_move(grid, i, j)

    return grid

class FridgeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Холодильник — головоломка")
        self.root.resizable(False, False)

        self.m = 4
        self.n = 4
        self.grid = random_solvable_grid(self.m, self.n)
        self.solution = None
        self.buttons = []

        self.build_ui()
        self.render()

    def build_ui(self):
        title = tk.Label(
            self.root,
            text="Головоломка с холодильником",
            font=("Arial", 18, "bold"),
        )
        title.pack(pady=(12, 4))

        subtitle = tk.Label(
            self.root,
            text="Нажатие клетки переворачивает всю строку и весь столбец.",
            font=("Arial", 11),
        )
        subtitle.pack(pady=(0, 12))

        controls = tk.Frame(self.root)
        controls.pack(pady=6)

        tk.Label(controls, text="Строки m:").grid(row=0, column=0, padx=4)
        self.rows_var = tk.IntVar(value=self.m)
        tk.Spinbox(
            controls,
            from_=1,
            to=MAX_SIZE,
            width=4,
            textvariable=self.rows_var,
            command=self.resize,
        ).grid(row=0, column=1, padx=4)

        tk.Label(controls, text="Столбцы n:").grid(row=0, column=2, padx=4)
        self.cols_var = tk.IntVar(value=self.n)
        tk.Spinbox(
            controls,
            from_=1,
            to=MAX_SIZE,
            width=4,
            textvariable=self.cols_var,
            command=self.resize,
        ).grid(row=0, column=3, padx=4)

        tk.Button(
            controls,
            text="Случайная разрешимая",
            command=self.generate,
        ).grid(row=0, column=4, padx=(18, 4))

        tk.Button(
            controls,
            text="Очистить",
            command=self.reset,
        ).grid(row=0, column=5, padx=4)

        tk.Button(
            controls,
            text="Показать решение",
            command=self.show_solution,
        ).grid(row=0, column=6, padx=4)

        tk.Button(
            controls,
            text="Применить решение",
            command=self.apply_solution,
        ).grid(row=0, column=7, padx=4)

        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack(pady=16)

        self.status_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 11),
            wraplength=760,
            justify="center",
        )
        self.status_label.pack(pady=(0, 12))

        instruction = (
            "Инструкция:\n"
            "1. Выберите размер поля от 1 до 8.\n"
            "2. Нажмите «Случайная разрешимая», чтобы получить задачу, имеющую решение.\n"
            "3. Кликайте по клетке: она переворачивает свою строку и свой столбец.\n"
            "4. Вертикальная ручка — тёмная клетка «┃», горизонтальная — светлая «━».\n"
            "5. Цель: добиться того, чтобы все ручки были в горизонталном положении.\n"
            "6. Если надоело, нажмите «Показать решение»: нужные клетки подсветятся жёлтым.\n"
            "7. Нажмите «Применить решение», чтобы выполнить подсвеченные ходы."
        )

        tk.Label(
            self.root,
            text=instruction,
            font=("Arial", 10),
            justify="left",
            bg="#f1f5f9",
            padx=12,
            pady=10,
        ).pack(padx=12, pady=(0, 12), fill="x")

    def resize(self):
        try:
            self.m = max(1, min(MAX_SIZE, int(self.rows_var.get())))
            self.n = max(1, min(MAX_SIZE, int(self.cols_var.get())))
        except tk.TclError:
            return

        self.grid = random_solvable_grid(self.m, self.n)
        self.solution = None
        self.render("Размер изменён, создана новая разрешимая конфигурация.")

    def generate(self):
        self.grid = random_solvable_grid(self.m, self.n)
        self.solution = None
        self.render("Сгенерирована новая разрешимая конфигурация.")

    def reset(self):
        self.grid = empty_grid(self.m, self.n)
        self.solution = None
        self.render("Поле очищено.")

    def click_cell(self, i, j):
        self.grid = toggle_move(self.grid, i, j)
        self.solution = None
        self.render("Ход сделан.")

    def show_solution(self):
        matrix = build_move_matrix(self.m, self.n)
        rhs = flatten(self.grid)
        x = solve_gf2(matrix, rhs)

        if x is None:
            self.solution = None
            self.render("Из текущей конфигурации решения нет.")
            messagebox.showinfo(
                "Решения нет",
                "Система Mx = a несовместна над полем F₂.",
            )
            return

        self.solution = unflatten(x, self.m, self.n)
        moves_count = sum(x)
        self.render(f"Найдено решение: нажмите {moves_count} подсвеченных клеток.")

    def apply_solution(self):
        if self.solution is None:
            messagebox.showinfo("Нет решения", "Сначала нажмите «Показать решение».")
            return

        for i in range(self.m):
            for j in range(self.n):
                if self.solution[i][j] == 1:
                    self.grid = toggle_move(self.grid, i, j)

        self.solution = None
        self.render("Решение применено.")

    def render(self, message=""):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.buttons = []

        for i in range(self.m):
            row_buttons = []
            for j in range(self.n):
                value = self.grid[i][j]
                highlighted = self.solution is not None and self.solution[i][j] == 1

                bg = "#1e293b" if value == 1 else "#e5e7eb"
                fg = "white" if value == 1 else "#64748b"

                if highlighted:
                    bg = "#facc15"
                    fg = "#111827"

                text = "┃" if value == 1 else "━"

                btn = tk.Button(
                    self.grid_frame,
                    text=text,
                    width=3,
                    height=1,
                    font=("Arial", 22, "bold"),
                    bg=bg,
                    fg=fg,
                    activebackground=bg,
                    activeforeground=fg,
                    command=lambda r=i, c=j: self.click_cell(r, c),
                )
                btn.grid(row=i, column=j, padx=4, pady=4)
                row_buttons.append(btn)

            self.buttons.append(row_buttons)

        ones = sum(flatten(self.grid))
        solved_text = "Холодильник открыт ✅" if is_solved(self.grid) else "Пока не решено ❌"

        self.status_label.config(
            text=f"{solved_text}. Вертикальных ручек: {ones}. {message}"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = FridgeApp(root)
    root.mainloop()