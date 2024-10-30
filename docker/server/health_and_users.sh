#!/bin/bash
#if [  -e /tmp/users_added -a /bin/true ]; then
if [  ! -e /tmp/users_added ]; then
    echo "No Users"
    exit 1
fi
adb utils execute status 2>/dev/null >/dev/null
RES=$?
if [[ $RES != 0 ]]; then
    echo "Can't connect to db"
    exit 1
fi

exit 0

