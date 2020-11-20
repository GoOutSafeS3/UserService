#!/bin/sh

case "$1" in
    "unittests-report")
        pytest --cov=users --cov-report term-missing --cov-report html --html=report.html
        ;;
    "unittests")
        pytest --cov=users
        ;;
    "setup")
        pip3 install -r requirements.txt
        pip3 install pytest pytest-cov
        pip3 install pytest-html
        ;;
    "docker-build")
        docker build . -t users
        ;;
    "docker")
        if [ -z "$2" ]
        then
            docker run -it -p 8081:8081 users
        else
            docker run -it -p 8081:8081 -e "CONFIG=$2" users
        fi
        ;;
    *)
        python3 users/app.py "$1"
        ;;
esac