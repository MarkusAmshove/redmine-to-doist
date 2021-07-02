FROM python

WORKDIR /opt/redmine-to-doist
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV TODOIST_API_KEY=

ENTRYPOINT ["python3"]
CMD ["/opt/redmine-to-doist/server.py"]

