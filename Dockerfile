# Stage 1: Base image with Node.js, Rust, and Conda
FROM continuumio/miniconda3 AS base

# Set working directory
WORKDIR /app

# Install Rust for Tauri
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH=/root/.cargo/bin:$PATH

# Install Tauri CLI globally
RUN npm install -g @tauri-apps/cli

# Copy Conda environment and install dependencies
COPY backend/environment.yml /app/backend/environment.yml
RUN conda env create -f backend/environment.yml && \
    conda clean -afy && \
    echo "conda activate venv" > ~/.bashrc

# Install PyInstaller in the Conda environment
RUN conda run -n venv pip install pyinstaller

# Expose Conda environment PATH
ENV PATH /opt/conda/envs/venv/bin:$PATH

# Stage 2: Build Tauri frontend and backend executables
FROM base AS tauri-builder

# Set working directory
WORKDIR /app

# Copy Tauri and Python project files
COPY package.json package-lock.json /app/
COPY src /app/src
COPY public /app/public
COPY backend /app/backend
COPY src-tauri /app/src-tauri

# Install Node.js dependencies and build Tauri frontend
RUN npm install && npm run build

# Package Python backend using PyInstaller
RUN pyinstaller backend/apppy.py -y \
    --distpath backend/ \
    --specpath backend/ \
    --workpath backend/build \
    --name apppy \
    --add-data "/opt/conda/envs/venv/Library/share/proj:Library/share/proj"

# Stage 3: Build Tauri release for all platforms
FROM tauri-builder AS tauri-build-release

# Build Tauri release
RUN npm run tauri build

# Stage 4: Build cross-platform binaries (optional)
FROM debian:bullseye AS tauri-cross-builder

# Install cross-compilation tools
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Rust and cross-compilation targets
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y \
    && ~/.cargo/bin/rustup target add x86_64-pc-windows-gnu x86_64-apple-darwin

# Copy built artifacts
COPY --from=tauri-build-release /app/src-tauri/target/release/bundle /artifacts
COPY --from=tauri-builder /app/backend /artifacts/backend

# Define outputs
CMD ["ls", "/artifacts"]