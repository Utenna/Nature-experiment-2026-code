# =============================================================================
# Code Ocean compute environment: R 4.4.x + Python 3 (single image).
# If you edit the environment through the Code Ocean UI instead, mirror these
# package lists in requirements.txt / install.R.
# =============================================================================
FROM rocker/r-ver:4.4.3

# Posit Package Manager snapshot -> reproducible CRAN resolution for the
# packages not explicitly version-pinned in install.R. Keep this date fixed.
ARG SNAPSHOT_DATE=2025-06-15
RUN echo "options(repos = c(CRAN = 'https://packagemanager.posit.co/cran/${SNAPSHOT_DATE}'))" \
      >> /usr/local/lib/R/etc/Rprofile.site

# ---- system libraries (igraph/qgraph/bnlearn/curl/xml) + python ------------
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-pip python3-venv \
      libglpk-dev libgmp-dev libxml2-dev libcurl4-openssl-dev libssl-dev \
      libblas-dev liblapack-dev gfortran \
      libfontconfig1-dev libfreetype6-dev libpng-dev libjpeg-dev libtiff5-dev \
      libharfbuzz-dev libfribidi-dev \
 && rm -rf /var/lib/apt/lists/*

# ---- Python ---------------------------------------------------------------
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

# ---- R ------------------------------------------------------------------
COPY install.R /tmp/install.R
# If you add renv.lock next to this Dockerfile, prefer:
#   COPY renv.lock /tmp/renv.lock
#   RUN Rscript -e "install.packages('renv'); renv::restore(lockfile='/tmp/renv.lock')"
RUN Rscript /tmp/install.R

WORKDIR /code
