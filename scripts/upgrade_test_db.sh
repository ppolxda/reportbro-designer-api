export DB_URL='postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/reportbro-test'
poetry run python -m reportbro_designer_api.backend.dbcli upgradedb
export DB_URL='mysql+aiomysql://root:root@127.0.0.1:3306/reportbro-test'
poetry run python -m reportbro_designer_api.backend.dbcli upgradedb
export DB_URL='sqlite+aiosqlite:///./reportbro.db'
poetry run python -m reportbro_designer_api.backend.dbcli upgradedb
