FROM python:3.12.2
WORKDIR /selection
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "machine_learning.py"]