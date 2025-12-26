FROM tomkat/usadd-base:latest

ENV TZ=Europe/Kiev

WORKDIR /app

COPY static/    /app/static/
COPY modules/   /app/modules/
COPY templates/ /app/templates/
COPY *.py /app/


CMD [ "python3", "main.py" ]