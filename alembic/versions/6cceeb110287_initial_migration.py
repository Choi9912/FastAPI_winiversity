"""Initial migration

Revision ID: 6cceeb110287
Revises: 
Create Date: 2024-10-01 14:26:02.405772

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = "6cceeb110287"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # 먼저 의존성이 있는 테이블들을 삭제합니다
    op.drop_table("code_submission_missions")
    op.drop_table("multiple_choice_submissions")
    op.drop_table("multiple_choice_missions")
    op.drop_table("mission_submissions")

    # 그 다음 기본 테이블인 missions를 삭제합니다
    op.drop_table("missions")

    # payments 테이블 관련 변경사항
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_columns = inspector.get_columns("payments")
    existing_column_names = [column["name"] for column in existing_columns]

    if "imp_uid" not in existing_column_names:
        op.add_column("payments", sa.Column("imp_uid", sa.String(), nullable=False))
    if "merchant_uid" not in existing_column_names:
        op.add_column(
            "payments", sa.Column("merchant_uid", sa.String(), nullable=False)
        )

    op.alter_column(
        "payments", "expiration_date", existing_type=sa.DATETIME(), nullable=True
    )

    # 인덱스가 존재하지 않을 경우에만 생성
    existing_indexes = [index["name"] for index in inspector.get_indexes("payments")]
    if "ix_payments_imp_uid" not in existing_indexes:
        op.create_index(
            op.f("ix_payments_imp_uid"), "payments", ["imp_uid"], unique=True
        )
    if "ix_payments_merchant_uid" not in existing_indexes:
        op.create_index(
            op.f("ix_payments_merchant_uid"), "payments", ["merchant_uid"], unique=True
        )
    # ### end Alembic commands ###
    # ### end Alembic commands ###
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_payments_merchant_uid"), table_name="payments")
    op.drop_index(op.f("ix_payments_imp_uid"), table_name="payments")
    op.alter_column(
        "payments", "expiration_date", existing_type=sa.DATETIME(), nullable=False
    )
    op.drop_column("payments", "merchant_uid")
    op.drop_column("payments", "imp_uid")
    op.create_table(
        "mission_submissions",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("user_id", sa.INTEGER(), nullable=False),
        sa.Column("mission_id", sa.INTEGER(), nullable=False),
        sa.Column("submitted_answer", sa.VARCHAR(), nullable=False),
        sa.Column("is_correct", sa.BOOLEAN(), nullable=False),
        sa.Column("submitted_at", sa.DATETIME(), nullable=False),
        sa.ForeignKeyConstraint(
            ["mission_id"],
            ["missions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_mission_submissions_id", "mission_submissions", ["id"], unique=False
    )
    op.create_table(
        "multiple_choice_submissions",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("submission_id", sa.INTEGER(), nullable=False),
        sa.Column("selected_option", sa.VARCHAR(length=1), nullable=False),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["mission_submissions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("submission_id"),
    )
    op.create_index(
        "ix_multiple_choice_submissions_id",
        "multiple_choice_submissions",
        ["id"],
        unique=False,
    )
    op.create_table(
        "multiple_choice_missions",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("mission_id", sa.INTEGER(), nullable=False),
        sa.Column("options", sqlite.JSON(), nullable=False),
        sa.Column("correct_answer", sa.VARCHAR(length=1), nullable=False),
        sa.ForeignKeyConstraint(
            ["mission_id"],
            ["missions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("mission_id"),
    )
    op.create_index(
        "ix_multiple_choice_missions_id",
        "multiple_choice_missions",
        ["id"],
        unique=False,
    )
    op.create_table(
        "missions",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("course", sa.VARCHAR(length=20), nullable=False),
        sa.Column("question", sa.VARCHAR(), nullable=False),
        sa.Column("type", sa.VARCHAR(length=20), nullable=False),
        sa.Column("exam_type", sa.VARCHAR(length=10), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_missions_id", "missions", ["id"], unique=False)
    op.create_index("ix_missions_course", "missions", ["course"], unique=False)
    op.create_table(
        "code_submission_missions",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("mission_id", sa.INTEGER(), nullable=False),
        sa.Column("problem_description", sa.VARCHAR(), nullable=False),
        sa.Column("initial_code", sa.VARCHAR(), nullable=True),
        sa.Column("test_cases", sqlite.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["mission_id"],
            ["missions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("mission_id"),
    )
    op.create_index(
        "ix_code_submission_missions_id",
        "code_submission_missions",
        ["id"],
        unique=False,
    )
    # ### end Alembic commands ###
