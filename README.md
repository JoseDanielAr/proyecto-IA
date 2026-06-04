# Reconocimiento de Ingredientes y Sugerencias de Recetas

Aplicación web construida con Flask que detecta frutas y vegetales en imágenes mediante un modelo YOLOv8 (PyTorch), y sugiere recetas según los ingredientes detectados.

---

## Funcionalidades

- **Detección por imagen** — Sube una foto (`.jpg`, `.jpeg`, `.png`) y el modelo identifica los ingredientes presentes. La imagen con las detecciones se guarda y se muestra en pantalla.
- **Lista editable** — Agrega o elimina ingredientes de la lista antes de confirmarla. Los cambios se mantienen en sesión.
- **Recetas posibles** — Recetas para las que ya tienes todos los ingredientes.
- **Recetas casi posibles** — Recetas para las que tienes al menos un ingrediente; se muestra por separado qué tienes y qué te falta.
- **Text-to-Speech** — Escucha el nombre, descripción e ingredientes de cada receta en voz alta desde la interfaz, usando la Web Speech API del navegador.

Cada receta incluye nombre, descripción, lista de ingredientes y pasos de preparación.

---

## Ingredientes reconocidos

El modelo puede detectar más de 60 ingredientes, entre ellos: manzana, plátano, tomate, zanahoria, brócoli, papa, espinaca, pepino, ajo, cebolla, pimiento, aguacate, mango, fresa, sandía, pollo, salmón, huevo, arroz, pasta, entre otros.

---

## Stack

| Área | Tecnología |
|---|---|
| Backend | Flask, Python |
| Detección | YOLOv8 (Ultralytics), PyTorch |
| Procesamiento de imagen | Pillow |
| Frontend | HTML, CSS, JavaScript |
| Text-to-Speech | Web Speech API |
| Sesiones | Flask Session |

---

## Requisitos

```
flask
ultralytics
pillow
werkzeug
```

El modelo entrenado (`model.pt`) debe colocarse en la raíz del proyecto. No está incluido en el repositorio.

## Capturas de pantalla

<img width="661" height="1019" alt="Screenshot 2026-06-04 113032" src="https://github.com/user-attachments/assets/81499e23-5c8b-473d-98c8-9a6c42c6e1ed" />

<img width="845" height="1270" alt="Screenshot 2026-06-04 122711" src="https://github.com/user-attachments/assets/5a5e54d5-ce4f-47a8-b250-d0d6b019b960" />

