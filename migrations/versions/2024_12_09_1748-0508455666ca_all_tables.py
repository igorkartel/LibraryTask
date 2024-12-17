"""all tables

Revision ID: 0508455666ca
Revises:
Create Date: 2024-12-09 17:48:58.819161

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0508455666ca"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "authors",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("surname", sa.String(), nullable=False),
        sa.Column("nationality", sa.String(), nullable=False),
        sa.Column("photo_s3_url", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title_rus", sa.String(), nullable=False),
        sa.Column("title_origin", sa.String(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("available_for_loan", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "genres",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "readers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("fathers_name", sa.String(), nullable=False),
        sa.Column("surname", sa.String(), nullable=False),
        sa.Column("passport_nr", sa.String(), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("address", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("passport_nr"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("surname", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("role", sa.Enum("ADMIN", "LIBRARIAN", name="userroleenum"), nullable=False),
        sa.Column("is_blocked", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "author_book_association",
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["authors.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("book_id", "author_id"),
    )
    op.create_table(
        "book_instances",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("imprint_year", sa.Integer(), nullable=True),
        sa.Column("pages", sa.Integer(), nullable=True),
        sa.Column("cover_s3_url", sa.String(), nullable=True),
        sa.Column("value", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("price_per_day", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("status", sa.Enum("AVAILABLE", "LOANED", "LOST", name="bookstatusenum"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "genre_book_association",
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("genre_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["genre_id"], ["genres.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("book_id", "genre_id"),
    )
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reader_id", sa.Integer(), nullable=False),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "CLOSED", name="orderstatusenum"), nullable=False),
        sa.Column("planned_return_date", sa.Date(), nullable=False),
        sa.Column("fact_return_date", sa.Date(), nullable=False),
        sa.Column("overdue_cost", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("damaged_books", sa.Integer(), nullable=False),
        sa.Column("damage_cost", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("lost_books", sa.Integer(), nullable=False),
        sa.Column("lost_cost", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("total_cost", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(
            ["reader_id"],
            ["readers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "order_book_instance_association",
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("book_instance_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["book_instance_id"], ["book_instances.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("order_id", "book_instance_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("order_book_instance_association")
    op.drop_table("orders")
    op.drop_table("genre_book_association")
    op.drop_table("book_instances")
    op.drop_table("author_book_association")
    op.drop_table("users")
    op.drop_table("readers")
    op.drop_table("genres")
    op.drop_table("books")
    op.drop_table("authors")
    # ### end Alembic commands ###
