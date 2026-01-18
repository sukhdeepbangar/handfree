#!/bin/bash
# HandFree management script

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

case "$1" in
    start)
        echo "Starting HandFree..."
        source venv/bin/activate
        nohup python main.py > handfree.log 2>&1 &
        PID=$!
        echo $PID > handfree.pid
        echo "HandFree started with PID: $PID"
        ;;
    stop)
        if [ -f handfree.pid ]; then
            PID=$(cat handfree.pid)
            echo "Stopping HandFree (PID: $PID)..."
            kill $PID 2>/dev/null && echo "Stopped" || echo "Already stopped"
            rm handfree.pid
        else
            echo "No PID file found. Trying pkill..."
            pkill -f "python main.py"
        fi
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        if [ -f handfree.pid ]; then
            PID=$(cat handfree.pid)
            if ps -p $PID > /dev/null; then
                echo "HandFree is running (PID: $PID)"
            else
                echo "PID file exists but process is not running"
            fi
        else
            echo "HandFree is not running"
        fi
        ;;
    logs)
        tail -f handfree.log
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
