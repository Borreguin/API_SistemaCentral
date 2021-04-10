
import datetime as dt

from dto.mongo_engine_handler.Info.Manual import Manual, Manuals_entry
from my_lib.utils import check_date
from settings import initial_settings as init
log=init.LogDefaultConfig('Valid_Manual.log').logger
import traceback


class Valid_Manual():
    def __init__(self,root_id:str,leaf_id:str,fecha_inicio,fecha_final):
        success,fecha_inicio=check_date(fecha_inicio)
        success,fecha_final = check_date(fecha_final)
        self.root_id=root_id
        self.leaf_id = leaf_id
        self.fecha_inicio=fecha_inicio
        self.fecha_final=fecha_final
    def validate(self):
        #Verificar si ya existe un reporte
        report=Manuals_entry.objects(root_id=self.root_id,leaf_id=self.leaf_id)
        if len(report)>0:
            for report_manual in report._result_cache:
                for manuals in report_manual.ingresos_manuales:
                    return False if manuals.fecha_inicio==self.fecha_inicio and manuals.fecha_final==self.fecha_final else True
        return True

