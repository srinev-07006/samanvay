"""initial schema with pg_trgm and timeline immutable trigger

Revision ID: 001_initial
Revises:
Create Date: 2026-10-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pg_trgm extension
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    # Create institutions table
    op.create_table(
        'institutions',
        sa.Column('permanent_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('region', sa.String(), nullable=False),
        sa.Column('pincode', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('permanent_id')
    )
    op.create_index(op.f('ix_institutions_name'), 'institutions', ['name'], unique=False)
    op.create_index(op.f('ix_institutions_permanent_id'), 'institutions', ['permanent_id'], unique=False)
    op.create_index(op.f('ix_institutions_region'), 'institutions', ['region'], unique=False)
    op.create_index(op.f('ix_institutions_pincode'), 'institutions', ['pincode'], unique=False)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('bureau_cell', sa.String(), nullable=True),
        sa.Column('region', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create cases table
    op.create_table(
        'cases',
        sa.Column('case_id', sa.String(), nullable=False),
        sa.Column('institution_id', sa.String(), nullable=True),
        sa.Column('source_bureau', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('current_bureau', sa.String(), nullable=False),
        sa.Column('assigned_officer', sa.String(), nullable=False),
        sa.Column('last_action', sa.String(), nullable=False),
        sa.Column('next_action_required', sa.String(), nullable=False),
        sa.Column('expected_disposal_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.permanent_id'], ),
        sa.PrimaryKeyConstraint('case_id')
    )
    op.create_index(op.f('ix_cases_case_id'), 'cases', ['case_id'], unique=False)
    op.create_index(op.f('ix_cases_category'), 'cases', ['category'], unique=False)
    op.create_index(op.f('ix_cases_institution_id'), 'cases', ['institution_id'], unique=False)
    op.create_index(op.f('ix_cases_source_bureau'), 'cases', ['source_bureau'], unique=False)
    op.create_index(op.f('ix_cases_status'), 'cases', ['status'], unique=False)

    # Create timeline_events table
    op.create_table(
        'timeline_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.String(), nullable=False),
        sa.Column('officer', sa.String(), nullable=False),
        sa.Column('bureau_cell', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('remarks', sa.Text(), nullable=False),
        sa.Column('attached_documents', sa.String(), nullable=True),
        sa.Column('transfer_escalation_info', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.case_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_timeline_events_case_id'), 'timeline_events', ['case_id'], unique=False)

    # Add trigger for timeline immutability (block UPDATE and DELETE)
    op.execute("""
    CREATE OR REPLACE FUNCTION block_timeline_modifications()
    RETURNS TRIGGER AS $$
    BEGIN
        RAISE EXCEPTION 'Timeline events are immutable and append-only. UPDATE and DELETE are prohibited.';
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE TRIGGER enforce_timeline_immutability
    BEFORE UPDATE OR DELETE ON timeline_events
    FOR EACH ROW
    EXECUTE FUNCTION block_timeline_modifications();
    """)

    # Create overlap_flags table
    op.create_table(
        'overlap_flags',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_a_id', sa.String(), nullable=False),
        sa.Column('case_b_id', sa.String(), nullable=False),
        sa.Column('institution_id', sa.String(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('state', sa.String(), nullable=False),
        sa.Column('decided_by', sa.String(), nullable=True),
        sa.Column('decided_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['case_a_id'], ['cases.case_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['case_b_id'], ['cases.case_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.permanent_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_overlap_flags_institution_id'), 'overlap_flags', ['institution_id'], unique=False)

    # Create alerts table
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('case_id', sa.String(), nullable=False),
        sa.Column('target_bureau_or_user', sa.String(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['cases.case_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_target_bureau_or_user'), 'alerts', ['target_bureau_or_user'], unique=False)

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('entity', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index(op.f('ix_alerts_target_bureau_or_user'), table_name='alerts')
    op.drop_table('alerts')
    op.drop_index(op.f('ix_overlap_flags_institution_id'), table_name='overlap_flags')
    op.drop_table('overlap_flags')

    op.execute("DROP TRIGGER IF EXISTS enforce_timeline_immutability ON timeline_events;")
    op.execute("DROP FUNCTION IF EXISTS block_timeline_modifications();")

    op.drop_index(op.f('ix_timeline_events_case_id'), table_name='timeline_events')
    op.drop_table('timeline_events')

    op.drop_index(op.f('ix_cases_status'), table_name='cases')
    op.drop_index(op.f('ix_cases_source_bureau'), table_name='cases')
    op.drop_index(op.f('ix_cases_institution_id'), table_name='cases')
    op.drop_index(op.f('ix_cases_category'), table_name='cases')
    op.drop_index(op.f('ix_cases_case_id'), table_name='cases')
    op.drop_table('cases')

    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

    op.drop_index(op.f('ix_institutions_pincode'), table_name='institutions')
    op.drop_index(op.f('ix_institutions_region'), table_name='institutions')
    op.drop_index(op.f('ix_institutions_permanent_id'), table_name='institutions')
    op.drop_index(op.f('ix_institutions_name'), table_name='institutions')
    op.drop_table('institutions')
