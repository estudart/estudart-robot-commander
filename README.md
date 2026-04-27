# RobotCommander (Raspberry Pi)

Small Python controller intended to run **only on a Raspberry Pi** connected to a robot.

This repo follows the same structure/pattern as `DroneCommander`, but targets a ground robot.

## What it does (today)

- Runs a `RobotRoutine` loop
- Listens to Redis pub/sub events (channel: `robot_command`)
- When a command is received (e.g. `patrol`), runs a routine against a `RobotAdapter`

## Requirements

- Python 3.10+
- A Redis instance reachable from the Pi (default: `localhost:6379`)

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run

From the repo root:

```bash
python -m src.main
```

Or run just the routine app:

```bash
python -m src.robot_routine_app
```

## Send a test command

From another shell on the same machine (or any machine that can reach Redis):

```bash
python -c "import redis; redis.Redis(decode_responses=True).publish('robot_command','patrol')"
```

