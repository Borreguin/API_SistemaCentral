
from my_lib.PI_connection.pi_connect import PIserver, PI_point, _time_range
import datetime as dt
from settings import initial_settings as init
log=init.LogDefaultConfig('Valid_Source_PI.log').logger
import traceback

class Valid_Source_PI():
    def __init__(self,piserver_name=None,tag_name=None,condicion_filtrado=None):
        # if PIserver is not found:
        self.server = PIserver(piserver_name)
        self.tag_name=tag_name
        self.condicion_filtrado=condicion_filtrado
        if self.server is not None:
            self.pt = self.server.find_PI_point(tag_name)
        else:
            self.pt=None
        success,value,msg=validate_expression(self.server,tag_name,condicion_filtrado)
        self.filter_validation=success
    def validate(self):
        return self.server is not None and self.pt is not None and self.filter_validation
    def get_value(self,time_range):
        return validate_expression(self.server,self.tag_name,self.condicion_filtrado,time_range)

def create_condition(condition,tag_name):
    # creando la condición de indisponibilidad:
    if not "expr:" in condition:
        # 'tag1' = "condicion1" OR 'tag1' = "condicion2" OR etc. v1
        #  Compare(DigText('tag1'), "condicion1*") OR Compare(DigText('tag1'), "condicion2*")
        conditions = str(condition).split("#")
        # expression = f"'{tag}' = \"{conditions[0].strip()}\"" v1
        expression = f'Compare(DigText(\'{tag_name}\'), "{conditions[0].strip()}")'
        for c in conditions[1:]:
            # expression += f" OR '{tag}' = \"{c}\""
            expression += f' OR Compare(DigText(\'{tag_name}\'), "{c.strip()}")'
    else:
        expression = condition.replace("expr:", "")

    return expression


def validate_expression(pi_svr,tag_name,condition,time_range=None):
    try:
        # buscando la Tag en el servidor PI
        pt = PI_point(pi_svr,tag_name)
       #pt = pi_svr.find_PI_point(tag_name)
        if pt is None:
            return False,f'La tag {tag_name} no ha sido encontrada'
        expression=create_condition(condition,tag_name)
        if time_range is None:
            ini_date=dt.datetime.now()-dt.timedelta(hours=1)
            end_date=dt.datetime.now()
            time_range=_time_range(ini_date, end_date)
        value = pt.time_filter(time_range, expression, span=None, time_unit="mi")
        value= value[tag_name].iloc[0]
        return True,value,f'El valor ha sido calculado exitosamente'
    except Exception as e:
        msg=f'La expresion no pudo ser validada'
        detalle=f'{msg}\n {str(e)} [{traceback.format_exc()}]'
        log.error(detalle)
        return False,None,msg