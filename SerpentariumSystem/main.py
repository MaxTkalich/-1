from pathlib import Path
import tkinter as tk

from database.db_connection import DatabaseConnection
from database.db_initializer import DatabaseInitializer

from services.serpentarium_service import SerpentariumService
from services.feeding_service import FeedingService

from ui.splash_screen import SplashScreen
from ui.main_window import MainWindow


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "serpentarium.db"


def main():
    db_connection = DatabaseConnection(DB_PATH)
    db_initializer = DatabaseInitializer(db_connection, DATA_DIR)

    first_start = not db_connection.exists()

    if first_start:
        root = tk.Tk()
        root.withdraw()

        splash = SplashScreen(root, db_initializer)
        root.wait_window(splash)

        root.destroy()
    else:
        db_initializer.initialize()

    serpentarium_service = SerpentariumService(db_connection)
    feeding_service = FeedingService(db_connection)

    app = MainWindow(
        serpentarium_service=serpentarium_service,
        feeding_service=feeding_service
    )

    app.mainloop()


if __name__ == "__main__":
    main()