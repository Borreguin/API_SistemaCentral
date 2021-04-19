import random as r
from dto.mongo_engine_handler.Info.Consignment import *
from dto.mongo_engine_handler.Components.Comp_Root import ComponenteRoot
from dto.mongo_engine_handler.Components.Comp_Internal import ComponenteInternal
from dto.mongo_engine_handler.Components.Comp_Leaf import ComponenteLeaf
from dto.mongo_engine_handler.Sources.ReportSource import ReportSource
from dto.mongo_engine_handler.Sources.Sources import Sources
from settings import initial_settings as init

DEBUG = True

d_n = dt.datetime.now()

ini_date = dt.datetime(year=d_n.year, month=d_n.month, day=1) - dt.timedelta(days=30)
end_date = dt.datetime(year=d_n.year, month=d_n.month, day=d_n.day) - dt.timedelta(days=d_n.day)
t_delta = end_date - ini_date
n_minutos_evaluate = t_delta.days * (60 * 24) + t_delta.seconds // 60 + t_delta.seconds % 60


def test_validate_sources():

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
   # parameters=dict(collection_name='REPORT|FinalReports',fecha_inicio='2020-06-01',
       #             fecha_final='2020-06-02',field='disponibilidad_promedio_porcentage')

    #source_db=Sources(type=init.AVAILABLE_SOURCES[2],parameters=parameters,
    #                   root_id=new_component.public_id,leaf_id=new_leaf_component.public_id)
    #source_db.save()
    #success=source_db.check_source()
    #print(success)

    report=ReportSource(root_id=new_component.public_id,leaf_id=new_leaf_component.public_id,fuente=init.AVAILABLE_SOURCES[1],
                        fecha_inicio='2020-06-01',fecha_final='2020-06-02',responsable='dp')
    #AÑADIR INDISPONIBILIDADES
    #CALCULAR DISPONIBILIDAD DEL REPORTE
    report.save()
    #Reporte mensual
    parameters_2=dict(fecha_inicio='2020-06-03',
                    fecha_final='2020-06-04')
    source_manual=Sources(type=init.AVAILABLE_SOURCES[1],parameters=parameters_2,
                       root_id=new_component.public_id,leaf_id=new_leaf_component.public_id)
    source_manual.save()
    success=source_manual.check_source()
    print(success)

if __name__ == "__main__":
    test_validate_sources()