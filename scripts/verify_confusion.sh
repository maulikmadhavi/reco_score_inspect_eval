#!/usr/bin/env bash
cd /mnt/d/dev_repos/dev_ir_result_analysis
PY=.pixi/envs/default/bin/python3.14
$PY app.py --csv data/sample.csv --port 5055 >/tmp/srv.log 2>&1 &
SRV=$!
# wait for the server to accept connections (up to ~15s)
for i in $(seq 1 30); do
  if curl -s -o /dev/null http://127.0.0.1:5055/confusion; then break; fi
  sleep 0.5
done
echo "--- /confusion page (http code) ---"
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:5055/confusion
echo "--- /api/confusion ---"
curl -s http://127.0.0.1:5055/api/confusion
echo
echo "--- cell gt=cat pred=dog (first 250 chars) ---"
curl -s 'http://127.0.0.1:5055/api/confusion/cell?gt=cat&pred=dog' | head -c 250
echo
echo "--- cell gt=BG pred=cat (first 200 chars) ---"
curl -s 'http://127.0.0.1:5055/api/confusion/cell?gt=BG&pred=cat' | head -c 200
echo
echo "--- server log ---"
cat /tmp/srv.log
kill $SRV 2>/dev/null
