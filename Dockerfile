# Security Extepts Community: ERM&CK Dockerfile
# Author: Anton Kutepov (@aw350m33)
# License: MIT

FROM python:3.11

LABEL maintainer="Anton Kutepov (@aw350m33)"
LABEL description="Dockerfile for ERM&CK project knowledge base"

WORKDIR /ermack
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY data/ data/
COPY assets/ assets/ 
COPY ermack/ ermack/
COPY config.yml config.yml
COPY main.py main.py
COPY README.md README.md
COPY *.md .
#COPY setup.py setup.py

#RUN pip3 install

CMD [ "/bin/bash", "-c", "python3 main.py mkdocs --init --all-entities --debug && cd build && python3 -m mkdocs serve -a 0.0.0.0:8000" ]
