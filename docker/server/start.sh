#!/bin/bash

set -e

rm -rf /tmp/users_added

DB_HOST=${DB_HOST:-localhost}
ADB_PORT=${ADB_PORT:-55555}
DB_USER=${DB_USER:-admin}
DB_PASS=${DB_PASS:-admin}

echo "Starting server, setting config to $DB_HOST on $ADB_PORT"
cd /aperturedb

aperturedb -cfg config.json &
pid=$!

echo adb config create default --host $DB_HOST --port $ADB_PORT --username $DB_USER --password "$DB_PASS" --no-interactive
adb config create default --overwrite --host $DB_HOST --port $ADB_PORT --username $DB_USER --password "$DB_PASS" --no-interactive

RES=1
export LOG_CONOSLE_LEVEL=50
set +e
while (( $RES != 0 )); do
    sleep 1
    echo "*** Waiting on db.."
    adb utils execute summary 2>/dev/null >/dev/null
    RES=$?
    #RES=0
done

set -e

echo "*** db wait done"
cd /
bash add_users.sh
echo "Database Ready"
touch /tmp/users_added

wait
