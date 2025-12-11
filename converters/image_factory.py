import os
from PIL import Image

class ImageFactory:
    def __init__(self):
        self.supported_formats = ('.png', '.jpg', '.jpeg')

    def to_ico(self, input_path):
        try:
            filename = os.path.basename(input_path)
            name, ext = os.path.splitext(filename)
            
            # Define saída (mesma pasta, extensão .ico)
            output_path = input_path.replace(ext, '.ico')
            
            print(f"   [Processando] {filename}...")
            
            img = Image.open(input_path)
            img.save(
                output_path, 
                format='ICO', 
                sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
            )
            
            print(f"   [Sucesso] Gerado: {output_path}")
            return True
            
        except Exception as e:
            print(f"   [Falha] Erro ao converter {input_path}: {e}")
            return False