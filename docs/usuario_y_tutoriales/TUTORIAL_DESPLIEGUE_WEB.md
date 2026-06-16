# Tutorial de Despliegue Web — LSP Vision AI
## Streamlit Community Cloud · Capstone Project Sistemas 2026
### Universidad Privada del Norte · Versión 2.0 · 2026-06-13

Cómo consolidar el dataset del equipo, reentrenar el modelo con la nueva estructura
`src/` y **publicar la app en Streamlit Community Cloud** para que sea accesible
desde cualquier dispositivo. Hazlo en el orden indicado.

---

## 🟦 PARTE A — Juntar los CSV de tus compañeros

1. Cada compañero te envía su archivo **`landmarks_NOMBRE.csv`** (siguiendo el
   `TUTORIAL_EQUIPO.md`).
2. En la carpeta del proyecto, abre la carpeta **`landmarks_csv`**.
3. **Copia ahí TODOS los CSV** que te enviaron (el tuyo también).
4. Verifica: dentro de `landmarks_csv` deben estar los 7 archivos `landmarks_*.csv`.

> **Nota:** la carpeta `landmarks_csv/` es **local únicamente** — está en `.gitignore` y no se sube al repositorio. Comparte los CSV entre compañeros por correo, Drive o similar.

---

## 🟦 PARTE B — Reentrenar el modelo con TODO

1. En la carpeta del proyecto, haz **doble clic** en **`4_ENTRENAR_desde_CSV.bat`**.
2. Verás cómo combina los CSV y entrena. Al final dice:
   *"✅ modelo.pkl actualizado con los datos de todo el equipo"*.
3. Esto regenera el archivo **`modelo.pkl`** (el "cerebro" con todas las señas del equipo).

---

## 🟦 PARTE C — Subir el modelo nuevo a GitHub

> Solo se sube el `modelo.pkl` (pesa ~100 KB). Las imágenes NO se suben.

1. Abre una terminal en la carpeta del proyecto (clic derecho → "Abrir terminal"
   o "Git Bash Here").
2. Pega estos 3 comandos, **uno por uno**, presionando Enter en cada uno:

   ```
   git add modelo.pkl
   ```
   ```
   git commit -m "Modelo actualizado con dataset del equipo"
   ```
   ```
   git push
   ```

3. Si te pide usuario/contraseña la primera vez, inicia sesión con tu cuenta de GitHub.

---

## 🟦 PARTE D — Desplegar la web (PRIMERA VEZ)

> Esto solo se hace **una vez**. Después se actualiza solo con cada `git push`.

1. Entra a **https://share.streamlit.io** e inicia sesión con **GitHub**.
2. Clic en **"Create app"** → **"Deploy a public app from GitHub"**.
3. Rellena:
   - **Repository:** `Oscar-Rodriguez-2022/Traductor-Senas-IA`
   - **Branch:** `main`
   - **Main file path:** `src/app.py`
4. Abre **"Advanced settings"** → **Python version**: elige **3.12** (MediaPipe 0.10.21 no es compatible con 3.13).
5. En **Secrets** agrega el hash de contraseña. Genera el valor con:
   ```
   python -c "import sys; sys.path.insert(0,'src'); from lsp_auth import hash_password; print(hash_password('UPN2026'))"
   ```
   Luego en Secrets escribe: `PASSWORD_HASH = "<resultado del comando anterior>"`
6. Clic en **"Deploy"** y espera 2-4 minutos.
7. Te dará una URL pública (ej. `https://traductor-senas-ia.streamlit.app`). Ese es el link para la sustentación.

---

## 🟦 PARTE E — Actualizar la web (las siguientes veces)

Cuando consigan más datos y reentrenen, solo repite:

```
git add modelo.pkl
git commit -m "Modelo mejorado"
git push
```

La web de Streamlit **se actualiza sola** en 1-2 minutos. No tienes que volver a
configurar nada.

---

## 💡 Consejo de oro para la sustentación

- **Demo fluida:** durante la exposición, corre la web **en tu laptop** con doble clic
  en `3_WEB_probar_local.bat` (usa tu CPU, va sin lag).
- **Accesibilidad:** muestra también el **link público** para demostrar que está
  desplegada y que cualquiera la puede abrir desde su celular.
- **Calidad:** abre `reportes/REPORTE_QA.pdf` y la página **"Metricas QA"** de la web
  para mostrar las pruebas y métricas (mira `docs/qa_y_pruebas/GUIA_QA.md`).

---

## Solución de Problemas de Despliegue

| Error en Streamlit | Causa y solución |
|---|---|
| `mediapipe==0.10.21 has no wheels...` | Python version no es 3.12. Borra la app en Streamlit Cloud y recréala eligiendo Python 3.12. |
| `libGL.so.1: cannot open...` | Falta `packages.txt` en la raíz del repo. Ya está incluido — asegúrate de haber hecho `git push`. |
| `ModuleNotFoundError: No module named 'lsp_core'` | El **Main file path** debe ser `src/app.py`, no `app.py`. Corrige en los ajustes del app. |
| `Error installing requirements` | Abre **"Manage app"** → "Logs" y revisa qué librería falla. Verifica que `requirements.txt` es el correcto. |
| La cámara pide permiso y no conecta | El usuario debe hacer clic en **"Permitir"** en el aviso del navegador. En redes corporativas, el servidor TURN de `openrelay.metered.ca` actúa como fallback. |
| `st.secrets has no key "PASSWORD_HASH"` | Falta el secreto en Streamlit Cloud. Añade `PASSWORD_HASH` en la sección Secrets del app. |

---

*Tutorial de Despliegue Web v2.1 · LSP Vision AI · UPN Sistemas 2026*
*Cambios v2.1: comando de generación de hash en §D, path GUIA_QA.md corregido*
