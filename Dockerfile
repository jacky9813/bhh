FROM python:slim
RUN mkdir -p /srv/static
COPY static/* /srv/static/
COPY src/* /srv/
WORKDIR /srv
CMD ["python3", "main.py"]