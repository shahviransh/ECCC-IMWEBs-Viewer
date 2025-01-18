# Stage 1: Base Image with Conda and Python
FROM continuumio/miniconda3 AS base

# Set working directory
WORKDIR /app

# Install necessary Linux tools
RUN apt-get update && apt-get install -y binutils

# Copy Python project files
COPY backend /app/backend
COPY backend/requirements.txt /app/backend/requirements.txt

# Activate the Conda environment by modifying the PATH environment variable
ENV PATH=/opt/conda/bin:$PATH

# Pip install Python dependencies
RUN conda install -c conda-forge gdal sqlite pillow libpng=1.6.44 -y && \
    conda run -n base pip install --no-cache-dir -r /app/backend/requirements.txt && \
    conda clean -afy

# Package Python backend using PyInstaller
RUN conda run -n base pyinstaller --collect-all PIL \
     /app/backend/apppy.py -y \
    --distpath /app/backend/ \
    --specpath /app/backend/ \
    --workpath /app/backend/build \
    --name apppy \
    --add-data "/opt/conda/share/proj:share/proj"

# Stage 2: Node.js and Rust for Tauri
FROM node:20 AS tauri-builder

# Set working directory
WORKDIR /app

# Install necessary Linux tools
RUN apt-get update && apt-get install -y libwebkit2gtk-4.0-dev libwebkit2gtk-4.1-dev \
    build-essential libssl-dev libgtk-3-dev tree \
    curl wget file \
    libappindicator3-dev libgdk-pixbuf2.0-dev \
    librsvg2-dev libjavascriptcoregtk-4.1-dev libfuse2

# Install Rust and Tauri CLI
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH=/root/.cargo/bin:$PATH

# Install Tauri CLI globally
RUN npm install -g @tauri-apps/cli

# Copy frontend and Tauri project files
COPY . /app/

# Install Node.js dependencies
RUN npm install

# Stage 3: Compilation with Rust
FROM tauri-builder AS cross-builder

# Copy outputs from Stage 1 (base) and Stage 2 (tauri-builder)
COPY --from=base /app/backend /app/backend
COPY --from=tauri-builder /app /app
COPY --from=base /opt/conda /opt/conda

# # Build Tauri for all targets
# RUN npm run tauri build

# # Stage 4: Artifact Collection
# FROM debian:bullseye AS artifact-collector

# # Set working directory
# WORKDIR /artifacts

# # Copy artifacts from previous stages
# COPY --from=cross-builder /app/src-tauri/target/release/bundle /artifacts/
# COPY --from=base /app/backend/apppy /artifacts/backend/apppy

CMD ["CARGO_BUILD_JOBS=8", "npm", "run", "tauri", "build", "--", "--verbose"]