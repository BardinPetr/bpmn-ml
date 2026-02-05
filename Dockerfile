FROM rayproject/ray:latest-py312-cu129

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_NO_DEV=1

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

ENV PATH="/app/.venv/bin:$PATH"

ENV EASYOCR_MODULE_PATH="/easyocr"
RUN mkdir -p /easyocr/model
COPY ~/.EasyOCR/model/* /easyocr/model/

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

CMD "/app/start.sh"
