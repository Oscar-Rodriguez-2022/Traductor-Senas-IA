# Makefile — automatización de QA del Traductor LSP
# Uso en Linux/Mac/Git-Bash:  make test | make coverage | make benchmark ...
# En Windows usa el menú: doble clic en QA.bat

PY ?= python

.PHONY: help test coverage benchmark fps stress evaluate confusion crossval robustez recursos report lint format quality all

help:
	@echo "Objetivos disponibles:"
	@echo "  make test        - Pruebas unitarias e integracion (pytest)"
	@echo "  make coverage    - Cobertura de codigo (HTML en htmlcov/)"
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

test:
	$(PY) -m pytest tests/

coverage:
	$(PY) -m pytest tests/ --cov=lsp_core --cov-report=html --cov-report=term

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
	$(PY) -m flake8 lsp_core.py qa tests
format:
	$(PY) -m black lsp_core.py qa tests app.py
quality:
	$(PY) -m pylint lsp_core.py qa

all: test benchmark fps stress evaluate confusion crossval robustez recursos report
	@echo "QA COMPLETO. Revisa la carpeta reportes/"
