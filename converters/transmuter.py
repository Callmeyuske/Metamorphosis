import os
from PIL import Image
from moviepy.editor import VideoFileClip, AudioFileClip
from rembg import remove
import numpy as np

class Transmuter:
    def __init__(self):
        self.valid_sources = {
            '.png', '.jpg', '.jpeg', '.webp', '.bmp', '.ico', 
            '.mp4', '.gif', '.mov', '.avi', '.mkv', '.mp3'
        }
        
        self.targets = {
            'Imagem': ['.png', '.jpg', '.webp', '.ico', '.pdf'],
            'Especial': ['PNG (Sem Fundo)'],
            'Vídeo/GIF': ['.mp4', '.gif'],
            'Áudio': ['.mp3', '.wav']
        }

    def get_all_targets(self):
        lista = []
        for k, v in self.targets.items():
            lista.extend(v)
        return sorted(list(set(lista)))

    def is_valid_source(self, filepath):
        _, ext = os.path.splitext(filepath)
        return ext.lower() in self.valid_sources

    def process(self, input_path, target_mode):
        try:
            filename = os.path.basename(input_path)
            name, src_ext = os.path.splitext(filename)
            src_ext = src_ext.lower()
            
            # Define extensão real de saída
            if target_mode == 'PNG (Sem Fundo)':
                out_ext = '.png'
            else:
                out_ext = target_mode if target_mode.startswith('.') else f'.{target_mode}'

            # Caminho de saída
            output_path = os.path.join(os.path.dirname(input_path), f"{name}_meta{out_ext}")


            if target_mode == 'PNG (Sem Fundo)':
                print(f"   [IA] Removendo fundo de {filename}...")
                with open(input_path, 'rb') as i:
                    with open(output_path, 'wb') as o:
                        input_data = i.read()
                        output_data = remove(input_data)
                        o.write(output_data)
                return True, output_path

            if src_ext in ['.mp4', '.gif', '.mov', '.avi', '.mkv']:
                
                # Vídeo -> Áudio
                if out_ext in ['.mp3', '.wav']:
                    clip = AudioFileClip(input_path)
                    clip.write_audiofile(output_path, logger=None)
                    clip.close()
                    return True, output_path

                # Vídeo/GIF -> Vídeo/GIF
                if out_ext in ['.mp4', '.gif']:
                    clip = VideoFileClip(input_path)
                    
                    if out_ext == '.gif':
                        # Resize 
                        clip = clip.resize(width=480) 
                        clip.write_gif(output_path, fps=15, logger=None)
                    else:
                        clip.write_videofile(output_path, codec='libx264', audio_codec='aac', logger=None)
                    
                    clip.close()
                    return True, output_path

            # --- LÓGICA DE IMAGEM PADRÃO (Pillow) ---
            if src_ext in ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.ico']:
                img = Image.open(input_path)
                
                # Tratamento de Alpha
                if out_ext in ['.jpg', '.jpeg', '.bmp', '.pdf'] and img.mode in ('RGBA', 'LA'):
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[-1])
                    img = bg
                elif out_ext != '.ico' and img.mode != 'RGB' and out_ext != '.png':
                    img = img.convert('RGB')

                if out_ext == '.ico':
                    img.save(output_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
                elif out_ext == '.pdf':
                     img.save(output_path, "PDF", resolution=100.0)
                else:
                    img.save(output_path, quality=95)
                
                return True, output_path

            return False, "Combinação não suportada."

        except Exception as e:
            return False, str(e)