FROM python:3.12

# install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR=/usr/bin sh

WORKDIR /nowhere

COPY . .

# Install python dependencies
RUN bash -c '\
  uv venv --python 3.12 --seed \
  && source .venv/bin/activate \
  && uv pip install --no-cache-dir .'

RUN chown -R nobody:nogroup .
USER nobody:nogroup

ARG uvicorn_port="8000"
ENV UVICORN_PORT="${uvicorn_port}"

ENTRYPOINT ["/bin/sh", "-c", "exec /nowhere/.venv/bin/uvicorn main:app --host 0.0.0.0 --port ${UVICORN_PORT}"]
