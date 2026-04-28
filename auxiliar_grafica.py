import time

import numpy as np

# Credits: Adrián Ortiz and Álvaro Calero.


def anadir_tooltip_interactivo(ax, entity_label="Molecule"):
    """
    Anade tooltips interactivos a las lineas actuales de un eje.

    La funcion elimina cualquier manejador previo asociado al eje para evitar
    referencias obsoletas cuando la grafica se redibuja. Se usa un unico
    annotation y callbacks de movimiento ligeros para evitar bloqueos en
    graficas con muchas lineas.
    """

    canvas = ax.figure.canvas

    for connection_id in getattr(ax, "_anatem_tooltip_connection_ids", []):
        try:
            canvas.mpl_disconnect(connection_id)
        except Exception:
            pass
    ax._anatem_tooltip_connection_ids = []

    anotaciones_previas = getattr(ax, "_anatem_tooltip_annotations", [])
    for anotacion in list(anotaciones_previas):
        try:
            anotacion.remove()
        except Exception:
            pass
    ax._anatem_tooltip_annotations = []

    if not ax.lines:
        ax._anatem_tooltip_cursor = None
        return None

    annotation = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(12, 12),
        textcoords="offset points",
        bbox={"boxstyle": "round", "fc": "white", "alpha": 0.9},
        arrowprops={"arrowstyle": "->", "color": "black"},
    )
    annotation.set_visible(False)
    ax._anatem_tooltip_annotations = [annotation]

    tooltip_state = {
        "last_time": 0.0,
        "last_xy": None,
        "last_point": None,
        "pixel_threshold": 14,
        "min_interval": 0.03,
    }

    def ocultar_anotacion():
        if annotation.get_visible():
            annotation.set_visible(False)
            tooltip_state["last_point"] = None
            canvas.draw_idle()

    def buscar_punto_cercano(event):
        if event.xdata is None or event.ydata is None:
            return None

        mejor = None
        mejor_distancia = None

        for linea in ax.lines:
            if not linea.get_visible():
                continue

            x_data = np.asarray(linea.get_xdata(orig=False))
            y_data = np.asarray(linea.get_ydata(orig=False))
            if x_data.size == 0 or y_data.size == 0:
                continue

            indice = np.searchsorted(x_data, event.xdata)
            candidatos = []
            if 0 <= indice < x_data.size:
                candidatos.append(indice)
            if indice - 1 >= 0:
                candidatos.append(indice - 1)

            for candidato in candidatos:
                x_valor = x_data[candidato]
                y_valor = y_data[candidato]
                if not np.isfinite(y_valor):
                    continue

                x_pixel, y_pixel = ax.transData.transform((x_valor, y_valor))
                distancia = ((x_pixel - event.x) ** 2 + (y_pixel - event.y) ** 2) ** 0.5
                if distancia > tooltip_state["pixel_threshold"]:
                    continue

                if mejor_distancia is None or distancia < mejor_distancia:
                    mejor = (linea, x_valor, y_valor)
                    mejor_distancia = distancia

        return mejor

    def al_mover_raton(event):
        if event.inaxes != ax:
            ocultar_anotacion()
            return

        ahora = time.monotonic()
        posicion_actual = (event.x, event.y)
        if ahora - tooltip_state["last_time"] < tooltip_state["min_interval"]:
            return

        tooltip_state["last_time"] = ahora
        tooltip_state["last_xy"] = posicion_actual

        punto = buscar_punto_cercano(event)
        if punto is None:
            ocultar_anotacion()
            return

        linea, x_valor, y_valor = punto
        punto_actual = (id(linea), x_valor, y_valor)
        if annotation.get_visible() and tooltip_state["last_point"] == punto_actual:
            return

        tooltip_state["last_point"] = punto_actual
        annotation.xy = (x_valor, y_valor)
        annotation.set_text(f"{entity_label}: {linea.get_label()}\nCycle: {int(round(x_valor))}\nIntensity: {y_valor:.4e}")
        annotation.get_bbox_patch().set_edgecolor(linea.get_color())
        if annotation.arrow_patch is not None:
            annotation.arrow_patch.set_color(linea.get_color())
        annotation.set_visible(True)
        canvas.draw_idle()

    def al_salir_axes(event):
        if event.inaxes != ax:
            ocultar_anotacion()

    connection_ids = [
        canvas.mpl_connect("motion_notify_event", al_mover_raton),
        canvas.mpl_connect("axes_leave_event", al_salir_axes),
    ]
    ax._anatem_tooltip_connection_ids = connection_ids
    ax._anatem_tooltip_cursor = annotation
    return annotation
