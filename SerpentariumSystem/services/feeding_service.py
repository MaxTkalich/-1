from datetime import date, datetime, timedelta


class FeedingService:
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

    def generate_feed_request(self, period_type):
        if period_type == "День":
            days = 1
        elif period_type == "Тиждень":
            days = 7
        else:
            days = 30

        date_from = date.today()
        date_to = date_from + timedelta(days=days - 1)

        snakes = self.query(
            """
            SELECT 
                s.snake_id,
                s.last_feeding_date,
                sp.food_type,
                sp.feeding_interval_days,
                sp.average_food_amount
            FROM snakes s
            JOIN species sp ON sp.species_id = s.species_id
            """
        )

        totals = {}

        for snake in snakes:
            if snake["last_feeding_date"]:
                last_feed = datetime.strptime(
                    snake["last_feeding_date"],
                    "%Y-%m-%d"
                ).date()
            else:
                last_feed = date_from - timedelta(
                    days=snake["feeding_interval_days"]
                )

            next_feed = last_feed + timedelta(
                days=snake["feeding_interval_days"]
            )

            if date_from <= next_feed <= date_to:
                food_type = snake["food_type"]
                amount = snake["average_food_amount"]
                totals[food_type] = totals.get(food_type, 0) + amount

        created_requests = []

        for food_type, amount in totals.items():
            request_id = self.execute(
                """
                INSERT INTO feed_requests (
                    period_type, date_from, date_to,
                    food_type, total_amount, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    period_type,
                    date_from.isoformat(),
                    date_to.isoformat(),
                    food_type,
                    amount,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )

            created_requests.append((request_id, food_type, amount))

        return created_requests, date_from, date_to