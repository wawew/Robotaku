FROM python:3.5.3
MAINTAINER Your Name "firdaus@alterra.id"
RUN mkdir -p /var/www/robotaku-backend
COPY . /var/www/robotaku-backend
RUN pip install -r /var/www/robotaku-backend/requirement.txt
ENV FLASK_ENV=FLASK_ENV_VALUE
ENV THIS_UNAME=THIS_UNAME_VALUE
ENV THIS_PWD=THIS_PWD_VALUE
ENV THIS_DB_TEST=THIS_DB_TEST_VALUE
ENV THIS_DB_DEV=THIS_DB_DEV_VALUE
ENV THIS_DB_ENDPOINT=THIS_DB_ENDPOINT_VALUE
WORKDIR /var/www/robotaku-backend
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
