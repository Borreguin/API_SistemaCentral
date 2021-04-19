"""
COMPONENT ROOT- BASE DE DATOS PARA SISTEMA CENTRAL
START DATE: 10/11/2020
DP V.2
"""
from my_lib.PI_connection import pi_connect as pi
from dto.mongo_engine_handler.Sources.ReportSource import ReportSource
from dto.Classes.Valid_BD_SR import Valid_BD_SR
from dto.Classes.Valid_Manual import Valid_Manual
from dto.Classes.Valid_Source_PI import Valid_Source_PI
from dto.mongo_engine_handler.Components.Comp_Leaf import *
from dto.mongo_engine_handler.Info.Manual import Manual, Manuals_entry
from my_lib.utils import check_date
from settings import initial_settings as init

class Sources(Document):
    public_id = StringField(required=True, default=None)
    type = StringField(choices=tuple(init.AVAILABLE_SOURCES))
    updated = DateTimeField(default=dt.datetime.now())
    parameters=DictField(required=False, default=dict())
    root_id = StringField(required=True, default=None)
    leaf_id = StringField(required=True, default=None)
    meta = {"collection": "CONFG|Fuentes"}

    def __init__(self, *args, **values):
        super().__init__(*args, **values)

        if self.public_id is None:
            # id = str(uuid.uuid4())
            self.public_id = str(uuid.uuid4())
        if self.type is None:
            self.type = init.AVAILABLE_SOURCES[0]
    def set_tipo(self,tipo:str):
        tipo=tipo.upper()
        if tipo in init.AVAILABLE_SOURCES:
            self.type=tipo
            return True
        return False

    def check_source(self):
        #HISTORICO
        if self.type==init.AVAILABLE_SOURCES[3]:
            #TAG,SERVIDOR,CONDICION DE FILTRADO
            piserver_name=self.parameters['piserver_name']
            tag_name=self.parameters['tag_name']
            condicion_filtrado=self.parameters['condicion_filtrado']
            success=Valid_Source_PI(piserver_name,tag_name,condicion_filtrado)
            return success, 'Validación exitosa' if success else 'Error: verificar Valid_Source_PI.log'
        if self.type == init.AVAILABLE_SOURCES[2]:
            collection_name=self.parameters['collection_name']
            fecha_inicio = self.parameters['fecha_inicio']
            fecha_final = self.parameters['fecha_final']
            field=self.parameters['field']
            success = Valid_BD_SR(collection_name,fecha_inicio, fecha_final,field).validate()
            return success, 'Validación exitosa' if success else 'Error: verificar parametros'
        if self.type == init.AVAILABLE_SOURCES[1]:
            fecha_inicio = self.parameters['fecha_inicio']  # VERIFICAR FORMATO DEL DICCIONARIO ??
            fecha_final = self.parameters['fecha_final']
            success = Valid_Manual(self.root_id,self.leaf_id,fecha_inicio,fecha_final).validate()
            return success,'Validación exitosa' if success else 'Error el reporte ya existe'
        else:
            return None

    def get_data(self):
        # HISTORICO
        if self.type == init.AVAILABLE_SOURCES[3]:
            fecha_inicio = self.parameters['fecha_inicio']
            fecha_final = self.parameters['fecha_final']
            return self.historico(fecha_inicio,fecha_final)
        # DESDE BASE DE DATOS (MONGO)
        if self.type == init.AVAILABLE_SOURCES[2]:
            fecha_inicio = self.parameters['fecha_inicio']
            fecha_final = self.parameters['fecha_final']
            return self.from_db(fecha_inicio, fecha_final)
        # MANUAL
        if self.type == init.AVAILABLE_SOURCES[1]:
            fecha_inicio = self.parameters['fecha_inicio']
            fecha_final = self.parameters['fecha_final']
            return self.manual(fecha_inicio, fecha_final)
        else:
            return None


    def historico(self, ini_date:dt.datetime, end_date: dt.datetime):
        historic_report=ReportSource(leaf_id=self.leaf_id,root_id=self.root_id,tipo='Historico',
                                     fuente=init.AVAILABLE_SOURCES[3],fecha_inicio=ini_date,fecha_final=end_date)
        piserver_name = self.parameters['piserver_name']
        tag_name = self.parameters['tag_name']
        condicion_filtrado = self.parameters['condicion_filtrado']
        valid_source = Valid_Source_PI(piserver_name,tag_name,condicion_filtrado)
        # verificar que exista el contenedor de consignaciones:
        consignaciones = ComponenteLeaf.consignments
        #Consultar consignaciones en el periodo
        consignaciones_historico = consignaciones.consignments_in_time_range(ini_date, end_date)
        #SI TIENE CONSIGNACIONES EXCLUIR PERIODOS CONSIGNADOS (FUNCION TIME_RANGES)
        time_ranges=generate_time_ranges(consignaciones_historico,ini_date,end_date)

        #CALCULO DE INDISPONIBILIDAD Y GUARDAR EN REPORTE
        indisponible_minutos = 0  # indisponibilidad acumulada
        for time_range in time_ranges:
            value=valid_source.get_value(time_range)
            # acumulando el tiempo de indisponibilidad
            indisponible_minutos += value[tag_name].iloc[0]
        disponible_minutos=cal_disp(indisponible_minutos,ini_date,end_date)
        historic_report.periodo_indisponibilidad=time_ranges
        historic_report.consignaciones_detalle = consignaciones_historico
        historic_report.indisponibilidad_minutos=indisponible_minutos
        historic_report.disponibilidad_minutos = disponible_minutos
        #GUARDAR REPORTSOURCE EN BD DESPUES RETORNO EL OBJETO (REPORTSOURCE)
        return historic_report

    #RESULTADO DESDE BD MONGO
    def from_db(self,ini_date:dt.datetime, end_date: dt.datetime):
        db_report = ReportSource(leaf_id=self.leaf_id, root_id=self.root_id, tipo='Desde_BD',
                                       fuente=init.AVAILABLE_SOURCES[2], fecha_inicio=ini_date, fecha_final=end_date)
        collection_name = self.parameters['collection_name']
        field = self.parameters['field']
        success,value_disp,msg = Valid_BD_SR(collection_name, ini_date, end_date, field).get_value()
        #Valor de disponibilidad
        db_report.disponibilidad_minutos= value_disp
        value_indis_porc=100-value_disp
        db_report.indisponibilidad_minutos = value_indis_porc
        return db_report


    def manual(self,ini_date:dt.datetime, end_date: dt.datetime):
        manual_report = ReportSource(leaf_id=self.leaf_id, root_id=self.root_id, tipo='Manual',
                                       fuente=init.AVAILABLE_SOURCES[1], fecha_inicio=ini_date, fecha_final=end_date)
        manual=Manual(fecha_inicio=ini_date,fecha_final=end_date)
        manual_info=Manuals_entry(root_id=self.root_id,leaf_id= self.leaf_id)
        manual_info.insert_manuals(manual)
        t_indis=manual.t_minutos
        manual_report.indisponibilidad_minutos=t_indis
        return manual_report


    def __repr__(self):
        return f"<Root {self.updated},{self.type},{self.parameters},{self.leaf_id},{self.root_id}>"

    def __str__(self):
        return f"<Root {self.updated},{self.type},{self.parameters},{self.leaf_id},{self.root_id}>"

#FUNCIONES AUXILIARES
#SI TIENE CONSIGNACIONES EXCLUIR PERIODOS CONSIGNADOS (FUNCION TIME_RANGES)
#Resultado de la funcion es una lista de rangos de tiempo
def generate_time_ranges(consignaciones: list, ini_date: dt.datetime, end_date: dt.datetime):
    # La función encuentra el periodo en el cual se puede examinar la disponibilidad:
    if len(consignaciones) == 0:
        return [pi._time_range(ini_date, end_date)]

    # caso inicial:
    # * ++ tiempo de análisis ++*
    # [ periodo de consignación ]
    time_ranges = list()  # lleva la lista de periodos válidos
    tail = None  # inicialización
    end = end_date  # inicialización
    if consignaciones[0].fecha_inicio < ini_date:
        # [-----*++++]+++++++++++++++++++++*------
        tail = consignaciones[0].fecha_final  # lo que queda restante a analizar
        end = end_date  # por ser caso inicial se asume que se puede hacer el cálculo hasta el final del periodo

    elif consignaciones[0].fecha_inicio > ini_date and consignaciones[0].fecha_final < end_date:
        # --*++++[++++++]+++++++++*---------------
        start = ini_date  # fecha desde la que se empieza un periodo válido para calc. disponi
        end = consignaciones[0].fecha_inicio  # fecha fin del periodo válido para calc. disponi
        tail = consignaciones[0].fecha_final  # siguiente probable periodo (lo que queda restante a analizar)
        time_ranges = [pi._time_range(start, end)]  # primer periodo válido

    elif consignaciones[0].fecha_inicio > ini_date and consignaciones[0].fecha_final >= end_date:
        # --*++++[+++++++++++++++*-----]----------
        # este caso es definitivo y no requiere continuar más alla:
        start = ini_date  # fecha desde la que se empieza un periodo válido para calc. disponi
        end = consignaciones[0].fecha_inicio  # fecha fin del periodo válido para calc. disponi
        return [pi._time_range(start, end)]
    elif consignaciones[0].fecha_inicio == ini_date and consignaciones[0].fecha_final == end_date:
        # ---*[+++++++]*---
        # este caso es definitivo y no requiere continuar más alla
        # nada que procesar en este caso
        return []

    # creando los demás rangos:
    for c in consignaciones[1:]:
        start = tail
        end = c.fecha_inicio
        if c.fecha_final < end_date:
            time_ranges.append(pi._time_range(start, end))
            tail = c.fecha_final
        else:
            end = c.fecha_inicio
            break
    # ultimo caso:
    time_ranges.append(pi._time_range(tail, end))
    return time_ranges

def cal_indisp(disp_min,fecha_inicio,fecha_final):
    fecha_inicio = check_date(fecha_inicio)
    fecha_final = check_date(fecha_final)
    t_delta = fecha_final - fecha_inicio
    periodo_evaluacion_minutos = t_delta.days * (60 * 24) + t_delta.seconds // 60 + t_delta.seconds % 60
    indis_min=periodo_evaluacion_minutos-disp_min
    return indis_min

def cal_disp(indisp_min,fecha_inicio,fecha_final):
    fecha_inicio = check_date(fecha_inicio)
    fecha_final = check_date(fecha_final)
    t_delta = fecha_final - fecha_inicio
    periodo_evaluacion_minutos = t_delta.days * (60 * 24) + t_delta.seconds // 60 + t_delta.seconds % 60
    dis_min=periodo_evaluacion_minutos-indisp_min
    return dis_min
