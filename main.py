import os
import sys
from converters.image_factory import ImageFactory


PASTA_INPUT = "input"

def banner():
    print("""
    === METAMORPHOSIS v1.0 (MVP) ===
    """)

def scan_folder(extension_list):
  
    if not os.path.exists(PASTA_INPUT):
        os.makedirs(PASTA_INPUT)
        print(f"[Aviso] Pasta '{PASTA_INPUT}' criada. Coloque seus arquivos.")
        return []

    files = [
        os.path.join(PASTA_INPUT, f) 
        for f in os.listdir(PASTA_INPUT) 
        if f.lower().endswith(extension_list)
    ]
    return files

def main():
    banner()
    print("1. Converter PNG/JPG para .ICO (Windows Icon)")
    print("0. Sair")
    
    choice = input("\nEscolha sua transmutação: ")

    if choice == '1':
        factory = ImageFactory()
        arquivos = scan_folder(('.png', '.jpg', '.jpeg'))
        
        if not arquivos:
            print(f"\n[Vazio] Nenhum arquivo de imagem encontrado em '{PASTA_INPUT}'.")
        else:
            print(f"\n--- Iniciando Transmutação em Lote ({len(arquivos)} arquivos) ---")
            for arq in arquivos:
                factory.to_ico(arq)
            print("\n[Concluído] Ciclo finalizado.")
            
    elif choice == '0':
        sys.exit()
    else:
        print("Opção inválida.")

if __name__ == "__main__":
    main()