import psycopg2
import csv
from decouple import config
from psycopg2 import sql

import ftp_access as ftp

db_host = config('DB_HOST', default='localhost')
db_name = config('DB_NAME', default='Teste')
db_user = config('DB_USER', default='postgres')
db_password = config('DB_PASSWORD', default='teste')

connection = psycopg2.connect(
    host=db_host,
    database=db_name,
    user=db_user,
    password=db_password
)


def select_query_disp_seg():
    query = sql.SQL("SELECT nome_fotopanoramica, ds_id, rodovia, regional_der, km_inicio, km_fim, auditoria, diamesano, * FROM public.tb_dispositivosdeseguranca WHERE auditoria=7 OR auditoria=2401 OR auditoria=2402 ORDER BY rodovia")
    return query


def select_query_pru():
    query = sql.SQL("SELECT nome_fotopanoramica, ru_id, rodovia, regional_der, km_inicio, km_fim, auditoria, diamesano, * FROM public.tb_restricaodeultrapassagem WHERE auditoria=7 OR auditoria=2401 OR auditoria=2402 ORDER BY rodovia")
    return query


def select_query_horizontal():
    query = sql.SQL('SELECT "FOTO1", "ID", "RODOVIA", "DR", "KM", "METROS", "AUDITORIA", "DATA_CADASTRO", * FROM public.retro_horizontal WHERE "AUDITORIA"=7 OR "AUDITORIA"=2401 OR "AUDITORIA"=2402 ORDER BY "RODOVIA"')
    return query


def select_query_vertical():
    query = sql.SQL('SELECT "FOTO1", "ID", "RODOVIA", "DR", "KM", "METROS", "AUDITORIA", "DATA_CADASTRO", * FROM public.retro_vertical WHERE "AUDITORIA"=7 OR "AUDITORIA"=2401 OR "AUDITORIA"=2402 ORDER BY "RODOVIA"')
    return query


if __name__ == '__main__':
    registers_type = {"DispSeg": select_query_disp_seg, "PRU": select_query_pru, "SH": select_query_horizontal, "SV": select_query_vertical}

    try:
        cursor = connection.cursor()

        for key, query_function in registers_type.items():
            query_select = query_function()
            cursor.execute(query_select)
            results = cursor.fetchall()

            file_name = f"{key}_falta_foto.csv"

            with open(file_name, 'w', newline='') as csvfile:
                fieldnames = ['id', 'rodovia', 'regional', 'km_i', 'km_f', 'auditoria', 'nome_foto']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()

                if results:
                    for result in results:
                        exist = ftp.ftp_search_photo(result[0], result[7], key)
                        if not exist:
                            print(f"Foto {result[0]} não existe")
                            writer.writerow({
                                'id': result[1],
                                'rodovia': result[2],
                                'regional': result[3],
                                'km_i': result[4],
                                'km_f': result[5],
                                'auditoria': result[6],
                                'nome_foto': result[0]
                            })
                        else:
                            print(f"Foto {result[0]} EXISTE")
    finally:
        cursor.close()
        connection.close()
    print("FIM")