# seqgpt-local-mcp

See https://www.anthropic.com/engineering/desktop-extensions

## Created (1 time) - You don't have to do this
```bash
npx @anthropic-ai/mcpb init
```

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
```

## Test

### Local Server
```bash
python test_server.py --local
```

### Remote Server
```bash
python test_server.py
```

## Pack
Install mcp as a package into `server/lib/` folder
```bash
python3 -m pip install -t server/lib "mcp>=1.0.0"
```

```bash
npx @anthropic-ai/mcpb pack
```