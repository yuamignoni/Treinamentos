import requests
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

flask_api_url = "http://localhost:5000"

conn = sqlite3.connect('internal_db.sqlite')
cursor = conn.cursor()

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

def sync_with_server():
    try:
        response = requests.get(f"{flask_api_url}/sync")
        if response.status_code == 200:
            server_db = response.json()
            sync_local_db_with_server(server_db)
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar ao servidor: {e}")

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

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Treinamentos")
        self.root.geometry("900x700")
        self.current_user = None

        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Helvetica", 12))
        self.style.configure("TButton", font=("Helvetica", 12), padding=6)
        self.style.configure("TEntry", font=("Helvetica", 12))
        self.style.configure("TCombobox", font=("Helvetica", 12))
        self.style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
        self.style.configure("Treeview", font=("Helvetica", 12))
        
        self.root.configure(bg='#f0f0f0')
        self.show_login_screen()

    def show_login_screen(self):
        self.clear_screen()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Usuário:").pack(pady=5)
        self.username_entry = ttk.Entry(frame)
        self.username_entry.pack(pady=5)

        ttk.Label(frame, text="Senha:").pack(pady=5)
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.pack(pady=5)

        login_button = ttk.Button(frame, text="Login", command=self.login)
        login_button.pack(pady=10)
        login_button.config(width=20)

    def show_main_screen(self):
        self.clear_screen()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text=f"Bem-vindo, {self.current_user}", font=("Helvetica", 14, "bold")).pack(pady=10)

        cursor.execute('SELECT cargo FROM usuarios WHERE username = ?', (self.current_user,))
        cargo = cursor.fetchone()[0]

        if cargo in ["Admin", "Gerente"]:
            gerenciamento_button = ttk.Button(frame, text="Gerenciar Funcionários", command=self.show_employee_management)
            gerenciamento_button.pack(pady=5)
            gerenciamento_button.config(width=25)

            treinamento_button = ttk.Button(frame, text="Gerenciar Treinamentos", command=self.show_training_management)
            treinamento_button.pack(pady=5)
            treinamento_button.config(width=25)
            
            if cargo == "Admin":
                cadastro_button = ttk.Button(frame, text="Cadastrar Usuário", command=self.show_register_user_screen)
                cadastro_button.pack(pady=5)
                cadastro_button.config(width=25)
        elif cargo == "Funcionário":
            treinamento_button = ttk.Button(frame, text="Visualizar Treinamentos", command=self.show_training_view)
            treinamento_button.pack(pady=5)
            treinamento_button.config(width=25)

        sair_button = ttk.Button(frame, text="Sair", command=self.show_login_screen)
        sair_button.pack(pady=5)
        sair_button.config(width=25)

    def show_register_user_screen(self):
        self.clear_screen()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Novo Usuário:", font=("Helvetica", 14, "bold")).pack(pady=5)
        ttk.Label(frame, text="Usuário:").pack(pady=5)
        self.new_username_entry = ttk.Entry(frame)
        self.new_username_entry.pack(pady=5)

        ttk.Label(frame, text="Senha:").pack(pady=5)
        self.new_password_entry = ttk.Entry(frame, show="*")
        self.new_password_entry.pack(pady=5)

        ttk.Label(frame, text="Cargo:").pack(pady=5)
        self.new_cargo_combobox = ttk.Combobox(frame, values=["Admin", "Gerente", "Funcionário"])
        self.new_cargo_combobox.pack(pady=5)

        cadastrar_button = ttk.Button(frame, text="Cadastrar", command=self.register_user)
        cadastrar_button.pack(pady=10)
        cadastrar_button.config(width=20)

        voltar_button = ttk.Button(frame, text="Voltar ao Menu Principal", command=self.show_main_screen)
        voltar_button.pack(pady=5)
        voltar_button.config(width=20)

    def show_employee_management(self):
        self.clear_screen()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Gerenciamento de Funcionários", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(frame, text="Nome:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.nome_entry = ttk.Entry(frame)
        self.nome_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        ttk.Label(frame, text="Cargo:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.cargo_entry = ttk.Entry(frame)
        self.cargo_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        ttk.Label(frame, text="ID do Funcionário:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.id_entry = ttk.Entry(frame)
        self.id_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        adicionar_button = ttk.Button(frame, text="Adicionar Funcionário", command=self.add_employee)
        adicionar_button.grid(row=4, column=0, columnspan=2, pady=10)
        adicionar_button.config(width=25)

        self.tree = ttk.Treeview(frame, columns=("Nome", "Cargo", "ID"), show='headings')
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Cargo", text="Cargo")
        self.tree.heading("ID", text="ID do Funcionário")
        self.tree.grid(row=5, column=0, columnspan=2, pady=10)
        self.load_employees()

        voltar_button = ttk.Button(frame, text="Voltar ao Menu Principal", command=self.show_main_screen)
        voltar_button.grid(row=6, column=0, columnspan=2, pady=10)
        voltar_button.config(width=25)

    def show_training_management(self):
        self.clear_screen()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Selecionar Funcionário:", font=("Helvetica", 14, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.funcionario_combobox = ttk.Combobox(frame)
        cursor.execute('SELECT emp_id FROM funcionarios')
        self.funcionario_combobox['values'] = [row[0] for row in cursor.fetchall()]
        self.funcionario_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.funcionario_combobox.bind("<<ComboboxSelected>>", self.update_employee_info)

        self.funcionario_info_label = ttk.Label(frame, text="Informações do Funcionário: ")
        self.funcionario_info_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        ttk.Label(frame, text="Treinamento:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.treinamento_entry = ttk.Entry(frame)
        self.treinamento_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        ttk.Label(frame, text="Validade:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.validade_entry = ttk.Entry(frame)
        self.validade_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        add_update_button = ttk.Button(frame, text="Adicionar/Atualizar Treinamento", command=self.add_update_training)
        add_update_button.grid(row=4, column=0, columnspan=2, pady=10)
        add_update_button.config(width=30)

        self.tree = ttk.Treeview(frame, columns=("Treinamento", "Validade"), show='headings')
        self.tree.heading("Treinamento", text="Treinamento")
        self.tree.heading("Validade", text="Validade")
        self.tree.grid(row=5, column=0, columnspan=2, pady=10)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

        excluir_button = ttk.Button(frame, text="Excluir Treinamento", command=self.delete_training)
        excluir_button.grid(row=6, column=0, columnspan=2, pady=10)
        excluir_button.config(width=25)

        voltar_button = ttk.Button(frame, text="Voltar ao Menu Principal", command=self.show_main_screen)
        voltar_button.grid(row=7, column=0, columnspan=2, pady=10)
        voltar_button.config(width=25)

    def show_training_view(self):
        self.clear_screen()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Visualização de Treinamentos", font=("Helvetica", 14, "bold")).pack(pady=10)

        search_frame = ttk.Frame(frame)
        search_frame.pack(pady=10)

        ttk.Label(search_frame, text="Buscar por:").pack(side="left", padx=5)
        self.search_combobox = ttk.Combobox(search_frame, values=["Funcionário", "Treinamento"])
        self.search_combobox.pack(side="left", padx=5)

        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", padx=5)

        search_button = ttk.Button(search_frame, text="Buscar", command=self.search_trainings)
        search_button.pack(side="left", padx=5)
        search_button.config(width=15)

        self.tree = ttk.Treeview(frame, columns=("Funcionário", "Treinamento", "Validade"), show='headings')
        self.tree.heading("Funcionário", text="Funcionário")
        self.tree.heading("Treinamento", text="Treinamento")
        self.tree.heading("Validade", text="Validade")
        self.tree.pack(pady=10)
        self.load_all_trainings()

        voltar_button = ttk.Button(frame, text="Voltar ao Menu Principal", command=self.show_main_screen)
        voltar_button.pack(pady=10)
        voltar_button.config(width=25)

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

    def load_all_trainings(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        cursor.execute('SELECT funcionarios.nome, treinamentos.treinamento, treinamentos.validade FROM treinamentos JOIN funcionarios ON treinamentos.emp_id = funcionarios.emp_id')
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)

    def search_trainings(self):
        search_by = self.search_combobox.get()
        search_term = self.search_entry.get()

        if search_by and search_term:
            for i in self.tree.get_children():
                self.tree.delete(i)
            if search_by == "Funcionário":
                cursor.execute('''
                    SELECT funcionarios.nome, treinamentos.treinamento, treinamentos.validade 
                    FROM treinamentos 
                    JOIN funcionarios ON treinamentos.emp_id = funcionarios.emp_id 
                    WHERE funcionarios.nome LIKE ?
                ''', (f'%{search_term}%',))
            elif search_by == "Treinamento":
                cursor.execute('''
                    SELECT funcionarios.nome, treinamentos.treinamento, treinamentos.validade 
                    FROM treinamentos 
                    JOIN funcionarios ON treinamentos.emp_id = funcionarios.emp_id 
                    WHERE treinamentos.treinamento LIKE ?
                ''', (f'%{search_term}%',))
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
        new_cargo = self.new_cargo_combobox.get()

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
    root = tk.Tk()
    app = App(root)
    root.mainloop()
