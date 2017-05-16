#!/bin/bash

#######################################################
#### Creator : Sudarshan Angirash #####################
#### Basic tomcat start/stop script ###################
#######################################################

export BASE=/home/osiuser/apache-tomcat-7.0.73/bin
prog=apache-tomcat-7.0.73
DEV=192.168.32.156
QA=192.168.32.219

stat() {
    if [ `ps auxwwww|grep $prog|grep -v grep|wc -l` -gt 0 ]
    then
        echo Tomcat is running.
    else
        echo Tomcat is not running.
    fi
}

statCheck() {
    if [ $1 -gt 0 ]
    then
        echo Tomcat is running.
    else
        echo Tomcat is not running.
    fi
}

case "$1" in
DEV)
    $BASE/catalina.sh stop
    sleep 60s
    stat
    $BASE/catalina.sh start
    sleep 60s
    stat
;;
QA)
    ssh osiuser@$QA "$BASE/catalina.sh stop"
    sleep 60s
    statusCode=`ssh osiuser@$QA ps auxwwww|grep $prog|grep -v grep|wc -l`
    statCheck $statusCode
    ssh osiuser@$QA "$BASE/catalina.sh start"
    sleep 60s
    statusCode=ssh osiuser@$QA "ps auxwwww|grep $prog|grep -v grep|wc -l"
    statCheck $statusCode
;;
status)
stat
;;
*)
    echo "Usage: tomcat_automation.sh DEV|QA|status"
esac
