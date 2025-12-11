import os
from PIL import Image

class ImageFactory:
    def __init__(self):
        # Formatos que aceitamos como oferenda
        self.valid_sources = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.ico', '.tiff'}
        
        # Formatos que podemos gerar
        self.valid_targets = ['.png', '.jpg', '.ico', '.webp', '.bmp', '.pdf']

    def is_valid_source(self, filepath):
        _, ext = os.path.splitext(filepath)
        return ext.lower() in self.valid_sources

    def get_supported_targets(self):
        return self.valid_targets

    def convert(self, input_path, target_ext):
        try:
            filename = os.path.basename(input_path)
            name, source_ext = os.path.splitext(filename)
            source_ext = source_ext.lower()
            
            if not target_ext.startswith('.'):
                target_ext = f'.{target_ext}'

            # Se a alma já é do formato desejado, ignoramos
            if source_ext == target_ext:
                return False, "Ignorado (Mesmo formato)"

            output_path = os.path.join(os.path.dirname(input_path), f"{name}{target_ext}")
            
            img = Image.open(input_path)

            # TRATAMENTO DE TRANSPARÊNCIA (ALPHA CHANNEL)
            # JPG e BMP não suportam transparência. Precisamos pintar o fundo de branco.
            if target_ext in ['.jpg', '.jpeg', '.bmp'] and img.mode in ('RGBA', 'LA'):
                fill_color = (255, 255, 255)
                background = Image.new(img.mode[:-1], img.size, fill_color)
                background.paste(img, img.split()[-1])
                img = background
            
            # Conversão de Modo para compatibilidade
            elif target_ext != '.ico' and img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')

            # SALVAMENTO ESPECÍFICO
            if target_ext == '.ico':
                # Ícones exigem tamanhos específicos
                img.save(output_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
            elif target_ext == '.pdf':
                 # PDF exige RGB
                 if img.mode == 'RGBA':
                     img = img.convert('RGB')
                 img.save(output_path, "PDF", resolution=100.0)
            else:
                # Padrão (PNG, WEBP, JPG)
                quality_val = 95 if target_ext in ['.jpg', '.jpeg', '.webp'] else None
                if quality_val:
                    img.save(output_path, quality=quality_val)
                else:
                    img.save(output_path)
            
            return True, output_path

        except Exception as e:
            return False, str(e)