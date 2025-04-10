FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Initialize the database
RUN mkdir -p instance
RUN flask --app app init-db

EXPOSE 5000

ENV FLASK_APP=app
ENV FLASK_ENV=production

CMD ["flask", "run", "--host=0.0.0.0"]