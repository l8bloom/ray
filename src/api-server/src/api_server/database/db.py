from pydantic import BaseModel
from sqlalchemy import URL, create_engine, text
from sqlalchemy.orm import sessionmaker

from api_server.services.env import AppEnv


class DatabaseConfig(BaseModel):
    """Configuration for a database setup, with a set of default values"""

    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_DRIVER_NAME: str


class Database:
    """Singleton database(sync nature) knows how to connect and start new sessions."""

    _databases = {}

    def __init__(self, db_cfg: DatabaseConfig):
        self.db_cfg = db_cfg
        self.conn_info = self.db_conn_info(self.db_cfg)
        self.engine = create_engine(self.conn_info)
        self.session_factory = self._session_factory()

    def _ping(self):
        with self.session_factory() as session:
            session.execute(text("SELECT 1;"))
        print(f"PONG Connected to {self.db_conn_info(self.db_cfg)}")

    def _session_factory(self) -> sessionmaker:
        """Creates new session."""
        return sessionmaker(bind=self.engine)

    @classmethod
    def create(cls, db_cfg: DatabaseConfig | None = None) -> "Database":
        """Creates new instance of Database if not created already."""
        db_cfg = db_cfg or DatabaseConfig()
        conn_info = cls.db_conn_info(db_cfg).render_as_string()
        db = cls._databases.get(conn_info)
        if db is None:
            db = cls(db_cfg=db_cfg)
            db._ping()
            cls._databases[conn_info] = db
        return db

    @staticmethod
    def db_conn_info(db_cfg: DatabaseConfig) -> URL:
        """Generate database connection string"""

        return URL.create(
            db_cfg.DATABASE_DRIVER_NAME,
            username=db_cfg.DATABASE_USER,
            password=db_cfg.DATABASE_PASSWORD,
            host=db_cfg.DATABASE_HOST,
            port=db_cfg.DATABASE_PORT,
            database=db_cfg.DATABASE_NAME,
        )


def get_db(env: AppEnv) -> Database:
    db_cfg = DatabaseConfig(
        DATABASE_USER=env.PG_USER,
        DATABASE_PASSWORD=env.PG_PASSWORD,
        DATABASE_HOST=env.PG_HOST,
        DATABASE_PORT=env.PG_PORT,
        DATABASE_NAME=env.PG_DATABASE,
        DATABASE_DRIVER_NAME=env.PG_DRIVER_NAME,
    )

    return Database.create(db_cfg=db_cfg)
