import random as r
from dto.mongo_engine_handler.Info.Consignment import *
from dto.mongo_engine_handler.Components.Comp_Root import ComponenteRoot
from dto.mongo_engine_handler.Components.Comp_Internal import ComponenteInternal
from dto.mongo_engine_handler.Components.Comp_Leaf import ComponenteLeaf
from dto.mongo_engine_handler.Sources.ReportSource import ReportSource
from dto.mongo_engine_handler.Sources.Sources import Sources
from settings import initial_settings as init
from dto.mongo_engine_handler.Info.Manual import Manual, Manuals_entry

DEBUG = True

d_n = dt.datetime.now()

ini_date = dt.datetime(year=d_n.year, month=d_n.month, day=1) - dt.timedelta(days=30)
end_date = dt.datetime(year=d_n.year, month=d_n.month, day=d_n.day) - dt.timedelta(days=d_n.day)
t_delta = end_date - ini_date
n_minutos_evaluate = t_delta.days * (60 * 24) + t_delta.seconds // 60 + t_delta.seconds % 60


def test_Sources():

    mongo_config = init.MONGOCLIENT_SETTINGS
    mongo_config.update(dict(db="DB_DISP_EMS"))
    connect(**mongo_config)
    new_component = ComponenteRoot(block="ROOT_TEST", name=f"ROOT_{str(r.randint(1, 1000))}")
    new_component.save()
    new_internal_component = ComponenteInternal(name="INTERNAL_TEST_1")
    new_component.add_internal_component([new_internal_component])
    new_component.save()
    new_leaf_component = ComponenteLeaf(name="LEAF_TEST_1")
    new_internal_component.add_leaf_component([new_leaf_component])
    new_component.save()
   #FUENTES
    case=init.AVAILABLE_SOURCES[3]
    #CASO MANUAL
    if case==init.AVAILABLE_SOURCES[1]:
        # Atributos de la Fuente
        parameters = dict(fecha_inicio='2020-06-03 16:00:00',
                            fecha_final='2020-06-04 16:00:00')
        source_manual = Sources(type=init.AVAILABLE_SOURCES[1], parameters=parameters,
                                root_id=new_component.public_id, leaf_id=new_leaf_component.public_id)
        #Caso reporte existente
        #source_manual = Sources(type=init.AVAILABLE_SOURCES[1], parameters=parameters,
        #                        root_id="b3593421-99cb-4433-8940-5b332c184b99", leaf_id="1cb90113-cf41-4257-8eb9-1cdae6908ed6")
        source_manual.save()
        #Validar fuente
        success,msg = source_manual.check_source()
        if success:
            # Guardar ingreso manual
            new_manual_entry=Manuals_entry(root_id=new_component.public_id,leaf_id=new_leaf_component.public_id)
            new_manual=Manual(fecha_inicio=parameters['fecha_inicio'],fecha_final=parameters['fecha_final'])
            new_manual_entry.insert_manuals(new_manual)
            new_manual_entry.save()
            #Generación de reporte
            Report_Manual=source_manual.get_data()
            Report_Manual.save()
            return True
        return False
    #CASO DESDE BASE DE DATOS
    if case == init.AVAILABLE_SOURCES[2]:
        #CASO NEGATIVO
        # parameters=dict(collection_name='REPORT|FinalReports',fecha_inicio='2021-06-01 00:00:00',
        #                 fecha_final='2021-06-02 00:00:00',field='disponibilidad_promedio_porcentage')
        #CASO POSITIVO
        parameters=dict(collection_name='REPORT|FinalReports',fecha_inicio='2020-06-01 00:00:00',
                        fecha_final='2020-06-02 00:00:00',field='disponibilidad_promedio_porcentage')

        source_bd = Sources(type=init.AVAILABLE_SOURCES[2], parameters=parameters,
                                root_id=new_component.public_id, leaf_id=new_leaf_component.public_id)
        source_bd.save()
        #Validar fuente
        success,msg = source_bd.check_source()
        if success:
            #GENERAR REPORTE
            Report_BD=source_bd.get_data()
            Report_BD.save()
            return True
        return False
    #CASO DESDE PI
    if case == init.AVAILABLE_SOURCES[3]:
        #TODO: REVISAR CONDICION DE FILTRADO
        #TODO: REVISAR FUENTE
        parameters = dict(type=init.AVAILABLE_SOURCES[3],piserver_name=None, fecha_inicio='2020-06-01 00:00:00',
                          fecha_final='2020-06-02 00:00:00', tag_name='UTR_D_PERIPA_IEC8705104.SV',condicion_filtrado="DISPONIBLE")
        source_PI = Sources(type=init.AVAILABLE_SOURCES[3], parameters=parameters,
                            root_id=new_component.public_id, leaf_id=new_leaf_component.public_id)
        source_PI.save()

        #Validar fuente
        success,msg = source_PI.check_source()
        if success:
            #GENERAR REPORTE
            Report_PI=source_PI.get_data()
            Report_PI.save()
            return True
        return False

    else:
        return False








if __name__ == "__main__":
    test_Sources()