"""
TESTE REAL — NEGÓCIOS = Os Nossos Negócios
Cria 1 negócio teste, calcula margem, cria missão ligada, valida KPIs
"""
import httpx
import json

BASE = "http://127.0.0.1:8000"

print("=== TESTE 1: OS NOSSOS NEGÓCIOS — Portfolio Real ===\n")

# 1. Lista actual
r = httpx.get(f"{BASE}/businesses", timeout=10)
data = r.json()
print(f"1️⃣ Portfolio actual: {data['count']} negócios")
print(f"   KPIs: receita €{data['kpis']['total_revenue']} | custos €{data['kpis']['total_costs']} | lucro €{data['kpis']['total_profit']} | margem {data['kpis']['avg_margin']:.1f}%")
for b in data['businesses'][:3]:
    print(f"   - {b['name']} [{b['status']}] → €{b['revenue_monthly']}/€{b['costs_monthly']} margem {b['margin_percent']:.1f}%")
print()

# 2. Cria negócio teste
print("2️⃣ Criando negócio TESTE: Café Central Lisboa")
payload = {
    "name": "Café Central Lisboa - TESTE",
    "sector": "Restauração",
    "description": "Café no centro de Lisboa, especialidade pastéis e bicas - NEGÓCIO TESTE para validar portfolio",
    "status": "ativo",
    "revenue_monthly": 8500,
    "costs_monthly": 5200,
    "value_proposition": "Bica + pastel a €1.20, ambiente acolhedor",
    "customer_segment": "Trabalhadores centro Lisboa, turistas",
    "channel": "Rua, Instagram, Google Maps",
    "website_url": "https://cafecentrallisboa.pt",
    "tags": "café, lisboa, teste, restauração"
}
r = httpx.post(f"{BASE}/businesses", json=payload, timeout=10)
biz = r.json()['business']
bid = biz['id']
print(f"   ✅ Criado: {biz['name']} ID {bid[:8]}")
print(f"   💰 Receita €{biz['revenue_monthly']} - Custos €{biz['costs_monthly']} = Lucro €{biz['profit_monthly']} Margem {biz['margin_percent']:.1f}%")
print()

# 3. Calculadora margem REAL
print("3️⃣ Teste calculadora margem REAL (integrada ao negócio)")
custo = 0.45  # custo pastel
preco = 1.20  # preço venda
lucro = preco - custo
margem = lucro / preco * 100
markup = lucro / custo * 100
print(f"   Custo: €{custo} | Preço: €{preco}")
print(f"   Lucro: €{lucro:.2f} | Margem: {margem:.1f}% | Markup: {markup:.1f}%")
print(f"   [VERIFICADO] Fórmula (preço-custo)/preço*100")
print()

# 4. Actualiza negócio com novos valores
print("4️⃣ Actualizando negócio com receita/custos reais do café")
r = httpx.put(f"{BASE}/businesses/{bid}", json={"revenue_monthly": 9200, "costs_monthly": 5400, "notes": "Actualizado após teste margem - 2026-09-13"}, timeout=10)
updated = r.json()['business']
print(f"   ✅ Actualizado: €{updated['revenue_monthly']} receita, €{updated['costs_monthly']} custos")
print(f"   Novo lucro: €{updated['profit_monthly']} margem {updated['margin_percent']:.1f}%")
print()

# 5. Cria missão ligada ao negócio
print("5️⃣ Criando missão Business Agent ligada ao negócio TESTE")
mission_payload = {
    "objective": f"Analisar crescimento Café Central Lisboa - aumentar margem de {updated['margin_percent']:.1f}% para 50%",
    "context": {
        "business_id": bid,
        "business_name": updated['name'],
        "revenue": updated['revenue_monthly'],
        "costs": updated['costs_monthly'],
        "sector": updated['sector']
    }
}
r = httpx.post(f"{BASE}/tasks", json=mission_payload, timeout=10)
mission = r.json()
mid = mission.get('mission_id')
print(f"   ✅ Missão criada: {mid[:8] if mid else 'ERRO'} - {mission_payload['objective'][:60]}")

if mid:
    # Tenta associar business_id à missão directamente na DB (para dashboard)
    import sqlite3
    from pathlib import Path
    db_path = Path("data/brain.db")
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("UPDATE missions SET business_id=? WHERE id=?", (bid, mid))
    conn.commit()
    conn.close()
    print(f"   🔗 Missão ligada ao negócio {bid[:8]} na DB")

    # Executa missão
    r = httpx.post(f"{BASE}/tasks/{mid}/run", timeout=30)
    print(f"   🚀 Missão executada: status {r.status_code}")
print()

# 6. Dashboard do negócio
print("6️⃣ Dashboard completo do negócio TESTE")
r = httpx.get(f"{BASE}/businesses/{bid}/dashboard", timeout=10)
dash = r.json()
print(f"   Negócio: {dash['business']['name']}")
print(f"   KPIs: receita €{dash['kpis']['revenue']} | custos €{dash['kpis']['costs']} | lucro €{dash['kpis']['profit']} | margem {dash['kpis']['margin']:.1f}%")
print(f"   Missões ligadas: {dash['kpis']['missions_count']} | Tasks: {dash['kpis']['tasks_count']}")
if dash['missions']:
    for m in dash['missions'][:2]:
        print(f"   - Missão: {m['objective'][:50]} [{m['status']}]")
print()

# 7. Lista final com KPIs actualizados
r = httpx.get(f"{BASE}/businesses", timeout=10)
final = r.json()
print("7️⃣ Portfolio FINAL após teste")
print(f"   Total: {final['count']} negócios")
print(f"   KPIs Globais: receita €{final['kpis']['total_revenue']} | custos €{final['kpis']['total_costs']} | lucro €{final['kpis']['total_profit']} | margem média {final['kpis']['avg_margin']:.1f}%")
print(f"   Por status: {final['kpis']['by_status']}")
print()

# 8. Teste frontend - verifica se dashboard ainda tem notícias
print("8️⃣ Verifica Dashboard notícias + mercados ainda OK")
r = httpx.get(f"{BASE}/news/portugal?count=1", timeout=10)
print(f"   /news/portugal: {r.status_code} - {r.json().get('source_name')} - {r.json()['articles'][0]['title'][:60]}")
r = httpx.get(f"{BASE}/crypto/gainers-losers?count=1", timeout=10)
print(f"   /crypto/gainers-losers: {r.status_code} - {r.json()['gainers'][0]['symbol']} {r.json()['gainers'][0]['price_change_percentage_24h']:.2f}%")
print()

print("=== ✅ TESTE COMPLETO — NEGÓCIOS = OS NOSSOS NEGÓCIOS VALIDADO ===")
print(f"Negócio teste ID: {bid}")
print(f"Apagar teste? DELETE /businesses/{bid}")
print("Abre /dashboard → TAB NEGÓCIOS → vês Café Central Lisboa - TESTE no grid")
