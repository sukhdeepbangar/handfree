# Claude Agent Loop - Usage Guide

Automated loop that runs Claude Code agent continuously with tasks from `prompt.md`.

## Quick Start

```bash
# Start the agent loop
./start_agent.sh

# View logs in real-time
tail -f agent_loop.log

# Stop the agent
./stop_agent.sh
```

## Scripts

### `start_agent.sh`
Starts the Claude agent in background using nohup.

```bash
./start_agent.sh
```

**What it does:**
1. Checks if an agent is already running
2. Starts the loop script in background with `nohup`
3. Saves the process PID to `agent_loop.pid`
4. Shows you the PID and how to monitor/stop it

**Output:**
- Prints the agent PID
- Shows commands to stop and monitor

### `stop_agent.sh`
Stops the running agent loop cleanly.

```bash
./stop_agent.sh
```

**What it does:**
1. Reads the PID from `agent_loop.pid`
2. Sends SIGTERM for graceful shutdown (triggers cleanup trap)
3. Waits 2 seconds for the process to exit
4. Uses SIGKILL if process doesn't respond
5. Removes the PID file
6. Verifies the process is terminated

### `run_agent_loop.sh`
The actual loop script (called by start_agent.sh). Runs Claude repeatedly with the prompt from `prompt.md`.

**Features:**
- Tracks the PID of each running Claude process
- Handles SIGINT and SIGTERM signals for proper cleanup
- Prevents orphaned processes when terminated
- Runs Claude with `--print` flag to exit after each task
- Logs all output with timestamps

### `cleanup_orphans.sh`
Interactive script to find and kill orphaned Claude processes from previous sessions.

```bash
./cleanup_orphans.sh
```

Use this if you notice Claude processes still running after stopping the agent.

## Monitoring

### View logs in real-time
```bash
tail -f agent_loop.log
```

### Check if the agent is running
```bash
# Check if PID file exists and process is alive
if [ -f agent_loop.pid ]; then
    kill -0 $(cat agent_loop.pid) 2>/dev/null && echo "Running" || echo "Stopped"
else
    echo "Not running"
fi
```

### View process details
```bash
ps -p $(cat agent_loop.pid)
```

### Check the current PID
```bash
cat agent_loop.pid
```

## Stopping the Agent

### Method 1: Using the stop script (recommended)
```bash
./stop_agent.sh
```

### Method 2: Manually kill the process
```bash
kill $(cat agent_loop.pid)
```

## How It Works

1. `start_agent.sh` uses `nohup` to run `run_agent_loop.sh` in the background
2. The main loop PID is saved to `agent_loop.pid`
3. The loop script reads `prompt.md` and starts a fresh Claude session with:
   - `--model opus` for better reasoning
   - `--print` for non-interactive mode (exits after completion)
   - `--dangerously-skip-permissions` to avoid interactive prompts
4. Each iteration is a completely new Claude Code session
5. After each completion, it waits 3 seconds and runs again
6. All output is logged to `agent_loop.log`
7. The loop continues until you stop it with `./stop_agent.sh`

**Note:** The `--print` flag makes Claude exit automatically after completing the task instead of waiting for user input.

## Customization

Edit `run_agent_loop.sh` to change:
- `PROMPT_FILE`: Source file for the agent prompt
- `LOG_FILE`: Where to save logs
- Sleep durations between iterations

## Troubleshooting

**Agent already running:**
```bash
./stop_agent.sh
./start_agent.sh
```

**Agent keeps failing:**
Check the logs:
```bash
tail -50 agent_loop.log
```

**Orphaned Claude processes:**
If Claude processes keep running after stopping the agent:
```bash
# Interactive cleanup
./cleanup_orphans.sh

# Or manually check
ps aux | grep claude | grep -v grep

# Kill specific PID
kill <PID>
```

**Stale PID file:**
If the PID file exists but the process isn't running:
```bash
rm agent_loop.pid
./start_agent.sh
```

**Prevention:** The scripts properly handle cleanup:
- `stop_agent.sh` sends SIGTERM to trigger the cleanup trap
- `run_agent_loop.sh` traps SIGINT/SIGTERM and kills child processes
- Each Claude process PID is tracked for proper termination
- No tmux means simpler, more reliable process management
