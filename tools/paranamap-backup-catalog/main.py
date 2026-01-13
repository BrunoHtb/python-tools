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


def normalize_hd_metadata(drive_letter):
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

ROOT = config["FILESYSTEM"]["root"]
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

drive_letter = ROOT.replace("\\", "")
hd_label, hd_serial = normalize_hd_metadata(drive_letter)

print("HD Label :", hd_label)
print("HD Serial:", hd_serial)

path_entregas = os.path.join(ROOT, ENTREGAS_DIR)
batch = []

# Percorre todo subdiretorios
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
                            stat = os.stat(full_file_path)

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
                                datetime.fromtimestamp(stat.st_mtime)
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

# Inserir o que sobrar
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

conn.close()

print("✔ Catálogo gerado com sucesso!")
