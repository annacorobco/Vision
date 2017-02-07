import os
import pypyodbc
import datetime

from app.diagnostic.models import EquipmentType, TestResult, Campaign, FluidProfile, \
    Country, TestReason, TestType, TestStatus, Equipment, Norm, Location, Manufacturer, \
    NormPhysic
from app.users.models import User
from app import db


DB_PATH = os.path.abspath('./Example_English.MDB')
odbc_connection_str = 'DRIVER={MDBTools};DBQ=%s;unicode_results=True;ansi=True;' % (DB_PATH,)


# Helper functions
def timestamp_to_date(val):
    if not val:
        return ''
    else:
        return datetime.datetime.strptime(val, '%m/%d/%y %H:%M:%S')


def clean_duplicates(data):
    return list(set(data) - set([None, '']))


def strip(data):
    return map(lambda x: x.strip() if isinstance(x, str) else None, data)


# Equipment records
def get_equipment(cursor):
    query = __equipment_sql()
    cursor.execute(query)
    return cursor.fetchall()


def fetch_additional_data(equipments):
    data = {
        'manufacturer': [],
        'location': []
    }
    for equipment in equipments:
        data['manufacturer'].append(equipment[7])   # Manufacturier
        data['location'].append(equipment[3])       # Localisation

    data['manufacturer'] = clean_duplicates(strip(data['manufacturer']))
    data['location'] = clean_duplicates(strip(data['location']))
    return data


def fetch_equipment_data(equipments):
    data = {
        'items': []
    }
    user_id = db.session.query(User).filter_by(name='admin').first().id
    for equipment in equipments:
        data['items'].append(
            {
                'equipment_number': equipment[0],
                'equipment_type_id': equipment[1].strip() if equipment[1] else None,   # Get type id
                'location_id': equipment[3].strip() if equipment[3] else None,         # Get location id
                'modifier': bool(equipment[9]),
                'comments': equipment[14],
                'assigned_to_id': user_id,
                'nbr_of_tap_change_ltc': equipment[60],     # Nbr_Change_Prise
                'status': None,
                'phys_position': equipment[97],      # PosPhys
                'tension4': equipment[104],     #Tension4
                'validated': equipment[150],     #Valider
                'invalidation': equipment[151],  #EnValidation
                'prev_serial_number': equipment[152],   #NoSerieEquipeAnc
                'prev_equipment_number': equipment[153],    #NoEquipementAnc
                'sibling': equipment[154],   #Fratrie
                'name': None,
                'serial': equipment[6], #NoSerieEquipe
                'manufacturer_id': equipment[7].strip() if equipment[7] else None,    #get id
                'manufactured': equipment[8],   #annee
                'description': equipment[5], #Description
                'frequency': equipment[54], #Frequence
                'tie_status': equipment[93],   #LocTie
                'norm_physic': equipment[61]    #NormePhy
            }
        )
    return data


def generate_insert_migration(data):
    query = ''
    for key, values in data.items():
        query += 'INSERT INTO {} (name) VALUES {};\n'.format(key, ','.join(map(lambda x: "('{}')".format(x), values)))
    return query


def generate_insert_equipment_migration(data):
    query = ''
    items = data['items']
    for item in items:
        item = generate_additional_selects(item)
        query += 'INSERT INTO equipment ({}) VALUES ({}); \n'.format(
            ', '.join(item.keys()),
            ', '.join(map(format_value, item.values()))
        )
    return query


def generate_additional_selects(item):
    if item['equipment_type_id']:
        item['equipment_type_id'] = "(SELECT id FROM equipment_type WHERE code = '{}')".format(
            item['equipment_type_id'])
    if item['location_id']:
        item['location_id'] = "(SELECT id FROM location WHERE name = '{}')".format(item['location_id'])
    if item['manufacturer_id']:
        item['manufacturer_id'] = "(SELECT id FROM manufacturer WHERE name = '{}')".format(item['manufacturer_id'])
    return item


def format_value(val):
    if val is None:
        return 'NULL'
    else:
        return "'{}'".format(val)


def save_additional_data(data):
    inserted_data = {}
    for name in data['location']:
        db.session.add(Location(name=name))
    for name in data['manufacturer']:
        db.session.add(Manufacturer(name=name))
    try:
        db.session.commit()
        print("Added locations and manufacturers")
    except Exception as e:
        db.session.rollback()
    return inserted_data


def save_equipment(data):
    items = data['items']
    for item in items:
        # Save equipment norms
        # equipment_norm = NormPhysicData(db.session.query(NormPhysic).filter_by(name=item['norm_physic']))
        del item['norm_physic']

        item = get_additional_info(item)
        db.session.add(Equipment(**item))
    try:
        db.session.commit()
        print('Added equipment')
    except Exception as e:
        db.session.rollback()
    return True


def get_additional_info(item):
    """ Getting foreign key ids """
    # TODO Get all items at once, not in the loop
    if item['frequency']:
        item['frequency'] = '{}'.format(item['frequency'])
    if item['equipment_type_id']:
        item['equipment_type_id'] = db.session.query(EquipmentType).filter_by(code=item['equipment_type_id']).first().id
    item['location_id'] = db.session.query(Location).filter_by(name=item['location_id']).first().id if item['location_id'] else 1
    item['manufacturer_id'] = db.session.query(Manufacturer).filter_by(name=item['manufacturer_id']).first().id if item['manufacturer_id'] else None
    return item


# Norms
def get_norms(cursor):
    query = __norm_physic_sql()
    cursor.execute(query)
    return cursor.fetchall()


def fetch_norm_physic(norms):
    data = {
        'items': []
    }
    norms_in_db = db.session.query(NormPhysic).all()
    existing_norms = [norm.name for norm in norms_in_db]

    for norm in norms:
        if norm[0] in existing_norms:
            continue

        data['items'].append(
            {
                'name': norm[0], #NORME
                'acid_min': norm[2],    #Acide_Min
                'acid_max': norm[3],    #Acide_Max
                'ift_min': norm[4],
                'ift_max': norm[5],
                'd1816_min': norm[6],
                'd1816_max': norm[7],
                'd877_min': norm[8],
                'd877_max': norm[9],
                'color_min': norm[10],
                'color_max': norm[11],
                'density_min': norm[12],
                'density_max': norm[13],
                'pf20_min': norm[14],   #FACTEURP_Min
                'pf20_max': norm[15],   #FACTEURP_Max
                'water_min': norm[16],  #EAU_Min
                'water_max': norm[17],  #EAU_Max
                'flashpoint_min': norm[18], #PECLAIR_Min
                'flashpoint_max': norm[19], #PECLAIR_Max
                'pourpoint_min': norm[20],  #PECOULEMENT_Min
                'pourpoint_max': norm[21],  #PECOULEMENT_Max
                'viscosity_min': norm[22],  #VISCOSITE_Min
                'viscosity_max': norm[23],  #VISCOSITE_Max
                'd1816_2_min': norm[24],
                'd1816_2_max': norm[25],
                'p100_min': norm[26],   #FacteurP100_MIN
                'p100_max': norm[27],   #FacteurP100_MAX
                'fluid_type_id': norm[28],  #TODO: TypeHuile - ?
                'equipment_id': -1,     #TODO: Why do we need equipment_id in the table - ?
                'cei156_min': norm[29],
                'cei156_max': norm[30],
                'equipment_type_id': db.session.query(EquipmentType).filter_by(code=norm[1]).first().id if norm[1] else None,
            }
        )
    return data


def save_items(data, model):
    items = data['items']
    for item in items:
        db.session.add(model(**item))
    try:
        db.session.commit()
        print('Added {}'.format(model))
    except Exception as e:
        print(e)
        db.session.rollback()
    return True


def process_equipment_records(cursor):
    # Get all equipment
    equipments = get_equipment(cursor)

    # Prepare and save additional data from equipment
    additional_data = fetch_additional_data(equipments)
    save_additional_data(data=additional_data)

    # Save equipment
    equipment_data = fetch_equipment_data(equipments)
    save_equipment(equipment_data)


def process_norms(cursor):
    norm_physic = get_norms(cursor)
    norm_physic = fetch_norm_physic(norm_physic)
    save_items(norm_physic, NormPhysic)


def run_import():
    connection = pypyodbc.connect(odbc_connection_str)
    connection.add_output_converter(pypyodbc.SQL_TYPE_TIMESTAMP, timestamp_to_date)
    cursor = connection.cursor()

    # Save equipment and data related to it
    process_equipment_records(cursor)
    # Save predefined norms
    process_norms(cursor)

    cursor.close()
    connection.close()


# SQL
def __equipment_sql():
    # Name all column names because cannot get them from cursor
    # (they are fetched as Chinese letters)
    # to know exact position of column on retrieve
    all_cols = 'NoEquipement,TypeEquipement,Site,Localisation,LitreHuile,Description,NoSerieEquipe,Manufacturier,Annee,Modifier,' \
               'NoExploitation,Scelle,CouvSoude,TriPhase,Commentaire,Capteur,NoClient,DateV,Ins_Vis_Par,CommentaireV,' \
               'Compteur,Filtreur,Tension1,Tension2,Tension3,Puissance1,Puissance2,Puissance3,Bobine,Auto_Transfo,' \
               'Raccord_Bobine1,Raccord_Bobine2,Raccord_Bobine3,BIL1,BIL2,BIL3,Ecran_Electro1,Ecran_Electro2,Ecran_Electro3,ChangeurP1,' \
               'ChangeurP2,ChangeurP3,Bushing_Neutre1,Bushing_Neutre2,Bushing_Neutre3,Resistance_Neutre1,ResInf1,Resistance_Neutre2,ResInf2,Bobine_Materiel,' \
               'Formule_Ratio,Etiquette1,Etiquette2,Etiquette3,Frequence,Impedance1,Imp_Base1,Impedance2,Imp_Base2,Temp_elevation,' \
               'Nbr_Change_Prise,NormePhy,NormeGD,NormeFur,Formule_Ratio2,Etiquette4,Etiquette5,Etiquette6,TypeHuile,Resistance_Neutre0,' \
               'ResInf0,Bush_Serie1,Bush_Serie2,Bush_Serie3,Bush_Serie4,Bush_Serie5,Bush_Serie6,Bush_Serie7,Bush_Serie8,Bush_Serie9,' \
               'Bush_Serie10,Bush_Serie11,Bush_Serie12,LocAmont1,LocAmont2,LocAmont3,LocAmont4,LocAmont5,LocAval1,LocAval2,' \
               'LocAval3,LocAval4,LocAval5,LocTie,LocEntretienEtat,LocAnalyseEtat,LocPos,PosPhys,MWActuel,MVARActuel,' \
               'MWReserve,MVARReserve,MWUltime,MVARUltime,Tension4,Puissance4,Raccord_Bobine4,BIL4,Ecran_Electro4,ChangeurP4,' \
               'Bushing_Neutre4,Resistance_Neutre3,Etiquette7,Etiquette8,ResInf3,Formule_Ratio3,PuisForce11,PuisForce12,PuisForce13,PuisForce14,' \
               'PuisForce21,PuisForce22,PuisForce23,PuisForce24,Impedance3,Imp_Base3,Bush_Mfr_H1,Bush_Mfr_H2,Bush_Mfr_H3,Bush_Mfr_HN,' \
               'Bush_Mfr_X1,Bush_Mfr_X2,Bush_Mfr_X3,Bush_Mfr_XN,Bush_Mfr_T1,Bush_Mfr_T2,Bush_Mfr_T3,Bush_Mfr_TN,Bush_Mfr_Q1,Bush_Mfr_Q2,' \
               'Bush_Mfr_Q3,Bush_Mfr_QN,Bush_Type_H,Bush_Type_HN,Bush_Type_X,Bush_Type_XN,Bush_Type_T,Bush_Type_TN,Bush_Type_Q,Bush_Type_QN,' \
               'Valider,EnValidation,NoSerieEquipeAnc,NoEquipementAnc,Fratrie'
    query = "SELECT {} FROM Equipement".format(all_cols)
    return query


def __norm_physic_sql():
    # Name all column names because cannot get them from cursor
    # (they are fetched as Chinese letters)
    # to know exact position of column on retrieve
    all_cols = 'NORME,TypeEquipement,Acide_Min,Acide_Max,IFT_Min,IFT_Max,D1816_Min,D1816_Max,D877_Min,D877_Max,' \
               'COULEUR_Min,COULEUR_Max,DENSITE_Min,DENSITE_Max,FACTEURP_Min,FACTEURP_Max,EAU_Min,EAU_Max,PECLAIR_Min,PECLAIR_Max,' \
               'PECOULEMENT_Min,PECOULEMENT_Max,VISCOSITE_Min,VISCOSITE_Max,D1816_2_MIN,D1816_2_MAX,FacteurP100_MIN,FacteurP100_MAX,TypeHuile,CEI156_Min,' \
               'CEI156_Max'
    query = "SELECT {} FROM NormePhysique".format(all_cols)
    return query


if __name__ == '__main__':
    run_import()
