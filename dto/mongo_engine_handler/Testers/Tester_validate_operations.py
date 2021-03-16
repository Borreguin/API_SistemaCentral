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
ini_date = dt.datetime(year=d_n.year, month=d_n.month - 1, day=1)
end_date = dt.datetime(year=d_n.year, month=d_n.month, day=d_n.day) - dt.timedelta(days=d_n.day)
t_delta = end_date - ini_date
n_minutos_evaluate = t_delta.days * (60 * 24) + t_delta.seconds // 60 + t_delta.seconds % 60


def test_operation():
    mongo_config = init.MONGOCLIENT_SETTINGS
    mongo_config.update(dict(db="DB_DISP_EMS"))
    connect(**mongo_config)
    case=4
    #case 1 bloque root, case 2 bloque leaf, case 3 componente root, case 4 componente internal
    if case==1:
        new_block = BloqueRoot(name=f"BLOQUE_ROOT_W_OP{str(r.randint(1, 1000))}")
        new_leafs = list()
        id_leafs = list()
        for i in range(1, 15):
            new_block_leaf = BloqueLeaf(name=f"BLOQUE_LEAF_TEST_{i}")
            new_leafs.append(new_block_leaf)
            id_leafs.append(new_block_leaf.public_id)
        new_block.add_new_leaf_block(new_leafs)
        serie = {"SERIE": [id_leafs[0], id_leafs[1], id_leafs[2]]}
        paralelo = {"PARALELO": [id_leafs[3], id_leafs[4], id_leafs[5]]}
        ponderado = {"PONDERADO": [id_leafs[6], id_leafs[7], id_leafs[8]]}
        promedio = {"PROMEDIO": [id_leafs[9], id_leafs[10], id_leafs[11]]}
        operation = dict(PROMEDIO=[serie, paralelo, id_leafs[12], id_leafs[13], ponderado, promedio])
        success, msg = new_block.add_operations(operation)
        new_block.save()
        return True
    elif case==2:
        new_block_root = BloqueRoot(name=f"BLOQUE_ROOT_W_OP{str(r.randint(1, 1000))}")
        new_block = BloqueLeaf(name=f"BLOQUE_LEAF_W_OP{str(r.randint(1, 1000))}")
        new_roots = list()
        id_roots = list()
        for i in range(1, 15):
            new_comp_root = ComponenteRoot(name=f"COMPONENTE_ROOT_TEST_{i}",block=f"BLOQUE_TEST_{i}")
            new_roots.append(new_comp_root)
            id_roots.append(new_comp_root.public_id)
            new_comp_root.save()
        new_block.add_new_root_component(new_roots)
        serie = {"SERIE": [id_roots[0], id_roots[1], id_roots[2]]}
        paralelo = {"PARALELO": [id_roots[3], id_roots[4], id_roots[5]]}
        ponderado = {"PONDERADO": [id_roots[6], id_roots[7], id_roots[8]]}
        promedio = {"PROMEDIO": [id_roots[9], id_roots[10], id_roots[11]]}
        operation = dict(PROMEDIO=[serie, paralelo, id_roots[12], id_roots[13], ponderado, promedio])
        success, msg = new_block.add_operations(operation)
        new_block_root.add_new_leaf_block([new_block])
        new_block_root.save()
        return True
    elif case == 3:
        new_comp = ComponenteRoot(name=f"COMP_ROOT_W_OP{str(r.randint(1, 1000))}",block=f"TEST_BLOCK{str(r.randint(1,1000))}")
        new_inter = list()
        id_inter = list()
        for i in range(1, 15):
            new_comp_inter = ComponenteInternal(name=f"COMPONENTE_INTERNAL_TEST_{i}")
            new_inter.append(new_comp_inter)
            id_inter.append(new_comp_inter.public_id)
        new_comp.add_internal_component(new_inter)
        serie = {"SERIE": [id_inter[0], id_inter[1], id_inter[2]]}
        paralelo = {"PARALELO": [id_inter[3], id_inter[4], id_inter[5]]}
        ponderado = {"PONDERADO": [id_inter[6], id_inter[7], id_inter[8]]}
        promedio = {"PROMEDIO": [id_inter[9], id_inter[10], id_inter[11]]}
        operation = dict(PROMEDIO=[serie, paralelo, id_inter[12], id_inter[13], ponderado, promedio])
        success, msg = new_comp.add_operations(operation)
        new_comp.save()
        return True
    elif case == 4:
        new_comp_root = ComponenteRoot(name=f"COMP_ROOT_W_OP{str(r.randint(1, 1000))}",
                                  block=f"TEST_BLOCK{str(r.randint(1, 1000))}")
        new_comp = ComponenteInternal(name=f"COMP_ROOT_W_OP{str(r.randint(1, 1000))}")
        new_inter = list()
        id_inter = list()
        new_leaf= list()
        id_leaf = list()
        for i in range(1, 15):
            new_comp_inter = ComponenteInternal(name=f"COMPONENTE_INTERNAL_TEST_{i}")
            new_inter.append(new_comp_inter)
            id_inter.append(new_comp_inter.public_id)
            new_comp_leaf = ComponenteLeaf(name=f"COMPONENTE_LEAF_TEST_{i}")
            new_leaf.append(new_comp_leaf)
            id_leaf.append(new_comp_leaf.public_id)
        new_comp.add_internal_component(new_inter)
        new_comp.add_leaf_component(new_leaf)
        serie = {"SERIE": [id_inter[0], id_inter[1], id_inter[2]]}
        paralelo = {"PARALELO": [id_inter[3], id_inter[4], id_inter[5]]}
        ponderado = {"PONDERADO": [id_inter[6], id_inter[7], id_inter[8]]}
        promedio = {"PROMEDIO": [id_leaf[0], id_leaf[1], id_leaf[2]]}
        operation = dict(PROMEDIO=[serie, paralelo, id_inter[12], id_inter[13], ponderado, promedio])
        success, msg = new_comp.add_operations(operation)
        new_comp_root.add_internal_component([new_comp])
        new_comp_root.save()
        return True


if __name__ == "__main__":
    test_operation()
