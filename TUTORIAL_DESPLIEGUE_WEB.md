# 🚀 TUTORIAL DE DESPLIEGUE — Para el encargado (tú)

Cómo juntar los datos del equipo, reentrenar el modelo y **publicar la web** para
que cualquiera la use desde un link (PC y celular). Hazlo en orden.

---

## 🟦 PARTE A — Juntar los CSV de tus compañeros

1. Cada compañero te envía su archivo **`landmarks_NOMBRE.csv`** (siguiendo el
   `TUTORIAL_EQUIPO.md`).
2. En la carpeta del proyecto, abre la carpeta **`landmarks_csv`**.
3. **Copia ahí TODOS los CSV** que te enviaron (el tuyo también).
4. Verifica: dentro de `landmarks_csv` deben estar los 6-7 archivos `landmarks_*.csv`.

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
   - **Repository:** `kepler04/IA-Traductor-Senas-LSP-UPN`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. ⚠️ **MUY IMPORTANTE:** abre **"Advanced settings"** y en **Python version**
   elige **3.12** (si no, falla).
5. Clic en **"Deploy"** y espera 2-4 minutos.
6. Te dará una URL pública (ej. `https://ia-traductor-senas-lsp-upn.streamlit.app`).
   **Ese es el link que compartes y le muestras al profe.** 🎉

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
  para mostrar las pruebas y métricas (mira `GUIA_QA.md`).

---

## ❓ Si el despliegue falla

| Error en Streamlit | Causa y solución |
|---|---|
| `mediapipe==0.10.21 has no wheels...` | No pusiste **Python 3.12** en Advanced settings. Borra la app y créala de nuevo eligiendo 3.12. |
| `libGL.so.1: cannot open...` | Falta el archivo `packages.txt` (ya está en el repo). Asegúrate de haber hecho `git push` de todo. |
| `Error installing requirements` | Abre **"Manage app"**, mira el log y revisa qué librería falla. |
| La cámara pide permiso y no carga | Es normal: el usuario debe **autorizar la cámara** en el navegador y pulsar **START**. |
```
