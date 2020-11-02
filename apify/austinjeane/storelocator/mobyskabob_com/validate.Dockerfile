FROM python:3.7
COPY . /app
WORKDIR /app
RUN pip install sgvalidator
CMD ["python", "validate.py", "apify_docker_storage"]