# Photoshop Batch Automation Tool  
Automação para processamento em lote no Adobe Photoshop utilizando Actions (ATN), exportação, e suporte a workflows GIS.

---

## 🚀 Visão Geral

Este projeto permite automatizar o processamento massivo de imagens no Photoshop, aplicando:

- Filtros personalizados via arquivos de ação (`.atn`)
- Exportação automática baseada na ação (.atn) gravada pelo usuário
- Processamento recursivo em diretórios
- Processamento apenas de arquivos que contenham a palavra-chave definida pelo usuário
- Ignorar automaticamente arquivos já processados

---

## ✨ Principais Recursos

- ✔ Processamento em lote de arquivos TIFF/BigTIFF
- ✔ Execução automática de Actions (.ATN)
- ✔ Exportação conforme definido pela Action (incluindo operações do Geographic Imager, se presentes)
- ✔ Evita reprocesamento de arquivos já finalizados
- ✔ Ignora automaticamente o diretório de saída dentro da pasta raiz
- ✔ Processamento seletivo: apenas arquivos que contêm a palavra-chave definida no `config.ini`

---

## ⚙️ Pré-requisitos

Antes de executar a aplicação, verifique os seguintes requisitos:

### 🖥️ Sistema Operacional
- Windows 10 ou superior  
  *(necessário para automação COM do Photoshop)*

### 🎨 Adobe Photoshop
- Adobe Photoshop CC 2015 ou superior  
- Os arquivos `.atn` utilizados pelo script devem estar funcionando corretamente no Photoshop
  
### 🐍 Python (somente para execução via script)

- Python **3.12+**
- Dependência necessária:

```bash
pip install pywin32
```

---

## 📄 Exemplo de `config.ini`

A aplicação utiliza um arquivo `config.ini` para definir caminhos, filtros e ações do Photoshop.  
A seguir, um exemplo completo:

```ini
[PATHS]
# Diretório contendo os arquivos a serem processados
DIRETORIO_PRINCIPAL = C:/Imagens/Entrada

# Diretório de saída
DIRETORIO_SAIDA = C:/Imagens/Saida

# Caminho para o arquivo ATN responsável pelos filtros
CAMINHO_ARQUIVO_ATN_FILTRO = C:/Actions/Filtros.atn

# Caminho para o arquivo ATN responsável pela exportação
CAMINHO_ARQUIVO_ATN_EXPORT = C:/Actions/Exportar.atn

[GERAL]
# Somente arquivos contendo esta palavra-chave serão processados
PALAVRA_CHAVE = _RGB

[FILTRO]
# Nome do ActionSet no arquivo ATN do filtro
ATN_SET_FILTRO = JOINVILLE

# Nome da Action dentro do ActionSet
ATN_ACTION_FILTRO = FILTRO_RGB

[EXPORT]
# Nome do ActionSet no arquivo ATN de exportação
ATN_SET_EXPORT = EXPORT

# Nome da Action que executa a exportação
ATN_ACTION_EXPORT = EXPORTAR_BIGTIFF
