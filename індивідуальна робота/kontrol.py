import pygame
import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
import random
from abc import ABC, abstractmethod

# Інтерфейс для посібників
class ManualInterface(ABC):
    @abstractmethod
    def get_details(self):
        pass

# Базовий клас для посібників
class Manual(ManualInterface):
    def __init__(self, title, subject, author, publication_year):
        self.title = title
        self.subject = subject
        self.author = author
        self.publication_year = publication_year

    def get_details(self):
        return (self.title, self.subject, self.author, self.publication_year)

# Клас для роботи з базою даних
class DatabaseHandler:
    def __init__(self, db_name="manuals.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS manuals
               (title TEXT, subject TEXT, author TEXT, publication_year INTEGER)'''
        )
        self.connection.commit()

    def save_manual(self, manual: Manual):
        self.cursor.execute(
            "INSERT INTO manuals VALUES (?, ?, ?, ?)",
            (manual.title, manual.subject, manual.author, manual.publication_year)
        )
        self.connection.commit()

    def load_manuals(self, search_filter=None):
        if search_filter:
            query = "SELECT * FROM manuals WHERE title LIKE ? OR author LIKE ?"
            self.cursor.execute(query, (f'%{search_filter}%', f'%{search_filter}%'))
        else:
            self.cursor.execute("SELECT * FROM manuals")
        rows = self.cursor.fetchall()
        return [Manual(*row) for row in rows]

    def delete_manual(self, title):
        self.cursor.execute("DELETE FROM manuals WHERE title=?", (title,))
        self.connection.commit()

    def update_manual(self, old_title, manual: Manual):
        self.cursor.execute(
            "UPDATE manuals SET title=?, subject=?, author=?, publication_year=? WHERE title=?",
            (manual.title, manual.subject, manual.author, manual.publication_year, old_title)
        )
        self.connection.commit()

# DVD заставка з логотипом, який відбивається від країв
def dvd_bouncing_splash():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("DVD Bouncing Splash")

    logo_color = (255, 255, 0)
    logo_font = pygame.font.Font(None, 75)
    logo_text = "DVD"
    logo_surface = logo_font.render(logo_text, True, logo_color)
    logo_rect = logo_surface.get_rect(center=(400, 300))

    logo_speed = [random.choice([2, -2]), random.choice([2, -2])]
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                running = False

        logo_rect = logo_rect.move(logo_speed)

        if logo_rect.left < 0 or logo_rect.right > screen.get_width():
            logo_speed[0] = -logo_speed[0]
            logo_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        if logo_rect.top < 0 or logo_rect.bottom > screen.get_height():
            logo_speed[1] = -logo_speed[1]
            logo_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        logo_surface = logo_font.render(logo_text, True, logo_color)

        screen.fill((0, 0, 0))
        screen.blit(logo_surface, logo_rect)
        pygame.display.flip()
        pygame.time.delay(10)

    pygame.quit()
    return True

# Вікно для перегляду всіх назв книг
class ViewAllTitlesWindow(tk.Toplevel):
    def __init__(self, db_handler):
        super().__init__()
        self.db_handler = db_handler
        self.title("Всі назви книг")
        self.geometry("400x300")

        tk.Label(self, text="Список всіх назв книг:").pack(pady=10)

        self.titles_listbox = tk.Listbox(self, width=50, height=15)
        self.titles_listbox.pack(pady=10)

        self.load_titles()

    def load_titles(self):
        # Завантажуємо всі книги з бази даних та додаємо їх назви у список
        manuals = self.db_handler.load_manuals()
        for manual in manuals:
            self.titles_listbox.insert(tk.END, manual.title)

# Основне вікно програми
class MainApp(tk.Tk):
    def __init__(self, db_handler):
        super().__init__()
        self.db_handler = db_handler
        self.title("DVD Management System")
        self.geometry("400x300")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # Додаємо підтвердження виходу
        self.create_menu()
        self.create_ui()

    def create_menu(self):
        menu = tk.Menu(self)
        self.config(menu=menu)

        # Додати меню "Файл"
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Вийти", command=self.on_closing)

    def create_ui(self):
        self.create_rounded_button("Додати нову книгу", self.open_add_manual_window, "#FF5C93", "#FFB6C1")
        self.create_rounded_button("Пошук", self.open_search_window, "#800080", "#FFB6C1")
        self.create_rounded_button("Редагувати", self.open_edit_window, "#FFA500", "#FFB6C1")
        self.create_rounded_button("Переглянути всі назви книг", self.open_view_all_titles_window, "#4682B4", "#B0E0E6")
        self.create_rounded_button("Вихід", self.on_closing, "#FF6347", "#FFB6C1")  # Кнопка виходу

    def create_rounded_button(self, text, command, normal_color, hover_color):
        button_canvas = tk.Canvas(self, width=300, height=50, bg=normal_color, highlightthickness=0)
        button_canvas.create_oval(0, 0, 20, 20, fill=normal_color, outline=normal_color)
        button_canvas.create_oval(280, 0, 300, 20, fill=normal_color, outline=normal_color)
        button_canvas.create_rectangle(10, 0, 290, 50, fill=normal_color, outline=normal_color, width=0)
        button_canvas.create_text(150, 25, text=text, fill="white", font=("Arial", 16))
        button_canvas.pack(pady=10)

        button_canvas.bind("<Button-1>", lambda event: command())
        button_canvas.bind("<Enter>", lambda event: button_canvas.config(bg=hover_color))
        button_canvas.bind("<Leave>", lambda event: button_canvas.config(bg=normal_color))

    def open_add_manual_window(self):
        AddManualWindow(self.db_handler)

    def open_search_window(self):
        SearchWindow(self.db_handler)

    def open_edit_window(self):
        EditManualWindow(self.db_handler)

    def open_view_all_titles_window(self):
        ViewAllTitlesWindow(self.db_handler)

    def on_closing(self):
        if messagebox.askokcancel("Вихід", "Ви дійсно хочете вийти?"):
            self.quit()

# Вікно для додавання нової книги
class AddManualWindow(tk.Toplevel):
    def __init__(self, db_handler):
        super().__init__()
        self.db_handler = db_handler
        self.title("Додати нову книгу")
        self.geometry("400x300")

        self.entries = {}
        fields = ["Title", "Subject", "Author", "Publication Year"]
        for idx, field in enumerate(fields):
            tk.Label(self, text=field + ":").grid(row=idx, column=0, padx=10, pady=5)
            entry = tk.Entry(self)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            self.entries[field] = entry

        save_button = tk.Button(self, text="Зберегти", command=self.save_manual, bg="#4CAF50", fg="white", 
                                relief="flat", cursor="hand2", width=30)
        save_button.grid(row=len(fields), columnspan=2, pady=10)

    def save_manual(self):
        try:
            manual = Manual(
                self.entries["Title"].get(),
                self.entries["Subject"].get(),
                self.entries["Author"].get(),
                int(self.entries["Publication Year"].get())
            )
            self.db_handler.save_manual(manual)
            messagebox.showinfo("Успіх", "Книгу успішно додано!")
            self.destroy()
        except ValueError:
            messagebox.showerror("Помилка вводу", "Рік видання повинен бути цілим числом.")

# Вікно для пошуку
class SearchWindow(tk.Toplevel):
    def __init__(self, db_handler):
        super().__init__()
        self.db_handler = db_handler
        self.title("Пошук книг")
        self.geometry("400x300")

        tk.Label(self, text="Пошук за назвою або автором:").pack(pady=10)
        self.search_entry = tk.Entry(self, width=40)
        self.search_entry.pack(pady=5)

        search_button = tk.Button(self, text="Знайти", command=self.search_manuals, bg="#4CAF50", fg="white", 
                                  relief="flat", cursor="hand2", width=30)
        search_button.pack(pady=10)

        self.results_listbox = tk.Listbox(self, width=50, height=10)
        self.results_listbox.pack(pady=10)

    def search_manuals(self):
        search_filter = self.search_entry.get()
        manuals = self.db_handler.load_manuals(search_filter)  # Отримуємо списки книг
        self.results_listbox.delete(0, tk.END)  # Очищаємо попередні результати
        if manuals:
            for manual in manuals:
                # Форматуємо дані книги в один рядок
                details = f"{manual.title} ({manual.publication_year}), Тема: {manual.subject}, Автор: {manual.author}"
                self.results_listbox.insert(tk.END, details)  # Додаємо нові результати у Listbox
        else:
            self.results_listbox.insert(tk.END, "Книги не знайдено.")


# Вікно для редагування книги
class EditManualWindow(tk.Toplevel):
    def __init__(self, db_handler):
        super().__init__()
        self.db_handler = db_handler
        self.title("Редагувати книгу")
        self.geometry("400x300")

        tk.Label(self, text="Назва книги для редагування:").pack(pady=10)
        self.title_entry = tk.Entry(self, width=40)
        self.title_entry.pack(pady=5)

        find_button = tk.Button(self, text="Знайти", command=self.find_manual, bg="#4CAF50", fg="white", 
                                relief="flat", cursor="hand2", width=30)
        find_button.pack(pady=10)

        self.entries = {}
        fields = ["Title", "Subject", "Author", "Publication Year"]
        for field in fields:
            tk.Label(self, text=field + ":").pack(pady=5)
            entry = tk.Entry(self, width=40)
            entry.pack(pady=5)
            self.entries[field] = entry

        save_button = tk.Button(self, text="Зберегти зміни", command=self.save_changes, bg="#FF6347", fg="white", 
                                relief="flat", cursor="hand2", width=30)
        save_button.pack(pady=10)

    def find_manual(self):
        title = self.title_entry.get()
        manuals = self.db_handler.load_manuals(title)
        if manuals:
            manual = manuals[0]
            self.entries["Title"].delete(0, tk.END)
            self.entries["Title"].insert(0, manual.title)
            self.entries["Subject"].delete(0, tk.END)
            self.entries["Subject"].insert(0, manual.subject)
            self.entries["Author"].delete(0, tk.END)
            self.entries["Author"].insert(0, manual.author)
            self.entries["Publication Year"].delete(0, tk.END)
            self.entries["Publication Year"].insert(0, manual.publication_year)
        else:
            messagebox.showinfo("Результат", "Книгу не знайдено.")

    def save_changes(self):
        old_title = self.title_entry.get()
        try:
            manual = Manual(
                self.entries["Title"].get(),
                self.entries["Subject"].get(),
                self.entries["Author"].get(),
                int(self.entries["Publication Year"].get())
            )
            self.db_handler.update_manual(old_title, manual)
            messagebox.showinfo("Успіх", "Книгу успішно оновлено!")
            self.destroy()
        except ValueError:
            messagebox.showerror("Помилка вводу", "Рік видання повинен бути цілим числом.")

# Основна частина програми
if __name__ == "__main__":
    if dvd_bouncing_splash():
        db_handler = DatabaseHandler()
        app = MainApp(db_handler)
        app.mainloop()
