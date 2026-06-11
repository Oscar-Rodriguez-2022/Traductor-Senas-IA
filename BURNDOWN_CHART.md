# Burndown Charts — LSP Vision AI
## Universidad Privada del Norte · Capstone Project Sistemas 2026
### Autor: Rodriguez Chacara, Oscar Daniel

Los siguientes gráficos muestran el avance del equipo en cada Sprint, comparando
el trabajo **ideal** (línea recta) contra el trabajo **real** completado.

- **Eje Y:** Story Points (SP) restantes
- **Eje X:** Días hábiles del Sprint
- Una curva real **por debajo** de la ideal indica adelanto; **por encima**, retraso.

---

## Resumen del Product Backlog

| Sprint | Historias | Story Points | Duración |
|--------|-----------|-------------|----------|
| Sprint 1 | HU-01 … HU-07 | 36 SP | 15 días hábiles |
| Sprint 2 | HU-08 … HU-14, HU-17, HU-18, HU-22 | 57 SP | 10 días hábiles |
| Sprint 3 | HU-15, HU-16, HU-19, HU-20, HU-21 | 24 SP | 10 días hábiles |
| **Total** | **22 HUs** | **117 SP** | **35 días hábiles** |

### Story Points por Historia

| HU | Descripción | SP |
|----|-------------|-----|
| HU-01 | Definición de requerimientos y alcance | 3 |
| HU-02 | Arquitectura modular del sistema | 5 |
| HU-03 | Configuración del entorno y repositorio | 2 |
| HU-04 | Recolección inicial del dataset LSP | 5 |
| HU-05 | Construcción completa del dataset LSP | 8 |
| HU-06 | Extracción de landmarks y preprocesamiento | 5 |
| HU-07 | Entrenamiento y validación del SVM | 8 |
| HU-08 | Captura de video en tiempo real | 5 |
| HU-09 | Detección de manos con MediaPipe | 5 |
| HU-10 | Reconocimiento y traducción en tiempo real | 8 |
| HU-11 | Historial de señas y construcción de texto | 3 |
| HU-12 | Integración completa de módulos | 5 |
| HU-13 | Acceso controlado (clave de sesión) | 8 |
| HU-14 | Registro anónimo de accesos (auditoría) | 5 |
| HU-15 | Interfaz accesible WCAG 2.1 AA | 5 |
| HU-16 | Explicación transparente del sistema de IA | 3 |
| HU-17 | Dashboard de métricas de calidad | 5 |
| HU-18 | Pruebas unitarias automatizadas | 8 |
| HU-19 | Pruebas de aceptación con usuarios finales | 5 |
| HU-20 | Validación de privacidad y protección de datos | 3 |
| HU-21 | Despliegue del sistema | 8 |
| HU-22 | Pruebas de rendimiento, carga y estrés | 5 |

---

## Release Burndown (Proyecto completo)

```mermaid
xychart-beta
    title "Release Burndown — LSP Vision AI (117 SP totales)"
    x-axis ["Sprint 1 ini", "S1 D3", "S1 D6", "S1 D9", "S1 D12", "Sprint 1 fin", "Sprint 2 ini", "S2 D2", "S2 D4", "S2 D6", "S2 D8", "Sprint 2 fin", "Sprint 3 ini", "S3 D2", "S3 D5", "S3 D8", "Sprint 3 fin"]
    y-axis "Story Points Restantes" 0 --> 120
    line [117, 117, 117, 117, 117, 117, 81, 81, 81, 81, 81, 81, 24, 24, 24, 24, 0]
    line [117, 97, 77, 57, 37, 81, 81, 69, 57, 45, 33, 24, 24, 19, 11, 5, 0]
```

> **Línea superior (ideal):** progreso esperado uniforme de 117 → 0 SP.
> **Línea inferior (real):** avance real del equipo por sprint.

---

## Sprint 1 — Planificación, Dataset y Modelo ML

**Duración:** 15 días hábiles · **Capacidad:** 36 SP · **Equipo:** 3 integrantes

| Día | SP Ideal Restantes | SP Real Restantes | HUs cerradas |
|-----|--------------------|-------------------|--------------|
| 0   | 36 | 36 | — |
| 1   | 33.6 | 36 | (planificación) |
| 3   | 28.8 | 33 | HU-01 (-3) |
| 5   | 24.0 | 28 | HU-02 (-5) |
| 7   | 19.2 | 26 | HU-03 (-2) |
| 9   | 14.4 | 21 | HU-04 (-5) |
| 11  | 9.6  | 13 | HU-05 (-8) |
| 13  | 4.8  | 8  | HU-06 (-5) |
| 15  | 0    | 0  | HU-07 (-8) |

```mermaid
xychart-beta
    title "Sprint 1 Burndown (36 SP / 15 días hábiles)"
    x-axis ["Día 0", "Día 1", "Día 3", "Día 5", "Día 7", "Día 9", "Día 11", "Día 13", "Día 15"]
    y-axis "Story Points Restantes" 0 --> 40
    line [36, 33.6, 28.8, 24, 19.2, 14.4, 9.6, 4.8, 0]
    line [36, 36, 33, 28, 26, 21, 13, 8, 0]
```

**Retrospectiva Sprint 1:**
- La construcción del dataset (HU-05) tomó más tiempo de lo estimado por variabilidad de condiciones de iluminación.
- El entrenamiento SVM (HU-07) fue más rápido gracias a la reducción dimensional con landmarks.
- El equipo terminó en tiempo pero con acumulación de trabajo en los días finales.

---

## Sprint 2 — Aplicación Web, Calidad y Seguridad

**Duración:** 10 días hábiles · **Capacidad:** 57 SP · **Equipo:** 3 integrantes

| Día | SP Ideal Restantes | SP Real Restantes | HUs cerradas |
|-----|--------------------|-------------------|--------------|
| 0   | 57 | 57 | — |
| 1   | 51.3 | 57 | (planificación) |
| 2   | 45.6 | 52 | HU-08 (-5) |
| 3   | 39.9 | 47 | HU-09 (-5) |
| 4   | 34.2 | 39 | HU-08+HU-10 parcial |
| 5   | 28.5 | 31 | HU-10 (-8) |
| 6   | 22.8 | 26 | HU-11 (-3), HU-12 (-2) |
| 7   | 17.1 | 18 | HU-12 (-3), HU-22 (-5) |
| 8   | 11.4 | 10 | HU-13 (-8) |
| 9   | 5.7  | 5  | HU-17 (-5) |
| 10  | 0    | 0  | HU-14 (-5), HU-18 (-8) |

```mermaid
xychart-beta
    title "Sprint 2 Burndown (57 SP / 10 días hábiles)"
    x-axis ["Día 0", "Día 1", "Día 2", "Día 3", "Día 4", "Día 5", "Día 6", "Día 7", "Día 8", "Día 9", "Día 10"]
    y-axis "Story Points Restantes" 0 --> 60
    line [57, 51.3, 45.6, 39.9, 34.2, 28.5, 22.8, 17.1, 11.4, 5.7, 0]
    line [57, 57, 52, 47, 39, 31, 26, 18, 10, 5, 0]
```

**Retrospectiva Sprint 2:**
- La autenticación HMAC (HU-13) fue más compleja de testear que una JWT estándar, pero el resultado fue más robusto para el contexto académico.
- Las 14 pruebas de `test_auth.py` y 9 de `test_audit.py` dieron confianza al equipo para el sprint siguiente.
- Se implementó TDD de forma estricta en `lsp_auth` y `lsp_audit`, con commits de tests en FAIL antes del código.

---

## Sprint 3 — Ética, Accesibilidad y Despliegue

**Duración:** 10 días hábiles · **Capacidad:** 24 SP · **Equipo:** 3 integrantes

| Día | SP Ideal Restantes | SP Real Restantes | HUs cerradas |
|-----|--------------------|-------------------|--------------|
| 0   | 24 | 24 | — |
| 1   | 21.6 | 24 | (planificación) |
| 2   | 19.2 | 19 | HU-20 (-3), HU-16 parcial |
| 4   | 14.4 | 16 | HU-16 (-3) |
| 5   | 12.0 | 11 | HU-15 (-5) |
| 7   | 7.2  | 8  | HU-19 (-3) |
| 8   | 4.8  | 5  | HU-19 completa (-2) |
| 9   | 2.4  | 3  | — |
| 10  | 0    | 0  | HU-21 (-8) |

```mermaid
xychart-beta
    title "Sprint 3 Burndown (24 SP / 10 días hábiles)"
    x-axis ["Día 0", "Día 1", "Día 2", "Día 4", "Día 5", "Día 7", "Día 8", "Día 9", "Día 10"]
    y-axis "Story Points Restantes" 0 --> 28
    line [24, 21.6, 19.2, 14.4, 12, 7.2, 4.8, 2.4, 0]
    line [24, 24, 19, 16, 11, 8, 5, 3, 0]
```

**Retrospectiva Sprint 3:**
- La accesibilidad WCAG 2.1 AA (HU-15) requirió ajustes iterativos en contrastes y roles ARIA que no estaban en el estimado inicial.
- El despliegue (HU-21) fue más fluido gracias a la guía `TUTORIAL_DESPLIEGUE_WEB.md` preparada con anticipación.
- Las pruebas UAT (HU-19) fueron la historia con más variabilidad: coordinar participantes sordos requirió más tiempo de agenda.

---

## Velocidad del Equipo

| Sprint | SP Planificados | SP Entregados | Velocidad |
|--------|----------------|---------------|-----------|
| Sprint 1 | 36 | 36 | 36 SP |
| Sprint 2 | 57 | 57 | 57 SP |
| Sprint 3 | 24 | 24 | 24 SP |
| **Promedio** | — | — | **39 SP/sprint** |

> La velocidad aumentó considerablemente del Sprint 1 al Sprint 2 porque el equipo ya tenía
> el entorno configurado, las abstracciones base (`lsp_core.py`) y el flujo de trabajo Git establecido.
> El Sprint 3 tuvo menor carga porque el enfoque fue en calidad y validación, no en nuevas funcionalidades.

---

*Documento generado para el Capstone Project · UPN Sistemas 2026*
*Herramienta de gestión: GitHub Projects (tablero Kanban por Sprint)*
