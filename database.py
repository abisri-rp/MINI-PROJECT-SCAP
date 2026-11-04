import sqlite3

try:
    import oracledb
except ImportError:
    oracledb = None


class Database:
    def __init__(self, db_type="sqlite", **config):
        self.db_type = db_type.lower()
        self.connection = None
        self.cursor = None

        self.connect(**config)
        self.initialize_database()

    # --------------------------------------------------
    # DATABASE CONNECTION
    # --------------------------------------------------
    def connect(self, **config):
        try:
            if self.db_type == "sqlite":
                database_path = config.get("database", "scap.db")

                self.connection = sqlite3.connect(database_path)
                self.connection.execute("PRAGMA foreign_keys = ON")

            elif self.db_type == "oracle":
                if oracledb is None:
                    raise ImportError(
                        "Oracle driver is missing. Install it using: "
                        "pip install oracledb"
                    )

                self.connection = oracledb.connect(
                    user=config["user"],
                    password=config["password"],
                    dsn=config["dsn"]
                )

            else:
                raise ValueError(
                    f"Unsupported database type: {self.db_type}"
                )

            self.cursor = self.connection.cursor()

        except Exception as exc:
            self.connection = None
            self.cursor = None

            raise RuntimeError(
                f"Could not connect to the database: {exc}"
            ) from exc

    # --------------------------------------------------
    # DATABASE INITIALIZATION
    # --------------------------------------------------
    def initialize_database(self):
        if self.connection is None:
            raise RuntimeError(
                "Cannot initialize database: no active connection."
            )

        try:
            self.create_tables()
            self.run_migrations()
            self.seed_admin()

            self.connection.commit()

        except Exception:
            self.connection.rollback()
            raise

    # --------------------------------------------------
    # TABLE CREATION
    # Keep your existing CREATE TABLE statements here.
    # --------------------------------------------------
    def create_tables(self):
        # Move your existing table-creation code here.
        pass

    # --------------------------------------------------
    # DATABASE MIGRATIONS
    # Keep your existing ALTER TABLE logic here.
    # --------------------------------------------------
    def run_migrations(self):
        # Move your existing migration code here.
        pass

    # --------------------------------------------------
    # DEFAULT ADMIN
    # Keep your existing admin seeding code here.
    # --------------------------------------------------
    def seed_admin(self):
        # Move your existing admin insertion code here.
        pass
