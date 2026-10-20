from pathlib import Path
import csv

import cv2
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt


BASE = Path(__file__).resolve().parent
ENTRADA = BASE / "imagenes"
SALIDA = BASE / "resultados"
COLOR = "rojo"
UMBRAL = 127

RANGOS = {
    "rojo": [((0, 80, 50), (10, 255, 255)), ((170, 80, 50), (179, 255, 255))],
    "amarillo": [((20, 80, 50), (35, 255, 255))],
    "verde": [((36, 60, 40), (85, 255, 255))],
    "azul": [((90, 80, 50), (130, 255, 255))],
}


def guardar_imagen(ruta, imagen):
    correcto, datos = cv2.imencode(".png", imagen)
    if not correcto:
        raise ValueError(f"No se pudo guardar {ruta.name}")
    datos.tofile(str(ruta))


def procesar(ruta):
    imagen = cv2.imdecode(np.fromfile(str(ruta), dtype=np.uint8), cv2.IMREAD_COLOR)
    if imagen is None:
        print(f"No se pudo leer: {ruta.name}")
        return None

    carpeta = SALIDA / ruta.name
    carpeta.mkdir(parents=True, exist_ok=True)
    alto, ancho, canales = imagen.shape
    bits_canal = imagen.dtype.itemsize * 8
    rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    _, binaria = cv2.threshold(gris, UMBRAL, 255, cv2.THRESH_BINARY)
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    mascara = np.zeros((alto, ancho), dtype=np.uint8)
    for inferior, superior in RANGOS[COLOR]:
        parcial = cv2.inRange(hsv, np.array(inferior, dtype=np.uint8),
                              np.array(superior, dtype=np.uint8))
        mascara = cv2.bitwise_or(mascara, parcial)
    segmentada = cv2.bitwise_and(imagen, imagen, mask=mascara)
    porcentaje = cv2.countNonZero(mascara) / (alto * ancho) * 100

    guardar_imagen(carpeta / "gris.png", gris)
    guardar_imagen(carpeta / "blanco_negro.png", binaria)
    guardar_imagen(carpeta / "mascara.png", mascara)
    guardar_imagen(carpeta / "segmentada.png", segmentada)
    np.save(carpeta / "hsv.npy", hsv)
    np.save(carpeta / "rgb.npy", rgb)

    figura, ejes = plt.subplots(2, 3, figsize=(12, 8))
    vistas = [rgb, gris, binaria, h, s, v]
    titulos = ["RGB", "Escala de grises", "Blanco y negro", "H: tono", "S: saturación", "V: brillo"]
    for eje, vista, titulo in zip(ejes.flat, vistas, titulos):
        if vista.ndim == 3:
            eje.imshow(vista)
        else:
            eje.imshow(vista, cmap="gray", vmin=0, vmax=179 if titulo == "H: tono" else 255)
        eje.set_title(titulo)
        eje.axis("off")
    figura.suptitle(ruta.name)
    figura.tight_layout()
    figura.savefig(carpeta / "representaciones.png", dpi=150)
    plt.close(figura)

    figura, ejes = plt.subplots(1, 3, figsize=(14, 4))
    hist_gris = cv2.calcHist([gris], [0], None, [256], [0, 256])
    ejes[0].plot(hist_gris, color="black")
    ejes[0].set_title("Histograma en gris")
    for canal, color, nombre in zip(range(3), ["red", "green", "blue"], ["R", "G", "B"]):
        hist = cv2.calcHist([rgb], [canal], None, [256], [0, 256])
        ejes[1].plot(hist, color=color, label=nombre)
    ejes[1].set_title("Histogramas RGB")
    ejes[1].legend()
    hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
    ejes[2].plot(hist_h, color="purple")
    ejes[2].set_title("Histograma del tono H")
    for indice, eje in enumerate(ejes):
        eje.set_xlabel("Tono H" if indice == 2 else "Intensidad")
        eje.set_ylabel("Número de píxeles")
        eje.set_xlim(0, 179 if indice == 2 else 255)
    figura.tight_layout()
    figura.savefig(carpeta / "histogramas.png", dpi=150)
    plt.close(figura)

    figura, ejes = plt.subplots(1, 3, figsize=(12, 4))
    for eje, vista, titulo in zip(ejes, [rgb, mascara, cv2.cvtColor(segmentada, cv2.COLOR_BGR2RGB)],
                                 ["Original", f"Máscara: {COLOR}", f"Segmentación: {porcentaje:.2f}%"]):
        eje.imshow(vista, cmap="gray", vmin=0, vmax=255)
        eje.set_title(titulo)
        eje.axis("off")
    figura.tight_layout()
    figura.savefig(carpeta / "segmentacion.png", dpi=150)
    plt.close(figura)

    print(f"{ruta.name}: {ancho} x {alto}, {bits_canal * canales} bits/píxel, {porcentaje:.2f}% de color {COLOR}")
    return {
        "archivo": ruta.name,
        "ancho_px": ancho,
        "alto_px": alto,
        "megapixeles": round(ancho * alto / 1_000_000, 3),
        "canales_cargados": canales,
        "tipo_cargado": str(imagen.dtype),
        "bits_por_canal": bits_canal,
        "bits_por_pixel_cargado": bits_canal * canales,
        "niveles_por_canal": 2 ** bits_canal,
        "memoria_rgb_bytes": rgb.nbytes,
        "archivo_bytes": ruta.stat().st_size,
        "umbral_binario": UMBRAL,
        "color_segmentado": COLOR,
        "porcentaje_color": round(porcentaje, 2),
    }


def main():
    ENTRADA.mkdir(exist_ok=True)
    extensiones = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
    archivos = sorted(ruta for ruta in ENTRADA.iterdir() if ruta.suffix.lower() in extensiones)
    if not archivos:
        print("Coloca tus fotografías en la carpeta imagenes y ejecuta de nuevo.")
        return
    if COLOR not in RANGOS:
        raise ValueError(f"Elige un color entre: {', '.join(RANGOS)}")
    SALIDA.mkdir(exist_ok=True)
    filas = []
    for ruta in archivos:
        fila = procesar(ruta)
        if fila is not None:
            filas.append(fila)
    if filas:
        with (SALIDA / "resumen.csv").open("w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=filas[0].keys())
            escritor.writeheader()
            escritor.writerows(filas)
        print(f"Resultados guardados en: {SALIDA}")


if __name__ == "__main__":
    main()
