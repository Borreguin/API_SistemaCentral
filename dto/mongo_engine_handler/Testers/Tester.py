import random as r
from mongoengine import *
import datetime as dt

from dto.mongo_engine_handler.Components.Comp_Root import ComponenteRoot
from dto.mongo_engine_handler.Components.Comp_Internal import ComponenteInternal
from dto.mongo_engine_handler.Components.Comp_Leaf import ComponenteLeaf
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

    new_component=ComponenteRoot(block="ROOT_TEST",name=f"ROOT_{str(r.randint(1,1000))}")
    new_component.save()
    new_internal_component=ComponenteInternal(name="INTERNAL_TEST_1")
    new_component.add_internal_component([new_internal_component])
    new_component.save()
    new_internal_component_2=ComponenteInternal(name="INTERNAL_TEST_2")
    new_component.add_internal_component([new_internal_component_2])
    new_component.save()

    new_leaf_component=ComponenteLeaf(name="LEAF_TEST_1")
    success,msg=new_internal_component.add_leaf_component([new_leaf_component])
    new_component.save()

    new_internal_component_3 = ComponenteInternal(name="INTERNAL_TEST_3")
    new_internal_component_2.add_internal_component([new_internal_component_3])
    new_internal_component_4 = ComponenteInternal(name="INTERNAL_TEST_4")
    new_internal_component_3.add_internal_component([new_internal_component_4])
    new_component.save()
    # id_to_search=new_internal_component_4.public_id
    # success,result=new_component.search_internal_by_id(id_to_search)

    # #----------------TEST CHANGE LEAF TO INTERNAL-----OK--------
    # new_leaf_component_2 = ComponenteLeaf(name="LEAF_TEST_2")
    # new_internal_component.add_leaf_component([new_leaf_component_2])
    # new_component.save()
    # new_leaf_component_3 = ComponenteLeaf(name="LEAF_TEST_3")
    # new_leaf_component_4 = ComponenteLeaf(name="LEAF_TEST_4")
    # new_internal_component.change_leaf_to_internal(new_leaf_component.public_id,[new_leaf_component_3,new_leaf_component_4])


    #new_component.change_internal_to_root(new_internal_component_2.public_id,[new_internal_component],"BLOQUE_ROOT")
    success,new_leaf,msg=new_component.change_internal_to_leaf(new_internal_component_3.public_id)
    new_component.save()

    disconnect()
    return True


if __name__ == "__main__":
    test()