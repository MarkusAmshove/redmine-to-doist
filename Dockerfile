FROM python

WORKDIR /opt/redmine-to-doist
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV TODOIST_API_KEY=

ENTRYPOINT ["gunicorn"]
CMD ["-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]

