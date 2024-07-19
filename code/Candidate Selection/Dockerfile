FROM python:3.12.2
WORKDIR /selection
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT [ "flask" ]
CMD ["--app", "candidate_selection", "run", "--host", "0.0.0.0", "--port", "8001"]