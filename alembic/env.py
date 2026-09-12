import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 1. Thêm thư mục gốc dự án vào sys.path để Alembic nhận diện được package `app`
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

# 2. Import config và models từ ứng dụng
from app.config import settings
from app.database import Base
import app.models  # Bắt buộc import models để Alembic quét các bảng

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 3. Ghi đè chuỗi kết nối Database từ app/config.py vào cấu hình Alembic
config.set_main_option("sqlalchemy.url", settings.CHUOI_KET_NOI)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name:
    fileConfig(config.config_file_name)

# 4. Gán metadata của Base để Alembic biết các bảng cần so sánh/tạo migration
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Xử lý riêng cho SQLite nếu dùng SQLite (như cấu hình mặc định)
    connectable = config.attributes.get("connection", None)

    if connectable is None:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            render_as_batch=True  # Rất quan trọng khi dùng SQLite để hỗ trợ ALTER TABLE
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()