# !/usr/bin/env python3
# -*- coding: utf-8 -*-


from datetime import (
    datetime, timedelta
)
from pandas import (
    read_json, to_datetime
)
from numpy import nan


class MicroclaudiaParser:
    @staticmethod
    def parse(json_data):
        microclaudia_df = read_json(json_data)
        microclaudia_df['IPADDRESS'] = microclaudia_df['IPADDRESS'].str[1:-1]
        microclaudia_df['MACADDRESS'] = microclaudia_df['MACADDRESS'].str[1:-1]

        # Note: Convertir a formato datetime las columnas 'ultima_conexion' y 'fecha_alta'
        microclaudia_df['ULTIMA_CONEXION'] = to_datetime(microclaudia_df['ULTIMA_CONEXION'], format="%d-%m-%Y %H:%M:%S")
        microclaudia_df['ULTIMA_CONEXION'] = microclaudia_df['ULTIMA_CONEXION'].dt.strftime("%Y-%m-%d %H:%M")
        microclaudia_df['FECHA_ALTA'] = to_datetime(microclaudia_df['FECHA_ALTA'], format="%d-%m-%Y %H:%M:%S")
        microclaudia_df['FECHA_ALTA'] = microclaudia_df['FECHA_ALTA'].dt.strftime("%Y-%m-%d %H:%M")
        microclaudia_df.replace({nan: None}, inplace=True)
        microclaudia_df['TAGS'] = microclaudia_df['TAGS'].str.replace('null', '').replace('', '-')
        # microclaudia_df['TAGS'] = microclaudia_df['TAGS'].fillna('-')
        # Note: Añadir al DataFrame una columna con la fecha de ayer
        fecha_ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        microclaudia_df['FECHA_REGISTRO'] = fecha_ayer

        # Note: Eliminar las filas donde 'NOMBRE' está duplicado, conservando la última ocurrencia
        microclaudia_df.drop_duplicates(subset=['NOMBRE'], keep='last', inplace=True)
        return microclaudia_df
