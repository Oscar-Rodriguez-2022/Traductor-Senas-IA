# Guía de Despliegue — Hugging Face Spaces (Docker)
## LSP Vision AI · Universidad Privada del Norte · Capstone Project Sistemas 2026
### Versión: 2.1 · 2026-06-16 · **✅ DESPLEGADO EN PRODUCCIÓN**

> **App en vivo:** [https://huggingface.co/spaces/OscarRodri/Traductor-Senas-IA](https://huggingface.co/spaces/OscarRodri/Traductor-Senas-IA)

Hugging Face Spaces es la plataforma estándar de la industria para publicar proyectos de IA/ML.
Esta guía cubre el despliegue con **Docker** (modalidad que demuestra competencias DevOps para el Capstone).
El `Dockerfile` del proyecto ya está configurado con las medidas de seguridad requeridas (usuario no-root, flags de seguridad Streamlit).

> **Demo en la sustentación:** la app ya está pública en la URL de arriba.
> Para máximo rendimiento en la presentación, ejecuta también la app localmente con `streamlit run src/app.py`.
> La URL de HF demuestra que el sistema está públicamente accesible sin necesidad de instalar nada.

---

## Prerequisitos

- [ ] Cuenta en [huggingface.co](https://huggingface.co) (gratuita)
- [ ] Repositorio del proyecto en GitHub con todos los archivos actualizados
- [ ] `modelo.pkl` entrenado con los datos del equipo y subido al repo
- [ ] Git instalado en tu máquina

---

## Parte A — Preparar el modelo antes de desplegar

El modelo debe estar entrenado con los datos de **todo el equipo** antes de subir a HF.

1. Asegúrate de tener los CSV de tus compañeros en la carpeta `landmarks_csv/`.
2. Haz doble clic en `4_ENTRENAR_desde_CSV.bat` para reentrenar.
3. Verifica que el archivo `modelo.pkl` existe y fue actualizado recientemente.
4. Sube el modelo a GitHub:

```bash
git add modelo.pkl
git commit -m "Actualizar modelo con dataset del equipo completo"
git push
```

---

## Parte B — Crear el Space en Hugging Face

1. Inicia sesión en [huggingface.co](https://huggingface.co).
2. Haz clic en tu avatar (esquina superior derecha) → **New Space**.
3. Configura el Space:

| Campo | Valor |
|-------|-------|
| **Owner** | Tu usuario de HF |
| **Space name** | `lsp-vision-ai` (o el nombre que prefieras) |
| **License** | MIT |
| **SDK** | **Docker** ← importante para demostrar competencias DevOps |
| **Docker template** | Blank |
| **Hardware** | CPU Basic — Free |
| **Visibility** | Public |

4. Clic en **Create Space**. HF crea un repositorio git vacío para el Space.

---

## Parte C — Conectar tu repositorio de GitHub al Space

Tienes dos opciones. Elige la que se adapte a tu situación:

### Opción 1 — Subir directamente al Space (recomendada si tu repo está listo)

Clona el Space de HF en tu máquina y copia los archivos del proyecto:

```bash
# 1. Clonar el Space vacío de HF
git clone https://huggingface.co/spaces/OscarRodri/Traductor-Senas-IA
cd lsp-vision-ai

# 2. Copiar TODOS los archivos del proyecto (reemplaza con tu ruta real)
xcopy /E /H /Y "C:\Traductor-Senas-IA\*" "."

# 3. Verificar que modelo.pkl está incluido
dir modelo.pkl

# 4. Subir todo al Space
git add .
git commit -m "Despliegue inicial LSP Vision AI"
git push
```

### Opción 2 — Sincronizar desde GitHub (si ya tienes el repo en GitHub)

En el Space de HF, ve a **Settings** → **Repository** → **Link to GitHub repository**.
Ingresa tu usuario y repo de GitHub. HF sincronizará automáticamente con cada push.

---

## Parte D — Configurar el secreto de autenticación

La app requiere una clave de acceso. Configúrala como secreto en HF para que no quede expuesta en el código.

1. En tu Space de HF, ve a **Settings** → **Repository secrets**.
2. Agrega el siguiente secret:

| Nombre | Valor |
|--------|-------|
| `LSP_PASSWORD_HASH` | (ver paso 3) |

3. Para generar el valor del hash, ejecuta esto en tu terminal local:

```bash
python -c "import sys; sys.path.insert(0,'src'); from lsp_auth import hash_password; print(hash_password('TU_CLAVE_AQUI'))"
```

Ejemplo con la clave de demo `UPN2026`:
```bash
python -c "import sys; sys.path.insert(0,'src'); from lsp_auth import hash_password; print(hash_password('UPN2026'))"
```

Copia el hash de 64 caracteres y pégalo como valor del secret `LSP_PASSWORD_HASH`.

> **Nota:** si no configuras el secret, la app funciona igual usando la clave de demo `UPN2026`.
> Para la sustentación esto es aceptable; para producción real se recomienda configurar el hash.

---

## Parte E — Verificar el despliegue

1. Ve a tu Space en `https://huggingface.co/spaces/OscarRodri/Traductor-Senas-IA`.
2. HF construirá la imagen Docker automáticamente (tarda 3-8 minutos la primera vez).
3. Puedes ver el log de construcción en la pestaña **Logs** (útil para depurar errores).
4. Cuando el indicador pase a verde (**Running**), la app está disponible.
5. Haz clic en **App** para abrir la URL pública y probarla.

### Verificación rápida

| Paso | Qué verificar |
|------|---------------|
| 1 | El formulario de login aparece (no el contenido de la app directamente) |
| 2 | Ingresar `UPN2026` redirige al traductor |
| 3 | La cámara se activa al presionar **START** |
| 4 | La letra detectada aparece en el panel derecho con porcentaje de confianza |
| 5 | La página **Métricas QA** carga correctamente desde el menú lateral |

---

## Parte F — Actualizaciones futuras

Cada vez que hagas cambios (nuevo modelo, mejoras en la UI, etc.):

```bash
# Si usaste la Opción 1 (clon directo del Space)
git add .
git commit -m "Descripción del cambio"
git push

# Si usaste la Opción 2 (GitHub sincronizado)
# Basta con hacer push a tu repo de GitHub — HF se actualiza solo
git push origin main
```

HF reconstruye la imagen Docker automáticamente tras cada push. El proceso tarda ~3-5 minutos.

---

## Solución de problemas frecuentes

| Síntoma | Causa probable | Solución |
|---------|---------------|----------|
| Build falla con `mediapipe` | `requirements.txt` no tiene versión fijada | Verificar `mediapipe==0.10.21` en `requirements.txt` |
| Build falla con `libGL.so.1` | Dockerfile no instala `libgl1` | Verificar que el `Dockerfile` tiene `apt-get install -y libgl1` |
| App arranca pero cámara no conecta | Solo STUN, sin TURN server | Ya está corregido en `src/app.py` con `openrelay.metered.ca` |
| App arranca pero da error 500 | `modelo.pkl` no está en el repo | `git add modelo.pkl && git push` |
| Login no acepta ninguna clave | Secret `LSP_PASSWORD_HASH` mal configurado | Borrar el secret; la app usará `UPN2026` como fallback |
| Space se queda en "Building..." | Primera construcción de Docker | Esperar hasta 8 minutos; ver logs para errores |
| Space se detiene solo | Hardware gratuito tiene límite de inactividad | Normal en HF Free; la app se reactiva al visitarla |

---

## Probar con Docker localmente (opcional — para verificar antes de subir)

Si quieres confirmar que el Dockerfile funciona antes de subir a HF:

```bash
# Construir la imagen
docker build -t lsp-vision-ai .

# Ejecutar (la app quedará en http://localhost:8501)
docker run -p 8501:7860 lsp-vision-ai
```

Abre `http://localhost:8501` en el navegador y verifica que todo funciona.

---

## Recursos utilizados (nivel de estudio)

| Recurso | Nivel | Para qué |
|---------|-------|----------|
| `modelo.pkl` | ~5-15 MB | Modelo SVM entrenado |
| RAM en ejecución | ~300-500 MB | MediaPipe + SVM en tiempo real |
| CPU | < 15% sostenido | Clasificación SVM (muy eficiente) |
| Almacenamiento | ~50 MB | Código + modelo |

El hardware gratuito de HF (2 vCPU, 16 GB RAM) es más que suficiente para esta aplicación.

---

## Evidencias para la sustentación

Captura o registra los siguientes elementos como evidencias del despliegue (HU-21):

1. **URL pública del Space** — `https://huggingface.co/spaces/OscarRodri/Traductor-Senas-IA`
2. **Captura del log de build exitoso** en la pestaña Logs de HF
3. **Captura del traductor funcionando** en la URL pública (login + cámara activa + letra detectada)
4. **Captura desde un dispositivo distinto al de desarrollo** (celular o laptop de un compañero)

Estas evidencias satisfacen los criterios CA-21.1, CA-21.2 y CA-21.3 de la HU-21.

---

*Guía de Despliegue HuggingFace v2.0 · LSP Vision AI · UPN Sistemas 2026*
*Cambios v2.0: rutas src/ actualizadas, comando hash_password con sys.path, INC-09 resuelto en Dockerfile*
