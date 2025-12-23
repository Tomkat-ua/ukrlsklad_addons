FROM tomkat/usadd-base:latest

ENV TZ=Europe/Kiev

WORKDIR /app
COPY modules/* /app/modules/
COPY templates/* /app/templates/
COPY *.py /app/
#COPY reports.json /app/

CMD [ "python3", "main.py" ]