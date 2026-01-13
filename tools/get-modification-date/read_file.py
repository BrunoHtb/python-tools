import os
from datetime import datetime

def obter_data_modificacao_arquivo(caminho_arquivo):
    timestamp = os.path.getmtime(caminho_arquivo)
    data_modificacao = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    
    return data_modificacao

def agrupar_arquivos_por_data(diretorio):
    arquivos = [arquivo for arquivo in os.listdir(diretorio) if arquivo.endswith(".las")]
    arquivos_por_data = {}

    for arquivo in arquivos:
        caminho_arquivo = os.path.join(diretorio, arquivo)
        data_modificacao = obter_data_modificacao_arquivo(caminho_arquivo)
        if data_modificacao in arquivos_por_data:
            arquivos_por_data[data_modificacao].append(arquivo)
        else:
            arquivos_por_data[data_modificacao] = [arquivo]

    return arquivos_por_data

def salvar_arquivos_por_data_em_txt(arquivos_por_data, caminho_saida_txt):
    with open(caminho_saida_txt, 'w') as arquivo_txt:
        for data_modificacao, arquivos in arquivos_por_data.items():
            arquivo_txt.write(f'\n\nData de modificação: {data_modificacao}\n')
            for arquivo in arquivos:
                arquivo_txt.write(f' - {arquivo}')
            arquivo_txt.write('\n')


if __name__ == "__main__":
    diretorio_alvo = "C:/Users/bruno/OneDrive/Imagens/Documentos/MicrostationConnection/SP_Fase2"
    caminho_saida_txt = "C:/Users/bruno/OneDrive/Imagens/Documentos/MicrostationConnection/SP_Fase2/arquivo.txt"

    arquivos_por_data = agrupar_arquivos_por_data(diretorio_alvo)
    salvar_arquivos_por_data_em_txt(arquivos_por_data, caminho_saida_txt)
