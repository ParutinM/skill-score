from pathlib import Path

import toml
from omegaconf import DictConfig
from sqlalchemy import create_engine, Engine
from sqlalchemy.schema import CreateSchema
from sqlalchemy_utils import database_exists, create_database
from general_tables import Base, ServiceBase


def create_db(cfg: DictConfig) -> None:
    # creates empty db if not exists
    engine = create_engine(f"{cfg.dialect}://{cfg.username}:{cfg.password}@{cfg.host}:{cfg.port}/{cfg.database}")
    if not database_exists(engine.url):
        create_database(engine.url)

    conn = engine.connect()

    # creates schemas if not exists
    for schema in ['general', 'service']:
        conn.execute(CreateSchema(schema, if_not_exists=True))
        conn.commit()

    # create all tables
    # Base.metadata.create_all(engine)
    ServiceBase.metadata.create_all(engine)
    conn.close()


if __name__ == "__main__":
    with open('../.streamlit/secrets.toml') as f:
        cfg = DictConfig(toml.loads(f.read()))
    create_db(cfg.connections.postgresql)
