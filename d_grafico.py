import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib import colormaps
import plotly.graph_objects as go
import tempfile
import webbrowser
import os
import atexit
import shutil
from datetime import datetime

# Credits: Adrián Ortiz and Álvaro Calero.

# --- CONFIGURACIÓN GLOBAL ---

# Creamos un directorio temporal para guardar las gráficas de Plotly
# y aseguramos que se limpie al cerrar el programa.
temp_dir = tempfile.mkdtemp()
print(f">>> [INFO] Directorio temporal para gráficas Plotly creado en: {temp_dir}")


def cleanup_temp_dir():
   try:
       shutil.rmtree(temp_dir)
       print(f">>> [INFO] Directorio temporal para gráficas Plotly limpiado de: {temp_dir}")
   except Exception as e:
       print(f">>> [ERROR] No se pudo limpiar el directorio temporal {temp_dir}: {e}")
atexit.register(cleanup_temp_dir)


# --- FUNCIÓN PRINCIPAL DE ENTRADA ---
def visualize_3d(notebook, cycles):
   # Esta función principal crea ambas pestañas de visualización 3D.
   visualize_3d_matplotlib(notebook, cycles)
   visualize_3d_plotly(notebook, cycles)


# --- 1. VISUALIZACIÓN NATIVA CON MATPLOTLIB (RESTAURADA Y MEJORADA) ---
def visualize_3d_matplotlib(notebook, cycles):
   print(">>> [DEBUG] Entrando a la función visualize_3d_matplotlib restaurada...")
   try:
       # 1. Crear la pestaña
       frame_3d_mat = ttk.Frame(notebook)
       notebook.add(frame_3d_mat, text="3D View (Matplotlib)")
      
       # 2. Panel superior para seleccionar la paleta
       control_frame = ttk.Frame(frame_3d_mat)
       control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
       ttk.Label(control_frame, text="Paleta de Colores:").pack(side=tk.LEFT, padx=5)
       paletas_disponibles = ['plasma', 'viridis', 'inferno', 'magma', 'cividis', 'turbo', 'ocean', 'coolwarm']
       paleta_seleccionada = tk.StringVar(value='plasma')
       combo_paleta = ttk.Combobox(control_frame, textvariable=paleta_seleccionada,
                                   values=paletas_disponibles, state="readonly", width=15)
       combo_paleta.pack(side=tk.LEFT, padx=5)


       # 3. Crear la figura y el lienzo, ortho para rotación geométrica
       fig = plt.figure(figsize=(10, 7))
       ax = fig.add_subplot(111, projection='3d', proj_type='ortho')
      
       # Guardamos el ángulo inicial por defecto
       ax.view_init(elev=20, azim=-45)
      
       def actualizar_grafica(*args):
           # Guardamos el ángulo de visión actual
           elev_actual = ax.elev
           azim_actual = ax.azim
           ax.clear()
          
           # Ajustes estéticos
           ax.set_box_aspect(aspect=(2, 4, 1))
           # Paneles transparentes
           ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
           ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
           ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
           ax.grid(color='gray', linestyle=':', linewidth=0.3, alpha=0.3)


           num_ciclos = len(cycles)
           colormap = colormaps.get_cmap(paleta_seleccionada.get())
          
           # REVERTIDO: Mostramos el 100% de los datos para precisión total.
           # No hay downsampling de puntos, por lo que el rendimiento será algo menor
           # pero no habrá artefactos visuales.
           lineas_3d = []
           colores = []
           min_x, max_x = float('inf'), float('-inf')
           min_z, max_z = float('inf'), float('-inf')
          
           for i, cycle_list in enumerate(cycles):
               cycle = cycle_list[0]
               x_full = cycle['Mass']
               z_full = cycle['Ion Current']
               y_full = np.full(len(x_full), i + 1)
              
               z_safe = np.maximum(z_full, 1e-12)
               z_log = np.log10(z_safe)
              
               # Actualizamos los mínimos y máximos para los límites
               if len(x_full) > 0:
                   min_x, max_x = min(min_x, np.min(x_full)), max(max_x, np.max(x_full))
                   min_z, max_z = min(min_z, np.min(z_log)), max(max_z, np.max(z_log))
              
               # Empaquetamos (X, Y, Z) en una lista de vértices
               verts = list(zip(x_full, y_full, z_log))
               lineas_3d.append(verts)
               colores.append(colormap(i / num_ciclos))
          
           # Colección de líneas optimizada.
           lc = Line3DCollection(lineas_3d, colors=colores, alpha=0.7, linewidth=0.8)
           ax.add_collection3d(lc)
          
           # Límites. Necesario un chequeo por si no hay datos.
           if len(lineas_3d) > 0:
               ax.set_xlim(min_x, max_x)
               ax.set_ylim(1, num_ciclos)
               ax.set_zlim(min_z, max_z)
         
           ax.set_xlabel('Mass/Charge (m/z)', fontweight='bold', labelpad=10)
           ax.set_ylabel('Cycle Number', fontweight='bold', labelpad=10)
           ax.set_zlabel('Log10 Ion Current', fontweight='bold', labelpad=10)
           ax.set_title('Evolución 3D (Matplotlib)', fontweight='bold', pad=15)
          
           # Restauramos el ángulo de visión
           ax.view_init(elev=elev_actual, azim=azim_actual)
           canvas.draw()


       # 4. Crear el lienzo
       canvas = FigureCanvasTkAgg(fig, master=frame_3d_mat)
      
       # 5. Conectar el menú desplegable a la función de redibujar
       combo_paleta.bind('<<ComboboxSelected>>', actualizar_grafica)
      
       # 6. RESTAURADO: Usamos la barra de herramientas estándar completa.
       # Esto te devuelve todos los botones, incluyendo el Zoom y el Paneo.
       # Recuerda que, aunque estén ahí, en 3D no son tan suaves como en 2D.
       toolbar = NavigationToolbar2Tk(canvas, frame_3d_mat)
       toolbar.update()
       toolbar.pack(side=tk.BOTTOM, fill=tk.X)
       canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
      
       # Dibujamos por primera vez
       actualizar_grafica()
      
       print(">>> [DEBUG] Pestaña visualize_3d_matplotlib restaurada con éxito!")
      
   except Exception as e:
       print(f">>> [ERROR FATAL en visualize_3d_matplotlib]: {e}")


# --- 2. VISUALIZACIÓN INTERACTIVA PERFECTA CON PLOTLY (NUEVA PESTAÑA) ---
def visualize_3d_plotly(notebook, cycles):
   # Esta función crea la pestaña que permite abrir la gráfica en Plotly.
   try:
       # 1. Crear la pestaña de elección.
       frame_3d_plo = ttk.Frame(notebook)
       notebook.add(frame_3d_plo, text="3D View (Plotly - Browser)")


       # 2. Añadir una etiqueta informativa.
       info_text = (
           "Esta pestaña le permite abrir una visualización 3D interactiva perfecta de sus datos.\n\n"
           "Matplotlib 3D es limitado en interacciones complejas. Plotly en el navegador "
           "le ofrece una experiencia de zoom (con la rueda del ratón) y paneo mucho más fluida "
           "y precisa.\n\n"
           "Al hacer clic en el botón de abajo, se generará y abrirá una nueva pestaña "
           "en su navegador predeterminado con la gráfica Plotly."
       )
       label_info = ttk.Label(frame_3d_plo, text=info_text, justify=tk.LEFT, wraplength=500)
       label_info.pack(pady=20, padx=20)


       # 3. Definir la función para generar y abrir la gráfica.
       def write_and_open_html():
           print(">>> [DEBUG] Generando y abriendo gráfica Plotly...")
           # ... lógica para generar datos con downsampling para el navegador ...
           # Plotly es rápido, pero para una experiencia de navegador súper fluida,
           # es recomendable downsamplar ligeramente las masas.
           puntos_maximos = 800
          
           fig = go.Figure()
          
           num_ciclos = len(cycles)
           # Usamos 'plasma' por consistencia con la gráfica anterior.
           colormap = colormaps.get_cmap('plasma')
          
           # Usaremos Scatter3d para las líneas de la waterfall.
           # El color es por línea (ciclo).
          
           for i, cycle_list in enumerate(cycles):
               cycle = cycle_list[0]
               x_full = cycle['Mass']
               z_full = cycle['Ion Current']
              
               # Downsampling de puntos para la visualización en navegador.
               salto_puntos = max(1, len(x_full) // puntos_maximos)
               x_red = x_full[::salto_puntos]
               z_red = z_full[::salto_puntos]
               y_red = np.full(len(x_red), i + 1)
              
               z_safe = np.maximum(z_red, 1e-12)
               z_log = np.log10(z_safe)
              
               # Obtenemos el color. Matplotlib color to plotly es hexadecimal.
               color_rgba = colormap(i / num_ciclos)
               # Convertimos a RGBA int (0-255).
               color_int = [int(255 * c) for c in color_rgba]
               # Formateamos a cadena hexadecimal.
               color_hex = '#{:02x}{:02x}{:02x}'.format(color_int[0], color_int[1], color_int[2])


               fig.add_trace(go.Scatter3d(
                   x=x_red, y=y_red, z=z_log,
                   mode='lines',
                   line=dict(color=color_hex, width=2),
                   name=f"Ciclo {i+1}",
                   showlegend=False, # Ocultamos leyenda para no saturar.
               ))


           # ... configuración de layout ...
           fig.update_layout(
               title='Evolución 3D (Plotly)',
               scene=dict(
                   xaxis_title='Mass/Charge (m/z)',
                   yaxis_title='Cycle Number',
                   zaxis_title='Log10 Ion Current'
               ),
               margin=dict(l=0, r=0, b=0, t=40)
           )


           # 4. Guardar en un archivo HTML temporal.
           # Usamos temp_dir y un nombre de archivo simple basado en timestamp.
           timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
           filename = os.path.join(temp_dir, f"plotly_plot_{timestamp}.html")
          
           fig.write_html(filename)
           print(f">>> [DEBUG] Gráfica Plotly guardada en: {filename}")
          
           # 5. Abrir en el navegador.
           webbrowser.open('file://' + filename)


       # 4. Añadir el botón.
       btn_open = ttk.Button(frame_3d_plo, text="Abrir Gráfica en Navegador (Plotly)", command=write_and_open_html)
       btn_open.pack(pady=20)
      
       print(">>> [DEBUG] Pestaña visualize_3d_plotly creada con éxito!")
      
   except Exception as e:
       print(f">>> [ERROR FATAL en visualize_3d_plotly]: {e}")