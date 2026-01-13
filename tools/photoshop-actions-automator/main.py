import os
import sys
import configparser
from win32com.client import Dispatch

def base_path():
    if getattr(sys, 'frozen', False):
        # Executável
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        # Script normal
        return os.path.dirname(os.path.abspath(__file__))


def remover_actionset_jsx(ps, nome_set):
    jsx = f'''
    try {{
        var setName = "{nome_set}";
        var ref = new ActionReference();
        ref.putName(charIDToTypeID("ASet"), setName);
        var desc = new ActionDescriptor();
        desc.putReference(charIDToTypeID("null"), ref);
        executeAction(charIDToTypeID("Dlt "), desc, DialogModes.NO);
        "REMOVED";
    }} catch(e) {{
        "NOT_FOUND";
    }}
    '''
    try:
        resultado = ps.DoJavaScript(jsx)
        return "REMOVED" in resultado
    except:
        return False


def actionset_existe(ps, nome_set):
    jsx = f'''
    try {{
        var setName = "{nome_set}";
        var ref = new ActionReference();
        ref.putName(charIDToTypeID("ASet"), setName);
        var desc = executeActionGet(ref);
        "EXISTS";
    }} catch(e) {{
        "NOT_FOUND";
    }}
    '''
    try:
        resultado = ps.DoJavaScript(jsx)
        return "EXISTS" in resultado
    except:
        return False


def remover_todos_actionsets(ps, nome_set):
    removidos = 0
    max_tentativas = 10
    
    for _ in range(max_tentativas):
        if actionset_existe(ps, nome_set):
            if remover_actionset_jsx(ps, nome_set):
                removidos += 1
            else:
                break
        else:
            break
    
    return removidos


def garantir_actionset_unico(ps, nome_set, atn_path):
    print(f"\n→ Configurando ActionSet: {nome_set}")
    
    removidos = remover_todos_actionsets(ps, nome_set)
    if removidos > 0:
        print(f"  ✓ Removidos {removidos} ActionSet(s) duplicado(s)")

    if not os.path.exists(atn_path):
        raise RuntimeError(f"Arquivo ATN não encontrado: {atn_path}")
    
    print(f"  → Carregando: {atn_path}")
    try:
        ps.Load(atn_path)
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar ATN: {e}")

    if not actionset_existe(ps, nome_set):
        raise RuntimeError(f"ActionSet '{nome_set}' não encontrado após carregar o ATN")
    
    print(f"  ✓ ActionSet '{nome_set}' pronto!")


def verificar_action_existe(ps, action_name, set_name):
    jsx = f'''
    try {{
        var ref = new ActionReference();
        ref.putName(charIDToTypeID("Actn"), "{action_name}");
        ref.putName(charIDToTypeID("ASet"), "{set_name}");
        var desc = executeActionGet(ref);
        "EXISTS";
    }} catch(e) {{
        "NOT_FOUND: " + e.toString();
    }}
    '''
    try:
        resultado = ps.DoJavaScript(jsx)
        return "EXISTS" in resultado
    except:
        return False


# INICIA
processados = []
config = configparser.ConfigParser()
CONFIG_PATH = os.path.join(base_path(), "config.ini")
config.read(CONFIG_PATH)

ROOT_INPUT = config["PATHS"]["DIRETORIO_PRINCIPAL"]
ROOT_OUTPUT = config["PATHS"]["DIRETORIO_SAIDA"]
FILTER_KEYWORD = config["GERAL"]["PALAVRA_CHAVE"]

ATN_PATH_FILTER = config["PATHS"]["CAMINHO_ARQUIVO_ATN_FILTRO"]
ATN_PATH_EXPORT = config["PATHS"]["CAMINHO_ARQUIVO_ATN_EXPORT"]

ATN_SET_FILTRO = config["FILTRO"]["ATN_SET_FILTRO"]
ATN_ACTION_FILTRO = config["FILTRO"]["ATN_ACTION_FILTRO"]

ATN_SET_EXPORT = config["EXPORT"]["ATN_SET_EXPORT"]
ATN_ACTION_EXPORT = config["EXPORT"]["ATN_ACTION_EXPORT"]

# Validação
required = {
    "DIRETORIO_PRINCIPAL": ROOT_INPUT,
    "PALAVRA_CHAVE": FILTER_KEYWORD,
    "CAMINHO_ARQUIVO_ATN_FILTRO": ATN_PATH_FILTER,
    "CAMINHO_ARQUIVO_ATN_EXPORT": ATN_PATH_EXPORT,
    "ATN_SET_FILTRO": ATN_SET_FILTRO,
    "ATN_ACTION_FILTRO": ATN_ACTION_FILTRO,
    "ATN_SET_EXPORT": ATN_SET_EXPORT,
    "ATN_ACTION_EXPORT": ATN_ACTION_EXPORT,
}

for key, value in required.items():
    if not value:
        print(f"ERRO: Variável não definida: {key}")
        input("ENTER...")
        sys.exit(1)


# Normalizar caminhos
root_input_abs = os.path.abspath(ROOT_INPUT)
root_output_abs = os.path.abspath(ROOT_OUTPUT) if ROOT_OUTPUT else None

if root_output_abs:
    os.makedirs(root_output_abs, exist_ok=True)

# Conectar Photoshop
print("\n→ Conectando ao Photoshop...")
ps = Dispatch("Photoshop.Application")
ps.DisplayDialogs = 2
print("  ✓ Conectado!")

try:
    garantir_actionset_unico(ps, ATN_SET_FILTRO, ATN_PATH_FILTER)
    
    # filtro
    if not verificar_action_existe(ps, ATN_ACTION_FILTRO, ATN_SET_FILTRO):
        raise RuntimeError(f"Action '{ATN_ACTION_FILTRO}' não encontrada no set '{ATN_SET_FILTRO}'")
    
    garantir_actionset_unico(ps, ATN_SET_EXPORT, ATN_PATH_EXPORT)
    # export
    if not verificar_action_existe(ps, ATN_ACTION_EXPORT, ATN_SET_EXPORT):
        raise RuntimeError(f"Action '{ATN_ACTION_EXPORT}' não encontrada no set '{ATN_SET_EXPORT}'")
    
except Exception as e:
    print(f"\n✗ ERRO na configuração: {e}")
    input("Pressione ENTER para sair...")
    sys.exit(1)

print("\n" + "="*50)
print("CONFIGURAÇÃO CONCLUÍDA COM SUCESSO")
print("="*50)
print("\n--- INICIANDO PROCESSAMENTO ---\n")

count = 0
sucesso = 0
falhas = 0

# PROCESSAMENTO
for root, dirs, files in os.walk(root_input_abs):
    if root_output_abs:
        try:
            dirs[:] = [
                d for d in dirs
                if not os.path.abspath(os.path.join(root, d)).startswith(root_output_abs)
            ]
        except:
            pass

    for name in files:
        if FILTER_KEYWORD.lower() not in name.lower():
            continue

        if not name.lower().endswith((".tif", ".tiff")):
            continue

        nome_base = os.path.basename(name)
        if nome_base in processados:
            print(f"→ Ignorando (já processado): {nome_base}")
            continue

        count += 1
        in_path = os.path.join(root, name)

        print(f"\n[{count}] {name}")
        print(f"    Caminho: {in_path}")

        try:
            print(f"    → Abrindo...")
            doc = ps.Open(in_path)

            # Aplicar action de filtro
            print(f"    → Aplicando filtros...")
            ps.DoAction(ATN_ACTION_FILTRO, ATN_SET_FILTRO)

            # Aplicar action de exportação
            print(f"    → Exportando...")
            ps.DoAction(ATN_ACTION_EXPORT, ATN_SET_EXPORT)

            # Fechar sem salvar
            doc.Close(2)

            processados.append(nome_base)

            print(f"    ✓ Concluído!")
            sucesso += 1

        except Exception as e:
            print(f"    ✗ ERRO: {e}")
            falhas += 1

            # Tentar fechar documento aberto
            try:
                ps.DoJavaScript("if(app.documents.length>0){app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);}")
            except:
                pass


print("\n" + "="*50)
print("PROCESSAMENTO FINALIZADO")
print("="*50)
print(f"Total processado: {count}")
print(f"Sucessos: {sucesso}")
print(f"Falhas: {falhas}")
print("="*50)
input("\nPressione ENTER para sair...")