import random as r
from mongoengine import *
import datetime as dt

from dto.mongo_engine_handler.Comp_Root import ComponenteRoot
from dto.mongo_engine_handler.Comp_Internal import ComponenteInternal
from dto.mongo_engine_handler.Comp_Leaf import ComponenteLeaf
from dto.mongo_engine_handler.Block_Root import*
from dto.mongo_engine_handler.Block_Leaf import *
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

    new_block=BloqueRoot(name=f"BLOQUE_ROOT_{str(r.randint(1,1000))}")
    new_block.save()

    new_block_leaf=BloqueLeaf(name="BLOQUE_LEAF_TEST_1")
    new_block.add_and_replace_leaf_block([new_block_leaf])
    new_block.save()

    new_component = ComponenteRoot(block=new_block_leaf.name, name=f"ROOT_{str(r.randint(1, 1000))}")
    new_component.save()
    new_component_1 = ComponenteRoot(block=new_block_leaf.name, name=f"ROOT_{str(r.randint(1, 1000))}")
    new_component_1.save()


    new_block_leaf.comp_roots.append(new_component)
  #  new_block_leaf.comp_roots.append(new_component_1)
    new_block.save()

    new_component_2 = ComponenteRoot(block=new_block_leaf.name, name=f"ROOT_{str(r.randint(1, 1000))}")
    new_component_2.save()
    new_block_leaf.add_root_component([new_component_2])
    new_block.save()

    new_block_leaf.delete_root_component([new_component_1])
    new_block.save()

    new_block_root_db=BloqueRoot.objects(public_id=new_block.public_id).first()
    print(new_block_root_db)
    print(new_block_root_db.to_dict())
   #  new_block_leaf_2=BloqueLeaf(name="BLOQUE_LEAF_TEST_2")
   #  new_block.add_leaf_block([new_block_leaf_2])
   #  new_block.save()
   #
   #
   #  #Buscar por id del bloque hoja
   #  id_to_search=new_block_leaf_2.public_id
   #  success,result=new_block.search_leaf_by_id(id_to_search)
   #  # Editar bloque hoja
   #  new_block_leaf.edit_leaf_block({'name':"BLOQUE_DE_TEST"})
   #  new_block.save()
   # #Borrar bloque hoja
   #  new_block.delete_leaf_by_id(id_to_search)
   #  new_block.save()


    disconnect()
    return True


if __name__ == "__main__":
    test()