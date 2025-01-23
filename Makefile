# Makefile for Tauri and Electron builds

.PHONY: all prestart install build run python clean

# Default target
all: prestart install python

# Prestart script
prestart:
	@echo "Running prestart script..."
	npm run prestart

# Install dependencies
install:
	@echo "Installing dependencies..."
	npm install

pipreq:
	@echo "Freezing Python dependencies..."
	@powershell -Command "conda activate venv; pip freeze | ForEach-Object { ($$_ -split '==')[0] } | Set-Content backend/requirements.txt; conda deactivate"

python:
	@echo "Building Python backend..."
	@call conda activate venv && \
	pyinstaller backend/apppy.py -y --distpath backend/ --specpath backend/ --workpath backend/build --name apppy \
	--add-data "C:/Users/viran/miniconda3/envs/venv/Library/share/proj;Library/share/proj" && \
	conda deactivate
	xcopy backend\Jenette_Creek_Watershed backend\apppy\_internal\Jenette_Creek_Watershed /E /I

# Build Electron or Tauri based on argument
build:
ifeq ($(ARG), tauri)
	@echo "Building Tauri app..."
	npm run tauri:build
	xcopy src-tauri\target\release "$(USERPROFILE)\OneDrive - McMaster University\Co-op 1st Work Term - ECCC\release" /Y /E /I /D
else ifeq ($(ARG), electron)
	@echo "Building Electron app..."
	npm run electron:build
	xcopy dist "$(USERPROFILE)\OneDrive - McMaster University\Co-op 1st Work Term - ECCC\dist" /Y /E /I /D
else
	@echo "Please specify a valid BUILD option (tauri or electron)."
	@exit 1
endif

# Run Electron or Tauri in development mode
run:
ifeq ($(ARG), tauri)
	@echo "Running Tauri app in development mode..."
	npm run tauri dev
else ifeq ($(ARG), electron)
	@echo "Running Electron app in development mode..."
	npm run electron
else
	@echo "Please specify a valid RUN option (tauri or electron)."
	@exit 1
endif

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist/ node_modules/ src-tauri/target/ backend/apppy/ backend/build/