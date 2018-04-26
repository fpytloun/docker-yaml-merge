FROM python:3-alpine
RUN pip install PyYAML
COPY yaml-merge.py /usr/local/bin/yaml-merge
ENTRYPOINT ["/usr/local/bin/yaml-merge"]
