import random as r
from mongoengine import *
import datetime as dt

from dto.mongo_engine_handler.Components import *
from settings import initial_settings as init
DEBUG = True

d_n = dt.datetime.now()
ini_date = dt.datetime(year=d_n.year, month=d_n.month-1, day=1)
end_date = dt.datetime(year=d_n.year, month=d_n.month, day=d_n.day) - dt.timedelta(days=d_n.day)
t_delta = end_date - ini_date
n_minutos_evaluate = t_delta.days*(60*24) + t_delta.seconds//60 + t_delta.seconds % 60


def test():
    mongo_config = init.MONGOCLIENT_SETTINGS
    mongo_config.update(dict(db="DB_DISP_EMS"))
    connect(**mongo_config)

    new_component=ComponenteRoot(bloque="ROOT_TEST",nombre=f"ROOT_{str(r.randint(1,1000))}")
    new_component.save()
    new_internal_component=ComponenteInternal(name="INTERNAL_TEST_1")
    new_component.add_internal_component([new_internal_component])
    new_component.save()
    new_leaf_component=ComponenteLeaf(name="LEAF_TEST_1")
    success,msg=new_internal_component.add_leaf_component([new_leaf_component])
    new_component.save()
    new_leaf_component_2 = ComponenteLeaf(name="LEAF_TEST_2")
    new_internal_component.add_leaf_component([new_leaf_component_2])
    new_component.save()
    new_leaf_component_3 = ComponenteLeaf(name="LEAF_TEST_3")
    new_leaf_component_4 = ComponenteLeaf(name="LEAF_TEST_4")
    new_internal_component.change_leaf_to_internal(new_leaf_component.public_id,[new_leaf_component_3,new_leaf_component_4])
    new_component.save()
    disconnect()
    return True


if __name__ == "__main__":
    test()