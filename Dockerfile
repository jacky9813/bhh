FROM python:slim
COPY src /srv
WORKDIR /srv
CMD ["python3", "main.py"]