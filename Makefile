# Makefile — automatización de QA del Traductor LSP
# Estructura del proyecto:
#   src/       — código fuente Python (lsp_core, lsp_auth, lsp_audit, lsp_ui, lsp_video, app)
#   scripts/   — ejecutables (.bat) y scripts de entrenamiento/captura
#   tests/     — suite de pruebas pytest
#   qa/        — scripts de rendimiento y métricas
#
# Uso en Linux/Mac/Git-Bash:  make test | make coverage | make benchmark ...
# En Windows usa el menú: doble clic en scripts/QA.bat

PY ?= python

.PHONY: help test coverage coverage-all security sistema run \
        benchmark fps stress evaluate confusion crossval robustez recursos report \
        lint format quality all clean hooks

help:
	@echo "Objetivos disponibles:"
	@echo "  make test        - Pruebas unitarias e integracion (pytest)"
	@echo "  make coverage    - Cobertura de codigo (HTML en htmlcov/)"
	@echo "  make coverage-all- Cobertura de todos los modulos (umbral 80%)"
	@echo "  make security    - Solo pruebas de seguridad (DevSecOps)"
	@echo "  make sistema     - Solo pruebas de sistema (test_sistema.py)"
	@echo "  make run         - Inicia la app Streamlit localmente"
	@echo "  make benchmark   - Rendimiento por etapa"
	@echo "  make fps         - FPS sostenidos"
	@echo "  make stress      - Test de estres (100..5000)"
	@echo "  make evaluate    - Accuracy/Precision/Recall/F1"
	@echo "  make confusion   - Matriz de confusion (PNG)"
	@echo "  make crossval    - Validacion cruzada K-Fold"
	@echo "  make robustez    - Robustez ante condiciones adversas"
	@echo "  make recursos    - Consumo de RAM y CPU"
	@echo "  make report      - Reporte consolidado PDF + HTML"
	@echo "  make lint        - flake8"
	@echo "  make format      - black"
	@echo "  make quality     - pylint (score de calidad)"
	@echo "  make all         - Ejecuta todo y genera reportes"
	@echo "  make clean       - Elimina __pycache__, .pytest_cache, htmlcov, .coverage"
	@echo "  make hooks       - Instala git hooks en .git/hooks/ (ejecutar al clonar)"

test:
	$(PY) -m pytest tests/

security:
	$(PY) -m pytest tests/test_seguridad.py -v -m security

sistema:
	$(PY) -m pytest tests/test_sistema.py -v

run:
	$(PY) -m streamlit run src/app.py

coverage:
	$(PY) -m pytest tests/ --cov=lsp_core --cov-report=html --cov-report=term

coverage-all:
	$(PY) -m pytest tests/ \
	  --cov=lsp_core --cov=lsp_auth --cov=lsp_audit --cov=lsp_video --cov=lsp_ui \
	  --cov-report=html --cov-report=term --cov-fail-under=80

benchmark:
	$(PY) qa/benchmark.py
fps:
	$(PY) qa/fps_test.py
stress:
	$(PY) qa/stress_test.py
evaluate:
	$(PY) qa/evaluate.py
confusion:
	$(PY) qa/confusion_matrix.py
crossval:
	$(PY) qa/cross_validation.py
robustez:
	$(PY) qa/robustez.py
recursos:
	$(PY) qa/recursos.py
report:
	$(PY) qa/generar_reportes.py

lint:
	$(PY) -m flake8 --config config/setup.cfg src/ qa/ tests/
format:
	$(PY) -m black src/ qa/ tests/
quality:
	$(PY) -m pylint src/lsp_core.py src/lsp_auth.py src/lsp_audit.py qa/

all: test benchmark fps stress evaluate confusion crossval robustez recursos report
	@echo "QA COMPLETO. Revisa la carpeta reportes/"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
	rm -rf .pytest_cache htmlcov .coverage
	@echo "Artefactos temporales eliminados."

hooks:
	cp scripts/hooks/pre-commit .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	@echo "Hook pre-commit instalado. Cada commit escaneara secretos automaticamente."
