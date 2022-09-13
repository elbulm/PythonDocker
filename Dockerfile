FROM snakepacker/python:all as builder

RUN python3.8 -m venv /usr/share/python3/venv \
 && /usr/share/python3/venv/bin/pip install -U pip
COPY . /mnt/PythonDocker
RUN /usr/share/python3/venv/bin/pip install -r /mnt/PythonDocker/requirements.txt
COPY entrypoint /entrypoint
RUN chmod +x /entrypoint
ENTRYPOINT ["/entrypoint"]