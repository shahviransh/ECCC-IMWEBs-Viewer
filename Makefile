# Makefile for Tauri and Electron builds

.PHONY: all prestart install build run-dev clean

# Default target
all: prestart install 

# Prestart script
prestart:
	@echo "Running prestart script..."
	npm run prestart

# Install dependencies
install:
	@echo "Installing dependencies..."
	npm install

# Build Electron or Tauri based on argument
build:
ifeq ($(BUILD), tauri)
	@echo "Building Tauri app..."
	npm run tauri:build
else ifeq ($(BUILD), electron)
	@echo "Building Electron app..."
	npm run electron:build
else
	@echo "Please specify a valid BUILD option (tauri or electron)."
	@exit 1
endif

# Run Electron or Tauri in development mode
run-dev:
ifeq ($(RUN), tauri)
	@echo "Running Tauri app in development mode..."
	npm run tauri
else ifeq ($(RUN), electron)
	@echo "Running Electron app in development mode..."
	npm run electron
else
	@echo "Please specify a valid RUN option (tauri or electron)."
	@exit 1
endif

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist/ node_modules/ src-tauri/target/