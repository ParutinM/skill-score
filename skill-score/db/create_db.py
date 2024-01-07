from pathlib import Path

import yaml
from omegaconf import DictConfig
from sqlalchemy import create_engine, Engine
from sqlalchemy.schema import CreateSchema
from sqlalchemy_utils import database_exists, create_database
from general_tables import Base


def create_db(cfg: DictConfig) -> None:
    # creates empty db if not exists
    engine = create_engine(f"{cfg.driver}://{cfg.host}:{cfg.port}/{cfg.database.name}")
    if not database_exists(engine.url):
        create_database(engine.url)

    conn = engine.connect()

    # creates schemas if not exists
    for schema in cfg.database.schemas:
        conn.execute(CreateSchema(schema, if_not_exists=True))
        conn.commit()

    # create all tables
    Base.metadata.create_all(engine)
    conn.close()


if __name__ == "__main__":
    with open(Path(__file__).parent / "config.yaml") as f:
        cfg = DictConfig(yaml.safe_load(f))
    create_db(cfg)
