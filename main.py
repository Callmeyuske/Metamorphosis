import sys
import tkinter as tk
from interface import MetamorphosisGUI

def main():
    try:
        root = tk.Tk()
        # Tenta definir um ícone na janela se houver (opcional)
        # root.iconbitmap("assets/icon.ico") 
        app = MetamorphosisGUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        print(f"Erro fatal no núcleo: {e}")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()