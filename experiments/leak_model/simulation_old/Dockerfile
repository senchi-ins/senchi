FROM python:3.11

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

# Build EPANET using OWA's exact instructions
WORKDIR /tmp/epanet-build
RUN git clone https://github.com/OpenWaterAnalytics/EPANET.git && \
    cd EPANET && \
    echo "=== Following OWA build instructions ===" && \
    mkdir build && \
    cd build && \
    cmake .. && \
    cmake --build . --config Release && \
    echo "=== Build complete, checking output ===" && \
    ls -la bin/ && \
    ls -la lib/ && \
    echo "=== Found shared library ===" && \
    find . -name "libepanet2.so" -exec ls -la {} \;

# Install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin/:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

WORKDIR /app

# Copy the current directory (which is data/) to /app
COPY . .

# Install dependencies using the pyproject.toml in current directory
RUN uv sync --locked

# Copy the built library to where WNTR expects it (in the virtual environment)
RUN mkdir -p .venv/lib/python3.11/site-packages/wntr/epanet/libepanet/linux-x64/ && \
    cp /tmp/epanet-build/EPANET/build/lib/libepanet2.so .venv/lib/python3.11/site-packages/wntr/epanet/libepanet/linux-x64/libepanet22.so && \
    chmod +x .venv/lib/python3.11/site-packages/wntr/epanet/libepanet/linux-x64/libepanet22.so && \
    echo "=== WNTR library placed ===" && \
    ls -la .venv/lib/python3.11/site-packages/wntr/epanet/libepanet/linux-x64/ && \
    cd / && \
    rm -rf /tmp/epanet-build

ENV PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1

# Run the script that's now in the current directory
CMD ["uv", "run", "WDN_sim.py"]