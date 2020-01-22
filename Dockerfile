FROM python:3.5.3
MAINTAINER Your Name "firdaus@alterra.id"
RUN mkdir -p /backend
COPY . /backend
RUN pip install -r /backend/requirement.txt
ENV FLASK_ENV="development"
ENV THIS_UNAME="root"
ENV THIS_PWD="wawew123"
ENV THIS_DB_TEST="robotaku_test"
ENV THIS_DB_DEV="robotaku"
ENV THIS_DB_ENDPOINT="robotaku-db.cbb8twxemu9y.ap-southeast-1.rds.amazonaws.com"
WORKDIR /backend
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
