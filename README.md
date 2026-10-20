# Práctica 1: Adquisición y representación de imágenes de productos

Objetivo: analizar fotografías propias de productos de supermercado o ferretería mediante su resolución, profundidad de color, representaciones, histogramas y segmentación por color en HSV.

## Adquisición

Captura al menos tres productos con colores identificables. Fotografía uno de ellos con luz intensa y con luz tenue, manteniendo el encuadre y la distancia. Evita reflejos fuertes y usa un fondo sencillo. Guarda las fotografías originales en `imagenes/`, en formato JPG o PNG. Registra el producto, el dispositivo y las condiciones de iluminación de cada captura.

## Ejecución

El archivo principal de trabajo es `practica1.ipynb`. Ábrelo en VS Code con las extensiones Python y Jupyter, selecciona el kernel de Python y ejecuta las celdas en orden. Cambia `NOMBRE_IMAGEN`, `COLOR` y `UMBRAL` en la celda de selección y vuelve a ejecutar desde esa celda para analizar otra fotografía. Los gráficos aparecen dentro del cuaderno y se guardan en `resultados/cuaderno/`.

Instala las dependencias con `python -m pip install -r requirements.txt`. El cuaderno comienza con `miloFront.jpeg` y segmentación verde.

Para procesar todas las fotografías mediante el script:

```powershell
python -m pip install -r requirements.txt
python practica1.py
```

El programa procesa todas las imágenes de la carpeta. Cambia `COLOR` al inicio de `practica1.py` por `rojo`, `amarillo`, `verde` o `azul`. Ajusta `RANGOS` según los colores de tus fotos. `UMBRAL = 127` controla la conversión a blanco y negro.

## Fundamento

La resolución se expresa como ancho × alto en píxeles. El programa trabaja con imágenes cargadas en tres canales de 8 bits: 24 bits por píxel y 256 niveles por canal. Esta es la representación utilizada al cargar la fotografía con OpenCV; no certifica la profundidad original del archivo. El tamaño comprimido del archivo y la memoria de la matriz se registran por separado.

OpenCV carga los canales en orden BGR. Para visualizarlos con Matplotlib se convierten a RGB. La escala de grises combina los canales mediante una ponderación aproximada de 0.299R + 0.587G + 0.114B. La imagen binaria asigna 255 a intensidades mayores que el umbral y 0 a las restantes. Aunque contiene dos valores y puede representarse con un bit por píxel, aquí se conserva en una matriz de 8 bits.

HSV representa tono, saturación y brillo. Para matrices de 8 bits, OpenCV utiliza H entre 0 y 179, y S y V entre 0 y 255. Los canales HSV se muestran por separado; la matriz HSV completa no debe interpretarse directamente como una imagen RGB.

Los histogramas muestran cuántos píxeles tienen cada intensidad o tono. Los picos cercanos a 0 en gris corresponden a zonas oscuras; los cercanos a 255, a zonas claras. Al comparar fotografías de distinta resolución, los conteos absolutos dependen también del número de píxeles.

La segmentación selecciona los píxeles dentro de los rangos HSV y aplica la máscara a la imagen original. El rojo requiere dos intervalos porque se encuentra en ambos extremos de H. El porcentaje calculado corresponde a la superficie de la imagen que cumple el rango; no equivale al porcentaje de productos detectados. También puede seleccionar fondos con colores similares. HSV facilita separar el tono del brillo, pero los umbrales siguen necesitando ajustes ante sombras, reflejos o cambios de iluminación.

## Entregables generados

Cada fotografía tiene su propia carpeta dentro de `resultados/`, con las representaciones, histogramas, máscara y segmentación. Las matrices RGB y HSV se guardan como archivos `.npy`. `resumen.csv` reúne las dimensiones, profundidad de la representación cargada, tamaños y porcentaje segmentado.

## Análisis pendiente de las fotografías

1. Identificar los productos y describir cómo se capturaron.
2. Comparar su resolución, memoria y tamaño de archivo usando `resumen.csv`.
3. Explicar qué información se conserva o pierde en gris y blanco y negro.
4. Relacionar los picos de los histogramas con las regiones visibles de cada producto.
5. Comparar la máscara del mismo producto bajo las dos condiciones de iluminación usando los mismos rangos HSV.
6. Describir aciertos y errores de la segmentación y concluir a partir de los resultados observados.

Los resultados y las conclusiones experimentales se completarán cuando estén disponibles las imágenes propias.

## Referencias

- [LearnOpenCV: Color spaces in OpenCV](https://learnopencv.com/color-spaces-in-opencv-cpp-python/)
- [PyImageSearch: OpenCV Color Spaces](https://pyimagesearch.com/2021/04/28/opencv-color-spaces-cv2-cvtcolor/)
- [PyImageSearch: OpenCV Image Histograms](https://pyimagesearch.com/2021/04/28/opencv-image-histograms-cv2-calchist/)
- [OpenCV: Changing Colorspaces](https://docs.opencv.org/4.x/df/d9d/tutorial_py_colorspaces.html)
- [OpenCV: Image Histograms](https://docs.opencv.org/4.x/d1/db7/tutorial_py_histogram_begins.html)
