import sqlite3
import re
from datetime import datetime

# Conexão com banco SQLite
conn = sqlite3.connect('nutricao.db')
cursor = conn.cursor()

# Criação das tabelas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        email TEXT PRIMARY KEY,
        senha TEXT NOT NULL,
        peso REAL NOT NULL,
        altura REAL NOT NULL,
        sexo TEXT NOT NULL,
        dieta TEXT NOT NULL,
        imc REAL NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS alimentos (
        nome TEXT PRIMARY KEY
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS refeicoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_usuario TEXT,
        alimento TEXT,
        quantidade_gramas REAL,
        data TEXT,
        FOREIGN KEY (email_usuario) REFERENCES usuarios(email)
    )
''')

conn.commit()

# ----------------- Funções Auxiliares ----------------- #

def validar_email(email):
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(padrao, email) is not None

def calcular_imc(peso, altura):
    return round(peso / (altura ** 2), 2)

def escolher_dieta():
    opcoes = ["Low carb", "Cetogênica", "Hiperproteica", "Bulking"]
    while True:
        print("\nEscolha sua dieta:")
        for i, dieta in enumerate(opcoes, 1):
            print(f"{i}. {dieta}")
        escolha = input("Digite o número da dieta: ")
        if escolha.isdigit() and 1 <= int(escolha) <= 4:
            return opcoes[int(escolha) - 1]
        else:
            print("❌ Opção inválida! Tente novamente.")

# ----------------- Cadastro ----------------- #

def registrar_usuario():
    print("\n=== Cadastro de Usuário ===")
    while True:
        email = input("E-mail: ").strip()
        if not validar_email(email):
            print("❌ E-mail inválido!")
            continue
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        if cursor.fetchone():
            print("❌ E-mail já está cadastrado!")
            continue
        break

    while True:
        senha = input("Senha: ").strip()
        if senha == "":
            print("❌ A senha não pode ser vazia!")
        else:
            break

    try:
        peso = float(input("Peso (kg): "))
        altura = float(input("Altura (m): "))
        if peso <= 0 or altura <= 0:
            print("❌ Peso e altura devem ser maiores que zero.")
            return
    except ValueError:
        print("❌ Digite apenas números válidos para peso e altura.")
        return

    sexo = input("Sexo (M/F): ").strip().upper()
    if sexo not in ['M', 'F']:
        print("❌ Sexo inválido! Use apenas 'M' ou 'F'.")
        return

    dieta = escolher_dieta()
    imc = calcular_imc(peso, altura)

    cursor.execute('''
        INSERT INTO usuarios (email, senha, peso, altura, sexo, dieta, imc)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (email, senha, peso, altura, sexo, dieta, imc))
    conn.commit()
    print(f"✅ Usuário cadastrado com sucesso! Seu IMC é {imc}")

# ----------------- Login ----------------- #

def login():
    print("\n=== Login ===")
    while True:
        email = input("E-mail: ").strip()
        cursor.execute("SELECT senha FROM usuarios WHERE email = ?", (email,))
        resultado = cursor.fetchone()
        if not resultado:
            print("❌ E-mail não encontrado. Tente novamente.")
            continue

        senha_correta = resultado[0]
        senha_digitada = input("Senha: ").strip()
        if senha_digitada != senha_correta:
            print("❌ Senha incorreta. Tente novamente.")
            continue

        print("✅ Login realizado com sucesso!")
        return email

# ----------------- Inserir Refeição ----------------- #

def registrar_refeicao(email_usuario):
    print("\n🍽️ Registro de Refeição Diária")
    alimento = input("Digite o nome do alimento consumido: ").strip().lower()

    # Verificar se alimento está cadastrado
    cursor.execute("SELECT nome FROM alimentos WHERE nome = ?", (alimento,))
    if not cursor.fetchone():
        print("❌ Alimento desconhecido! Peça ao administrador para cadastrá-lo.")
        return

    try:
        quantidade = float(input("Digite a quantidade consumida (em gramas): "))
        if quantidade <= 0:
            print("❌ Quantidade deve ser maior que zero.")
            return
    except ValueError:
        print("❌ Digite apenas números válidos para a quantidade.")
        return

    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO refeicoes (email_usuario, alimento, quantidade_gramas, data)
        VALUES (?, ?, ?, ?)
    ''', (email_usuario, alimento, quantidade, data))
    conn.commit()
    print("✅ Refeição registrada com sucesso!")

# ----------------- Menu do Usuário Logado ----------------- #

def menu_usuario_logado(email):
    while True:
        print(f"\n🔐 Bem-vindo, {email}")
        print("1. Ver meus dados")
        print("2. Registrar refeição diária")
        print("3. Logout")
        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            cursor.execute("SELECT peso, altura, sexo, dieta, imc FROM usuarios WHERE email = ?", (email,))
            dados = cursor.fetchone()
            if dados:
                print(f"\n📄 Seus dados:")
                print(f"Peso: {dados[0]} kg")
                print(f"Altura: {dados[1]} m")
                print(f"Sexo: {dados[2]}")
                print(f"Dieta: {dados[3]}")
                print(f"IMC: {dados[4]}")
            else:
                print("⚠️ Erro ao carregar dados.")
        elif escolha == "2":
            registrar_refeicao(email)
        elif escolha == "3":
            print("🔒 Logout realizado.")
            break
        else:
            print("❌ Opção inválida!")

# ----------------- Funções de Administrador ----------------- #

def menu_administrador():
    senha_admin = input("Digite a senha do administrador: ")
    if senha_admin != "admin123":
        print("❌ Senha incorreta!")
        return

    while True:
        print("\n🔧 Menu do Administrador")
        print("1. Inserir alimentos")
        print("2. Acompanhar usuários")
        print("3. Sair do modo administrador")
        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            alimento = input("Digite o nome do alimento a ser cadastrado: ").strip().lower()
            cursor.execute("SELECT * FROM alimentos WHERE nome = ?", (alimento,))
            if cursor.fetchone():
                print("⚠️ Alimento já está cadastrado.")
            else:
                cursor.execute("INSERT INTO alimentos (nome) VALUES (?)", (alimento,))
                conn.commit()
                print("✅ Alimento cadastrado com sucesso.")
        elif escolha == "2":
            print("\n👥 Lista de usuários:")
            cursor.execute("SELECT email, dieta, imc FROM usuarios")
            for row in cursor.fetchall():
                print(f"- {row[0]} | Dieta: {row[1]} | IMC: {row[2]}")
        elif escolha == "3":
            print("🚪 Saindo do modo administrador.")
            break
        else:
            print("❌ Opção inválida!")

# ----------------- Menu Principal ----------------- #

def menu_principal():
    while True:
        print("\n===== MENU - APLICATIVO DE NUTRIÇÃO =====")
        print("1. Sou Usuário")
        print("2. Sou Administrador")
        print("3. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            while True:
                print("\n--- Menu do Usuário ---")
                print("1. Registrar novo usuário")
                print("2. Fazer login")
                print("3. Voltar")
                escolha = input("Escolha uma opção: ")
                if escolha == "1":
                    registrar_usuario()
                elif escolha == "2":
                    email = login()
                    if email:
                        menu_usuario_logado(email)
                elif escolha == "3":
                    break
                else:
                    print("❌ Opção inválida.")
        elif opcao == "2":
            menu_administrador()
        elif opcao == "3":
            print("👋 Saindo do sistema. Até logo!")
            break
        else:
            print("❌ Opção inválida!")

# ----------------- Executar sistema ----------------- #
menu_principal()
conn.close()
