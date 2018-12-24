#!/bin/bash

# Text ################################################################################################################

read -d  SERVER_PROPERTIES <<-END
allow-flight=true
allow-nether=true
announce-player-achievements=true
difficulty=2
enable-command-block=false
enable-query=false
enable-rcon=false
force-gamemode=false
gamemode=0
generate-structures=true
generator-settings=
hardcore=false
level-name=world
level-seed=world-seed-1
level-type=BOP
max-build-height=256
max-players=4
online-mode=true
op-permission-level=4
player-idle-timeout=20
pvp=true
resource-pack=
server-ip=
server-port=25565
snooper-enabled=false
spawn-animals=true
spawn-monsters=true
spawn-npcs=true
spawn-protection=0
view-distance=12
white-list=false
END

read -d  USAGE <<-END
USAGE: $(basename $0)
END

# Helper Functions ####################################################################################################

function cancel {
    usage
    if [[ "$1" != "" ]]; then
        printf "\n\n$1\n"
    fi
    printf "Canceled.\n\n"
    exit 0
}

function find-running-server-pid {
    PORT=$(cat server/server.properties | grep server-port | cut -d= -f2)
    lsof -i -n 2>/dev/null | grep $PORT | grep LISTEN | awk '{print $2}'
}

function find-running-script-pid {
    ps -ef | grep "bash.*$(basename $0)" | grep -v grep | grep -v $$ | awk '{print $2}'
}

function require-ops {
    [[ -e ../ops.txt ]] || cancel "No ops.txt file was found."
}

function require-players {
    [[ -e ../players.txt ]] || cancel "No players.txt file was found."
}

function server-cmd {
    echo $* > server/server.stdin
}

function usage {
    printf "\n$USAGE\n\n"
}

# Command Functions ###################################################################################################

function command-installer {
    rm -rf installers/*.zip 2>/dev/null

    rm -rf installers/tmp
    mkdir -p installers/tmp

    REPO_DIR="$PWD"

    pushd installers/tmp
        git clone "$REPO_DIR" $SERVER_NAME
        rm -rf $SERVER_NAME/.git
        zip -r9 "../$SERVER_NAME-$(date +'%Y-%m-%d-%H-%M').zip" $SERVER_NAME
    popd >/dev/null

    rm -rf installers/tmp
}

function command-backup {
    mkdir -p "backups"
    echo "/save-all" >> "server/server.stdin"

    find . -name ".DS_Store" | xargs rm
    zip -r9 "backups/$SERVER_NAME-backup-$(date +'%Y-%m-%d-%H-%M').zip" server

    pushd "backups" &>/dev/null
    ls -t | awk 'NR>5' | while read FILE; do rm $FILE; done
    popd &>/dev/null
}

function command-delete {
    rm -rf "server"
}

function command-create {
    if [[ -d "server" ]]; then
        echo "Server $SERVER_NAME already exists. Skipping."
        return
    fi

    FORGE_INSTALLER_JAR=$(ls | grep "forge-.*-installer.jar" | tail -n1)
    if [[ ! -e "$FORGE_INSTALLER_JAR" ]]; then
        echo "$SERVER_NAME doesn't have a forge installer. Aborting..."
        return
    fi

    echo "Creating server for $SERVER_NAME..."
    mkdir -p "server"


    pushd "server" >/dev/null
    java -jar "../$FORGE_INSTALLER_JAR" --installServer

    rm -rf mods
    ln -s ../config .
    ln -s ../mods .
    ls -s ../scripts .
    echo "eula=true" > eula.txt

    mkdir logs
    mv *.log logs

    if [[ -e "../server.properties" ]]; then
        ln -s ../server.properties .
    else
        echo "$SERVER_PROPERTIES" > server.properties
    fi

    popd >/dev/null
}

function command-restart {
    command-stop
    sleep 2
    command-start
}

function command-start {
    require-ops
    require-players

    PID=$(find-running-script-pid)
    if [[ "$PID" != "" ]]; then
        exit 0
    fi

    PID=$(find-running-server-pid)
    if [[ "$PID" != "" ]]; then
        exit 0
    fi

    echo "[$(date)] No server running..."
    pushd "server" &>/dev/null

        mkdir -p logs

        echo "[$(date)] Starting server..."
        printf "Starting Minecraft Server with properties:\n\n$(cat server.properties)\n\n" >> logs/server.log

        rm "ops.json" &>/dev/null
        rm "whitelist.json" &>/dev/null

        rm server.stdin &>/dev/null
        touch server.stdin

        SERVER_JAR=$(ls forge*universal.jar | tail -n1)

        tail -n 0 -F server.stdin \
            | java -XX:+UseG1GC -Xmx6G -Xms6G \
                -Dsun.rmi.dgc.server.gcInterval=2147483646 \
                -XX:+UnlockExperimentalVMOptions \
                -XX:G1NewSizePercent=20 \
                -XX:G1ReservePercent=20 \
                -XX:MaxGCPauseMillis=50 \
                -XX:G1HeapRegionSize=32M \
                -jar $SERVER_JAR nogui $SERVER_NAME \
            >> logs/server.log 2>&1 &
        disown

        sleep 10

        cat ../../ops.txt | while read USER_NAME; do
            echo "/op $USER_NAME" >> server.stdin
            echo "/whitelist add $USER_NAME" >> server.stdin
        done

        cat ../../players.txt | while read USER_NAME; do
            echo "/whitelist add $USER_NAME" >> server.stdin
        done

        echo "/say Minecraft Server $SERVER_NAME is ready!" >> server.stdin

    popd &>/dev/null

    ATTEMPTS=0
    STOP="NO"
    while [[ "$STOP" == "NO" ]]; do
        PID=$(find-running-server-pid)
        [[ "$PID" != "" ]] && STOP="YES"

        if [[ $ATTEMPTS -gt 60 ]]; then
            echo "Failed to start server after 60 seconds"
            exit 1
        fi
        (( ATTEMPTS = ATTEMPTS + 1 ))
        sleep 1
    done


    PORT=$(cat "server/server.properties" | grep server-port | cut -d= -f2)
    echo "[$(date)] Server started on port $PORT after $ATTEMPTS seconds"
    echo "[$(date)] Input at: server/server.stdin"
    echo "[$(date)] Logs at: server/logs/server.log"
    echo ""
}

function command-status {
    PID=$(find-running-server-pid)
    if [[ "$PID" == "" ]]; then
        printf "[$(date)] No server is running for $SERVER_NAME\n\n"
    else
        PORT=$(cat "server/server.properties" | grep server-port | cut -d= -f2)
        printf "[$(date)] Server for $SERVER_NAME is runnning on port $PORT\n\n"
    fi
}

function command-stop {
    PID=$(find-running-server-pid)
    if [[ "$PID" == "" ]]; then
        printf "[$(date)] No server running.\n\n"
    else
        printf "[$(date)] Stopping server...\n"
        (( COUNT = DELAY ))
        echo "/say Server going down in $COUNT seconds..." >> "server/server.stdin"
        while [[ $COUNT -gt 0 ]]; do
            sleep 1
            (( COUNT = COUNT - 1 ))
            echo "/say $COUNT..." >> "server/server.stdin"
        done

        echo "/stop" >> "server/server.stdin"
        while [[ "$PID" != "" ]]; do
            PID=$(find-running-server-pid)
            if [[ "$PID" == "" ]]; then
                rm "server/server.stdin" &>/dev/null
                printf "[$(date)] Server stopped\n\n"
                return
            fi

            sleep 1
        done
    fi
}

# Script ##############################################################################################################

COMMAND="$1"; shift
DELAY=10
SERVER_NAME=$(basename $PWD)

case $COMMAND in
    -h)         usage;;
    backup)     command-backup;;
    client)     command-installer;;
    create)     command-create;;
    delete)     command-delete;;
    restart)    command-restart;;
    script-pid) find-running-script-pid;;
    server-pid) find-running-server-pid;;
    server-cmd) server-cmd;;
    start)      command-start;;
    status)     command-status;;
    stop)       command-stop;;
    *)          cancel "Unrecognized command: $COMMAND"
esac

