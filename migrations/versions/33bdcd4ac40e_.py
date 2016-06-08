"""empty message

Revision ID: 33bdcd4ac40e
Revises: 131926f0bc2b
Create Date: 2016-06-07 16:40:35.558757

"""

# revision identifiers, used by Alembic.
revision = '33bdcd4ac40e'
down_revision = '131926f0bc2b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Boolean, DateTime, Date

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    ### end Alembic commands ###
    gas_level = table(
        'gas_level',
        column('id', Integer),
        column('name', String)
    )

    op.bulk_insert(
        gas_level, [
            # Electrical group
            {'id': 1, 'name': 'Normal'},
            {'id': 2, 'name': 'Caution'},
            {'id': 3, 'name': 'Danger'},
            {'id': 4, 'name': 'Extreme'}
        ]
    )

    # op.add_column('test_type', sa.Column('group_id', Integer))
    # op.add_column('test_type', sa.Column('is_group', Boolean, nullable=False, default=False))

    # Test types must be added automatical
    test_type_table = table(
        'test_type',
        column('id', Integer),
        column('name', String),
        column('group_id', Integer),
        column('is_group', Boolean),
    )

    op.bulk_insert(
        test_type_table, [
            # Electrical group
            {'id': 1, 'name': 'Electrical', 'is_group': True},
            {'id': 2, 'name': 'Bushing Cap. and PF', 'group_id': 1, 'is_group': False},
            {'id': 3, 'name': 'Winding Cap. and PF', 'group_id': 1, 'is_group': False},
            {'id': 4, 'name': 'Winding Cap. and PF Doble', 'group_id': 1, 'is_group': False},
            {'id': 5, 'name': 'Insulation resistance', 'group_id': 1, 'is_group': False},
            {'id': 6, 'name': 'Visual inspection', 'group_id': 1, 'is_group': False},
            {'id': 7, 'name': 'Resistance; winding/contact', 'group_id': 1, 'is_group': False},
            {'id': 8, 'name': 'Degree of Polymerization (DP)', 'group_id': 1, 'is_group': False},
            {'id': 9, 'name': 'Turns ratio test (TTR)', 'group_id': 1, 'is_group': False},
            # Fluid group
            {'id': 10, 'name': 'Fluid', 'is_group': True},
            # Syringe subgroup
            {'id': 11, 'name': 'Syringe', 'is_group': True, 'group_id': 10},
            {'id': 12, 'name': 'Dissolved gas', 'group_id': 11, 'is_group': False},
            {'id': 13, 'name': 'Water', 'group_id': 11, 'is_group': False},
            {'id': 14, 'name': 'Furans', 'group_id': 11, 'is_group': False},
            {'id': 15, 'name': 'Inhibitor', 'group_id': 11, 'is_group': False},
            {'id': 16, 'name': 'PBC', 'group_id': 11, 'is_group': False},
            # Jar subgroup
            {'id': 17, 'name': 'Jar', 'is_group': True, 'group_id': 10},
            {'id': 18, 'name': 'Dielec.D1816(1mm)(kV)', 'group_id': 17, 'is_group': False},
            {'id': 19, 'name': 'Acidity(D974)', 'group_id': 17, 'is_group': False},
            {'id': 20, 'name': 'Density(D1298)', 'group_id': 17, 'is_group': False},
            {'id': 21, 'name': 'PCB', 'group_id': 17, 'is_group': False},
            {'id': 22, 'name': 'Inhibitor', 'group_id': 17, 'is_group': False},
            {'id': 23, 'name': 'Pour point', 'group_id': 17, 'is_group': False},
            {'id': 24, 'name': 'Dielec.D1816(2mm)(kV)', 'group_id': 17, 'is_group': False},
            {'id': 25, 'name': 'Color(D1500)', 'group_id': 17, 'is_group': False},
            {'id': 26, 'name': 'PF 25C(D924)', 'group_id': 17, 'is_group': False},
            {'id': 27, 'name': 'Particles', 'group_id': 17, 'is_group': False},
            {'id': 28, 'name': 'Metals in oil', 'group_id': 17, 'is_group': False},
            {'id': 29, 'name': 'Viscosity', 'group_id': 17, 'is_group': False},
            {'id': 30, 'name': 'Dielec. D877(kV)', 'group_id': 17, 'is_group': False},
            {'id': 31, 'name': 'IFT (D971)', 'group_id': 17, 'is_group': False},
            {'id': 32, 'name': 'PF 100C (D924)', 'group_id': 17, 'is_group': False},
            {'id': 33, 'name': 'Furans', 'group_id': 17, 'is_group': False},
            {'id': 34, 'name': 'Water', 'group_id': 17, 'is_group': False},
            {'id': 35, 'name': 'Corr. sulfur', 'group_id': 17, 'is_group': False},
            {'id': 36, 'name': 'Dielec. IEC-156(kV)', 'group_id': 17, 'is_group': False},
            {'id': 37, 'name': 'Visual (D1524)', 'group_id': 17, 'is_group': False},
            # 4-ml vial subgroup
            {'id': 38, 'name': '4 - ml vial', 'is_group': True, 'group_id': 10},
            {'id': 39, 'name': 'PCB', 'group_id': 38, 'is_group': False},
            {'id': 40, 'name': 'Antioxidant', 'group_id': 38, 'is_group': False},
        ]
    )

    # test_param_table = table(
    #     'test_param',
    #     column('id', Integer),
    #     column('name', String),
    # )
    # op.bulk_insert(
    #     test_param_table, [
    #
    #     ]
    # )

    # test_type_param_table = table(
    #     'test_type_param',
    #     column('id', Integer),
    #     column('test_type_id', Integer),
    #     column('test_param_id', Integer),
    # )
    # op.bulk_insert(
    #     test_type_param_table, [
    #
    #     ]
    # )

    # move test_type specific connections from campaign to test_results
    # we drop tables and on start app will create them from models
    # move test_type specific connections from campaign to test_results
    # op.drop_column('campaign', 'test_type_id')
    op.drop_column('campaign', 'sampling_point_id')
    op.drop_column('campaign', 'test_reason_id')
    op.drop_column('campaign', 'date_analyse')
    # op.drop_column('campaign', 'campaign_status_id')
    # op.rename_table('campaign_status', 'test_status')
    op.add_column('test_result', sa.Column('tests_type_id', Integer))
    op.add_column('test_result', sa.Column('sampling_point_id', Integer))
    op.add_column('test_result', sa.Column('test_reason_id', Integer))
    op.add_column('test_result', sa.Column('date_analyse', DateTime, index=True))
    op.add_column('test_result', sa.Column('test_status_id', Integer))
    # add new table of individual for test type params
    # op.create_table('test_result_param_values',
    #     sa.Column('id', Integer, primary_key=True),
    #     sa.Column('test_result_id', Integer),
    #     sa.Column('test_param_id', Integer),
    #     sa.Column('test_param_value', String(100)),
    #     sa.ForeignKeyConstraint(['test_result_id'], [u'test_result.id'], name=u'test_result_param_values_test_result_id_fkey'),
    #     sa.ForeignKeyConstraint(['test_param_id'], [u'test_param.id'], name=u'test_result_param_values_test_param_id_fkey')
    # )


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    ### end Alembic commands ###
    test_type_table = table(
        'test_type',
        column('id', Integer),
        column('name', String),
    )

    op.drop_table('test_type')

    op.execute(sql="TRUNCATE test_type;")
    op.execute(sql="TRUNCATE gas_level;")

    # rollback movement of test_type specifik connection from campaign to test_results
    # we drop tables and on start app will create them from models
    op.drop_table('campaign')
    op.drop_table('test_result')
    op.drop_table('test_result_param_values')
    op.rename_table('test_status', 'campaign_status')