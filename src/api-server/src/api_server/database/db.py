import uuid

from pydantic import BaseModel
from sqlalchemy import URL, create_engine, text
from sqlalchemy.orm import sessionmaker

from api_server.contracts.services.incoming import BatchJobStatus
from api_server.services.env import AppEnv
from api_server.services.time import utc_datetime

from .orm_models import Batch, BatchPrompt


class DatabaseConfig(BaseModel):
    """Configuration for a database setup."""

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
    def create(cls, db_cfg: DatabaseConfig) -> "Database":
        """Creates new instance of Database if not created already."""
        db_cfg = db_cfg
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

    def save_inference_result(
        self,
        batch_id: uuid.UUID,
        inference_outputs,
        inference_time_ms: float,
    ):
        """Saves inference outputs and associated metrics."""
        with self.session_factory() as session:
            batch_prompts = []
            total_in = 0
            total_out = 0

            for prompt_res in inference_outputs:
                completion = prompt_res.outputs[0]
                in_cnt = len(prompt_res.prompt_token_ids)
                out_cnt = len(completion.token_ids)

                total_in += in_cnt
                total_out += out_cnt

                bp = BatchPrompt(
                    batch_id=batch_id,
                    prompt=prompt_res.prompt,
                    in_tokens_cnt=in_cnt,
                    answer=completion.text,
                    out_tokens_cnt=out_cnt,
                    finish_reason=completion.finish_reason,
                )
                batch_prompts.append(bp)

            session.add_all(batch_prompts)

            # for precision use tokens / milisecond
            tokens_per_ms = (
                total_out / inference_time_ms if inference_time_ms > 0 else 0
            )
            tps = tokens_per_ms * 1_000

            # Update batch job
            session.query(Batch).filter(Batch.id == batch_id).update(
                {
                    "status": BatchJobStatus.COMPLETE,
                    "finished_at": utc_datetime(),
                    "total_in_tokens": total_in,
                    "total_out_tokens": total_out,
                    "tokens_per_second": tps,
                }
            )

            session.commit()


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
