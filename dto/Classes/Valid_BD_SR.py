import datetime as dt
from mongoengine import *
from my_lib.utils import check_date
from settings import initial_settings as init
log=init.LogDefaultConfig('Valid_Manual.log').logger
import traceback
import pymongo

class Valid_BD_SR():

    def __init__(self,collection_name:str,fecha_inicio,fecha_final,field:str):
        success, self.fecha_inicio = check_date(fecha_inicio)
        success, self.fecha_final = check_date(fecha_final)
        self.field=field
        self.collecction_name=collection_name

    def validate(self):
        mongo_config = init.MONGOCLIENT_SETTINGS
        db_name=mongo_config.pop('db')
        client=pymongo.MongoClient(**mongo_config)
        db=client['DB_DISP_EMS']
        collection=db[self.collecction_name]
        filter_dict=dict(fecha_inicio=self.fecha_inicio,fecha_final=self.fecha_final)
        report=collection.find_one(filter_dict)
        client.close()
        if report is not None:
            return self.field in report.keys()
        return False
    def get_value(self):
        mongo_config = init.MONGOCLIENT_SETTINGS
        #db_name=mongo_config.pop('db')
        client=pymongo.MongoClient(**mongo_config)
        db=client['DB_DISP_EMS']
        collection=db[self.collecction_name]
        filter_dict=dict(fecha_inicio=self.fecha_inicio,fecha_final=self.fecha_final)
        report=collection.find_one(filter_dict)
        client.close()
        if report is not None and self.field in report.keys():
            return True,report[self.field],'Valor obtenido correctamente'
        return False,None,'No se encontro el campo'
    # def get_consigment(self):
    #     mongo_config = init.MONGOCLIENT_SETTINGS
    #     db_name = mongo_config.pop('db')
    #     client = pymongo.MongoClient(**mongo_config)
    #     db = client[db_name]
    #     collection = db['INFO|Consignaciones']
    #