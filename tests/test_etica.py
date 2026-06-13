"""
tests/test_etica.py — TDD: verificación de principios de IA Ética (HU-16, HU-20).

Cubre: equidad por clase, calibración de confianza, explicabilidad en la UI,
privacidad por diseño, transparencia sobre limitaciones del modelo y
funciones XAI (explicar_prediccion, nombres_landmarks, sesgos_conocidos).

Trazabilidad:
  HU-16 CA-16.1 — Explicabilidad del pipeline (diagrama y expander en lsp_ui)
  HU-16 CA-16.2 — Alternativas XAI del SVM (explicar_prediccion)
  HU-16 CA-16.2 — Nombres anatómicos de landmarks (nombres_landmarks)
  HU-16 CA-16.2 — Honestidad sobre sesgos (sesgos_conocidos)
  HU-20         — Privacidad: no biométricos en el log de auditoría
  IA_ETICA.md   — Criterios de equidad y sesgo documentados
"""
import inspect
import numpy as np
import pytest
import lsp_core
import lsp_audit
import lsp_ui


# ═══════════════════════════════════════════════════════════════════════════════
# EQUIDAD — Ninguna clase sistemáticamente discriminada
# ═══════════════════════════════════════════════════════════════════════════════

class TestEquidad:

    def test_todas_las_clases_tienen_recall_positivo(self, modelo):
        """
        Ninguna clase del modelo debe tener recall 0% con el dataset disponible.
        Un recall 0% en una clase indica un sesgo total hacia esa letra.
        """
        from sklearn.metrics import classification_report
        X, y = lsp_core.cargar_dataset(limite_por_letra=5)
        if len(X) == 0:
            pytest.skip("Dataset vacío — no se puede evaluar equidad por clase")
        y_pred = modelo.predict(X)
        report = classification_report(y, y_pred, output_dict=True, zero_division=0)
        clases_sin_recall = []
        for label in modelo.classes_:
            recall = report.get(str(label), {}).get("recall", 0)
            if recall == 0:
                clases_sin_recall.append(label)
        assert len(clases_sin_recall) == 0, \
            f"Clases con recall 0% (sesgo total): {clases_sin_recall}. " \
            f"Agrega más muestras o aplica augmentación para estas letras."

    def test_accuracy_global_supera_umbral_minimo(self, modelo):
        """HU-07 CA-07.2: accuracy global ≥ 85% garantiza equidad básica del modelo."""
        from sklearn.model_selection import train_test_split
        X, y = lsp_core.cargar_dataset(limite_por_letra=5)
        if len(X) < 10:
            pytest.skip("Insuficientes muestras para evaluar accuracy")
        _, X_test, _, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
        predicciones = modelo.predict(X_test)
        accuracy = np.mean(predicciones == y_test)
        assert accuracy >= 0.85, \
            f"Accuracy {accuracy:.1%} < 85% — el modelo puede tener sesgo sistemático"

    def test_no_hay_clase_dominante_absoluta(self, modelo):
        """El modelo no debe predecir siempre la misma letra (sesgo de dominancia)."""
        X, y = lsp_core.cargar_dataset(limite_por_letra=3)
        if len(X) == 0:
            pytest.skip("Dataset vacío")
        predicciones = modelo.predict(X)
        clases_predichas = set(predicciones)
        assert len(clases_predichas) > 1, \
            f"El modelo solo predice la clase '{list(clases_predichas)[0]}' — sesgo de dominancia"


# ═══════════════════════════════════════════════════════════════════════════════
# CALIBRACIÓN — La confianza es una probabilidad real
# ═══════════════════════════════════════════════════════════════════════════════

class TestCalibracion:

    def test_confianza_es_probabilidad_valida(self, modelo, landmarks_validos):
        """La confianza del modelo debe ser una probabilidad en [0, 100]."""
        _, confianza = lsp_core.predecir(modelo, landmarks_validos)
        assert 0.0 <= confianza <= 100.0, \
            f"Confianza {confianza} fuera del rango válido [0, 100]"

    def test_predict_proba_suma_uno(self, modelo, landmarks_validos):
        """Las probabilidades de Platt para todas las clases deben sumar 1."""
        vector = np.array(landmarks_validos).reshape(1, -1)
        probas = modelo.predict_proba(vector)[0]
        assert np.all(probas >= 0), "Alguna probabilidad es negativa"
        assert np.all(probas <= 1), "Alguna probabilidad supera 1"
        assert abs(sum(probas) - 1.0) < 1e-5, \
            f"Probabilidades no suman 1: suma={sum(probas):.6f}"

    def test_confianza_alta_para_prediccion_determinista(self, modelo, landmarks_validos):
        """Un vector válido de buena calidad debe producir confianza > umbral de alerta."""
        _, confianza = lsp_core.predecir(modelo, landmarks_validos)
        assert confianza >= 60.0, \
            f"Vector de imagen real devolvió confianza {confianza:.1f}% — debería superar el umbral de 60%"


# ═══════════════════════════════════════════════════════════════════════════════
# EXPLICABILIDAD — XAI visible en la interfaz de usuario
# ═══════════════════════════════════════════════════════════════════════════════

class TestExplicabilidad:

    def test_umbral_confianza_60_presente_en_render_resultado(self):
        """HU-16 CA-16.1: el umbral del 60% debe estar en el código de render_resultado."""
        fuente = inspect.getsource(lsp_ui.render_resultado)
        assert "60" in fuente, \
            "El umbral de confianza del 60% debe aparecer en render_resultado para ser auditable"

    def test_pipeline_explicado_menciona_limitaciones(self):
        """HU-16 CA-16.2: la UI debe mencionar las limitaciones o sesgos del modelo."""
        fuente = inspect.getsource(lsp_ui.render_pipeline_explicado).lower()
        palabras_honestidad = ["sesgo", "limitacion", "limitación", "error", "equivocar"]
        assert any(p in fuente for p in palabras_honestidad), \
            "render_pipeline_explicado debe mencionar que el modelo puede equivocarse (honestidad)"

    def test_pipeline_explicado_menciona_mediapipe_y_svm(self):
        """HU-16 CA-16.1: la explicación debe nombrar las tecnologías reales del sistema."""
        fuente = inspect.getsource(lsp_ui.render_pipeline_explicado).lower()
        assert "mediapipe" in fuente, "La explicación debe mencionar MediaPipe"
        assert "svm" in fuente, "La explicación debe mencionar el clasificador SVM"

    def test_render_resultado_tiene_aria_live(self):
        """HU-15/HU-16: el resultado debe tener aria-live para screen readers."""
        fuente = inspect.getsource(lsp_ui.render_resultado)
        assert 'aria-live' in fuente, \
            "render_resultado debe tener aria-live para anunciar cambios a lectores de pantalla"

    def test_render_resultado_tiene_role_progressbar(self):
        """HU-15: la barra de confianza debe tener role='progressbar' para WCAG."""
        fuente = inspect.getsource(lsp_ui.render_resultado)
        assert 'progressbar' in fuente, \
            "La barra de confianza debe tener role='progressbar'"

    def test_modelo_solo_predice_letras_del_alfabeto(self, modelo, landmarks_validos):
        """El modelo nunca debe predecir clases fuera del alfabeto LSP (a–z)."""
        letra, _ = lsp_core.predecir(modelo, landmarks_validos)
        assert str(letra).lower() in lsp_core.LETTERS, \
            f"El modelo predijo '{letra}', que no es una letra del alfabeto LSP"


# ═══════════════════════════════════════════════════════════════════════════════
# XAI — Funciones de explicabilidad algorítmica (HU-16 CA-16.2)
# ═══════════════════════════════════════════════════════════════════════════════

class TestXAI:
    """HU-16 CA-16.2: verificar que las funciones XAI devuelven datos válidos y coherentes."""

    def test_explicar_prediccion_devuelve_estructura_correcta(self, modelo, landmarks_validos):
        """explicar_prediccion debe devolver dict con letra, confianza, alternativas y n_clases."""
        resultado = lsp_core.explicar_prediccion(modelo, landmarks_validos)
        assert isinstance(resultado, dict), "El resultado debe ser un dict"
        assert "letra" in resultado
        assert "confianza" in resultado
        assert "alternativas" in resultado
        assert "n_clases" in resultado

    def test_explicar_prediccion_letra_valida(self, modelo, landmarks_validos):
        """La letra principal predicha debe pertenecer al alfabeto LSP."""
        resultado = lsp_core.explicar_prediccion(modelo, landmarks_validos)
        assert str(resultado["letra"]).lower() in lsp_core.LETTERS, \
            f"La letra '{resultado['letra']}' no es del alfabeto LSP"

    def test_explicar_prediccion_confianza_valida(self, modelo, landmarks_validos):
        """La confianza principal debe estar en el rango [0, 100]."""
        resultado = lsp_core.explicar_prediccion(modelo, landmarks_validos)
        assert 0.0 <= resultado["confianza"] <= 100.0, \
            f"Confianza {resultado['confianza']} fuera del rango [0, 100]"

    def test_explicar_prediccion_coincide_con_predecir(self, modelo, landmarks_validos):
        """La letra y confianza de explicar_prediccion deben coincidir con predecir()."""
        letra_pred, conf_pred = lsp_core.predecir(modelo, landmarks_validos)
        xai = lsp_core.explicar_prediccion(modelo, landmarks_validos)
        assert xai["letra"] == letra_pred, \
            "La letra de explicar_prediccion no coincide con predecir()"
        assert abs(xai["confianza"] - conf_pred) < 0.2, \
            "La confianza de explicar_prediccion difiere de predecir() en más de 0.2%"

    def test_explicar_prediccion_alternativas_ordenadas(self, modelo, landmarks_validos):
        """Las alternativas deben estar ordenadas de mayor a menor confianza."""
        xai = lsp_core.explicar_prediccion(modelo, landmarks_validos, top_n=5)
        confianzas = [a["confianza"] for a in xai["alternativas"]]
        assert confianzas == sorted(confianzas, reverse=True), \
            "Las alternativas no están ordenadas de mayor a menor confianza"

    def test_explicar_prediccion_alternativas_suman_aprox_100(self, modelo, landmarks_validos):
        """La suma de todas las probabilidades del modelo debe ser ≈100%."""
        xai = lsp_core.explicar_prediccion(modelo, landmarks_validos, top_n=modelo.classes_.size)
        total = sum(a["confianza"] for a in xai["alternativas"])
        assert abs(total - 100.0) < 1.0, \
            f"La suma de probabilidades es {total:.2f}%, debería ser ≈100%"

    def test_explicar_prediccion_landmarks_invalidos_lanza_error(self, modelo):
        """explicar_prediccion debe lanzar ValueError con landmarks inválidos."""
        with pytest.raises(ValueError, match="42"):
            lsp_core.explicar_prediccion(modelo, [0.5] * 10)

    def test_nombres_landmarks_tiene_21_puntos(self):
        """nombres_landmarks debe devolver exactamente 21 entradas (0–20)."""
        nombres = lsp_core.nombres_landmarks()
        assert isinstance(nombres, dict), "nombres_landmarks debe devolver un dict"
        assert len(nombres) == lsp_core.NUM_LANDMARKS, \
            f"Se esperaban {lsp_core.NUM_LANDMARKS} landmarks, se obtuvieron {len(nombres)}"
        assert set(nombres.keys()) == set(range(lsp_core.NUM_LANDMARKS)), \
            "Las claves deben ser los índices 0–20"

    def test_nombres_landmarks_todos_son_strings(self):
        """Todos los nombres anatómicos deben ser cadenas no vacías."""
        for idx, nombre in lsp_core.nombres_landmarks().items():
            assert isinstance(nombre, str) and nombre.strip(), \
                f"El landmark {idx} tiene nombre inválido: {repr(nombre)}"

    def test_sesgos_conocidos_devuelve_dict_no_vacio(self):
        """sesgos_conocidos debe devolver un dict con al menos 3 entradas documentadas."""
        sesgos = lsp_core.sesgos_conocidos()
        assert isinstance(sesgos, dict), "sesgos_conocidos debe devolver un dict"
        assert len(sesgos) >= 3, \
            f"Se esperaban ≥3 sesgos documentados, se obtuvieron {len(sesgos)}"

    def test_sesgos_conocidos_menciona_diversidad_entrenamiento(self):
        """El sesgo de diversidad de entrenamiento debe estar documentado (IA Ética)."""
        sesgos = lsp_core.sesgos_conocidos()
        assert "diversidad_entrenamiento" in sesgos, \
            "Debe documentarse el sesgo de diversidad del dataset de entrenamiento"

    def test_sesgos_conocidos_menciona_letras_dinamicas(self):
        """El sesgo de letras dinámicas (J, Z) debe estar documentado."""
        sesgos = lsp_core.sesgos_conocidos()
        assert "letras_dinamicas" in sesgos, \
            "Debe documentarse que J y Z no están soportadas (sesgo por omisión)"

    def test_render_alternativas_no_falla_con_lista_vacia(self):
        """render_alternativas no debe lanzar excepción con lista vacía (sin mano)."""
        # No debe ejecutar ningún st.markdown si la lista está vacía
        import inspect
        fuente = inspect.getsource(lsp_ui.render_alternativas)
        assert "if not alternativas" in fuente, \
            "render_alternativas debe verificar la lista vacía antes de renderizar"

    def test_render_alternativas_menciona_xai_en_aria_label(self):
        """El panel XAI debe tener aria-label para accesibilidad (HU-15 + HU-16)."""
        import inspect
        fuente = inspect.getsource(lsp_ui.render_alternativas)
        assert "aria-label" in fuente, \
            "render_alternativas debe incluir aria-label para lectores de pantalla"


# ═══════════════════════════════════════════════════════════════════════════════
# PRIVACIDAD — Datos biométricos y personales
# ═══════════════════════════════════════════════════════════════════════════════

class TestPrivacidadEtica:

    def test_log_no_almacena_landmarks_biometricos(self, tmp_path, monkeypatch):
        """HU-20: el log de auditoría no debe contener vectores de landmarks (datos biométricos)."""
        import re
        monkeypatch.setattr(lsp_audit, "AUDIT_FILE", str(tmp_path / "audit.jsonl"))
        # Simular un evento con detalle que podría incluir coordenadas
        lsp_audit.registrar_acceso("TRADUCCION_INICIADA", "letra=A,conf=95.0")
        contenido = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
        # Detectar patrón de vector de landmarks: muchos floats seguidos
        patron_landmarks = re.compile(r"(\d+\.\d+[,\s]+){5,}")
        assert not patron_landmarks.search(contenido), \
            "El log no debe contener vectores de landmarks (datos biométricos)"

    def test_log_no_almacena_ip_ni_nombre(self, tmp_path, monkeypatch):
        """HU-20: ninguna entrada del log debe contener IP o nombre de usuario."""
        import re
        monkeypatch.setattr(lsp_audit, "AUDIT_FILE", str(tmp_path / "audit.jsonl"))
        lsp_audit.registrar_acceso("LOGIN_OK")
        contenido = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
        assert not re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", contenido), \
            "El log no debe contener IPs"
        assert "usuario" not in contenido.lower() and "nombre" not in contenido.lower(), \
            "El log no debe contener nombres de usuario"

    def test_predecir_no_persiste_datos(self, modelo, landmarks_validos, tmp_path):
        """La predicción no debe crear archivos de datos en disco."""
        import glob as _glob
        antes = set(_glob.glob("*.pkl") + _glob.glob("*.npy") + _glob.glob("*.csv"))
        lsp_core.predecir(modelo, landmarks_validos)
        despues = set(_glob.glob("*.pkl") + _glob.glob("*.npy") + _glob.glob("*.csv"))
        nuevos = despues - antes
        assert len(nuevos) == 0, f"predecir() creó archivos inesperados: {nuevos}"
