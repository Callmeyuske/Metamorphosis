import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
from converters.transmuter import Transmuter

# Cores do Tema
COLOR_BG = "#0f0f0f"
COLOR_FG = "#e0e0e0"
COLOR_ACCENT = "#ff3333"
COLOR_DARK_RED = "#800000"
COLOR_SURFACE = "#1a1a1a"

class MetamorphosisGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("METAMORPHOSIS v5 | The Librarian (Fixed)")
        self.root.geometry("900x650")
        self.root.configure(bg=COLOR_BG)

        self.engine = Transmuter()
        
        self.files_map = {} 
        self.target_var = tk.StringVar()

        # Mapa de Compatibilidade
        self.compat_map = {
            'book': ['.epub'],
            'video': ['.mp4', '.gif', '.mov', '.avi', '.mkv'],
            'audio': ['.mp3', '.wav'],
            'image': ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.ico']
        }

        self._setup_styles()
        self._setup_ui()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
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
        
        style.configure("TFrame", background=COLOR_BG)
        style.configure("TLabel", background=COLOR_BG, foreground=COLOR_FG)
        style.configure("Title.TLabel", font=("Impact", 24), foreground=COLOR_ACCENT)
        style.configure("Status.TLabel", font=("Consolas", 9), foreground="#666666")
        
        style.configure("TButton", 
                        background="#2a2a2a", 
                        foreground="#ffffff", 
                        font=("Segoe UI", 9, "bold"), 
                        borderwidth=1, 
                        focuscolor="none")
        style.map('TButton', background=[('active', COLOR_DARK_RED)])
        
        style.configure("TCombobox", 
                        fieldbackground=COLOR_SURFACE, 
                        background="#2a2a2a", 
                        foreground=COLOR_FG, 
                        arrowcolor=COLOR_FG)

    def _setup_ui(self):
        header = ttk.Frame(self.root, padding="20 20 20 10")
        header.pack(fill=tk.X)
        ttk.Label(header, text="M E T A M O R P H O S I S  V", style="Title.TLabel").pack(pady=(0, 10))
        
        ctrl_panel = ttk.Frame(self.root, padding="20 0 20 10")
        ctrl_panel.pack(fill=tk.X)

        lbl_target = ttk.Label(ctrl_panel, text="OBJETIVO DO RITUAL:", font=("Segoe UI", 10, "bold"))
        lbl_target.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cb_target = ttk.Combobox(ctrl_panel, textvariable=self.target_var, state="readonly", width=25)
        self.cb_target['values'] = self.engine.get_all_targets()
        self.cb_target.current(0)
        self.cb_target.pack(side=tk.LEFT)

        btn_frame = ttk.Frame(ctrl_panel)
        btn_frame.pack(side=tk.RIGHT)
        
        self.btn_add = ttk.Button(btn_frame, text="INVOCAR MÍDIA", command=self.add_files)
        self.btn_add.pack(side=tk.LEFT, padx=5)
        
        self.btn_clear = ttk.Button(btn_frame, text="LIMPAR", command=self.clear_list)
        self.btn_clear.pack(side=tk.LEFT, padx=5)

        list_frame = ttk.Frame(self.root, padding="20 10 20 10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("file", "ext", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="extended")
        
        self.tree.heading("file", text="Arquivo Original")
        self.tree.heading("ext", text="Tipo")
        self.tree.heading("status", text="Estado")
        
        self.tree.column("file", width=450)
        self.tree.column("ext", width=80, anchor="center")
        self.tree.column("status", width=250, anchor="w")
        
        # --- BINDING REFORÇADO (MÁGICA AQUI) ---
        # Dispara ao selecionar, ao soltar o mouse e ao usar setas do teclado
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        self.tree.bind("<ButtonRelease-1>", self.on_item_select)
        self.tree.bind("<KeyRelease>", self.on_item_select)
        
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        footer = ttk.Frame(self.root, padding="20")
        footer.pack(fill=tk.X)
        
        self.btn_run = ttk.Button(footer, text="EXECUTAR TRANSMUTAÇÃO", command=self.start_thread)
        self.btn_run.pack(fill=tk.X, ipady=12)
        
        self.lbl_status = ttk.Label(footer, text="Aguardando oferendas...", style="Status.TLabel", anchor="center")
        self.lbl_status.pack(pady=(10, 0))

    def on_item_select(self, event):
        """Atualiza Combobox com detecção tripla de eventos."""
        try:
            selected_items = self.tree.selection()
            
            # Se a seleção estiver vazia ou múltipla, mostra tudo
            if len(selected_items) != 1:
                # Só reseta se realmente mudou o estado para evitar flicker
                return

            iid = selected_items[0]
            file_path = self.files_map.get(iid)
            
            if not file_path: return
            
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()

            options = []
            
            # Lógica de Filtro
            if ext in self.compat_map['book']:
                options = ['.pdf']
                
            elif ext in self.compat_map['video']:
                options = ['.mp3', '.wav', '.mp4', '.gif']
                
            elif ext in self.compat_map['audio']:
                options = ['.mp3', '.wav', '.mp4']
                
            elif ext in self.compat_map['image']:
                options = ['.png', '.jpg', '.jpeg', '.webp', '.ico', '.pdf', 'PNG (Sem Fundo)']
                
            else:
                options = self.engine.get_all_targets()

            # Atualiza apenas se as opções forem diferentes das atuais para performance
            self._update_combo_options(options)
            
            # Debug visual no terminal
            print(f"[DEBUG] Arquivo: {ext} | Opções carregadas: {len(options)}")
            
        except Exception as e:
            print(f"Erro no evento de seleção: {e}")

    def _update_combo_options(self, options):
        current_values = list(self.cb_target['values'])
        
        # Se a lista já é a mesma, não faz nada (evita resetar seleção à toa)
        if current_values == options:
            return

        current_selection = self.target_var.get()
        self.cb_target['values'] = options
        
        if current_selection in options:
            self.cb_target.set(current_selection)
        elif options:
            self.cb_target.current(0)

    def add_files(self):
        ftypes = [
            ("Mídia Suportada", "*.png *.jpg *.jpeg *.webp *.mp4 *.gif *.mp3 *.wav *.epub"),
            ("Imagens", "*.png *.jpg *.jpeg *.bmp"),
            ("Vídeo/GIF", "*.mp4 *.gif *.avi *.mkv"),
            ("Livros", "*.epub"),
            ("Todos", "*.*")
        ]
        files = filedialog.askopenfilenames(title="Selecione as Oferendas", filetypes=ftypes)
        
        for f in files:
            if self.engine.is_valid_source(f):
                fname = os.path.basename(f)
                ext = os.path.splitext(fname)[1]
                
                if f not in self.files_map.values():
                    iid = self.tree.insert("", tk.END, values=(fname, ext, "Pendente"))
                    self.files_map[iid] = f
        
        self.lbl_status.config(text=f"{len(self.files_map)} itens carregados.")
        
        # Se adicionou apenas 1 arquivo, já seleciona ele automaticamente para ativar o filtro
        if len(self.files_map) == 1:
            first_iid = list(self.files_map.keys())[0]
            self.tree.selection_set(first_iid)
            self.on_item_select(None) # Força atualização manual

    def clear_list(self):
        self.tree.delete(*self.tree.get_children())
        self.files_map.clear()
        self.lbl_status.config(text="Altar limpo.")
        # Reseta o combo para mostrar tudo
        self.cb_target['values'] = self.engine.get_all_targets()
        self.cb_target.current(0)

    def start_thread(self):
        t = threading.Thread(target=self.run_process)
        t.start()

    def run_process(self):
        if not self.files_map:
            messagebox.showwarning("Vazio", "O altar requer sacrifícios. Adicione arquivos.")
            return

        target = self.target_var.get()
        self.btn_run.config(state="disabled")
        self.lbl_status.config(text=f"Processando fila para {target}...")
        
        done = 0
        total = len(self.files_map)

        for iid in list(self.files_map.keys()):
            fpath = self.files_map[iid]
            
            self.root.after(0, lambda id=iid: self.tree.set(id, "status", "Processando..."))
            self.root.after(0, lambda id=iid: self.tree.see(id))
            
            success, msg = self.engine.process(fpath, target)
            
            if success:
                self.root.after(0, lambda id=iid: self.tree.set(id, "status", "✔ CONCLUÍDO"))
                done += 1
            else:
                self.root.after(0, lambda id=iid, m=msg: self.tree.set(id, "status", f"✖ {m}"))

        self.btn_run.config(state="normal")
        self.lbl_status.config(text=f"Ritual finalizado. {done}/{total} arquivos processados.")
        messagebox.showinfo("Fim", f"Processo concluído.\n{done} arquivos gerados.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MetamorphosisGUI(root)
    root.mainloop()