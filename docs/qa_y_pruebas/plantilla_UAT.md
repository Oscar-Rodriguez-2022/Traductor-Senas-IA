# Plantilla de Pruebas de Aceptación (UAT)
## LSP Vision AI — Capstone Project Sistemas 2026
### Universidad Privada del Norte
### Versión del documento: 1.0 · Fecha: 2026-06-13

**Proyecto:** Traductor de Lengua de Señas Peruana (LSP) con IA  
**Versión del sistema:** v1.1 (MediaPipe Tasks API · 25 letras reconocibles)  
**Responsable UAT:** Rodriguez Chacara, Oscar Daniel  
**HU de referencia:** HU-19 (Pruebas de Aceptación con Usuarios Reales)

---

## 1. Objetivo

Validar que el sistema cumple los Criterios de Aceptación (CA) definidos en las Historias de Usuario desde la perspectiva del usuario final. Esta plantilla es el artefacto requerido por el CA-21.4 y constituye evidencia para la sustentación del Capstone.

---

## 2. Datos de la Sesión

| Campo | Valor |
|---|---|
| Fecha | _______________ |
| Facilitador | _______________ |
| Participante ID | UAT-XXX (anonimizado) |
| Perfil del participante | ☐ Persona con discapacidad auditiva  ☐ Oyente |
| Dispositivo | _______________ |
| Navegador | ☐ Chrome  ☐ Firefox  ☐ Edge |
| URL del sistema | _______________ |

---

## 3. Instrucciones para el Facilitador

1. Presentar la aplicación sin dar instrucciones previas de uso (prueba exploratoria).
2. Pedir al participante que **piense en voz alta** mientras realiza cada tarea.
3. Registrar el resultado (✅/❌) y anotar observaciones sin interrumpir.
4. Al final, aplicar el cuestionario SUS (Sección 6).
5. No revelar las respuestas correctas durante la sesión.

---

## 4. Escenarios de Prueba por Historia de Usuario

### UAT-01 · Acceso al sistema (HU-13)

**Descripción:** El usuario intenta ingresar al sistema con la clave correcta e incorrecta.

| Paso | Acción del participante | Resultado esperado | CA | ✅/❌ | Observaciones |
|------|------------------------|-------------------|-----|-------|---------------|
| 1 | Abrir la URL del sistema | Se muestra el formulario de login con título "LSP Vision AI" | CA-13.1 | | |
| 2 | Ingresar una clave incorrecta (ej. "abc123") | Aparece mensaje de error con intentos restantes | CA-13.5 | | |
| 3 | Ingresar la clave correcta "UPN2026" | El sistema muestra la página principal con la cámara | CA-13.2 | | |
| 4 | Esperar 60 minutos inactivo (simulado: manipular reloj) | El sistema solicita nueva autenticación | CA-13.3 | | |
| 5 | Ingresar 5 veces seguidas una clave incorrecta | El sistema bloquea el acceso por 5 minutos y muestra mensaje de bloqueo claro | CA-13.7 | | |

**Criterio de aprobación:** 4/5 pasos exitosos.

---

### UAT-02 · Detección de mano en tiempo real (HU-09)

**Descripción:** El participante pone su mano frente a la cámara y verifica la detección.

| Paso | Acción del participante | Resultado esperado | CA | ✅/❌ | Observaciones |
|------|------------------------|-------------------|-----|-------|---------------|
| 1 | Hacer clic en "START" para activar la cámara | La cámara se activa y muestra video en vivo con badge "EN VIVO" | CA-08.1 | | |
| 2 | Mostrar la mano abierta frente a la cámara | Aparece el skeleton azul sobre la mano en el video | CA-09.2 | | |
| 3 | Alejar la mano del encuadre | El skeleton desaparece, el resultado muestra "-" | CA-09.3 | | |
| 4 | Verificar el contador de FPS en la esquina | El contador muestra ≥ 24 FPS | CA-08.4 | | |

**Criterio de aprobación:** 3/4 pasos exitosos.

---

### UAT-03 · Reconocimiento de señas del abecedario LSP (HU-10)

**Descripción:** El participante hace señas de letras del abecedario y verifica el reconocimiento.

| Seña | Letra esperada | Confianza mínima | Resultado obtenido | Confianza obtenida | ✅/❌ |
|------|---------------|------------------|-------------------|--------------------|-------|
| Seña de la letra A | A | ≥ 70% | | | |
| Seña de la letra B | B | ≥ 70% | | | |
| Seña de la letra C | C | ≥ 70% | | | |
| Seña de la letra L | L | ≥ 70% | | | |
| Seña de la letra N | N | ≥ 70% | | | |
| Seña de la letra V | V | ≥ 70% | | | |

**Criterio de aprobación:** ≥ 4/6 letras reconocidas con confianza ≥ 70%.

**Nota:** El sistema reconoce 25 letras LSP estáticas (A–Z excepto O). La letra **O** no está disponible
en esta versión por falta de muestras detectables (ver INC-12). Las letras **J** y **Z** requieren
movimiento y no son soportadas en el modo estático de esta versión (deuda técnica v1.1).

---

### UAT-04 · Indicador de confianza (HU-10 CA-10.3)

**Descripción:** El participante verifica que el indicador de confianza cambia visualmente.

| Condición | Comportamiento esperado | ✅/❌ | Observaciones |
|-----------|------------------------|-------|---------------|
| Seña clara y bien iluminada | Barra de confianza verde, ≥ 80% | | |
| Seña parcialmente ocluida | Barra amarilla, 40–79% | | |
| Mano no detectada | Resultado muestra "-", sin barra | | |

---

### UAT-05 · Accesibilidad para usuario con discapacidad auditiva (HU-15)

**Descripción:** El participante (preferiblemente con discapacidad auditiva) evalúa la usabilidad de la interfaz.

| Aspecto | Pregunta al participante | Escala 1–5 | Observaciones |
|---------|--------------------------|-----------|---------------|
| Claridad del resultado | "¿Puedes ver claramente qué letra detectó el sistema?" | | |
| Panel de resultado | "¿El tamaño del resultado es suficientemente grande para leerlo?" | | |
| Historial de señas | "¿El historial de letras detectadas es útil para construir palabras?" | | |
| Barra de confianza | "¿Entiendes qué significa la barra de porcentaje?" | | |
| Navegación general | "¿Pudiste usar la aplicación sin necesitar audio?" | | |

**Criterio de aprobación:** Promedio ≥ 3.5/5.

---

### UAT-06 · Explicabilidad del sistema IA (HU-16)

**Descripción:** El participante revisa la sección de explicabilidad y evalúa si entiende el proceso.

| Paso | Acción | Resultado esperado | CA | ✅/❌ |
|------|--------|-------------------|-----|-------|
| 1 | Hacer clic en "¿Cómo funciona el sistema?" | Se expande el panel con el pipeline paso a paso | CA-16.1 | |
| 2 | Leer cada paso del pipeline | Cada paso tiene una descripción comprensible sin jerga técnica | CA-16.1 | |
| 3 | Ver la sección de limitaciones | Aparece información honesta sobre las limitaciones del sistema | CA-16.3 | |
| 4 | Hacer una seña y observar el panel de alternativas XAI | Aparece el panel con el top-5 de letras candidatas y sus porcentajes de confianza | CA-16.2 | |

---

### UAT-07 · Privacidad y datos del usuario (HU-20)

**Descripción:** Verificar que el sistema informa correctamente sobre privacidad.

| Criterio | Verificación | ✅/❌ |
|----------|-------------|-------|
| El sistema NO graba video | El facilitador confirma que no hay archivos de video creados | |
| El sistema NO solicita datos personales | No hay formularios con nombre, DNI o correo | |
| La clave no se muestra en pantalla | El campo de contraseña oculta el texto | |

---

### UAT-08 · Rendimiento percibido (HU-22)

**Descripción:** El participante evalúa la fluidez del sistema durante uso sostenido.

| Periodo | Observación | FPS medido | ✅/❌ |
|---------|-------------|-----------|-------|
| Primeros 30 segundos | Sistema fluido y responsivo | | |
| Entre 1 y 3 minutos | Sin degradación de rendimiento | | |
| 5 minutos de uso continuo | Sin congelamiento ni lag visible | | |

**Criterio de aprobación:** FPS ≥ 24 en todos los periodos.

---

## 5. Resumen de Resultados

| UAT | Nombre | Criterio aprobación | Resultado | Estado |
|-----|--------|---------------------|-----------|--------|
| UAT-01 | Acceso al sistema | 4/5 pasos | /5 | ☐ PASA  ☐ FALLA |
| UAT-02 | Detección de mano | 3/4 pasos | /4 | ☐ PASA  ☐ FALLA |
| UAT-03 | Reconocimiento LSP | ≥ 4/6 letras | /6 | ☐ PASA  ☐ FALLA |
| UAT-04 | Indicador de confianza | 2/3 condiciones | /3 | ☐ PASA  ☐ FALLA |
| UAT-05 | Accesibilidad auditiva | Promedio ≥ 3.5/5 | /5 | ☐ PASA  ☐ FALLA |
| UAT-06 | Explicabilidad IA | 3/4 pasos | /4 | ☐ PASA  ☐ FALLA |
| UAT-07 | Privacidad | 3/3 criterios | /3 | ☐ PASA  ☐ FALLA |
| UAT-08 | Rendimiento | FPS ≥ 24 | FPS: ___ | ☐ PASA  ☐ FALLA |

**Total UATsaprobados:** ___ / 8

**Resultado global:**  ☐ APROBADO (≥ 6/8)  ☐ RECHAZADO (< 6/8)

---

## 6. Cuestionario SUS (System Usability Scale)

Instrucciones: Puntuar del **1 (muy en desacuerdo)** al **5 (muy de acuerdo)**.

| # | Afirmación | 1 | 2 | 3 | 4 | 5 |
|---|-----------|---|---|---|---|---|
| 1 | Creo que me gustaría usar este sistema con frecuencia | | | | | |
| 2 | Encontré el sistema innecesariamente complejo | | | | | |
| 3 | Pensé que el sistema era fácil de usar | | | | | |
| 4 | Creo que necesitaría asistencia técnica para usar este sistema | | | | | |
| 5 | Las diversas funciones del sistema estaban bien integradas | | | | | |
| 6 | Había demasiada inconsistencia en el sistema | | | | | |
| 7 | Imagino que la mayoría de personas aprendería rápido a usar este sistema | | | | | |
| 8 | Encontré el sistema muy difícil de usar | | | | | |
| 9 | Me sentí muy seguro/a al usar el sistema | | | | | |
| 10 | Necesité aprender mucho antes de poder usar este sistema | | | | | |

**Cálculo del puntaje SUS:**
- Ítems impares (1,3,5,7,9): suma = valor - 1
- Ítems pares (2,4,6,8,10): suma = 5 - valor
- Puntaje total = suma × 2.5

**Puntaje SUS obtenido:** ___ / 100  
**Interpretación:**  ≥ 80 = Excelente · 68–79 = Bueno · 51–67 = Marginal · < 51 = Deficiente

**Umbral de aprobación HU-19 CA-19.4:** ≥ 3.5/5 (equivale a ≥ 70 SUS)

---

## 7. Observaciones Adicionales del Participante

_[Espacio para comentarios libres, sugerencias de mejora y problemas no cubiertos por los escenarios anteriores]_

---

## 8. Firma y Conformidad

| Rol | Nombre | Firma | Fecha |
|-----|--------|-------|-------|
| Participante | | | |
| Facilitador | Rodriguez Chacara, Oscar Daniel | | |

---

*Este documento fue generado como artefacto de cierre del Capstone Project LSP Vision AI, Universidad Privada del Norte, 2026.*
