# Stage 1: Base Image with Conda and Python
FROM continuumio/miniconda3 AS base

# Set working directory
WORKDIR /app

# Copy Python project files
COPY backend /app/backend

# Install Conda dependencies
RUN conda env create -f backend/environment.yml && \
    conda clean -afy && \
    echo "conda activate venv" > ~/.bashrc

# Expose Conda environment PATH
ENV PATH=/opt/conda/envs/venv/bin:$PATH

# Package Python backend using PyInstaller
RUN pyinstaller /app/backend/apppy.py -y \
    --distpath /app/backend/ \
    --specpath /app/backend/ \
    --workpath /app/backend/build \
    --name apppy \
    --add-data "/opt/conda/envs/venv/Library/share/proj:Library/share/proj"

# Stage 2: Node.js and Rust for Tauri
FROM node:20 AS tauri-builder

# Set working directory
WORKDIR /app

# Install Rust and Tauri CLI
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    ~/.cargo/bin/rustup target add x86_64-unknown-linux-gnu x86_64-pc-windows-msvc aarch64-apple-darwin
ENV PATH=/root/.cargo/bin:$PATH

# Install Tauri CLI globally
RUN npm install -g @tauri-apps/cli

# Copy frontend and Tauri project files
COPY package.json package-lock.json /app/
COPY src /app/src
COPY public /app/public
COPY src-tauri /app/src-tauri

# Install Node.js dependencies and build frontend
RUN npm install && npm run build

# Stage 3: Cross-Compilation with Rust
FROM tauri-builder AS cross-builder

# Build Tauri for all targets
RUN npm run tauri build -- \
    --target x86_64-unknown-linux-gnu \
    --target x86_64-pc-windows-msvc \
    --target aarch64-apple-darwin

# Stage 4: Artifact Collection
FROM debian:bullseye AS artifact-collector

# Set working directory
WORKDIR /artifacts

# Copy Python and Tauri outputs
COPY --from=base /app/backend/apppy /artifacts/backend/apppy
COPY --from=cross-builder /app/src-tauri/target/release/bundle /artifacts/

CMD ["ls", "/artifacts"]