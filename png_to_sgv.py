import tkinter as tk
from tkinter import filedialog
from PIL import Image
import numpy as np
import svgwrite

def png_to_svg_alternative(input_png_path, output_svg_path):
    # Abrir la imagen PNG
    image = Image.open(input_png_path).convert("L")  # Convertir a escala de grises
    
    # Reducir la imagen para simplificar los trazos (opcional)
    image = image.resize((100, 100))
    
    # Convertir a blanco y negro
    threshold = 128
    bw_image = image.point(lambda x: 255 if x > threshold else 0, mode='1')
    
    # Crear archivo SVG
    dwg = svgwrite.Drawing(output_svg_path, profile='tiny', size=(image.width, image.height))
    
    # Procesar píxeles negros y crear rectángulos
    pixels = np.array(bw_image)
    for y, row in enumerate(pixels):
        for x, pixel in enumerate(row):
            if pixel == 0:  # Si es negro
                dwg.add(dwg.rect(insert=(x, y), size=(1, 1), fill='black'))
    
    # Guardar el SVG
    dwg.save()

# Configurar la interfaz gráfica para seleccionar los archivos
def main():
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal

    # Seleccionar archivo PNG de entrada
    input_png_path = filedialog.askopenfilename(
        title="Seleccionar archivo PNG",
        filetypes=[("PNG Files", "*.png")]
    )
    if not input_png_path:
        print("No se seleccionó ningún archivo PNG.")
        return

    # Seleccionar ubicación y nombre del archivo SVG de salida
    output_svg_path = filedialog.asksaveasfilename(
        title="Guardar archivo SVG",
        defaultextension=".svg",
        filetypes=[("SVG Files", "*.svg")]
    )
    if not output_svg_path:
        print("No se seleccionó un destino para el archivo SVG.")
        return

    # Convertir PNG a SVG
    png_to_svg_alternative(input_png_path, output_svg_path)
    print(f"Archivo SVG guardado en: {output_svg_path}")

if __name__ == "__main__":
    main()
