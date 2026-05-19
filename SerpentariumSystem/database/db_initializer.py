from pathlib import Path


class DatabaseInitializer:
    def __init__(self, db_connection, data_folder):
        self.db_connection = db_connection
        self.data_folder = Path(data_folder)

    def initialize(self, progress_callback=None):
        self.data_folder.mkdir(exist_ok=True)

        steps = [
            "Створення таблиці видів рептилій...",
            "Створення таблиці доглядачів...",
            "Створення таблиці вольєрів...",
            "Створення таблиці змій...",
            "Створення таблиці заявок на корми...",
            "Заповнення початкових даних...",
            "Перевірка бази даних..."
        ]

        connection = self.db_connection.get_connection()
        cursor = connection.cursor()

        commands = [
            self.create_species_table(),
            self.create_caretakers_table(),
            self.create_enclosures_table(),
            self.create_snakes_table(),
            self.create_feed_requests_table()
        ]

        for index, step in enumerate(steps):
            if progress_callback:
                progress_callback(index + 1, len(steps), step)

            if index < len(commands):
                cursor.execute(commands[index])
                connection.commit()

            if index == 5:
                self.insert_default_data(cursor)
                connection.commit()

            if index == 6:
                cursor.execute("PRAGMA integrity_check;")
                connection.commit()

        connection.close()

    def create_species_table(self):
        return """
        CREATE TABLE IF NOT EXISTS species (
            species_id INTEGER PRIMARY KEY AUTOINCREMENT,
            common_name TEXT NOT NULL,
            latin_name TEXT NOT NULL,
            family_name TEXT,
            is_venomous INTEGER NOT NULL DEFAULT 0,
            min_temperature REAL NOT NULL,
            max_temperature REAL NOT NULL,
            humidity_min REAL NOT NULL,
            humidity_max REAL NOT NULL,
            water_requirement TEXT NOT NULL,
            food_type TEXT NOT NULL,
            feeding_interval_days INTEGER NOT NULL,
            average_food_amount REAL NOT NULL,
            notes TEXT
        );
        """

    def create_caretakers_table(self):
        return """
        CREATE TABLE IF NOT EXISTS caretakers (
            caretaker_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            qualification TEXT NOT NULL,
            can_handle_venomous INTEGER NOT NULL DEFAULT 0,
            phone TEXT,
            max_animals INTEGER NOT NULL DEFAULT 20,
            is_active INTEGER NOT NULL DEFAULT 1
        );
        """

    def create_enclosures_table(self):
        return """
        CREATE TABLE IF NOT EXISTS enclosures (
            enclosure_id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            zone TEXT NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            has_water INTEGER NOT NULL DEFAULT 1,
            lighting_mode TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            notes TEXT
        );
        """

    def create_snakes_table(self):
        return """
        CREATE TABLE IF NOT EXISTS snakes (
            snake_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT NOT NULL,
            species_id INTEGER NOT NULL,
            age_years INTEGER NOT NULL,
            sex TEXT NOT NULL,
            health_status TEXT NOT NULL,
            enclosure_id INTEGER NOT NULL,
            caretaker_id INTEGER NOT NULL,
            arrival_date TEXT NOT NULL,
            last_feeding_date TEXT,
            notes TEXT,

            FOREIGN KEY (species_id) REFERENCES species(species_id),
            FOREIGN KEY (enclosure_id) REFERENCES enclosures(enclosure_id),
            FOREIGN KEY (caretaker_id) REFERENCES caretakers(caretaker_id)
        );
        """

    def create_feed_requests_table(self):
        return """
        CREATE TABLE IF NOT EXISTS feed_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            period_type TEXT NOT NULL,
            date_from TEXT NOT NULL,
            date_to TEXT NOT NULL,
            food_type TEXT NOT NULL,
            total_amount REAL NOT NULL,
            created_at TEXT NOT NULL
        );
        """

    def insert_default_data(self, cursor):
        cursor.execute("SELECT COUNT(*) FROM species")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                """
                INSERT INTO species (
                    common_name, latin_name, family_name, is_venomous,
                    min_temperature, max_temperature, humidity_min, humidity_max,
                    water_requirement, food_type, feeding_interval_days,
                    average_food_amount, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        "Королівська кобра",
                        "Ophiophagus hannah",
                        "Elapidae",
                        1,
                        26,
                        30,
                        60,
                        80,
                        "Постійна поїлка",
                        "Миші/щури",
                        7,
                        1.5,
                        "Отруйний вид. Потрібен доглядач із допуском."
                    ),
                    (
                        "Маїсовий полоз",
                        "Pantherophis guttatus",
                        "Colubridae",
                        0,
                        24,
                        29,
                        40,
                        60,
                        "Постійна поїлка",
                        "Миші",
                        6,
                        1.0,
                        "Неотруйний вид."
                    ),
                    (
                        "Тигровий пітон",
                        "Python bivittatus",
                        "Pythonidae",
                        0,
                        27,
                        32,
                        55,
                        75,
                        "Велика ємність з водою",
                        "Щури/кролі",
                        14,
                        3.0,
                        "Потребує просторого вольєра."
                    )
                ]
            )

        cursor.execute("SELECT COUNT(*) FROM caretakers")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                """
                INSERT INTO caretakers (
                    full_name, qualification, can_handle_venomous,
                    phone, max_animals, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        "Іваненко Олександр Петрович",
                        "Герпетолог вищої категорії",
                        1,
                        "+380671111111",
                        25,
                        1
                    ),
                    (
                        "Коваленко Марина Сергіївна",
                        "Доглядач рептилій",
                        0,
                        "+380672222222",
                        18,
                        1
                    ),
                    (
                        "Бондар Дмитро Ігорович",
                        "Старший доглядач, допуск до отруйних рептилій",
                        1,
                        "+380673333333",
                        20,
                        1
                    )
                ]
            )

        cursor.execute("SELECT COUNT(*) FROM enclosures")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                """
                INSERT INTO enclosures (
                    code, zone, temperature, humidity,
                    has_water, lighting_mode, capacity, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        "A-01",
                        "Отруйні рептилії",
                        28,
                        70,
                        1,
                        "12/12",
                        2,
                        "Вольєр із підвищеним рівнем безпеки."
                    ),
                    (
                        "B-01",
                        "Неотруйні рептилії",
                        27,
                        55,
                        1,
                        "12/12",
                        4,
                        "Стандартний тераріум."
                    ),
                    (
                        "B-02",
                        "Великі рептилії",
                        30,
                        65,
                        1,
                        "14/10",
                        2,
                        "Вольєр для великих змій."
                    )
                ]
            )