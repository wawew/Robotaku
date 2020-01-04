#!/usr/bin/env bash

clear
export FLASK_ENV="development"
export THIS_UNAME="root" # ganti ke username mysql
export THIS_PWD="" # ganti ke password mysql
export THIS_DB_TEST="robotaku_test" # ganti ke nama database yang dipake untuk unit testing
export THIS_DB_DEV="robotaku" # ganti ke nama database yang dipake untuk development

mysql --user=$THIS_UNAME --password=$THIS_PWD -e "create database if not exists $THIS_DB_DEV; create database if not exists $THIS_DB_TEST"

export FLASK_ENV="testing"
pytest --cov-fail-under=96 --cov=blueprints --cov-report html -s tests/*
export FLASK_ENV="development"