"""
Desarrollado en la Gerencia de Desarrollo Técnico
by: Roberto Sánchez Abril 2020
motto:
"Whatever you do, work at it with all your heart, as working for the Lord, not for human master"
Colossians 3:23

Consignación:
•	DOCUMENTO TIPO JSON
•	Permite indicar tiempos de consignación donde el elemento no será consgnado para el cálculo de disponibilidad

"""

import hashlib
import traceback
import uuid

from mongoengine import *
import datetime as dt
import os
from settings import initial_settings as init
from shutil import rmtree


class Manual(EmbeddedDocument):
    fecha_inicio = DateTimeField(required=True, default=dt.datetime.now())
    fecha_final = DateTimeField(required=True, default=dt.datetime.now())
    t_minutos = IntField(required=True)
    id_manual = StringField(default=None, required=True)
    detalle = DictField()
    responsable=StringField(required=True, default=None)
    updated = DateTimeField(required=False, default=dt.datetime.now())

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        if self.id_manual is None:
            id = str(uuid.uuid4()) + str(self.fecha_inicio) + str(self.fecha_final)
            self.id_manual = hashlib.md5(id.encode()).hexdigest()
        self.calculate()
        if self.responsable is None:
            self.responsable='Usuario Generico'

    def calculate(self):
        if self.fecha_inicio is None or self.fecha_final is None:
            return
        if isinstance(self.fecha_inicio, str):
            self.fecha_inicio = dt.datetime.strptime(self.fecha_inicio, "%Y-%m-%d %H:%M:%S")
        if isinstance(self.fecha_final, str):
            self.fecha_final = dt.datetime.strptime(self.fecha_final, "%Y-%m-%d %H:%M:%S")

        if self.fecha_inicio >= self.fecha_final:
            raise ValueError("La fecha de inicio no puede ser mayor o igual a la fecha de fin")
        t = self.fecha_final - self.fecha_inicio
        self.t_minutos = t.days * (60 * 24) + t.seconds // 60 + t.seconds % 60

    def __str__(self):
        return f"({self.id_manual}: min={self.t_minutos}) [{self.fecha_inicio.strftime('%d-%m-%Y %H:%M')}, " \
               f"{self.fecha_final.strftime('%d-%m-%Y %H:%M')}]"

    def to_dict(self):
        return dict(fecha_inicio=str(self.fecha_inicio), fecha_final=str(self.fecha_final),
                    id_consignacion=self.id_manual,
                    detalle=self.detalle)

    def edit(self, new_manual: dict):
        try:
            to_update = ["fecha_inicio", "fecha_final", "detalle"]
            for key, value in new_manual.items():
                if key in to_update:
                    setattr(self, key, value)
            self.updated = dt.datetime.now()
            return True, f"Ingreso manual editado"
        except Exception as e:
            msg = f"Error al actualizar {self}: {str(e)}"
            tb = traceback.format_exc()  # Registra últimos pasos antes del error
            return False, msg


class Manuals_entry(Document):
    id_elemento = StringField(required=True, unique=True)
    root_id = StringField(required=True, default=None)
    leaf_id = StringField(required=True, default=None)
    ingreso_reciente = EmbeddedDocumentField(Manual)
    ingresos_manuales = ListField(EmbeddedDocumentField(Manual))
    meta = {"collection": "INFO|Manual"}

    def __init__(self, *args, **values):
        super().__init__(*args, **values)

        if self.id_elemento is None:
            # id = str(uuid.uuid4())
            self.id_elemento= str(uuid.uuid4())

    def update_last_manual(self):
        t, ixr = dt.datetime(1900, 1, 1), -1
        for ix, c in enumerate(self.ingresos_manuales):
            # check last date:
            if c.fecha_final > t:
                t, ixr = c.fecha_final, ix
        if ixr != -1:
            self.ingreso_reciente = self.ingresos_manuales[ixr]
        else:
            self.ingreso_reciente = None

    def insert_manuals(self, manual: Manual):
        # si es primera consignacion a insertar
        if len(self.ingresos_manuales) == 0:
            self.ingresos_manuales.append(manual)
            self.update_last_manual()
            return True, f"Ingreso manual insertado: {manual}"
        where = 0
        for ix, c in enumerate(self.ingresos_manuales):
            # check si no existe overlapping
            incorrect_ini = c.fecha_inicio <= manual.fecha_inicio < c.fecha_final
            incorrect_end = c.fecha_inicio < manual.fecha_final <= c.fecha_final
            # check si no existe closure
            incorrect_closure = manual.fecha_inicio < c.fecha_inicio and manual.fecha_final > c.fecha_final
            # si existe overlapping or closure no se puede ingresar
            if incorrect_ini or incorrect_end or incorrect_closure:
                return False, f"{manual} Conflicto con el ingreso manual: {c}"
            # evaluar donde se puede ingresar
            correct_ini = manual.fecha_inicio > c.fecha_inicio
            correct_end = manual.fecha_final > c.fecha_inicio
            if correct_ini and correct_end:
                where = ix + 1
        if 0 <= where < len(self.ingresos_manuales):
            self.ingresos_manuales = self.ingresos_manuales[0:where] + [manual] + self.ingresos_manuales[where:]
        else:
            self.ingresos_manuales.append(manual)
        self.update_last_manual()
        return True, f"Ingreso manual insertado: {manual}"

    def delete_manual_by_id(self, id_manual):
        new_manual = [c for c in self.ingresos_manuales if c.id_manual != id_manual]
        if len(new_manual) == len(self.ingresos_manuales):
            return False, f"No existe el ingreso manual [{id_manual}] en el elemento [{self.leaf_id}]"
        self.ingresos_manuales = new_manual
        self.update_last_manual()
        return True, f"Ingreso manual [{id_manual}] ha sido eliminado"

    def manual_in_time_range(self, ini_date: dt.datetime, end_time: dt.datetime):
        return [c for c in self.ingresos_manuales if
                (ini_date <= c.fecha_inicio < end_time or ini_date < c.fecha_final <= end_time) or
                # el periodo ingresado cubre la totalidad del periodo a evaluar:
                (c.fecha_inicio <= ini_date and c.fecha_final >= end_time)]

    def search_manual_by_id(self, id_to_search):
        for manual in self.ingresos_manuales:
            if manual.id_consignacion == id_to_search:
                return True, manual
        return False, None

    def search_manual_by_date(self, ini_date,end_date):
        for manual in self.ingresos_manuales:
            if manual.fecha_inicio == ini_date and manual.fecha_final == end_date:
                return True, manual
        return False, None

    def edit_manual_by_id(self, id_to_edit, manual: Manual):
        found = False
        for manual in self.ingresos_manuales:
            if manual.id_manual == id_to_edit:
                found = True
                manual.edit(manual.to_dict())
                break
        return found, f"El ingreso manual {manual.id_manual} ha sido editado correctamente" if found \
            else f"El ingreso manual no ha sido encontrado"

    def __str__(self):
        return f"{self.id_elemento}: [last: {self.ingreso_reciente}] " \
               f" Total: {len(self.ingresos_manuales)}"
