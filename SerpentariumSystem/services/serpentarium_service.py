from datetime import date


class SerpentariumService:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def query(self, sql, params=()):
        connection = self.db_connection.get_connection_with_rows()
        cursor = connection.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        connection.close()
        return rows

    def execute(self, sql, params=()):
        connection = self.db_connection.get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, params)
        connection.commit()
        last_id = cursor.lastrowid
        connection.close()
        return last_id

    def get_species(self):
        return self.query("SELECT * FROM species ORDER BY common_name")

    def get_caretakers(self):
        return self.query("SELECT * FROM caretakers ORDER BY full_name")

    def get_enclosures(self):
        return self.query("SELECT * FROM enclosures ORDER BY code")

    def get_feed_requests(self):
        return self.query("SELECT * FROM feed_requests ORDER BY request_id DESC")

    def get_snakes(self):
        return self.query(
            """
            SELECT 
                s.snake_id,
                s.nickname,
                sp.common_name,
                sp.is_venomous,
                s.age_years,
                s.sex,
                s.health_status,
                e.code AS enclosure_code,
                c.full_name AS caretaker_name,
                s.arrival_date,
                s.last_feeding_date
            FROM snakes s
            JOIN species sp ON sp.species_id = s.species_id
            JOIN enclosures e ON e.enclosure_id = s.enclosure_id
            JOIN caretakers c ON c.caretaker_id = s.caretaker_id
            ORDER BY s.snake_id DESC
            """
        )

    def add_species(self, species):
        return self.execute(
            """
            INSERT INTO species (
                common_name, latin_name, family_name, is_venomous,
                min_temperature, max_temperature,
                humidity_min, humidity_max,
                water_requirement, food_type,
                feeding_interval_days, average_food_amount, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                species.common_name,
                species.latin_name,
                species.family_name,
                species.is_venomous,
                species.min_temperature,
                species.max_temperature,
                species.humidity_min,
                species.humidity_max,
                species.water_requirement,
                species.food_type,
                species.feeding_interval_days,
                species.average_food_amount,
                species.notes
            )
        )

    def update_species(self, species_id, species):
        self.execute(
            """
            UPDATE species
            SET common_name = ?,
                latin_name = ?,
                family_name = ?,
                is_venomous = ?,
                min_temperature = ?,
                max_temperature = ?,
                humidity_min = ?,
                humidity_max = ?,
                water_requirement = ?,
                food_type = ?,
                feeding_interval_days = ?,
                average_food_amount = ?,
                notes = ?
            WHERE species_id = ?
            """,
            (
                species.common_name,
                species.latin_name,
                species.family_name,
                species.is_venomous,
                species.min_temperature,
                species.max_temperature,
                species.humidity_min,
                species.humidity_max,
                species.water_requirement,
                species.food_type,
                species.feeding_interval_days,
                species.average_food_amount,
                species.notes,
                species_id
            )
        )

    def add_caretaker(self, caretaker):
        return self.execute(
            """
            INSERT INTO caretakers (
                full_name, qualification, can_handle_venomous,
                phone, max_animals, is_active
            )
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                caretaker.full_name,
                caretaker.qualification,
                caretaker.can_handle_venomous,
                caretaker.phone,
                caretaker.max_animals
            )
        )

    def update_caretaker(self, caretaker_id, caretaker):
        self.execute(
            """
            UPDATE caretakers
            SET full_name = ?,
                qualification = ?,
                can_handle_venomous = ?,
                phone = ?,
                max_animals = ?
            WHERE caretaker_id = ?
            """,
            (
                caretaker.full_name,
                caretaker.qualification,
                caretaker.can_handle_venomous,
                caretaker.phone,
                caretaker.max_animals,
                caretaker_id
            )
        )

    def add_enclosure(self, enclosure):
        return self.execute(
            """
            INSERT INTO enclosures (
                code, zone, temperature, humidity,
                has_water, lighting_mode, capacity, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                enclosure.code,
                enclosure.zone,
                enclosure.temperature,
                enclosure.humidity,
                enclosure.has_water,
                enclosure.lighting_mode,
                enclosure.capacity,
                enclosure.notes
            )
        )

    def update_enclosure(self, enclosure_id, enclosure):
        self.execute(
            """
            UPDATE enclosures
            SET code = ?,
                zone = ?,
                temperature = ?,
                humidity = ?,
                has_water = ?,
                lighting_mode = ?,
                capacity = ?,
                notes = ?
            WHERE enclosure_id = ?
            """,
            (
                enclosure.code,
                enclosure.zone,
                enclosure.temperature,
                enclosure.humidity,
                enclosure.has_water,
                enclosure.lighting_mode,
                enclosure.capacity,
                enclosure.notes,
                enclosure_id
            )
        )

    def find_suitable_enclosures(self, species_id):
        species = self.query(
            "SELECT * FROM species WHERE species_id = ?",
            (species_id,)
        )

        if not species:
            return []

        species = species[0]

        return self.query(
            """
            SELECT 
                e.*,
                (
                    SELECT COUNT(*) 
                    FROM snakes s 
                    WHERE s.enclosure_id = e.enclosure_id
                ) AS current_count
            FROM enclosures e
            WHERE e.temperature BETWEEN ? AND ?
              AND e.humidity BETWEEN ? AND ?
              AND e.has_water = 1
              AND (
                    SELECT COUNT(*) 
                    FROM snakes s 
                    WHERE s.enclosure_id = e.enclosure_id
                  ) < e.capacity
            ORDER BY current_count ASC, e.code ASC
            """,
            (
                species["min_temperature"],
                species["max_temperature"],
                species["humidity_min"],
                species["humidity_max"]
            )
        )

    def choose_caretaker_for_species(self, species_id):
        species = self.query(
            "SELECT * FROM species WHERE species_id = ?",
            (species_id,)
        )

        if not species:
            raise ValueError("Обраний вид рептилії не знайдено.")

        is_venomous = species[0]["is_venomous"]

        candidates = self.query(
            """
            SELECT 
                c.*,

                (
                    SELECT COUNT(*) 
                    FROM snakes s 
                    WHERE s.caretaker_id = c.caretaker_id
                ) AS total_animals,

                (
                    SELECT COUNT(*) 
                    FROM snakes s 
                    WHERE s.caretaker_id = c.caretaker_id
                      AND s.species_id = ?
                ) AS same_species_count

            FROM caretakers c
            WHERE c.is_active = 1
              AND (? = 0 OR c.can_handle_venomous = 1)
              AND (
                    SELECT COUNT(*) 
                    FROM snakes s 
                    WHERE s.caretaker_id = c.caretaker_id
                  ) < c.max_animals
            ORDER BY 
                same_species_count ASC,
                total_animals ASC,
                c.can_handle_venomous DESC,
                c.full_name ASC
            LIMIT 1
            """,
            (species_id, is_venomous)
        )

        if not candidates:
            raise ValueError(
                "Немає доступного доглядача з потрібною кваліфікацією."
            )

        return candidates[0]

    def add_snake(self, snake):
        caretaker = self.choose_caretaker_for_species(snake.species_id)

        snake_id = self.execute(
            """
            INSERT INTO snakes (
                nickname, species_id, age_years, sex,
                health_status, enclosure_id, caretaker_id,
                arrival_date, last_feeding_date, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snake.nickname,
                snake.species_id,
                snake.age_years,
                snake.sex,
                snake.health_status,
                snake.enclosure_id,
                caretaker["caretaker_id"],
                date.today().isoformat(),
                snake.last_feeding_date,
                snake.notes
            )
        )

        return snake_id, caretaker

    def update_snake(self, snake_id, snake):
        self.execute(
            """
            UPDATE snakes
            SET nickname = ?,
                species_id = ?,
                age_years = ?,
                sex = ?,
                health_status = ?,
                enclosure_id = ?,
                last_feeding_date = ?,
                notes = ?
            WHERE snake_id = ?
            """,
            (
                snake.nickname,
                snake.species_id,
                snake.age_years,
                snake.sex,
                snake.health_status,
                snake.enclosure_id,
                snake.last_feeding_date,
                snake.notes,
                snake_id
            )
        )

    def update_feed_request(
        self,
        request_id,
        period_type,
        date_from,
        date_to,
        food_type,
        total_amount
    ):
        self.execute(
            """
            UPDATE feed_requests
            SET period_type = ?,
                date_from = ?,
                date_to = ?,
                food_type = ?,
                total_amount = ?
            WHERE request_id = ?
            """,
            (
                period_type,
                date_from,
                date_to,
                food_type,
                total_amount,
                request_id
            )
        )