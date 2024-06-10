FROM python:3.10.7-slim-bullseye
RUN adduser --disabled-password --gecos '' epo_queue_cp
WORKDIR /home/epo_queue_cp
COPY REQUIREMENTS.txt ./
COPY main.py ./
COPY api.py ./
COPY monitoring.py ./
COPY process_data.py ./
COPY wd.py ./
COPY config config/
COPY handler handler/
COPY model model/
COPY templates templates/
RUN mkdir input
RUN mkdir output
RUN mkdir report
RUN mkdir output/errors
RUN mkdir report/errors
RUN apt-get update && apt-get install -y gcc wget
RUN apt-get install -y libmariadb-dev
RUN wget https://dlm.mariadb.com/2678574/Connectors/c/connector-c-3.3.3/mariadb-connector-c-3.3.3-debian-bullseye-amd64.tar.gz -O - | tar -zxf - --strip-components=1 -C /usr
RUN chown -R epo_queue_cp:epo_queue_cp ./
RUN pip3 install --no-cache-dir -r REQUIREMENTS.txt
USER epo_queue_cp
ENV PYTHONPATH "${PYTHONPATH}:/home/epo_queue_cp/"
ENV LD_LIBRARY_PATH=/usr/lib/mariadb
CMD ["python", "main.py"]