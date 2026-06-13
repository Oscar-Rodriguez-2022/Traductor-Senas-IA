# Tutorial para Nuevos Integrantes del Equipo — LSP Vision AI
## Propiedad Compartida del Código, Captura de Dataset y Contribución al Proyecto
### Universidad Privada del Norte · Capstone Project Sistemas 2026
### Versión: 2.0 · 2026-06-13

> **Lee en orden y no te saltes pasos.**
> Tiempo estimado: 30-40 minutos (mayoría es instalación y captura).

Tu misión: **instalar el entorno, capturar tus señas con la cámara y enviar UN
archivo pequeño** (`landmarks_TuNombre.csv`) al responsable del equipo.
No necesitas enviar fotos — solo el archivo CSV de landmarks.

---

## Normas de Propiedad Compartida (XP — Extreme Programming)

Este proyecto sigue el principio de **Collective Code Ownership** de XP:

| Norma | Descripción |
|-------|------------|
| **Cualquiera puede cambiar cualquier módulo** | No hay "dueños" individuales de archivos — todos somos responsables del código completo |
| **Tests antes de mergear** | Antes de hacer `git push`, ejecuta `pytest tests/ -v` y verifica 0 FAIL |
| **Rama por feature** | Usa `feature/nombre-del-cambio` para cada modificación; nunca commitear directo a `main` |
| **Pull Request con revisión** | Toda rama necesita aprobación de al menos 1 integrante antes de mergear |
| **Estilo consistente** | Ejecutar `black src/ tests/` y `flake8 src/ tests/` antes de cada commit |
| **Commits descriptivos** | Formato: `tipo(módulo): descripción corta`. Ej: `feat(lsp_ui): agregar skip-nav WCAG` |

---

## 🟦 PARTE 1 — Instalar Python (el motor del programa)

1. Entra a este link: **https://www.python.org/downloads/release/python-31210/**
2. Baja hasta la sección **"Files"**.
3. Descarga **"Windows installer (64-bit)"**.
4. Abre el archivo descargado.
5. ⚠️ **MUY IMPORTANTE:** en la primera pantalla, **MARCA la casilla de abajo que dice
   `Add python.exe to PATH`** ✅ (si no la marcas, nada va a funcionar).
6. Haz clic en **"Install Now"** y espera a que termine.
7. Clic en **"Close"**.

> 🔴 Usa **Python 3.12** (este link), NO la versión más nueva. Las versiones nuevas
> dan error con una librería del proyecto.

---

## 🟦 PARTE 2 — Instalar Git (para descargar el proyecto)

1. Entra a: **https://git-scm.com/download/win**
2. Descarga **"64-bit Git for Windows Setup"**.
3. Abre el archivo.
4. Dale **"Next"** a TODO (no cambies nada, deja lo que viene por defecto) hasta que
   aparezca **"Install"**. Clic en Install y espera.
5. Clic en **"Finish"**.

---

## PARTE 3 — Descargar el proyecto

1. Crea una carpeta fácil de encontrar, por ejemplo en el **Escritorio**.
2. Entra a esa carpeta, haz **clic derecho** en un espacio vacío.
3. Elige **"Abrir el terminal"** o **"Git Bash Here"** (sale una ventana negra).
4. Copia y pega este comando y presiona **Enter**:

   ```
   git clone https://github.com/Oscar-Rodriguez-2022/Traductor-Senas-IA.git
   ```

5. Espera a que termine. Se creará una carpeta llamada **`Traductor-Senas-IA`**.

---

## 🟦 PARTE 4 — Instalar las librerías (una sola vez)

1. En la **misma ventana negra**, entra a la carpeta del proyecto pegando esto y Enter:

   ```
   cd Traductor-Senas-IA
   ```

2. Ahora pega este comando y presiona **Enter** (tarda unos minutos, descarga cosas):

   ```
   pip install -r requirements.txt
   ```

3. Espera a que termine. Cuando veas que aparece de nuevo la línea para escribir,
   ya está listo.

> 🔴 Respeta el `mediapipe==0.10.21` tal cual. Esa versión exacta es la que funciona.

---

## PARTE 5 — Capturar tus señas con la cámara

1. Abre la carpeta **`Traductor-Senas-IA`** en tu explorador de archivos.
2. Haz **doble clic** en el archivo **`1_CAPTURAR_dataset.bat`**.
3. Se abrirá una ventana negra y luego **la ventana de tu cámara**.
4. El programa te irá pidiendo letra por letra (A, B, C...). Para cada una:
   - Verás el mensaje *"Listo para la 'A'. Presiona una tecla"*.
   - **Haz la seña de esa letra con tu mano frente a la cámara.**
   - **Haz clic sobre la ventana de la cámara** y **presiona cualquier tecla** del teclado.
   - Empezará a tomar fotos solo (verás un contador verde subiendo: `0/500`, `1/500`...).
   - Cuando llegue a 500, te preguntará en la ventana negra:
     escribe **`G`** y Enter para **guardar** y pasar a la siguiente letra.
5. Si una letra ya tenía fotos, te dará 3 opciones (escribe el número + Enter):
   - **1** = pasar a la siguiente
   - **2** = borrar y rehacer
   - **3** = agregar más
6. **No tienes que hacer las 26 letras.** Ponte de acuerdo con tu equipo sobre cuáles
   te tocan. Hazlas con **buena luz** y la **mano bien visible**.
7. Para cerrar en cualquier momento: presiona la tecla **`q`** sobre la ventana de la cámara.

### 💡 Consejos para que tus señas sirvan
- Buena iluminación de frente (nada de contraluz ni oscuridad).
- Fondo despejado.
- Mano completa dentro del recuadro verde.
- Mueve un poquito la mano (gírala/acércala) mientras graba, para dar variedad.

---

## 🟩 PARTE 6 — Generar TU archivo para enviar

1. En la carpeta del proyecto, haz **doble clic** en
   **`COMPANEROS_extraer_landmarks.bat`**.
2. Te pedirá: *"Escribe tu nombre o apodo SIN espacios"*.
   Escribe tu nombre (ej. `juan`, `maria`, `pedro22`) y presiona **Enter**.
3. Espera unos segundos. Procesará tus fotos.
4. Al terminar, se creará un archivo llamado **`landmarks_TuNombre.csv`**
   dentro de la carpeta del proyecto.

---

## 🟩 PARTE 7 — Enviar el archivo

1. Busca en la carpeta el archivo **`landmarks_TuNombre.csv`** (pesa muy poco, unos KB).
2. **Envíaselo al encargado** del equipo por WhatsApp, Drive o correo.
3. ✅ **¡Listo, eso es todo!** Ya cumpliste tu parte.

> No mandes las fotos ni la carpeta `data`. **Solo el archivo `.csv`.**

---

## Solución de Problemas Comunes

| Problema | Solución |
|---|---|
| `'python' no se reconoce...` o `'pip' no se reconoce...` | No marcaste **"Add Python to PATH"**. Desinstala Python y reinstálalo marcando esa casilla (Parte 1, paso 5). |
| `'git' no se reconoce...` | No instalaste Git o no reiniciaste la ventana. Cierra la ventana negra, abre una nueva e intenta de nuevo. |
| La cámara no abre / pantalla negra | Cierra otras apps que usen la cámara (Zoom, Meet, Teams). Revisa que ninguna otra ventana del programa esté abierta. |
| `AttributeError: module 'mediapipe' has no attribute 'solutions'` | Instalaste la versión incorrecta. Ejecuta: `pip install mediapipe==0.10.21 --force-reinstall` |
| `ModuleNotFoundError: No module named 'lsp_core'` | Los módulos están en `src/`. Usa siempre los scripts `.bat` o ejecuta desde la raíz del proyecto con `pythonpath = ["src"]`. |
| El `.bat` no encuentra Python | Abre la terminal en la carpeta del proyecto y ejecuta: `python scripts/extraer_landmarks.py` |
| Se cierra muy rápido la ventana negra | Ábrela desde una terminal para leer el error, o toma captura y mándala al encargado. |

---

## Resumen Rápido (si ya instalaste todo)

1. Doble clic en **`1_CAPTURAR_dataset.bat`** → graba tus señas.
2. Doble clic en **`COMPANEROS_extraer_landmarks.bat`** → escribe tu nombre.
3. Envía el archivo **`landmarks_TuNombre.csv`** al encargado.
4. Para ejecutar la app web localmente: doble clic en **`3_WEB_probar_local.bat`**.

---

*Tutorial para Nuevos Integrantes v2.1 · LSP Vision AI · UPN Sistemas 2026*
*Cambios v2.1: PARTE 4 — corregido nombre de carpeta (cd Traductor-Senas-IA, no IA-Traductor-Senas-LSP-UPN)*
