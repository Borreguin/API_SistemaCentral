import random as r
from mongoengine import *
import datetime as dt
from dto.mongo_engine_handler.Consignment import *
from dto.mongo_engine_handler.Comp_Root import ComponenteRoot
from dto.mongo_engine_handler.Comp_Internal import ComponenteInternal
from dto.mongo_engine_handler.Comp_Leaf import ComponenteLeaf
from settings import initial_settings as init

DEBUG = True

d_n = dt.datetime.now()

ini_date = dt.datetime(year=d_n.year, month=d_n.month, day=1) - dt.timedelta(days=30)
end_date = dt.datetime(year=d_n.year, month=d_n.month, day=d_n.day) - dt.timedelta(days=d_n.day)
t_delta = end_date - ini_date
n_minutos_evaluate = t_delta.days * (60 * 24) + t_delta.seconds // 60 + t_delta.seconds % 60


def test_leafs_and_consignments():
    # This test creates:
    # 15 leafs and for each leaf it creates 1000 random consignments
    # what does it probes?:
    # collision of unique ID if it exists.
    # It allows to know whether a folder could collapse in one already created or not
    # since id are created using uuid.uuid4 and since is based on current time and some randomness should not collapse
    mongo_config = init.MONGOCLIENT_SETTINGS
    mongo_config.update(dict(db="DB_DISP_EMS"))
    connect(**mongo_config)

    new_component = ComponenteRoot(block="ROOT_TEST", name=f"ROOT_{str(r.randint(1, 1000))}")
    new_internal_component = ComponenteInternal(name="INTERNAL_TEST_1")
    new_component.add_internal_component([new_internal_component])
    new_component.save()
    print(f"Componentes creados y guardados en DB: \n{new_component} \n{new_internal_component}")
    # to save the id of the created leafs
    id_leafs = list()
    # count number of created folders
    n_folders = 0
    # count number of consignments
    n_consignaciones = 0
    # create a collection of leafs
    print("Creando hojas y consignaciones por cada hoja:")
    for i in range(1, 15):
        new_leaf_component = ComponenteLeaf(name=f"COMPONENTE_LEAF_TEST_{i}")
        success, msg = new_internal_component.add_leaf_component([new_leaf_component])
        if not success:
            print(msg)
            continue  # continue with the next

        # if success the following goes
        new_component.save()
        id_leafs.append(new_leaf_component.public_id)
        new_leaf_component.create_consignments_container()
        consignaciones = new_leaf_component.consignments
        for j in range(1, 1000):
            n_days = r.uniform(1, 1000)
            t_ini_consig = end_date - dt.timedelta(days=n_days)
            t_end_consig = t_ini_consig + dt.timedelta(days=r.uniform(0, 4), hours=r.uniform(0, 23))
            consignacion = Consignment(fecha_inicio=t_ini_consig, fecha_final=t_end_consig,
                                       no_consignacion=str(r.randint(1, 1000)))
            success, msg = consignaciones.insert_consignments(consignacion)
            if not success:
                # print(msg)
                # It was not inserted because some time conflict with others
                continue  # continue with the next

            # if success the following goes
            n_consignaciones += 1
            success_create = consignacion.create_folder()
            if success_create:
                n_folders += 1
        consignaciones.save()
        print(f"{new_internal_component} \t {new_leaf_component}")
        print(f"{consignaciones}")

    # saving all changes
    new_component.save()
    print("Todos los cambios guardados")

    print("Leyendo desde base de datos: "
          "\n-Midiendo el tiempo que toma en leer las consignaciones en todas las hojas")
    print("Tiempo acumulado por hoja")
    t_ini = dt.datetime.now()
    new_component_db = ComponenteRoot.objects(public_id=new_component.public_id).first()
    for id_leaf in id_leafs:
        success, result = new_component_db.search_leaf_by_id(id_leaf)
        if success:
            if result.consignments is None:
                print(f"Error con esta hoja: {result}")
            else:
                temp = result.consignments.consignaciones
                total_time_consignment = 0
                for t in temp:
                    total_time_consignment += t.t_minutos
                print(f"{result}: {total_time_consignment} minutos")

    print("Finalización de lectura:")
    t_end = dt.datetime.now()
    t_delta_time = t_end - t_ini
    print(f"Tiempo total de lectura: {t_delta_time.microseconds / 1000} milisegundos")
    print(f"No. Total de consignaciones = {n_consignaciones} \nNo. Total de folders = {n_folders}")
    disconnect()
    return True


def test_path():
    mongo_config = init.MONGOCLIENT_SETTINGS
    mongo_config.update(dict(db="DB_DISP_EMS"))
    connect(**mongo_config)

    new_component = ComponenteRoot(block="ROOT_TEST", name=f"ROOT_{str(r.randint(1, 1000))}")
    new_internal_component = ComponenteInternal(name="INTERNAL_TEST_1")
    new_component.add_internal_component([new_internal_component])
    new_leaf_component = ComponenteLeaf(name="LEAF_TEST_1")
    new_internal_component.add_leaf_component([new_leaf_component])
    new_component.save()
    consignaciones = Consignments(id_elemento=new_leaf_component.public_id)
    n_days = 30
    t_ini_consig = end_date - dt.timedelta(days=n_days)
    t_end_consig = t_ini_consig + dt.timedelta(days=r.uniform(0, 4), hours=r.uniform(0, 23))
    consignacion = Consignment(fecha_inicio=t_ini_consig, fecha_final=t_end_consig,
                               no_consignacion=str(r.randint(1, 1000)))
    success, msg = consignaciones.insert_consignments(consignacion)
    if not success:
        print(msg)

    consignacion.create_folder()
    consignaciones.save()
    new_leaf_component.consignments = consignaciones
    new_component.save()

    success_del, msg = consignaciones.delete_consignment_by_id(consignacion.no_consignacion)
    print(msg)
    consignaciones.save()
    new_component.save()

    disconnect()
    return True


if __name__ == "__main__":
    # test_path()
    test_leafs_and_consignments()
