FROM python:3.10-slim-bullseye

RUN apt-get update && apt install -y curl gpg libgssapi-krb5-2

# install Microsoft ODBC Driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install .

RUN adduser --system --group --no-create-home app
RUN chown -R app:app /app
USER app

CMD "/bin/bash"



