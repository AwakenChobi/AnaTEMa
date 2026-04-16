import platform

# Credits: Adrián Ortiz and Álvaro Calero.

def maximizar(ventana):

    ventana.update_idletasks()  # Updates the window to get the correct dimensions

    sistema = platform.system()
    if sistema == "Windows":
        try:
            ventana.state('zoomed')  # Maximize windows on Windows
        except:
            ancho = ventana.winfo_screenwidth()
            alto = ventana.winfo_screenheight()
            ventana.geometry(f"{ancho}x{alto}+0+0")  # Maximizes window in case of error
    elif sistema == "Darwin":  # macOS
        try:
            ventana.attributes('-fullscreen', True)  # macOS
        except:
            ancho = ventana.winfo_screenwidth()
            alto = ventana.winfo_screenheight()
            ventana.geometry(f"{ancho}x{alto}+0+0")
    else:  #  (Linux, etc.)
        try:
            ventana.attributes('-zoomed', True)  # Maximize windows on Linux, etc.
        except:
            ancho = ventana.winfo_screenwidth()
            alto = ventana.winfo_screenheight()
            ventana.geometry(f"{ancho}x{alto}+0+0")