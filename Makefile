# Makefile for Tauri and Electron builds

.PHONY: all prestart install build

# Default target
all: prestart install build

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