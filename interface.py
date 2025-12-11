import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from converters.image_factory import ImageFactory

# --- PALETA INFERNAL (VISUAL CLÁSSICO v1) ---
COLOR_BG = "#0f0f0f"         # Fundo Preto
COLOR_FG = "#e0e0e0"         # Texto Cinza Claro
COLOR_ACCENT = "#ff3333"     # Vermelho Sangue (Títulos)
COLOR_DARK_RED = "#800000"   # Vermelho Escuro (Hover/Select)
COLOR_SURFACE = "#1a1a1a"    # Cinza Escuro (Listas/Campos)

class MetamorphosisGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("METAMORPHOSIS | Chaos Factory")
        self.root.geometry("850x600")
        self.root.configure(bg=COLOR_BG)

        self.factory = ImageFactory()
        self.files_map = {} # {id_tree: caminho_completo}
        self.target_var = tk.StringVar()

        self._setup_styles()
        self._setup_ui()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configuração da Lista (Treeview)
        style.configure("Treeview", 
                        background=COLOR_SURFACE, 
                        foreground=COLOR_FG, 
                        fieldbackground=COLOR_SURFACE, 
                        borderwidth=0,
                        font=("Consolas", 10))
        
        style.configure("Treeview.Heading", 
                        background="#2a2a2a", 
                        foreground=COLOR_ACCENT, 
                        font=("Segoe UI", 9, "bold"))
        
        style.map('Treeview', background=[('selected', COLOR_DARK_RED)])

        # Configuração Geral
        style.configure("TFrame", background=COLOR_BG)
        style.configure("TLabel", background=COLOR_BG, foreground=COLOR_FG)
        style.configure("Title.TLabel", font=("Impact", 24), foreground=COLOR_ACCENT)
        style.configure("Status.TLabel", font=("Consolas", 9), foreground="#666666")

        # Botões do Mal
        style.configure("TButton", 
                        background="#2a2a2a", 
                        foreground="#ffffff", 
                        font=("Segoe UI", 9, "bold"),
                        borderwidth=1,
                        focuscolor="none")
        style.map('TButton', background=[('active', COLOR_DARK_RED)])

        # Dropdown
        style.configure("TCombobox", fieldbackground=COLOR_SURFACE, background="#2a2a2a", foreground=COLOR_FG, arrowcolor=COLOR_FG)

    def _setup_ui(self):
        # Header
        header = ttk.Frame(self.root, padding="20 20 20 10")
        header.pack(fill=tk.X)
        ttk.Label(header, text="M E T A M O R P H O S I S", style="Title.TLabel").pack(pady=(0, 10))
        
        # Painel de Controle
        ctrl_panel = ttk.Frame(self.root, padding="20 0 20 10")
        ctrl_panel.pack(fill=tk.X)

        # Seletor de Destino
        lbl_target = ttk.Label(ctrl_panel, text="FORJAR PARA O FORMATO:", font=("Segoe UI", 10, "bold"))
        lbl_target.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cb_target = ttk.Combobox(ctrl_panel, textvariable=self.target_var, state="readonly", width=10)
        self.cb_target['values'] = self.factory.get_supported_targets()
        self.cb_target.current(0)
        self.cb_target.pack(side=tk.LEFT)

        # Botões de Ação
        btn_frame = ttk.Frame(ctrl_panel)
        btn_frame.pack(side=tk.RIGHT)

        self.btn_add = ttk.Button(btn_frame, text="INVOCAR ARQUIVOS", command=self.add_files)
        self.btn_add.pack(side=tk.LEFT, padx=5)

        self.btn_clear = ttk.Button(btn_frame, text="LIMPAR ALTAR", command=self.clear_list)
        self.btn_clear.pack(side=tk.LEFT, padx=5)

        # Lista de Oferendas
        list_frame = ttk.Frame(self.root, padding="20 10 20 10")
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("file", "ext", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="extended")
        
        self.tree.heading("file", text="Arquivo Original")
        self.tree.heading("ext", text="Tipo")
        self.tree.heading("status", text="Estado do Ritual")
        
        self.tree.column("file", width=450)
        self.tree.column("ext", width=80, anchor="center")
        self.tree.column("status", width=200, anchor="w")
        
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Rodapé / Execução
        footer = ttk.Frame(self.root, padding="20")
        footer.pack(fill=tk.X)

        self.btn_run = ttk.Button(footer, text="INICIAR TRANSMUTAÇÃO", command=self.run_process)
        self.btn_run.pack(fill=tk.X, ipady=12) # Botão gordo e satisfatório

        self.lbl_status = ttk.Label(footer, text="Aguardando oferendas...", style="Status.TLabel", anchor="center")
        self.lbl_status.pack(pady=(10, 0))

    def add_files(self):
        filetypes = [("Imagens Suportadas", "*.png *.jpg *.jpeg *.webp *.bmp *.ico *.tiff"), ("Todos", "*.*")]
        files = filedialog.askopenfilenames(title="Selecione as Oferendas", filetypes=filetypes)
        
        for f in files:
            if self.factory.is_valid_source(f):
                fname = os.path.basename(f)
                ext = os.path.splitext(fname)[1]
                # Verifica duplicatas visualmente
                found = False
                for item in self.files_map.values():
                    if item == f: found = True
                
                if not found:
                    item_id = self.tree.insert("", tk.END, values=(fname, ext, "Pendente"))
                    self.files_map[item_id] = f
        
        self.lbl_status.config(text=f"{len(self.files_map)} almas prontas para o sacrifício.")

    def clear_list(self):
        self.tree.delete(*self.tree.get_children())
        self.files_map.clear()
        self.lbl_status.config(text="Altar limpo.")

    def run_process(self):
        if not self.files_map:
            messagebox.showwarning("Vazio", "O altar requer sacrifícios. Adicione arquivos.")
            return

        target_ext = self.target_var.get()
        total = len(self.files_map)
        done = 0

        self.btn_run.config(state="disabled")
        self.lbl_status.config(text=f"Transmutando matéria para {target_ext}...")
        
        # Loop do Caos
        for item_id in self.files_map:
            filepath = self.files_map[item_id]
            
            # Feedback visual
            self.tree.set(item_id, "status", "Processando...")
            self.tree.selection_set(item_id)
            self.tree.see(item_id)
            self.root.update()

            success, msg = self.factory.convert(filepath, target_ext)
            
            if success:
                self.tree.set(item_id, "status", f"✔ FEITO")
                done += 1
            else:
                self.tree.set(item_id, "status", f"✖ {msg}")

        self.btn_run.config(state="normal")
        self.lbl_status.config(text=f"Ritual finalizado. {done}/{total} transmutados.")
        messagebox.showinfo("Sucesso", "A transmutação foi concluída com sucesso.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MetamorphosisGUI(root)
    root.mainloop()