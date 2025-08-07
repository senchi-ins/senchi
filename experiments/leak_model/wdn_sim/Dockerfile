FROM python:3.11

# --- System deps ------------------------------------------------------------
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    libc6-dev \
    libgfortran5 \
    build-essential \
    libssl-dev \
    libffi-dev \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# --- Build EPANET shared library exactly as recommended by OpenWaterAnalytics -
WORKDIR /tmp/epanet-build
RUN git clone https://github.com/OpenWaterAnalytics/EPANET.git && \
    cd EPANET && \
    echo "=== Building EPANET shared library ===" && \
    mkdir build && cd build && \
    cmake .. && \
    cmake --build . --config Release && \
    echo "=== Build complete: listing artefacts ===" && \
    ls -la bin/ && ls -la lib/

# --- Install uv -------------------------------------------------------------
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin/:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# --- Python deps ------------------------------------------------------------
WORKDIR /app
COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Install dependencies declared in pyproject.toml (generates uv.lock if absent)
RUN uv sync --python "$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')"

# Make EPANET shared library available both system-wide (so ctypes can find it)
# and inside WNTR’s vendored path (used when it falls back to the bundled location).
RUN set -e && \
    LIB_SRC="/tmp/epanet-build/EPANET/build/lib/libepanet2.so" && \
    # 1) Install system-wide so ANY Python environment (including the runtime .venv
    #    that `uv` creates) can locate the library via the dynamic loader.
    cp "$LIB_SRC" /usr/local/lib/libepanet22.so && \
    ln -sf /usr/local/lib/libepanet22.so /usr/local/lib/libepanet.so && \
    ldconfig && \
    # 2) Also copy to the path hard-coded inside WNTR wheels, to cover that code path.
    SITE_PKGS=$(python -c "import site, json, sys; print(site.getsitepackages()[0])") && \
    mkdir -p "$SITE_PKGS/wntr/epanet/libepanet/linux-x64/" && \
    cp "$LIB_SRC" "$SITE_PKGS/wntr/epanet/libepanet/linux-x64/libepanet22.so" && \
    chmod +x /usr/local/lib/libepanet22.so "$SITE_PKGS/wntr/epanet/libepanet/linux-x64/libepanet22.so" && \
    echo "=== EPANET shared library installed system-wide and for WNTR ===" && \
    ls -la /usr/local/lib/libepanet22.so "$SITE_PKGS/wntr/epanet/libepanet/linux-x64/" && \
    rm -rf /tmp/epanet-build

# Prevent numpy / scipy from using multi-threaded BLAS inside containers
ENV PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1

# Default command: run a tiny smoke simulation (override in docker-compose)
ENV SIM_HOUSES=1 SIM_DAYS=1 SIM_LIGHT_MODE=true
CMD ["/app/entrypoint.sh"]