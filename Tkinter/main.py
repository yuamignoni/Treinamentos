import requests
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# URL da API do Flask (ensure this is correct, e.g., using the host's IP address or localhost if running on the same machine)
flask_api_url = "http://localhost:5000"

# Inicializa o banco de dados SQLite
conn = sqlite3.connect('internal_db.sqlite')
cursor = conn.cursor()

# Criação das tabelas se não existirem
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    username TEXT PRIMARY KEY,
    senha TEXT NOT NULL,
    cargo TEXT NOT NULL
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS funcionarios (
    emp_id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    cargo TEXT NOT NULL
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS treinamentos (
    emp_id TEXT,
    treinamento TEXT,
    validade TEXT,
    FOREIGN KEY(emp_id) REFERENCES funcionarios(emp_id)
)
''')
conn.commit()

# Função para sincronizar com o servidor Flask
def sync_with_server():
    try:
        response = requests.get(f"{flask_api_url}/sync")
        if response.status_code == 200:
            server_db = response.json()
            sync_local_db_with_server(server_db)
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar ao servidor: {e}")

# Função para sincronizar a base de dados local com a do servidor
def sync_local_db_with_server(server_db):
    with conn:
        conn.execute('DELETE FROM usuarios')
        conn.execute('DELETE FROM funcionarios')
        conn.execute('DELETE FROM treinamentos')
        
        for user in server_db['usuarios']:
            conn.execute('INSERT INTO usuarios (username, senha, cargo) VALUES (?, ?, ?)', 
                         (user['username'], user['senha'], user['cargo']))
        for emp in server_db['funcionarios']:
            conn.execute('INSERT INTO funcionarios (emp_id, nome, cargo) VALUES (?, ?, ?)', 
                         (emp['emp_id'], emp['nome'], emp['cargo']))
        for tr in server_db['treinamentos']:
            conn.execute('INSERT INTO treinamentos (emp_id, treinamento, validade) VALUES (?, ?, ?)', 
                         (tr['emp_id'], tr['treinamento'], tr['validade']))

# Classe principal da aplicação Tkinter
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Treinamentos")
        self.root.geometry("800x600")
        self.current_user = None

        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 12), padding=5)
        self.style.configure("TButton", font=("Arial", 12), padding=5)
        self.style.configure("TEntry", font=("Arial", 12), padding=5)
        self.style.configure("TCombobox", font=("Arial", 12), padding=5)
        self.style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        self.style.configure("Treeview", font=("Arial", 12))

        self.root.configure(bg='#f0f0f0')
        self.show_login_screen()

    def show_login_screen(self):
        self.clear_screen()

        ttk.Label(self.root, text="Usuário:").pack(pady=5)
        self.username_entry = ttk.Entry(self.root)
        self.username_entry.pack(pady=5)

        ttk.Label(self.root, text="Senha:").pack(pady=5)
        self.password_entry = ttk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        ttk.Button(self.root, text="Login", command=self.login).pack(pady=10)

    def show_main_screen(self):
        self.clear_screen()

        ttk.Label(self.root, text=f"Bem-vindo, {self.current_user}", font=("Arial", 14, "bold")).pack(pady=10)

        ttk.Button(self.root, text="Gerenciar Funcionários", command=self.show_employee_management).pack(pady=5)
        ttk.Button(self.root, text="Gerenciar Treinamentos", command=self.show_training_management).pack(pady=5)
        cursor.execute('SELECT cargo FROM usuarios WHERE username = ?', (self.current_user,))
        cargo = cursor.fetchone()[0]
        if cargo == "Admin":
            ttk.Button(self.root, text="Cadastrar Usuário", command=self.show_register_user_screen).pack(pady=5)
        ttk.Button(self.root, text="Sair", command=self.show_login_screen).pack(pady=5)

    def show_register_user_screen(self):
        self.clear_screen()

        ttk.Label(self.root, text="Novo Usuário:", font=("Arial", 14, "bold")).pack(pady=5)
        ttk.Label(self.root, text="Usuário:").pack(pady=5)
        self.new_username_entry = ttk.Entry(self.root)
        self.new_username_entry.pack(pady=5)

        ttk.Label(self.root, text="Senha:").pack(pady=5)
        self.new_password_entry = ttk.Entry(self.root, show="*")
        self.new_password_entry.pack(pady=5)

        ttk.Label(self.root, text="Cargo:").pack(pady=5)
        self.new_cargo_entry = ttk.Entry(self.root)
        self.new_cargo_entry.pack(pady=5)

        ttk.Button(self.root, text="Cadastrar", command=self.register_user).pack(pady=10)
        ttk.Button(self.root, text="Voltar ao Menu Principal", command=self.show_main_screen).pack(pady=5)

    def show_employee_management(self):
        self.clear_screen()

        ttk.Label(self.root, text="Gerenciamento de Funcionários", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self.root, text="Nome:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.nome_entry = ttk.Entry(self.root)
        self.nome_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        ttk.Label(self.root, text="Cargo:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.cargo_entry = ttk.Entry(self.root)
        self.cargo_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        ttk.Label(self.root, text="ID do Funcionário:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.id_entry = ttk.Entry(self.root)
        self.id_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        ttk.Button(self.root, text="Adicionar Funcionário", command=self.add_employee).grid(row=4, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self.root, columns=("Nome", "Cargo", "ID"), show='headings')
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Cargo", text="Cargo")
        self.tree.heading("ID", text="ID do Funcionário")
        self.tree.grid(row=5, column=0, columnspan=2, pady=10)
        self.load_employees()

        ttk.Button(self.root, text="Voltar ao Menu Principal", command=self.show_main_screen).grid(row=6, column=0, columnspan=2, pady=10)

    def show_training_management(self):
        self.clear_screen()

        ttk.Label(self.root, text="Selecionar Funcionário:", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.funcionario_combobox = ttk.Combobox(self.root)
        cursor.execute('SELECT emp_id FROM funcionarios')
        self.funcionario_combobox['values'] = [row[0] for row in cursor.fetchall()]
        self.funcionario_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.funcionario_combobox.bind("<<ComboboxSelected>>", self.update_employee_info)

        self.funcionario_info_label = ttk.Label(self.root, text="")
        self.funcionario_info_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        ttk.Label(self.root, text="Treinamento:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.treinamento_entry = ttk.Entry(self.root)
        self.treinamento_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        ttk.Label(self.root, text="Validade (dd/mm/yyyy):").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.validade_entry = ttk.Entry(self.root)
        self.validade_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        ttk.Button(self.root, text="Adicionar/Atualizar Treinamento", command=self.add_update_training).grid(row=4, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self.root, columns=("Treinamento", "Validade"), show='headings')
        self.tree.heading("Treinamento", text="Treinamento")
        self.tree.heading("Validade", text="Validade")
        self.tree.grid(row=5, column=0, columnspan=2, pady=10)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

        ttk.Button(self.root, text="Excluir Treinamento", command=self.delete_training).grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(self.root, text="Voltar ao Menu Principal", command=self.show_main_screen).grid(row=7, column=0, columnspan=2, pady=10)

    def update_employee_info(self, event):
        selected_employee = self.funcionario_combobox.get()
        cursor.execute('SELECT nome, cargo FROM funcionarios WHERE emp_id = ?', (selected_employee,))
        employee = cursor.fetchone()
        if employee:
            self.funcionario_info_label.config(text=f"Nome: {employee[0]}, Cargo: {employee[1]}")
            self.load_trainings(selected_employee)

    def add_employee(self):
        nome = self.nome_entry.get()
        cargo = self.cargo_entry.get()
        emp_id = self.id_entry.get()

        if nome and cargo and emp_id:
            with conn:
                conn.execute('INSERT OR REPLACE INTO funcionarios (emp_id, nome, cargo) VALUES (?, ?, ?)', 
                             (emp_id, nome, cargo))
            self.load_employees()
            self.sync_with_flask()

    def load_employees(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        cursor.execute('SELECT nome, cargo, emp_id FROM funcionarios')
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)

    def add_update_training(self):
        emp_id = self.funcionario_combobox.get()
        treinamento = self.treinamento_entry.get()
        validade = self.validade_entry.get()

        if emp_id and treinamento and validade:
            with conn:
                conn.execute('INSERT INTO treinamentos (emp_id, treinamento, validade) VALUES (?, ?, ?)', 
                             (emp_id, treinamento, validade))
            self.load_trainings(emp_id)
            self.sync_with_flask()

    def load_trainings(self, emp_id):
        for i in self.tree.get_children():
            self.tree.delete(i)
        cursor.execute('SELECT treinamento, validade FROM treinamentos WHERE emp_id = ?', (emp_id,))
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)

    def on_tree_select(self, event):
        selected_item = self.tree.selection()[0]
        training = self.tree.item(selected_item, 'values')
        self.treinamento_entry.delete(0, tk.END)
        self.treinamento_entry.insert(0, training[0])
        self.validade_entry.delete(0, tk.END)
        self.validade_entry.insert(0, training[1])

    def delete_training(self):
        selected_item = self.tree.selection()[0]
        training = self.tree.item(selected_item, 'values')
        emp_id = self.funcionario_combobox.get()
        with conn:
            conn.execute('DELETE FROM treinamentos WHERE emp_id = ? AND treinamento = ?', (emp_id, training[0]))
        self.load_trainings(emp_id)
        self.sync_with_flask()

    def sync_with_flask(self):
        try:
            cursor.execute('SELECT * FROM usuarios')
            usuarios = [{'username': row[0], 'senha': row[1], 'cargo': row[2]} for row in cursor.fetchall()]

            cursor.execute('SELECT * FROM funcionarios')
            funcionarios = [{'emp_id': row[0], 'nome': row[1], 'cargo': row[2]} for row in cursor.fetchall()]

            cursor.execute('SELECT * FROM treinamentos')
            treinamentos = [{'emp_id': row[0], 'treinamento': row[1], 'validade': row[2]} for row in cursor.fetchall()]

            local_db = {
                'usuarios': usuarios,
                'funcionarios': funcionarios,
                'treinamentos': treinamentos
            }

            response = requests.post(f"{flask_api_url}/sync", json=local_db)
            if response.status_code != 200:
                print(f"Erro ao sincronizar com o servidor: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao conectar ao servidor: {e}")

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        cursor.execute('SELECT senha FROM usuarios WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user and user[0] == password:
            self.current_user = username
            self.show_main_screen()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos")

    def register_user(self):
        new_username = self.new_username_entry.get()
        new_password = self.new_password_entry.get()
        new_cargo = self.new_cargo_entry.get()

        if new_username and new_password and new_cargo:
            with conn:
                conn.execute('INSERT INTO usuarios (username, senha, cargo) VALUES (?, ?, ?)', 
                             (new_username, new_password, new_cargo))
            self.sync_with_flask()
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso")
            self.show_main_screen()
        else:
            messagebox.showerror("Erro", "Preencha todos os campos")

if __name__ == "__main__":
    sync_with_server()
    root = tk.Tk()
    app = App(root)
    root.mainloop()
