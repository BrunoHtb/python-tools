from ftplib import FTP
import os
from datetime import datetime
from decouple import config

ftp_host = config('FTP_HOST', default='localhost')
ftp_user = config('FTP_USER', default='ftp')
ftp_passwd = config('FTP_PASSWORD', default='a')    


def get_path_directory_disp_seg_pru(registered_date):  
    day, month, year  = registered_date.split('/')
    photo_folder = os.path.join('/Arquivos', year, month, day)
    photo_folder = photo_folder.replace('\\', '/')

    return photo_folder


def get_path_directory_vertical_horizontal(registered_date):
    data_obj = registered_date.strftime("%Y-%m-%d")
    year, month, day = data_obj.split('-')
    photo_folder = os.path.join('/Arquivos', year, month, day)
    photo_folder = photo_folder.replace('\\', '/')

    return photo_folder


def ftp_search_photo(photo_name, date, register):
    ftp = FTP(ftp_host)
    ftp.login(user=ftp_user, passwd=ftp_passwd)
    try:
        if register == "PRU" or register == "DispSeg":
            photo_folder = get_path_directory_disp_seg_pru(date)
        else:
            photo_folder = get_path_directory_vertical_horizontal(date)

        ftp.cwd(photo_folder)
        files_remote = ftp.nlst()

        if photo_name in files_remote:
            return True
        else:
            return False 

    except Exception as e:
        return
    
    finally:        
        ftp.quit()

   
