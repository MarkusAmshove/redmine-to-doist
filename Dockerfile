FROM python

WORKDIR /opt/redmine-to-doist
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV TODOIST_API_KEY=
ENV BASIC_AUTH_USERNAME=test
ENV BASIC_AUTH_PASSWORD=test

ENTRYPOINT ["gunicorn"]
CMD ["-w", "4", "--timeout", "120", "-b", "0.0.0.0:5000", "wsgi:app"]

