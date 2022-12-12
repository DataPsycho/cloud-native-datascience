FROM python:3.9-slim

ENV WORK_DIR=InternalBusiness
COPY ./clientside $WORK_DIR

# THis is for poc purpose do not do that in production, use aws secret manager and env variable instead
COPY ./.env $WORK_DIR

WORKDIR $WORK_DIR

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


EXPOSE 8080

ENTRYPOINT [ "streamlit", "run", "main.py"]