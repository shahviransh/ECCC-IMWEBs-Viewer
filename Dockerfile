# Stage 1: Base Image with Conda and Python
FROM continuumio/miniconda3 AS base

# Set working directory
WORKDIR /app

# Install necessary Linux tools
RUN apt-get update && apt-get install -y binutils

# Copy Python project files
COPY backend /app/backend
COPY backend/requirements.txt /app/backend/requirements.txt

# Define a variable for the Conda environment path
ENV CONDA_ENV_PATH=/opt/conda

# Create a Conda environment named 'venv' and install dependencies
RUN $CONDA_ENV_PATH/bin/pip install --no-cache-dir -r /app/backend/requirements.txt && \
    conda install -c conda-forge gdal && \
    conda clean -afy

# Expose Conda environment PATH
ENV PATH=$CONDA_ENV_PATH/bin:$PATH

# Package Python backend using PyInstaller
RUN $CONDA_ENV_PATH/bin/pyinstaller /app/backend/apppy.py -y \
    --distpath /app/backend/ \
    --specpath /app/backend/ \
    --workpath /app/backend/build \
    --name apppy \
    --add-data "$CONDA_ENV_PATH/share/proj:share/proj"

# Stage 2: Node.js and Rust for Tauri
FROM node:20 AS tauri-builder

# Set working directory
WORKDIR /app

# Install necessary Linux tools
RUN apt-get update && apt-get install -y libwebkit2gtk-4.0-dev libwebkit2gtk-4.1-dev build-essential \
        libssl-dev libgtk-3-dev tree \
        libayatana-appindicator3-dev libgdk-pixbuf2.0-dev \
        librsvg2-dev libjavascriptcoregtk-4.1-dev libfuse2 libxau-dev libxau6
    
# Install Rust and Tauri CLI
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH=/root/.cargo/bin:$PATH

# Install Tauri CLI globally
RUN npm install -g @tauri-apps/cli

# Copy frontend and Tauri project files
COPY package.json package-lock.json index.html LICENSE README.md tailwind.config.js vite.config.js postcss.config.cjs .env /app/
COPY src /app/src
COPY public /app/public
COPY src-tauri /app/src-tauri

# Install Node.js dependencies and build frontend
RUN npm install && npm run build

# Stage 3: Compilation with Rust
FROM tauri-builder AS cross-builder

# Copy outputs from Stage 1 (base) and Stage 2 (tauri-builder)
COPY --from=base /app/backend /app/backend
COPY --from=tauri-builder /app /app

RUN dpkg -l | grep libxau

# Build Tauri for all targets
RUN npm run tauri build --verbose

# Stage 4: Artifact Collection
FROM debian:bullseye AS artifact-collector

# Set working directory
WORKDIR /artifacts

# Copy artifacts from previous stages
COPY --from=cross-builder /app/src-tauri/target/release/bundle /artifacts/
COPY --from=base /app/backend/apppy /artifacts/backend/apppy

CMD ["ls", "/artifacts"]