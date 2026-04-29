# RobotCommander (Raspberry Pi)

Robot control service intended to run **only on a Raspberry Pi** connected to a **Sunfounder PiCrawler AI** robot.

## What it does

- **API container (WebSocket)**: exposes `/v1/ws/publish` to receive commands over WebSocket.
- **Worker container**: runs a `RobotWorker` loop that reads robot state from Redis and triggers routines.
- **Robot adapter**: `RobotAdapter` is currently a stub implementation (logs actions only).

## Architecture and flow

```mermaid
flowchart LR
  client["WebSocket client"] -->|JSON message| wss["WSS API"]

  subgraph api["API container"]
    wss --> commander["RobotCommander (dispatch)"]
  end

  commander -->|SET robot:state| redis[("Redis")]

  camera["CameraThreatDetector"] -->|PUBLISH threat events| redis

  redis -->|GET robot:state (poll)| cmdThread["Worker thread: state poller"]
  redis -->|SUBSCRIBE: threat| alertThread["Worker thread: alert consumer"]

  subgraph worker["Worker container"]
    cmdThread --> workerSvc[RobotWorker]
    alertThread --> workerSvc
    workerSvc --> adapter["RobotAdapter (hardware abstraction)"]
  end
```

## Requirements

- Docker (recommended on the Raspberry Pi)
- If running locally (no Docker): a Redis instance reachable from the process (defaults to `localhost:6379`)

## Run with Docker (recommended)

```bash
make up
```

This uses `docker-compose.yaml` to build and run:

- `raspberry-pi-wss-server` (WebSocket API)
- `raspberry-pi-worker` (Robot worker loop)
- `redis` (local Redis used by both containers)

### Useful Make targets

```bash
make build        # Build images
make up           # Start all services (builds if needed)
make logs         # Follow logs
make down         # Stop services
make clean        # Remove services + volumes
```

## Run locally (no Docker)

```bash
python -m pip install -r requirements.txt
python -m src.main
```

## WebSocket API

- **Endpoint**: `ws://<host>:8000/v1/ws/publish`
- **Payload**: JSON text frames with an explicit `channel`:
  - `{"channel":"robot-command","command":"stop"}`
  - `{"channel":"threat","command":"knife"}`

Supported commands (current implementation):
- `knife` / `gun`: triggers the routine in the worker
- `stop`: triggers a stop in the worker (stub)

## Robot state (Redis)

The API writes the latest robot state to a Redis key:

- **Key**: `robot:state`
- **Value**: a JSON string, e.g.
  - `{"type":"movement","direction":"forward","steps":1,"speed":0.5,"ts":"2026-04-29T15:00:00.000000+00:00"}`

The worker polls `robot:state` and ignores stale commands based on the embedded `ts` (TTL window).

## Send test commands

### Option A: bundled test script

Install the client dependency:

```bash
python -m pip install websockets
```

Run the test publisher (publishes every 10 seconds by default):

```bash
python -m src.tests.websocket_publish_test --host 127.0.0.1 --port 8000 --mode command --commands "stop" --interval 10
```

Examples (explicit channels):

```bash
python -m src.tests.websocket_publish_test --mode command --command-channel robot-command --alert-channel threat --commands "stop"
python -m src.tests.websocket_publish_test --mode alert --command-channel robot-command --alert-channel threat --commands "knife,gun"
python -m src.tests.websocket_publish_test --mode movement --command-channel robot-command --alert-channel threat --commands "forward,left,right,stop"
```

### Option B: manual Redis publish (worker channel)

To bypass the API and trigger the worker directly, publish to Redis.
The worker listens on the `threat` channel by default:

```bash
python -c "import redis; redis.Redis(decode_responses=True).publish('threat','knife')"
```

