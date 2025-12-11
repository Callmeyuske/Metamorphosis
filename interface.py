import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
from converters.transmuter import Transmuter

# --- PALETA INFERNAL ---
COLOR_BG = "#0f0f0f"
COLOR_FG = "#e0e0e0"
COLOR_ACCENT = "#ff3333"
COLOR_DARK_RED = "#800000"
COLOR_SURFACE = "#1a1a1a"

class MetamorphosisGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("METAMORPHOSIS")
        self.root.geometry("900x650")
        self.root.configure(bg=COLOR_BG)

        self.engine = Transmuter()
        self.files_map = {} 
        self.target_var = tk.StringVar()

        self._setup_styles()
        self._setup_ui()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background=COLOR_SURFACE, foreground=COLOR_FG, fieldbackground=COLOR_SURFACE, borderwidth=0, font=("Consolas", 10))
        style.configure("Treeview.Heading", background="#2a2a2a", foreground=COLOR_ACCENT, font=("Segoe UI", 9, "bold"))
        style.map('Treeview', background=[('selected', COLOR_DARK_RED)])
        style.configure("TFrame", background=COLOR_BG)
        style.configure("TLabel", background=COLOR_BG, foreground=COLOR_FG)
        style.configure("Title.TLabel", font=("Impact", 24), foreground=COLOR_ACCENT)
        style.configure("Status.TLabel", font=("Consolas", 9), foreground="#666666")
        style.configure("TButton", background="#2a2a2a", foreground="#ffffff", font=("Segoe UI", 9, "bold"), borderwidth=1, focuscolor="none")
        style.map('TButton', background=[('active', COLOR_DARK_RED)])
        style.configure("TCombobox", fieldbackground=COLOR_SURFACE, background="#2a2a2a", foreground=COLOR_FG, arrowcolor=COLOR_FG)

    def _setup_ui(self):
        header = ttk.Frame(self.root, padding="20 20 20 10")
        header.pack(fill=tk.X)
        ttk.Label(header, text="M E T A M O R P H O S I S  IV", style="Title.TLabel").pack(pady=(0, 10))
        
        # Painel de Controle
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

        # Lista
        list_frame = ttk.Frame(self.root, padding="20 10 20 10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        columns = ("file", "ext", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("file", text="Arquivo Original")
        self.tree.heading("ext", text="Tipo")
        self.tree.heading("status", text="Estado")
        self.tree.column("file", width=450)
        self.tree.column("ext", width=80, anchor="center")
        self.tree.column("status", width=200, anchor="w")
        
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Footer
        footer = ttk.Frame(self.root, padding="20")
        footer.pack(fill=tk.X)
        self.btn_run = ttk.Button(footer, text="EXECUTAR", command=self.start_thread)
        self.btn_run.pack(fill=tk.X, ipady=12)
        self.lbl_status = ttk.Label(footer, text="Aguardando mídia...", style="Status.TLabel", anchor="center")
        self.lbl_status.pack(pady=(10, 0))

    def add_files(self):
        # Filtros expandidos
        ftypes = [
            ("Mídia Suportada", "*.png *.jpg *.jpeg *.webp *.mp4 *.gif *.mp3 *.wav *.mkv"),
            ("Imagens", "*.png *.jpg *.jpeg"),
            ("Vídeo/GIF", "*.mp4 *.gif *.avi"),
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

    def clear_list(self):
        self.tree.delete(*self.tree.get_children())
        self.files_map.clear()
        self.lbl_status.config(text="Altar limpo.")

    def start_thread(self):
        # Threading para não travar a GUI enquanto processa vídeo pesado
        t = threading.Thread(target=self.run_process)
        t.start()

    def run_process(self):
        if not self.files_map:
            messagebox.showwarning("Vazio", "Adicione arquivos primeiro.")
            return

        target = self.target_var.get()
        self.btn_run.config(state="disabled")
        self.lbl_status.config(text=f"Processando para {target}...")
        
        done = 0
        total = len(self.files_map)

        for iid in list(self.files_map.keys()):
            fpath = self.files_map[iid]
            
            self.root.after(0, lambda id=iid: self.tree.set(id, "status", "Processando..."))
            
            success, msg = self.engine.process(fpath, target)
            
            if success:
                self.root.after(0, lambda id=iid: self.tree.set(id, "status", "✔ CONCLUÍDO"))
                done += 1
            else:
                self.root.after(0, lambda id=iid, m=msg: self.tree.set(id, "status", f"✖ PULEI: {m}"))

        self.btn_run.config(state="normal")
        self.lbl_status.config(text=f"Finalizado: {done}/{total}.")
        messagebox.showinfo("Fim", f"Processo concluído.\n{done} arquivos gerados.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MetamorphosisGUI(root)
    root.mainloop()