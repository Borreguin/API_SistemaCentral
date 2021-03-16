"""
CLASE FUENTE: Permite seleccionar las diferentes fuentes del componente leaf, que luego serviran
              como entradas para las operaciones y calculos.

AVAILABLE_SOURCES:[None, "MANUAL", "CÁLCULO", "PISERVER", "OTROS"



"""
import datetime as dt
from dto.mongo_engine_handler.Comp_Leaf import *


class Source:
    leaf = ()
    fecha_inicio = ()
    fecha_final = ()
    update = dt.datetime.now()

    def check_leaf(self):  # CHECKEA SI EL LEAF ELEGIDO ES DE TIPO COMPONENTE LEAF
        check = isinstance(self.leaf, ComponenteLeaf)
        if not check:
            return False, f"Leaf: {self.leaf} no es un componente hoja"
        return True

    def manual(self, valor: float):
        if valor > 100 or valor < 0:
            return False, "Valor erroneo, ingresar valores entre 0 y 100"
        return True, valor

    def calculo(self):
        # DEBE TOMAR EL VALOR DE UN MOTOR DE CÁLCULO INDEPENDIENTE (EJ: DISP.SIST.REM, CÁLCULO DE PI, ETC...)
        # TODO: FUNCIÓN CALCULO
        pass

    def piserver(self):
        # TOMA VALORES DEL PI, FUNCION A PARTE O DENTRO DE ESTA CLASE?
        # TODO: FUNCIÓN PISERVER
        # TODO: DEFINIR OTROS METODOS DE FUENTES DE DISPONIBILIDAD
        pass
