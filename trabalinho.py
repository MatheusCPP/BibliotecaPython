import sqlite3
import csv
import os
import pathlib
import shutil
from datetime import datetime

# Diretórios de trabalho
BASE_DIR = pathlib.Path(__file__).parent.resolve()
BACKUP_DIR = BASE_DIR / 'backups'
DATA_DIR = BASE_DIR / 'data'
EXPORTS_DIR = BASE_DIR / 'exports'

# Criação dos diretórios, se não existirem
for directory in [BACKUP_DIR, DATA_DIR, EXPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / 'livraria.db'

# Conexão com o banco de dados
def connect_db():
    return sqlite3.connect(DB_PATH)

def create_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            ano_publicacao INTEGER NOT NULL,
            preco REAL NOT NULL
        )
    ''')

def input_positive_int(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
            print("O valor deve ser um número positivo.")
        except ValueError:
            print("Valor inválido. Digite um número inteiro.")

def input_positive_float(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value > 0:
                return value
            print("O valor deve ser um número positivo.")
        except ValueError:
            print("Valor inválido. Digite um número.")

def adicionar_livro(cursor):
    titulo = input("Título: ")
    autor = input("Autor: ")
    ano_publicacao = input_positive_int("Ano de Publicação: ")
    preco = input_positive_float("Preço: ")

    cursor.execute('''
        INSERT INTO livros (titulo, autor, ano_publicacao, preco)
        VALUES (?, ?, ?, ?)
    ''', (titulo, autor, ano_publicacao, preco))
    print("Livro adicionado com sucesso!")
    return True

def exibir_livros(cursor):
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    if livros:
        for livro in livros:
            print(f"ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: R$ {livro[4]:.2f}")
    else:
        print("Nenhum livro cadastrado.")

def atualizar_preco(cursor):
    id_livro = input_positive_int("ID do livro a ser atualizado: ")
    novo_preco = input_positive_float("Novo preço: ")
    cursor.execute('UPDATE livros SET preco = ? WHERE id = ?', (novo_preco, id_livro))
    
    if cursor.rowcount > 0:
        print("Preço atualizado com sucesso!")
    else:
        print("Livro não encontrado.")

def remover_livro(cursor):
    id_livro = input_positive_int("ID do livro a ser removido: ")
    cursor.execute('DELETE FROM livros WHERE id = ?', (id_livro,))
    
    if cursor.rowcount > 0:
        print("Livro removido com sucesso!")
    else:
        print("Livro não encontrado.")

def buscar_por_autor(cursor):
    autor = input("Digite o nome do autor: ")
    cursor.execute('SELECT * FROM livros WHERE autor = ?', (autor,))
    livros = cursor.fetchall()
    
    if livros:
        for livro in livros:
            print(f"ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: R$ {livro[4]:.2f}")
    else:
        print("Nenhum livro encontrado para o autor informado.")

def exportar_para_csv(cursor):
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    csv_path = EXPORTS_DIR / 'livros_exportados.csv'
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'titulo', 'autor', 'ano_publicacao', 'preco'])
        writer.writerows(livros)
    print(f"Dados exportados para {csv_path}")

def importar_de_csv(cursor):
    csv_path = input("Caminho para o arquivo CSV: ")
    
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Pula o cabeçalho
        for row in reader:
            cursor.execute('''
                INSERT INTO livros (id, titulo, autor, ano_publicacao, preco)
                VALUES (?, ?, ?, ?, ?)
            ''', row)
    print("Dados importados com sucesso!")

def fazer_backup():
    backup_filename = f"backup_livraria_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.db"
    backup_path = BACKUP_DIR / backup_filename
    shutil.copy2(DB_PATH, backup_path)
    print(f"Backup realizado em {backup_path}")
    limpar_backups_antigos()

def limpar_backups_antigos():
    backups = sorted(BACKUP_DIR.glob('*.db'), key=os.path.getmtime, reverse=True)
    for backup in backups[5:]:
        backup.unlink()

def main():
    with connect_db() as conn:
        cursor = conn.cursor()
        create_table(cursor)

        while True:
            print("\nMenu:")
            print("1. Adicionar novo livro")
            print("2. Exibir todos os livros")
            print("3. Atualizar preço de um livro")
            print("4. Remover um livro")
            print("5. Buscar livros por autor")
            print("6. Exportar dados para CSV")
            print("7. Importar dados de CSV")
            print("8. Fazer backup do banco de dados")
            print("9. Sair")

            opcao = input("Escolha uma opção: ")

            if opcao == '1':
                if adicionar_livro(cursor):
                    fazer_backup()
                    conn.commit()
            elif opcao == '2':
                exibir_livros(cursor)
            elif opcao == '3':
                atualizar_preco(cursor)
                fazer_backup()
                conn.commit()
            elif opcao == '4':
                remover_livro(cursor)
                fazer_backup()
                conn.commit()
            elif opcao == '5':
                buscar_por_autor(cursor)
            elif opcao == '6':
                exportar_para_csv(cursor)
            elif opcao == '7':
                importar_de_csv(cursor)
                conn.commit()
                fazer_backup()
            elif opcao == '8':
                fazer_backup()
            elif opcao == '9':
                break
            else:
                print("Opção inválida.")

if __name__ == "__main__":
    main()
