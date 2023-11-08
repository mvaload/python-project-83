FROM python:3.10
RUN pip install poetry
COPY . /app
WORKDIR /app
RUN poetry install --no-root --no-dev
RUN apt-get update && apt-get install -y postgresql postgresql-contrib
COPY pg_hba.conf /etc/postgresql/12/main/pg_hba.conf
USER root
EXPOSE 5050
CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:5050", "page_analyzer.app:app"]