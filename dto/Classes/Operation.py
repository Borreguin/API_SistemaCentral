"""
    clase Operation: permite estructurar un diccionario que contenga las operaciones a realizarse dentro
    de un bloque/componente

    example:
    operations = {
        "operador": [op1,
                    op2,
                    {"operador": [op3, op4]},
                    ...
        ]
    }

    1. Primer nivel se valida que el diccionario tenga una operación resultante (y sólo una)
    2. Se valida dependiendo del tipo de operador, si la lista deba tener un numero determinado de operandos
"""
from settings import initial_settings as init




class Operation:
    # TOPOLOGIA: ESTRUCTURA DEL DICCIONARIO
    # OPERATING_LIST: LISTA DE OPERANDOS EXISTENTES (Ej:[id_1,id_2,id_3,etc...])
    # REGISTER_OPERATING: LISTA DE OPERANDOS REGISTRADOS EN TOPOLOGÍA
    # ["AVAILABLE_OPERATIONS"] = ["LEAF", "ROOT", "PARALELO", "SERIE", "PONDERADO", "PROMEDIO", "OTROS"]
    topology = dict()
    operating_list = list()
    register_operating = list()
    available_operations = init.AVAILABLE_OPERATIONS

    #Inicializa la clase con la topologia y la lista de operandos existentes (atributos de la clase)
    def __init__(self, topology: dict, operating_list=list, *args, **values):
        super().__init__(*args, **values)
        self.topology = topology
        self.operating_list = operating_list

    #Función recursiva para validar operacion
    def validate_operations(self):
        return self.validate_unique_operation(self.topology)

    #Función validar operación inicial en el nivel más alto
    def validate_unique_operation(self, to_validate: dict):
        if len(to_validate.keys()) > 1:
            return False, "No puede existir más de una operación resultante"
        if len(to_validate.keys()) == 0:
            return False, "No existe una operación válida"
        k = list(to_validate.keys())
        if not k[0] in self.available_operations:
            return False, f"La operación {k[0]}  no se encuentra dentro de las operaciones " \
                          f"válidas: {self.available_operations}"
        operandos = to_validate[k[0]]
        print(operandos)
        if not isinstance(operandos, list) or len(operandos) < 2: #Verifico condiciones de lista operandos
            return False, f"[{k[0]}] Los operandos deben estar dentro de una lista no menor a dos operadores"

        # si los operandos son una lista:
        return self.check_operandos(operandos)

    def check_operandos(self, operandos):
        is_ok = True
        msg = str()
        for operando in operandos:
            print(operando)
            # validando operando tipo string
            if isinstance(operando, str):
                check_op_exists = operando in self.operating_list #Valida si el operando esta en la lista de operandos existentes
                check_op_was_registered = operando in self.register_operating #Verifica si el operando ya esta registrado
                #Registra el operando
                if check_op_exists and not check_op_was_registered:
                    is_ok = is_ok and True
                    self.register_operating.append(operando)
                    continue
                elif not check_op_exists:
                    is_ok, msg = False, f"El operando {operando} no existe en la lista de operandos"
                    break
                elif check_op_was_registered:
                    is_ok, msg = False, f"El operando {operando} ya es utilizado en otra operación"
                    break
            # validando operando tipo dict
            if isinstance(operando, dict):
                success, msg = self.validate_unique_operation(operando)
                is_ok = is_ok and success
                if is_ok:
                    continue
                else:
                    break
            else:
                msg = f"Operador inválido: {operando}"
                is_ok = False
                break
        resp = "Estructura válida" if is_ok else msg
        return is_ok, resp
