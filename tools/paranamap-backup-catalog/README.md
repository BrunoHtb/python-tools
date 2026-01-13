# ParanaMap Backup Catalog

Script em Python para catalogação e controle de backups de entregas do projeto **ParanaMap**, armazenados em HDs externos.

O sistema percorre recursivamente a estrutura de diretórios das entregas e registra os arquivos em um banco PostgreSQL, evitando duplicações e permitindo auditoria, rastreabilidade e buscas rápidas.

---

## 🎯 Objetivo

- Catalogar arquivos de entregas armazenados em HDs externos
- Evitar duplicação de registros
- Permitir reexecução segura do script
- Manter histórico de modificações dos arquivos
- Integrar o controle de backup ao banco do projeto

---

## 📁 Estrutura esperada no HD

```text
ROOT/
└── 8 - Entregas/
    └── REMESSA/
        └── EMPRESA/
            └── SERVICO/
                └── LOTE/
                    └── BLOCO/
                        └── (subdiretórios e arquivos)
```

---

## 🗄️ Modelo de Dados (PostgreSQL)

A catalogação dos arquivos é realizada em uma tabela PostgreSQL, garantindo unicidade lógica e permitindo reexecuções seguras do script.
### 🔑 Regra de Unicidade
A unicidade dos registros é garantida pela seguinte constraint:
```bash
UNIQUE (file_path, file_name)
```
Essa abordagem assegura que um mesmo arquivo (identificado pelo caminho lógico e nome) não seja duplicado, independentemente do HD físico utilizado.

### 📌 Principais Colunas

- **hd_label**  
  Identificação do HD (metadado). Quando não disponível, é preenchido com um valor genérico.

- **hd_serial**  
  Serial físico ou lógico do HD.

- **remessa**  
  Identificador da remessa de entrega.

- **empresa**  
  Empresa responsável pela entrega.

- **servico**  
  Tipo de serviço executado.

- **lote**  
  Lote associado ao serviço.

- **bloco**  
  Bloco associado ao lote.

- **file_path**  
  Caminho lógico completo do diretório do arquivo (sem a letra do disco).

- **file_name**  
  Nome do arquivo.

- **modified**  
  Data e hora da última modificação do arquivo.
