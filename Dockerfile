FROM python:3.10-slim


RUN apt -y update && apt -y install ffmpeg curl
RUN pip install poetry
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
RUN pip install torch

WORKDIR /app
COPY . /app
RUN python3 -m poetry config virtualenvs.create false
RUN python3 -m poetry install --without dev
RUN chmod +x ./entrypoint.sh

CMD [ "./entrypoint.sh" ]
