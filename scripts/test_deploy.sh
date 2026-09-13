#!/bin/bash
# Testa deploy — passa URL como arg: ./scripts/test_deploy.sh http://localhost:8000
BASE=${1:-http://localhost:8000}
echo "🧪 Testando deploy em $BASE"
echo "================================"

test_endpoint() {
  local path=$1
  local name=$2
  echo -n "→ $name ($path)... "
  code=$(curl -s -o /tmp/resp.json -w "%{http_code}" "$BASE$path" --max-time 10)
  if [ "$code" = "200" ]; then
    echo "✅ $code"
    head -c 200 /tmp/resp.json | tr '\n' ' '
    echo ""
  else
    echo "❌ $code"
    cat /tmp/resp.json | head -c 500
    echo ""
  fi
}

test_endpoint "/" "Root"
test_endpoint "/health" "Health"
test_endpoint "/system/status" "System Status"
test_endpoint "/system/network" "Network 8 agentes + 21 tools"
test_endpoint "/businesses" "Negócios"
test_endpoint "/agents" "Agents"
test_endpoint "/dashboard/" "Dashboard HTML"
test_endpoint "/docs" "Swagger Docs"
test_endpoint "/system/workspace-list" "Workspace List"

echo ""
echo "🔍 Verificando contagens..."
curl -s "$BASE/system/network" | python3 -c "
import sys, json
try:
    d=json.load(sys.stdin)
    print(f\"Agentes: {d['agents']['count']} (esperado 8) {'✅' if d['agents']['count']==8 else '❌'}\")
    print(f\"Tools: {d['tools']['count']} (esperado 21) {'✅' if d['tools']['count']==21 else '❌'}\")
    print(f\"DB: {d['db']['size_mb']}MB • Missions: {d['kpis']['total_missions']}\")
    print(f\"External OK: {d['kpis']['external_ok']}/{d['kpis']['external_total']}\")
except Exception as e:
    print('Erro parse:', e)
    print(open('/tmp/resp.json').read()[:500])
"

echo ""
echo "✅ Teste completo — se tudo ✅, deploy OK para testar!"
echo "Abre: $BASE/dashboard/"
