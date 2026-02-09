import os
import wmi
import psycopg2
import configparser
from datetime import datetime
from psycopg2.extras import execute_batch


def get_hd_label(drive_letter):
    try:
        c = wmi.WMI()
        drive_letter = drive_letter.replace("\\", "")
        for disk in c.Win32_LogicalDisk(DeviceID=drive_letter):
            if disk.VolumeName and disk.VolumeName.strip():
                return disk.VolumeName.strip()
    except Exception:
        pass
    return "NAO_EXISTE"


def get_hd_serial(drive_letter):
    try:
        c = wmi.WMI()
        drive_letter = drive_letter.replace("\\", "")
        logical_disks = c.Win32_LogicalDisk(DeviceID=drive_letter)
        if not logical_disks:
            return None

        ld = logical_disks[0]
        # Tentando pegar serial físico
        partitions = ld.associators(wmi_result_class="Win32_DiskPartition")
        for partition in partitions:
            disks = partition.associators(wmi_result_class="Win32_DiskDrive")
            for disk in disks:
                if disk.SerialNumber and disk.SerialNumber.strip():
                    return disk.SerialNumber.strip()

        # Tentando pegar serial lógico
        if ld.VolumeSerialNumber:
            return f"VOL_{ld.VolumeSerialNumber}"     
    except Exception:
        pass

    return None


def normalize_hd_metadata(root_path):
    drive_letter, _ = os.path.splitdrive(root_path)

    if not drive_letter:
        return "NAO_DETECTADO", "NAO_DETECTADO"

    label = get_hd_label(drive_letter)
    serial = get_hd_serial(drive_letter)

    if not serial:
        serial = "NAO_EXISTE"

    if not label:
        label = "NAO_EXISTE"

    return label, serial


def strip_drive(path):
    _, rest = os.path.splitdrive(path)
    return rest.replace("\\", "/")


# Ler config.ini
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

raw_roots = config["FILESYSTEM"]["root"]
roots = [r.strip() for r in raw_roots.split('\n') if r.strip()]

ENTREGAS_DIR = config["FILESYSTEM"]["entregas_dir"]

DB_CONFIG = {
    "host": config["POSTGRES"]["host"],
    "database": config["POSTGRES"]["database"],
    "user": config["POSTGRES"]["user"],
    "password": config["POSTGRES"]["password"],
    "port": config["POSTGRES"].getint("port", 5432)
}

batch_size = config["EXECUTION"].getint("batch_size", 1000)

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

batch = []

# Percorre todos os HDs
for current_root in roots:
    print(f"\n--- Iniciando processamento de: {current_root} ---")
    
    if not os.path.exists(current_root):
        print(f"❌ Caminho não encontrado: {current_root}. Pulando...")
        continue

    hd_label, hd_serial = normalize_hd_metadata(current_root)
    print(f"   HD Label : {hd_label}")
    print(f"   HD Serial: {hd_serial}")
    path_entregas = os.path.join(current_root, ENTREGAS_DIR)

    if not os.path.exists(path_entregas):
        print(f"⚠️ Pasta de entregas não encontrada neste HD: {path_entregas}")
        continue

    # Percorre todos os subdiretorios
    for remessa in os.listdir(path_entregas):
        path_remessa = os.path.join(path_entregas, remessa)
        if not os.path.isdir(path_remessa):
            continue

        for empresa in os.listdir(path_remessa):
            path_empresa = os.path.join(path_remessa, empresa)
            if not os.path.isdir(path_empresa):
                continue

            for servico in os.listdir(path_empresa):
                path_servico = os.path.join(path_empresa, servico)
                if not os.path.isdir(path_servico):
                    continue

                for lote in os.listdir(path_servico):
                    path_lote = os.path.join(path_servico, lote)
                    if not os.path.isdir(path_lote):
                        continue

                    for bloco in os.listdir(path_lote):
                        path_bloco = os.path.join(path_lote, bloco)
                        if not os.path.isdir(path_bloco):
                            continue

                        # Varredura recursiva a partir do BLOCO
                        for root_dir, _, files in os.walk(path_bloco):
                            for file_name in files:
                                full_file_path = os.path.join(root_dir, file_name)
                                try:
                                    stat = os.stat(full_file_path)
                                    mtime = datetime.fromtimestamp(stat.st_mtime)
                                except FileNotFoundError:
                                    continue

                                batch.append((
                                    hd_label,
                                    hd_serial,
                                    remessa,
                                    empresa,
                                    servico,
                                    lote,
                                    bloco,
                                    file_name,
                                    strip_drive(os.path.dirname(full_file_path)),
                                    mtime
                                ))

                                if len(batch) >= batch_size:
                                    execute_batch(cur, """
                                        INSERT INTO controle_backup_hds.entregas
                                        (hd_label, hd_serial,
                                         remessa, empresa, servico, lote, bloco,
                                         file_name, file_path, modified)
                                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                        ON CONFLICT (file_path, file_name)
                                        DO UPDATE SET
                                            modified = EXCLUDED.modified,
                                            remessa  = EXCLUDED.remessa,
                                            empresa  = EXCLUDED.empresa,
                                            servico  = EXCLUDED.servico,
                                            lote     = EXCLUDED.lote,
                                            bloco    = EXCLUDED.bloco,
                                            hd_label = EXCLUDED.hd_label,
                                            hd_serial= EXCLUDED.hd_serial
                                    """, batch)
                                    conn.commit()
                                    batch.clear()
                                    print(f"   ...lote de {batch_size} inserido.")

# Caso sobre alguns arquivos para inserir no final
if batch:
    execute_batch(cur, """
        INSERT INTO controle_backup_hds.entregas
        (hd_label, hd_serial,
         remessa, empresa, servico, lote, bloco,
         file_name, file_path, modified)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (file_path, file_name)
        DO UPDATE SET
            modified = EXCLUDED.modified,
            remessa  = EXCLUDED.remessa,
            empresa  = EXCLUDED.empresa,
            servico  = EXCLUDED.servico,
            lote     = EXCLUDED.lote,
            bloco    = EXCLUDED.bloco,
            hd_label = EXCLUDED.hd_label,
            hd_serial= EXCLUDED.hd_serial
    """, batch)
    conn.commit()
    print(f"   ...lote final de {len(batch)} inserido.")

conn.close()
print("✔ Catálogo de TODOS os HDs gerado com sucesso!")
