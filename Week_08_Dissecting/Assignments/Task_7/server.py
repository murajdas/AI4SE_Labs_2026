import json
import sys


TOOL = {
    "name": "greet",
    "description": "Return a greeting for a person.",
    "inputSchema": {
        "type": "object",
        "properties": {"name": {"type": "string", "description": "Person to greet"}},
        "required": ["name"],
    },
}


def respond(message):
    request_id = message.get("id")
    method = message.get("method")
    params = message.get("params", {})

    if not isinstance(params, dict):
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32602, "message": "Invalid params"},
        }
        print(json.dumps(response), flush=True)
        return

    if method == "initialize":
        result = {
            "protocolVersion": params.get("protocolVersion", "2025-03-26"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "task7-local", "version": "1.0.0"},
        }
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": [TOOL]}
    elif method == "tools/call":
        arguments = params.get("arguments", {})
        name = arguments.get("name")
        if params.get("name") != TOOL["name"]:
            result = {
                "content": [{"type": "text", "text": "Unknown tool."}],
                "isError": True,
            }
        elif not isinstance(name, str) or not name.strip():
            result = {
                "content": [{"type": "text", "text": "A non-empty name is required."}],
                "isError": True,
            }
        else:
            result = {
                "content": [{"type": "text", "text": "Hello, " + name.strip() + "!"}],
                "isError": False,
            }
    elif method == "notifications/initialized":
        return
    else:
        if "id" not in message:
            return
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }
        print(json.dumps(response), flush=True)
        return

    if "id" in message:
        print(json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result}), flush=True)


for line in sys.stdin:
    try:
        message = json.loads(line)
    except json.JSONDecodeError:
        print(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error"},
                }
            ),
            flush=True,
        )
        continue
    if not isinstance(message, dict):
        print(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32600, "message": "Invalid request"},
                }
            ),
            flush=True,
        )
        continue
    respond(message)
