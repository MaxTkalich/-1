import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from models.species import Species
from models.caretaker import Caretaker
from models.enclosure import Enclosure
from models.snake import Snake


class MainWindow(tk.Tk):
    def __init__(self, serpentarium_service, feeding_service):
        super().__init__()

        self.serpentarium_service = serpentarium_service
        self.feeding_service = feeding_service

        self.selected_snake_id = None
        self.selected_species_id = None
        self.selected_caretaker_id = None
        self.selected_enclosure_id = None
        self.selected_feed_request_id = None

        self.title("Інформаційна система управління серпентарієм")
        self.geometry("1280x760")
        self.minsize(1100, 680)
        self.configure(bg="#EEF2F7")

        self.setup_styles()
        self.create_interface()
        self.refresh_all()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook", background="#EEF2F7", borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 10), font=("Segoe UI", 10, "bold"))
        style.configure("TFrame", background="#EEF2F7")
        style.configure("TLabel", background="#EEF2F7", font=("Segoe UI", 10))
        style.configure("Header.TLabel", background="#EEF2F7", foreground="#0F172A", font=("Segoe UI", 20, "bold"))
        style.configure("Subheader.TLabel", background="#EEF2F7", foreground="#475569", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(12, 8))
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def create_interface(self):
        header = ttk.Frame(self)
        header.pack(fill="x", padx=24, pady=(18, 8))

        ttk.Label(
            header,
            text="Інформаційна система управління серпентарієм",
            style="Header.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Облік змій, доглядачів, умов утримання та автоматизоване формування заявок на корми",
            style="Subheader.TLabel"
        ).pack(anchor="w", pady=(4, 0))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=24, pady=14)

        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_snakes = ttk.Frame(self.notebook)
        self.tab_species = ttk.Frame(self.notebook)
        self.tab_caretakers = ttk.Frame(self.notebook)
        self.tab_enclosures = ttk.Frame(self.notebook)
        self.tab_feeding = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_dashboard, text="Панель огляду")
        self.notebook.add(self.tab_snakes, text="Змії")
        self.notebook.add(self.tab_species, text="Класифікатор")
        self.notebook.add(self.tab_caretakers, text="Доглядачі")
        self.notebook.add(self.tab_enclosures, text="Вольєри")
        self.notebook.add(self.tab_feeding, text="Корми")

        self.build_dashboard_tab()
        self.build_snakes_tab()
        self.build_species_tab()
        self.build_caretakers_tab()
        self.build_enclosures_tab()
        self.build_feeding_tab()

    def create_entry(self, parent, label_text, row, column, width=22):
        ttk.Label(parent, text=label_text).grid(row=row, column=column, padx=8, pady=8, sticky="w")

        entry = ttk.Entry(parent, width=width)
        entry.grid(row=row, column=column + 1, padx=8, pady=8, sticky="ew")

        return entry

    def create_combobox(self, parent, label_text, values, row, column):
        ttk.Label(parent, text=label_text).grid(row=row, column=column, padx=8, pady=8, sticky="w")

        combobox = ttk.Combobox(parent, values=values, state="readonly", width=24)
        combobox.grid(row=row, column=column + 1, padx=8, pady=8, sticky="ew")

        if values:
            combobox.set(values[0])

        return combobox

    def create_treeview(self, parent, columns, headings):
        tree = ttk.Treeview(parent, columns=columns, show="headings")

        for column in columns:
            tree.heading(column, text=headings[column])
            tree.column(column, width=130, anchor="center")

        return tree

    def get_id_from_combobox(self, combobox):
        value = combobox.get()

        if not value or " — " not in value:
            return None

        return int(value.split(" — ")[0])

    def set_entry(self, entry, value):
        entry.delete(0, "end")
        entry.insert(0, "" if value is None else str(value))

    def build_dashboard_tab(self):
        wrapper = ttk.Frame(self.tab_dashboard)
        wrapper.pack(fill="both", expand=True, padx=10, pady=10)

        self.dashboard_text = tk.Text(
            wrapper,
            height=20,
            font=("Segoe UI", 12),
            bg="white",
            fg="#0F172A",
            relief="flat",
            padx=24,
            pady=20
        )
        self.dashboard_text.pack(fill="both", expand=True)

    def build_snakes_tab(self):
        container = ttk.Frame(self.tab_snakes)
        container.pack(fill="both", expand=True, padx=8, pady=8)

        form = ttk.LabelFrame(container, text="Додавання / редагування змії")
        form.pack(fill="x", padx=4, pady=4)

        self.snake_name_entry = self.create_entry(form, "Кличка / номер:", 0, 0)
        self.snake_age_entry = self.create_entry(form, "Вік:", 0, 2)

        self.snake_sex_combobox = self.create_combobox(
            form,
            "Стать:",
            ["Самець", "Самка", "Невідомо"],
            0,
            4
        )

        self.snake_species_combobox = self.create_combobox(form, "Вид:", [], 1, 0)

        self.snake_health_combobox = self.create_combobox(
            form,
            "Стан здоров’я:",
            ["Здоровий", "Під наглядом", "Карантин", "Лікування"],
            1,
            2
        )

        self.snake_enclosure_combobox = self.create_combobox(form, "Вольєр:", [], 1, 4)

        self.snake_last_feed_entry = self.create_entry(form, "Останнє годування YYYY-MM-DD:", 2, 0)
        self.snake_notes_entry = self.create_entry(form, "Примітки:", 2, 2, width=44)

        ttk.Button(
            form,
            text="Додати змію та автоматично призначити доглядача",
            command=self.add_snake
        ).grid(row=3, column=0, columnspan=3, sticky="ew", padx=8, pady=12)

        ttk.Button(
            form,
            text="Оновити вибрану змію",
            command=self.update_snake
        ).grid(row=3, column=3, columnspan=3, sticky="ew", padx=8, pady=12)

        self.snake_species_combobox.bind(
            "<<ComboboxSelected>>",
            lambda event: self.refresh_enclosures_by_species()
        )

        columns = (
            "id", "name", "species", "venom", "age", "sex",
            "health", "enclosure", "caretaker", "arrival", "feed"
        )

        headings = {
            "id": "ID",
            "name": "Змія",
            "species": "Вид",
            "venom": "Отруйна",
            "age": "Вік",
            "sex": "Стать",
            "health": "Здоров’я",
            "enclosure": "Вольєр",
            "caretaker": "Доглядач",
            "arrival": "Дата надходження",
            "feed": "Останнє годування"
        }

        self.snakes_tree = self.create_treeview(container, columns, headings)
        self.snakes_tree.pack(fill="both", expand=True, padx=4, pady=8)
        self.snakes_tree.bind("<Double-1>", self.load_selected_snake)

    def build_species_tab(self):
        container = ttk.Frame(self.tab_species)
        container.pack(fill="both", expand=True, padx=8, pady=8)

        form = ttk.LabelFrame(container, text="Класифікатор рептилій")
        form.pack(fill="x", padx=4, pady=4)

        self.species_common_entry = self.create_entry(form, "Назва:", 0, 0)
        self.species_latin_entry = self.create_entry(form, "Латинська назва:", 0, 2)
        self.species_family_entry = self.create_entry(form, "Родина:", 0, 4)

        self.species_venomous_var = tk.IntVar()

        ttk.Checkbutton(
            form,
            text="Отруйна рептилія",
            variable=self.species_venomous_var
        ).grid(row=1, column=0, sticky="w", padx=8, pady=8)

        self.species_temp_min_entry = self.create_entry(form, "Темп. мін:", 1, 1, width=10)
        self.species_temp_max_entry = self.create_entry(form, "Темп. макс:", 1, 2, width=10)
        self.species_humidity_min_entry = self.create_entry(form, "Волог. мін:", 1, 3, width=10)
        self.species_humidity_max_entry = self.create_entry(form, "Волог. макс:", 1, 4, width=10)

        self.species_water_entry = self.create_entry(form, "Вода:", 2, 0)
        self.species_food_entry = self.create_entry(form, "Тип корму:", 2, 2)
        self.species_interval_entry = self.create_entry(form, "Інтервал годування:", 2, 4)
        self.species_amount_entry = self.create_entry(form, "Кількість корму:", 3, 0)
        self.species_notes_entry = self.create_entry(form, "Примітки:", 3, 2, width=44)

        ttk.Button(
            form,
            text="Додати вид",
            command=self.add_species
        ).grid(row=4, column=0, columnspan=3, sticky="ew", padx=8, pady=12)

        ttk.Button(
            form,
            text="Оновити вибраний вид",
            command=self.update_species
        ).grid(row=4, column=3, columnspan=3, sticky="ew", padx=8, pady=12)

        columns = (
            "id", "common", "latin", "venom",
            "temperature", "humidity", "water", "food", "interval"
        )

        headings = {
            "id": "ID",
            "common": "Назва",
            "latin": "Латинська назва",
            "venom": "Отруйна",
            "temperature": "Температура",
            "humidity": "Вологість",
            "water": "Вода",
            "food": "Корм",
            "interval": "Інтервал"
        }

        self.species_tree = self.create_treeview(container, columns, headings)
        self.species_tree.pack(fill="both", expand=True, padx=4, pady=8)
        self.species_tree.bind("<Double-1>", self.load_selected_species)

    def build_caretakers_tab(self):
        container = ttk.Frame(self.tab_caretakers)
        container.pack(fill="both", expand=True, padx=8, pady=8)

        form = ttk.LabelFrame(container, text="Доглядачі")
        form.pack(fill="x", padx=4, pady=4)

        self.caretaker_name_entry = self.create_entry(form, "ПІБ:", 0, 0)
        self.caretaker_qualification_entry = self.create_entry(form, "Кваліфікація:", 0, 2, width=44)

        self.caretaker_phone_entry = self.create_entry(form, "Телефон:", 1, 0)
        self.caretaker_max_entry = self.create_entry(form, "Макс. тварин:", 1, 2)

        self.caretaker_venomous_var = tk.IntVar()

        ttk.Checkbutton(
            form,
            text="Є допуск до отруйних рептилій",
            variable=self.caretaker_venomous_var
        ).grid(row=1, column=4, sticky="w", padx=8, pady=8)

        ttk.Button(
            form,
            text="Додати доглядача",
            command=self.add_caretaker
        ).grid(row=2, column=0, columnspan=3, sticky="ew", padx=8, pady=12)

        ttk.Button(
            form,
            text="Оновити вибраного доглядача",
            command=self.update_caretaker
        ).grid(row=2, column=3, columnspan=3, sticky="ew", padx=8, pady=12)

        columns = ("id", "name", "qualification", "venom", "phone", "max", "active")

        headings = {
            "id": "ID",
            "name": "ПІБ",
            "qualification": "Кваліфікація",
            "venom": "Допуск",
            "phone": "Телефон",
            "max": "Макс. тварин",
            "active": "Активний"
        }

        self.caretakers_tree = self.create_treeview(container, columns, headings)
        self.caretakers_tree.pack(fill="both", expand=True, padx=4, pady=8)
        self.caretakers_tree.bind("<Double-1>", self.load_selected_caretaker)

    def build_enclosures_tab(self):
        container = ttk.Frame(self.tab_enclosures)
        container.pack(fill="both", expand=True, padx=8, pady=8)

        form = ttk.LabelFrame(container, text="Вольєри")
        form.pack(fill="x", padx=4, pady=4)

        self.enclosure_code_entry = self.create_entry(form, "Код:", 0, 0)
        self.enclosure_zone_entry = self.create_entry(form, "Зона:", 0, 2)
        self.enclosure_temperature_entry = self.create_entry(form, "Температура:", 0, 4)

        self.enclosure_humidity_entry = self.create_entry(form, "Вологість:", 1, 0)
        self.enclosure_lighting_entry = self.create_entry(form, "Освітлення:", 1, 2)
        self.enclosure_capacity_entry = self.create_entry(form, "Місткість:", 1, 4)

        self.enclosure_water_var = tk.IntVar(value=1)

        ttk.Checkbutton(
            form,
            text="Є вода",
            variable=self.enclosure_water_var
        ).grid(row=2, column=0, sticky="w", padx=8, pady=8)

        self.enclosure_notes_entry = self.create_entry(form, "Примітки:", 2, 2, width=44)

        ttk.Button(
            form,
            text="Додати вольєр",
            command=self.add_enclosure
        ).grid(row=3, column=0, columnspan=3, sticky="ew", padx=8, pady=12)

        ttk.Button(
            form,
            text="Оновити вибраний вольєр",
            command=self.update_enclosure
        ).grid(row=3, column=3, columnspan=3, sticky="ew", padx=8, pady=12)

        columns = (
            "id", "code", "zone", "temperature",
            "humidity", "water", "lighting", "capacity"
        )

        headings = {
            "id": "ID",
            "code": "Код",
            "zone": "Зона",
            "temperature": "Температура",
            "humidity": "Вологість",
            "water": "Вода",
            "lighting": "Освітлення",
            "capacity": "Місткість"
        }

        self.enclosures_tree = self.create_treeview(container, columns, headings)
        self.enclosures_tree.pack(fill="both", expand=True, padx=4, pady=8)
        self.enclosures_tree.bind("<Double-1>", self.load_selected_enclosure)

    def build_feeding_tab(self):
        container = ttk.Frame(self.tab_feeding)
        container.pack(fill="both", expand=True, padx=8, pady=8)

        form = ttk.LabelFrame(container, text="Формування / редагування заявки на корми")
        form.pack(fill="x", padx=4, pady=4)

        ttk.Label(form, text="Період:").grid(row=0, column=0, padx=8, pady=12)

        self.feed_period_combobox = ttk.Combobox(
            form,
            values=["День", "Тиждень", "Місяць"],
            state="readonly",
            width=20
        )
        self.feed_period_combobox.set("Тиждень")
        self.feed_period_combobox.grid(row=0, column=1, padx=8, pady=12)

        ttk.Button(
            form,
            text="Сформувати заявку автоматично",
            command=self.generate_feed_request
        ).grid(row=0, column=2, columnspan=2, padx=8, pady=12, sticky="ew")

        self.feed_edit_period_entry = self.create_entry(form, "Період:", 1, 0)
        self.feed_edit_from_entry = self.create_entry(form, "Дата з:", 1, 2)
        self.feed_edit_to_entry = self.create_entry(form, "Дата по:", 1, 4)
        self.feed_edit_food_entry = self.create_entry(form, "Тип корму:", 2, 0)
        self.feed_edit_amount_entry = self.create_entry(form, "Кількість:", 2, 2)

        ttk.Button(
            form,
            text="Оновити вибрану заявку",
            command=self.update_feed_request
        ).grid(row=3, column=0, columnspan=6, sticky="ew", padx=8, pady=12)

        columns = ("id", "period", "from", "to", "food", "amount", "created")

        headings = {
            "id": "ID",
            "period": "Період",
            "from": "З",
            "to": "По",
            "food": "Тип корму",
            "amount": "Кількість",
            "created": "Створено"
        }

        self.feed_tree = self.create_treeview(container, columns, headings)
        self.feed_tree.pack(fill="both", expand=True, padx=4, pady=8)
        self.feed_tree.bind("<Double-1>", self.load_selected_feed_request)

    def refresh_all(self):
        self.refresh_species_combobox()
        self.refresh_enclosure_combobox()
        self.refresh_tables()
        self.refresh_dashboard()

    def refresh_species_combobox(self):
        species = self.serpentarium_service.get_species()

        values = [
            f"{item['species_id']} — {item['common_name']}"
            for item in species
        ]

        self.snake_species_combobox["values"] = values

        if values and not self.snake_species_combobox.get():
            self.snake_species_combobox.set(values[0])

    def refresh_enclosure_combobox(self):
        enclosures = self.serpentarium_service.get_enclosures()

        values = [
            f"{item['enclosure_id']} — {item['code']} ({item['temperature']}°C, {item['humidity']}%)"
            for item in enclosures
        ]

        self.snake_enclosure_combobox["values"] = values

        if values and not self.snake_enclosure_combobox.get():
            self.snake_enclosure_combobox.set(values[0])

    def refresh_enclosures_by_species(self):
        species_id = self.get_id_from_combobox(self.snake_species_combobox)

        if not species_id:
            return

        enclosures = self.serpentarium_service.find_suitable_enclosures(species_id)

        if not enclosures:
            messagebox.showwarning(
                "Увага",
                "Для цього виду немає відповідного вольєра."
            )
            self.refresh_enclosure_combobox()
            return

        values = [
            f"{item['enclosure_id']} — {item['code']} "
            f"({item['temperature']}°C, {item['humidity']}%, "
            f"зайнято {item['current_count']}/{item['capacity']})"
            for item in enclosures
        ]

        self.snake_enclosure_combobox["values"] = values
        self.snake_enclosure_combobox.set(values[0])

    def refresh_tables(self):
        for tree in [
            self.snakes_tree,
            self.species_tree,
            self.caretakers_tree,
            self.enclosures_tree,
            self.feed_tree
        ]:
            for item in tree.get_children():
                tree.delete(item)

        for snake in self.serpentarium_service.get_snakes():
            self.snakes_tree.insert(
                "",
                "end",
                values=(
                    snake["snake_id"],
                    snake["nickname"],
                    snake["common_name"],
                    "Так" if snake["is_venomous"] else "Ні",
                    snake["age_years"],
                    snake["sex"],
                    snake["health_status"],
                    snake["enclosure_code"],
                    snake["caretaker_name"],
                    snake["arrival_date"],
                    snake["last_feeding_date"] or "-"
                )
            )

        for species in self.serpentarium_service.get_species():
            self.species_tree.insert(
                "",
                "end",
                values=(
                    species["species_id"],
                    species["common_name"],
                    species["latin_name"],
                    "Так" if species["is_venomous"] else "Ні",
                    f"{species['min_temperature']}–{species['max_temperature']}°C",
                    f"{species['humidity_min']}–{species['humidity_max']}%",
                    species["water_requirement"],
                    species["food_type"],
                    f"{species['feeding_interval_days']} дн."
                )
            )

        for caretaker in self.serpentarium_service.get_caretakers():
            self.caretakers_tree.insert(
                "",
                "end",
                values=(
                    caretaker["caretaker_id"],
                    caretaker["full_name"],
                    caretaker["qualification"],
                    "Є" if caretaker["can_handle_venomous"] else "Немає",
                    caretaker["phone"],
                    caretaker["max_animals"],
                    "Так" if caretaker["is_active"] else "Ні"
                )
            )

        for enclosure in self.serpentarium_service.get_enclosures():
            self.enclosures_tree.insert(
                "",
                "end",
                values=(
                    enclosure["enclosure_id"],
                    enclosure["code"],
                    enclosure["zone"],
                    f"{enclosure['temperature']}°C",
                    f"{enclosure['humidity']}%",
                    "Так" if enclosure["has_water"] else "Ні",
                    enclosure["lighting_mode"],
                    enclosure["capacity"]
                )
            )

        for request in self.serpentarium_service.get_feed_requests():
            self.feed_tree.insert(
                "",
                "end",
                values=(
                    request["request_id"],
                    request["period_type"],
                    request["date_from"],
                    request["date_to"],
                    request["food_type"],
                    request["total_amount"],
                    request["created_at"]
                )
            )

    def refresh_dashboard(self):
        stats = self.serpentarium_service.query(
            """
            SELECT
                (SELECT COUNT(*) FROM snakes) AS snakes_count,
                (SELECT COUNT(*) FROM species) AS species_count,
                (SELECT COUNT(*) FROM caretakers WHERE is_active = 1) AS caretakers_count,
                (SELECT COUNT(*) FROM enclosures) AS enclosures_count
            """
        )[0]

        text = f"""ОГЛЯД СИСТЕМИ

Усього змій: {stats['snakes_count']}
Видів у класифікаторі: {stats['species_count']}
Активних доглядачів: {stats['caretakers_count']}
Вольєрів: {stats['enclosures_count']}

Для редагування запису потрібно двічі натиснути на рядок у таблиці.
Після цього дані автоматично завантажуються у форму, їх можна змінити
та натиснути кнопку оновлення.

Програма побудована за принципами об'єктно-орієнтованого програмування.
Підключення до бази даних, створення таблиць, бізнес-логіка та графічний
інтерфейс винесені в окремі класи й модулі.
"""

        self.dashboard_text.delete("1.0", "end")
        self.dashboard_text.insert("1.0", text)

    def load_selected_snake(self, event):
        selected = self.snakes_tree.selection()

        if not selected:
            return

        values = self.snakes_tree.item(selected[0], "values")
        self.selected_snake_id = values[0]

        rows = self.serpentarium_service.query(
            "SELECT * FROM snakes WHERE snake_id = ?",
            (self.selected_snake_id,)
        )

        if not rows:
            return

        snake = rows[0]

        self.set_entry(self.snake_name_entry, snake["nickname"])
        self.set_entry(self.snake_age_entry, snake["age_years"])
        self.snake_sex_combobox.set(snake["sex"])
        self.snake_health_combobox.set(snake["health_status"])

        for value in self.snake_species_combobox["values"]:
            if value.startswith(str(snake["species_id"]) + " — "):
                self.snake_species_combobox.set(value)
                break

        self.refresh_enclosures_by_species()

        for value in self.snake_enclosure_combobox["values"]:
            if value.startswith(str(snake["enclosure_id"]) + " — "):
                self.snake_enclosure_combobox.set(value)
                break

        self.set_entry(self.snake_last_feed_entry, snake["last_feeding_date"] or "")
        self.set_entry(self.snake_notes_entry, snake["notes"] or "")

    def load_selected_species(self, event):
        selected = self.species_tree.selection()

        if not selected:
            return

        values = self.species_tree.item(selected[0], "values")
        self.selected_species_id = values[0]

        rows = self.serpentarium_service.query(
            "SELECT * FROM species WHERE species_id = ?",
            (self.selected_species_id,)
        )

        if not rows:
            return

        species = rows[0]

        self.set_entry(self.species_common_entry, species["common_name"])
        self.set_entry(self.species_latin_entry, species["latin_name"])
        self.set_entry(self.species_family_entry, species["family_name"] or "")
        self.species_venomous_var.set(species["is_venomous"])

        self.set_entry(self.species_temp_min_entry, species["min_temperature"])
        self.set_entry(self.species_temp_max_entry, species["max_temperature"])
        self.set_entry(self.species_humidity_min_entry, species["humidity_min"])
        self.set_entry(self.species_humidity_max_entry, species["humidity_max"])
        self.set_entry(self.species_water_entry, species["water_requirement"])
        self.set_entry(self.species_food_entry, species["food_type"])
        self.set_entry(self.species_interval_entry, species["feeding_interval_days"])
        self.set_entry(self.species_amount_entry, species["average_food_amount"])
        self.set_entry(self.species_notes_entry, species["notes"] or "")

    def load_selected_caretaker(self, event):
        selected = self.caretakers_tree.selection()

        if not selected:
            return

        values = self.caretakers_tree.item(selected[0], "values")
        self.selected_caretaker_id = values[0]

        rows = self.serpentarium_service.query(
            "SELECT * FROM caretakers WHERE caretaker_id = ?",
            (self.selected_caretaker_id,)
        )

        if not rows:
            return

        caretaker = rows[0]

        self.set_entry(self.caretaker_name_entry, caretaker["full_name"])
        self.set_entry(self.caretaker_qualification_entry, caretaker["qualification"])
        self.set_entry(self.caretaker_phone_entry, caretaker["phone"] or "")
        self.set_entry(self.caretaker_max_entry, caretaker["max_animals"])
        self.caretaker_venomous_var.set(caretaker["can_handle_venomous"])

    def load_selected_enclosure(self, event):
        selected = self.enclosures_tree.selection()

        if not selected:
            return

        values = self.enclosures_tree.item(selected[0], "values")
        self.selected_enclosure_id = values[0]

        rows = self.serpentarium_service.query(
            "SELECT * FROM enclosures WHERE enclosure_id = ?",
            (self.selected_enclosure_id,)
        )

        if not rows:
            return

        enclosure = rows[0]

        self.set_entry(self.enclosure_code_entry, enclosure["code"])
        self.set_entry(self.enclosure_zone_entry, enclosure["zone"])
        self.set_entry(self.enclosure_temperature_entry, enclosure["temperature"])
        self.set_entry(self.enclosure_humidity_entry, enclosure["humidity"])
        self.set_entry(self.enclosure_lighting_entry, enclosure["lighting_mode"])
        self.set_entry(self.enclosure_capacity_entry, enclosure["capacity"])
        self.set_entry(self.enclosure_notes_entry, enclosure["notes"] or "")
        self.enclosure_water_var.set(enclosure["has_water"])

    def load_selected_feed_request(self, event):
        selected = self.feed_tree.selection()

        if not selected:
            return

        values = self.feed_tree.item(selected[0], "values")
        self.selected_feed_request_id = values[0]

        rows = self.serpentarium_service.query(
            "SELECT * FROM feed_requests WHERE request_id = ?",
            (self.selected_feed_request_id,)
        )

        if not rows:
            return

        request = rows[0]

        self.set_entry(self.feed_edit_period_entry, request["period_type"])
        self.set_entry(self.feed_edit_from_entry, request["date_from"])
        self.set_entry(self.feed_edit_to_entry, request["date_to"])
        self.set_entry(self.feed_edit_food_entry, request["food_type"])
        self.set_entry(self.feed_edit_amount_entry, request["total_amount"])

    def add_snake(self):
        try:
            last_feed = self.snake_last_feed_entry.get().strip()

            if last_feed:
                datetime.strptime(last_feed, "%Y-%m-%d")
            else:
                last_feed = None

            snake = Snake(
                nickname=self.snake_name_entry.get().strip(),
                species_id=self.get_id_from_combobox(self.snake_species_combobox),
                age_years=int(self.snake_age_entry.get()),
                sex=self.snake_sex_combobox.get(),
                health_status=self.snake_health_combobox.get(),
                enclosure_id=self.get_id_from_combobox(self.snake_enclosure_combobox),
                last_feeding_date=last_feed,
                notes=self.snake_notes_entry.get().strip()
            )

            if not snake.nickname:
                raise ValueError("Введіть кличку або інвентарний номер змії.")

            snake_id, caretaker = self.serpentarium_service.add_snake(snake)

            messagebox.showinfo(
                "Змію додано",
                f"Запис №{snake_id} створено.\n\n"
                f"Автоматично призначено доглядача:\n{caretaker['full_name']}"
            )

            self.refresh_all()

        except Exception as error:
            messagebox.showerror("Помилка", str(error))

    def update_snake(self):
        try:
            if not self.selected_snake_id:
                raise ValueError("Спочатку двічі натисніть на змію в таблиці.")

            last_feed = self.snake_last_feed_entry.get().strip()

            if last_feed:
                datetime.strptime(last_feed, "%Y-%m-%d")
            else:
                last_feed = None

            snake = Snake(
                nickname=self.snake_name_entry.get().strip(),
                species_id=self.get_id_from_combobox(self.snake_species_combobox),
                age_years=int(self.snake_age_entry.get()),
                sex=self.snake_sex_combobox.get(),
                health_status=self.snake_health_combobox.get(),
                enclosure_id=self.get_id_from_combobox(self.snake_enclosure_combobox),
                last_feeding_date=last_feed,
                notes=self.snake_notes_entry.get().strip()
            )

            self.serpentarium_service.update_snake(self.selected_snake_id, snake)

            messagebox.showinfo("Готово", "Дані змії оновлено.")
            self.selected_snake_id = None
            self.refresh_all()

        except Exception as error:
            messagebox.showerror("Помилка", str(error))

    def add_species(self):
        try:
            species = Species(
                common_name=self.species_common_entry.get().strip(),
                latin_name=self.species_latin_entry.get().strip(),
                family_name=self.species_family_entry.get().strip(),
                is_venomous=self.species_venomous_var.get(),
                min_temperature=float(self.species_temp_min_entry.get()),
                max_temperature=float(self.species_temp_max_entry.get()),
                humidity_min=float(self.species_humidity_min_entry.get()),
                humidity_max=float(self.species_humidity_max_entry.get()),
                water_requirement=self.species_water_entry.get().strip(),
                food_type=self.species_food_entry.get().strip(),
                feeding_interval_days=int(self.species_interval_entry.get()),
                average_food_amount=float(self.species_amount_entry.get()),
                notes=self.species_notes_entry.get().strip()
            )

            self.serpentarium_service.add_species(species)
            messagebox.showinfo("Готово", "Вид додано до класифікатора.")
            self.refresh_all()

        except Exception as error:
            messagebox.showerror("Помилка", str(error))

    def update_species(self):
        try:
            if not self.selected_species_id:
                raise ValueError("Спочатку двічі натисніть на вид у таблиці.")

            species = Species(
                common_name=self.species_common_entry.get().strip(),
                latin_name=self.species_latin_entry.get().strip(),
                family_name=self.species_family_entry.get().strip(),
                is_venomous=self.species_venomous_var.get(),
                min_temperature=float(self.species_temp_min_entry.get()),
                max_temperature=float(self.species_temp_max_entry.get()),
                humidity_min=float(self.species_humidity_min_entry.get()),
                humidity_max=float(self.species_humidity_max_entry.get()),
                water_requirement=self.species_water_entry.get().strip(),
                food_type=self.species_food_entry.get().strip(),
                feeding_interval_days=int(self.species_interval_entry.get()),
                average_food_amount=float(self.species_amount_entry.get()),
                notes=self.species_notes_entry.get().strip()
            )

            self.serpentarium_service.update_species(self.selected_species_id, species)

            messagebox.showinfo("Готово", "Дані виду оновлено.")
            self.selected_species_id = None
            self.refresh_all()

        except Exception as error:
            messagebox.showerror("Помилка", str(error))

    def add_caretaker(self):
        try:
            caretaker = Caretaker(
                full_name=self.caretaker_name_entry.get().strip(),
                qualification=self.caretaker_qualification_entry.get().strip(),
                can_handle_venomous=self.caretaker_venomous_var.get(),
                phone=self.caretaker_phone_entry.get().strip(),
                max_animals=int(self.caretaker_max_entry.get())
            )

            self.serpentarium_service.add_caretaker(caretaker)
            messagebox.showinfo("Готово", "Доглядача додано.")
            self.refresh_all()

        except Exception as error:
            messagebox.showerror("Помилка", str(error))

    def update_caretaker(self):
        try:
            if not self.selected_caretaker_id:
                raise ValueError("Спочатку двічі натисніть на доглядача в таблиці.")

            caretaker = Caretaker(
                full_name=self.caretaker_name_entry.get().strip(),
                qualification=self.caretaker_qualification_entry.get().strip(),
                can_handle_venomous=self.caretaker_venomous_var.get(),
                phone=self.caretaker_phone_entry.get().strip(),
                max_animals=int(self.caretaker_max_entry.get())
            )

            self.serpentarium_service.update_caretaker(self.selected_caretaker_id, caretaker)

            messagebox.showinfo("Готово", "Дані доглядача оновлено.")
            self.selected_caretaker_id = None
            self.refresh_all()

        except Exception as error:
            messagebox.showerror("Помилка", str(error))

    def add_enclosure(self):
        try:
            enclosure = Enclosure(
                code=self.enclosure_code_entry.get().strip(),
                zone=self.enclosure_zone_entry.get().strip(),
                temperature=float(self.enclosure_temperature_entry.get()),
                humidity=float(self.enclosure_humidity_entry.get()),
                has_water=self.enclosure_water_var.get(),
                lighting_mode=self.enclosure_lighting_entry.get().strip(),
                capacity=int(self.enclosure_capacity_entry.get()),
                notes=self.enclosure_notes_entry.get().strip()
            )

            self.serpentarium_service.add_enclosure(enclosure)
            messagebox.showinfo("Готово", "Вольєр додано.")
            self.refresh_all()

        except Exception as error:
            messagebox.showerror("Помилка", str(error))

    def update_enclosure(self):
        try:
            if not self.selected_enclosure_id:
                raise ValueError("Спочатку двічі натисніть на вольєр у таблиці.")

            enclosure = Enclosure(
                code=self.enclosure_code_entry.get().strip(),
                zone=self.enclosure_zone_entry.get().strip(),
                temperature=float(self.enclosure_temperature_entry.get()),
                humidity=float(self.enclosure_humidity_entry.get()),
                has_water=self.enclosure_water_var.get(),
                lighting_mode=self.enclosure_lighting_entry.get().strip(),
                capacity=int(self.enclosure_capacity_entry.get()),
                notes=self.enclosure_notes_entry.get().strip()
            )

            self.serpentarium_service.update_enclosure(self.selected_enclosure_id, enclosure)

            messagebox.showinfo("Готово", "Дані вольєра оновлено.")
            self.selected_enclosure_id = None
            self.refresh_all()

        except Exception as error:
            messagebox.showerror("Помилка", str(error))

    def generate_feed_request(self):
        try:
            period = self.feed_period_combobox.get()

            created, date_from, date_to = self.feeding_service.generate_feed_request(period)

            if not created:
                messagebox.showinfo(
                    "Заявка",
                    "На обраний період немає змій, яким потрібно планове годування."
                )
            else:
                details = ""

                for request_id, food_type, amount in created:
                    details += f"{food_type}: {amount}\n"

                messagebox.showinfo(
                    "Заявку сформовано",
                    f"Період: {date_from} — {date_to}\n\n{details}"
                )

            self.refresh_all()

        except Exception as error:
            messagebox.showerror("Помилка", str(error))

    def update_feed_request(self):
        try:
            if not self.selected_feed_request_id:
                raise ValueError("Спочатку двічі натисніть на заявку в таблиці.")

            period_type = self.feed_edit_period_entry.get().strip()
            date_from = self.feed_edit_from_entry.get().strip()
            date_to = self.feed_edit_to_entry.get().strip()
            food_type = self.feed_edit_food_entry.get().strip()
            total_amount = float(self.feed_edit_amount_entry.get())

            datetime.strptime(date_from, "%Y-%m-%d")
            datetime.strptime(date_to, "%Y-%m-%d")

            self.serpentarium_service.update_feed_request(
                self.selected_feed_request_id,
                period_type,
                date_from,
                date_to,
                food_type,
                total_amount
            )

            messagebox.showinfo("Готово", "Заявку на корм оновлено.")
            self.selected_feed_request_id = None
            self.refresh_all()

        except Exception as error:
            messagebox.showerror("Помилка", str(error))