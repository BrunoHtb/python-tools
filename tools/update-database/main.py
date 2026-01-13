import psycopg2
import schedule
import time
from datetime import datetime
from decouple import config

def update_database():
    with open("caminho_script_sql.txt", "r") as file:
        file_path = file.readline().strip()

    file_path = file_path.replace("\\\\", "\\")
    
    file_name = file_path
    commands = []
    db_host = config('DB_HOST', default='localhost')
    db_name = config('DB_NAME', default='Teste')
    db_user = config('DB_USER', default='postgres')
    db_password = config('DB_PASSWORD', default='teste')

    connection_config = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )

    connection = connection_config.cursor()

    with open(file_name, "r", encoding="utf-8") as file:
        content = file.read()

    commands = content.split(';')
    start_date = datetime.now().strftime("%d de %B de %Y, %H:%M")

    for command in commands:
        try:
            print(command)
            connection.execute(command)
            connection_config.commit()
        except Exception as e:
            print(f"Erro ao executar o comando: {command}\n Erro: {e}")
            connection_config.rollback()
    connection.close()
    connection_config.close() 

    end_date = datetime.now().strftime("%d de %B de %Y, %H:%M")
    print("Começou as: ", start_date)
    print("Terminou as:", end_date)

update_database()
schedule.every(2).hours.do(update_database)
while True:
    print("Aguardando...")
    schedule.run_pending()
    time.sleep(3600)