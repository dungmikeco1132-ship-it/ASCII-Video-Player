# 🎬 Reproductor de Video ASCII v5 — Edición Ultimate (Fork Español)

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![NumPy](https://img.shields.io/badge/NumPy-1.20+-blue.svg)
![Estado](https://img.shields.io/badge/Versi%C3%B3n-Fork%20Espa%C3%B1ol-orange.svg)

Este es un reproductor de video basado en texto (CLI) que renderiza cada cuadro de video en arte ASCII de alta calidad directamente en tu terminal. Esta versión es un **fork mejorado y traducido al español** basado en el trabajo original de @stepanussaruran.

---

## ✨ Características de este Fork

- **🌍 Traducción Completa**: Interfaz, mensajes, menús interactivos y ayuda totalmente en español.
- **🖥️ Ajuste Automático Dinámico**: La imagen se adapta automáticamente al ancho **y alto** de tu terminal en tiempo real, manteniendo la relación de aspecto correcta.
- **🌈 Modo Color/B&W**: Soporte para color ANSI de 24 bits para una experiencia visual premium o modo blanco y negro para máximo rendimiento.
- **🕹️ Modo Interactivo Mejorado**: Preguntas guiadas al iniciar para configurar color, bucle, ajuste y saltos de cuadro.
- **⚡ Decodificación en Segundo Plano**: Uso de hilos (threading) para una reproducción fluida sin tirones.
- **🔄 Modo Bucle**: Opción para repetir el video automáticamente.
- **📍 Barra de Estado Fija**: La barra de progreso se mantiene en la parte inferior de la ventana para evitar parpadeos y desorden visual.

---

## 🛠️ Requisitos del Sistema

Antes de ejecutar, asegúrate de tener instaladas las librerías necesarias:

```bash
pip install opencv-python numpy
```
*(Si tienes problemas con las versiones en Windows, prueba con: `python -m pip install opencv-python numpy`)*

---

## 🚀 Cómo Usar

### 1. Modo Interactivo (Recomendado)
Simplemente ejecuta el script y sigue las instrucciones en pantalla:
```bash
python ASCII_v5_ultimate_ES.py
```

### 2. Modo Línea de Comandos
Para usuarios avanzados que prefieren usar flags:
```bash
# Reproducir con color y ajuste automático
python ASCII_v5_ultimate_ES.py mi_video.mp4 --color

# Desactivar ajuste automático y fijar ancho a 150
python ASCII_v5_ultimate_ES.py mi_video.mp4 --no-fit --width 150

# Modo informativo (solo ver detalles del video)
python ASCII_v5_ultimate_ES.py mi_video.mp4 --info
```

---

## ⌨️ Controles
- **Ctrl + C**: Detiene la reproducción de forma segura y restaura el cursor de la terminal.

## 💡 Créditos
- **Creador Original**: [stepanussaruran](https://github.com/stepanussaruran)
- **Traducción y Mejoras**: Nicolas Romero (coralgamer) & Gemini AI.

---
*Para la versión en inglés, consulta [README_EN.md](README_EN.md).*
