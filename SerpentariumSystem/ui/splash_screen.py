import tkinter as tk
from tkinter import ttk, messagebox


class SplashScreen(tk.Toplevel):
    def __init__(self, master, db_initializer):
        super().__init__(master)

        self.db_initializer = db_initializer

        self.title("Перший запуск системи")
        self.geometry("560x260")
        self.resizable(False, False)
        self.configure(bg="#101827")
        self.grab_set()

        title = tk.Label(
            self,
            text="Підготовка інформаційної системи",
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#101827"
        )
        title.pack(pady=(30, 10))

        self.status_label = tk.Label(
            self,
            text="Створення бази даних...",
            font=("Segoe UI", 11),
            fg="#CBD5E1",
            bg="#101827"
        )
        self.status_label.pack(pady=(5, 20))

        self.progress = ttk.Progressbar(
            self,
            orient="horizontal",
            length=420,
            mode="determinate"
        )
        self.progress.pack(pady=10)

        self.percent_label = tk.Label(
            self,
            text="0%",
            font=("Segoe UI", 11),
            fg="#93C5FD",
            bg="#101827"
        )
        self.percent_label.pack()

        self.after(300, self.start_database_creation)

    def update_progress(self, current, total, text):
        value = int(current / total * 100)

        self.progress["value"] = value
        self.status_label.config(text=text)
        self.percent_label.config(text=f"{value}%")

        self.update()
        self.after(200)

    def start_database_creation(self):
        try:
            self.db_initializer.initialize(self.update_progress)

            messagebox.showinfo(
                "Готово",
                "Базу даних SQLite успішно створено."
            )

            self.destroy()

        except Exception as error:
            messagebox.showerror("Помилка", str(error))
            self.destroy()