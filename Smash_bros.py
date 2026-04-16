import os
import json
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

# Credits: Adrián Ortiz and Álvaro Calero.


# Archivo donde se guardan los perfiles
ARCHIVO_PERFILES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perfiles_smash.json")

def cargar_todos_los_perfiles():
   """Lee el archivo interno y devuelve el diccionario de perfiles."""
   if os.path.exists(ARCHIVO_PERFILES):
       try:
            with open(ARCHIVO_PERFILES, 'r', encoding='utf-8') as f:
               return json.load(f)
       except Exception:
           pass
   return {}


def inyectar_panel_perfiles(parent, frame_destino, variables):
   """
   Panel organizado en dos filas, con textos en inglés pero nombres
   de función en español para mantener compatibilidad con main2_0.py
   """
   perfiles_frame = ttk.LabelFrame(frame_destino, text="Exclusion Profiles")
   perfiles_frame.pack(side="top", fill="x", padx=5, pady=5)


   # 1. FILA SUPERIOR: Menú desplegable
   combo_var = tk.StringVar()
   combo = ttk.Combobox(perfiles_frame, textvariable=combo_var, state="readonly")
   combo.pack(side="top", fill="x", padx=10, pady=5)


   def actualizar_combo():
       perfiles = cargar_todos_los_perfiles()
       combo['values'] = list(perfiles.keys())
       if perfiles:
           combo.current(0)
       else:
           combo.set("No profiles saved")


   actualizar_combo()


   # --- FUNCIONES DE LOS BOTONES ---
   def cargar_perfil():
       nombre = combo_var.get()
       if not nombre or nombre == "No profiles saved": return
      
       perfiles = cargar_todos_los_perfiles()
       descartados = perfiles.get(nombre, [])
      
       for comp, var in variables:
           if comp in descartados:
               var.set(False)
           else:
               var.set(True)
              
   def guardar_perfil():
       nombre_actual = combo_var.get()
       if nombre_actual == "No profiles saved":
           nombre_actual = ""
          
       nombre = simpledialog.askstring(
           "Save Profile",
           "Profile name (leave unchanged to update):",
           initialvalue=nombre_actual,
           parent=parent
       )
      
       if not nombre: return
       nombre = nombre.strip()
       if not nombre: return
      
       descartados = [c for c, v in variables if not v.get()]
       perfiles = cargar_todos_los_perfiles()
       perfiles[nombre] = descartados
      
       try:
           with open(ARCHIVO_PERFILES, 'w', encoding='utf-8') as f:
               json.dump(perfiles, f, indent=4)
           actualizar_combo()
           combo_var.set(nombre)
       except Exception as e:
           messagebox.showerror("Error", f"Could not save profile: {e}", parent=parent)


   def borrar_perfil():
       nombre = combo_var.get()
       if not nombre or nombre == "No profiles saved": return
      
       if messagebox.askyesno("Delete", f"Are you sure you want to delete '{nombre}'?", parent=parent):
           perfiles = cargar_todos_los_perfiles()
           if nombre in perfiles:
               del perfiles[nombre]
               try:
                   with open(ARCHIVO_PERFILES, 'w', encoding='utf-8') as f:
                       json.dump(perfiles, f, indent=4)
                   actualizar_combo()
               except Exception:
                   pass


   # 2. FILA INFERIOR: Contenedor para los 3 botones
   botones_frame = ttk.Frame(perfiles_frame)
   botones_frame.pack(side="top", pady=5)


   # Botones en inglés
   btn_cargar = ttk.Button(botones_frame, text="Load", command=cargar_perfil)
   btn_cargar.pack(side="left", padx=5)


   btn_guardar = ttk.Button(botones_frame, text="Save Current", command=guardar_perfil)
   btn_guardar.pack(side="left", padx=5)
  
   btn_borrar = ttk.Button(botones_frame, text="Delete", command=borrar_perfil)
   btn_borrar.pack(side="left", padx=5)