Set-Location $PSScriptRoot
py -m uvicorn api.server:app --reload --host 127.0.0.1 --port 8000
