import os, glob, ntpath, subprocess, sys
from pathlib import Path

diretorio_atual = Path(__file__).resolve().parent
diretorio_pai = diretorio_atual / '..'
caminho_arquivo = diretorio_pai / 'folder.txt'

if caminho_arquivo.exists():
    with open(caminho_arquivo, 'r') as arquivo:
        conteudo_arquivo_diretorio_imagens = arquivo.readline().strip()
        conteudo_arquivo_osgeo4w_bat = arquivo.readline().strip()
else:
    print(f'O arquivo {caminho_arquivo} não foi encontrado.')
    input('Pressione Enter para continuar...')
    sys.exit()

APP_PATH = conteudo_arquivo_osgeo4w_bat
dir_path = conteudo_arquivo_diretorio_imagens

def filename_from_path(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def get_list_file_tif(dir_path):        
    listTif = glob.glob(os.path.join(dir_path, '*.tif'))
    listTiff = glob.glob(os.path.join(dir_path, '*.tiff'))
    listTIF = glob.glob(os.path.join(dir_path, '*.TIF'))
    listTIFF = glob.glob(os.path.join(dir_path, '*.TIFF'))
    return listTif + listTiff + listTIF + listTIFF

def pair_dictionary(dir_path):
    img_list = get_list_file_tif(dir_path)
    dictionary = {}

    for img in img_list:
        filename = filename_from_path(img)
        main_name = filename.rsplit('_', 1)[0] 

        if main_name not in dictionary:
            dictionary[main_name] = {'RGB': None, 'INF': None}
        if 'RGB' in filename:
            dictionary[main_name]['RGB'] = img
        if 'INF' in filename:
            dictionary[main_name]['INF'] = img
    return dictionary

def create_directory(dir_path):
    out_folder_final = os.path.join(dir_path, 'final')
    if not os.path.isdir(out_folder_final):
        os.mkdir(out_folder_final)
    return out_folder_final

if __name__ == "__main__": 
    out_folder_result = create_directory(dir_path)
    dictionary = pair_dictionary(dir_path)

    for key, value in dictionary.items():
        rgb_img_path = value['RGB']
        inf_img_path = value['INF']

        outpath = os.path.join(out_folder_result,key + ".tif")
        run_strings = [
            f'"{APP_PATH}" gdalbuildvrt r_rgb.vrt "{rgb_img_path}" -b 1',
            f'"{APP_PATH}" gdalbuildvrt g_rgb.vrt "{rgb_img_path}" -b 2',
            f'"{APP_PATH}" gdalbuildvrt b_rgb.vrt "{rgb_img_path}" -b 3',
            f'"{APP_PATH}" gdalbuildvrt r_inf.vrt "{inf_img_path}" -b 1',
            f'"{APP_PATH}" gdalbuildvrt -separate RGBNA.vrt r_rgb.vrt g_rgb.vrt b_rgb.vrt "{out_folder_result}" r_inf.vrt',
        ]
        
        for command in run_strings:
            try:
                subprocess.run(command, shell=True, check=True)
                print(f'Success: {command}')
            except subprocess.CalledProcessError as e:
                print(f'Error executing command: {command}\nError: {e}')

        runstring_final_img =  f'"{APP_PATH}" gdal_translate RGBNA.vrt "{outpath}" -co tfw=yes -co -BIGTIFF=YES -colorinterp red,green,blue,gray,alpha'
        runstring_final_img_alt = f'"{APP_PATH}" gdal_translate RGBNA.vrt "{outpath}" -co tfw=yes -colorinterp red,green,blue,gray,alpha'

        try:
            subprocess.run(runstring_final_img, shell=True)    
        except:
            subprocess.run(runstring_final_img_alt, shell=True)  

    temp_files = ['r_rgb.vrt','g_rgb.vrt','b_rgb.vrt','r_inf.vrt','RGBNA.vrt']
    for file_name in temp_files:
        if os.path.isfile(file_name):
            os.remove(file_name)

    print("Processo concluído.")
    input()
    sys.exit()
