from flask import Flask, jsonify, render_template_string
import stats
from config import MANAGER_IDS

app = Flask(__name__)

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="kk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>juz40_career — Админ дашборд</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', Arial, sans-serif; background: #0f1117; color: #e2e8f0; min-height: 100vh; }

  header {
    background: linear-gradient(135deg, #1a1f2e 0%, #16213e 100%);
    border-bottom: 1px solid #2d3748;
    padding: 18px 32px;
    display: flex; align-items: center; gap: 14px;
  }
  header h1 { font-size: 1.5rem; font-weight: 700; color: #fff; }
  header span { font-size: 0.85rem; color: #718096; margin-left: auto; }
  .dot { width: 10px; height: 10px; background: #48bb78; border-radius: 50%; animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

  main { max-width: 1400px; margin: 0 auto; padding: 28px 24px; }

  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }
  .card {
    background: #1a1f2e; border: 1px solid #2d3748; border-radius: 12px;
    padding: 22px 20px; display: flex; flex-direction: column; gap: 8px;
    transition: transform .15s;
  }
  .card:hover { transform: translateY(-2px); }
  .card-icon { font-size: 1.8rem; }
  .card-label { font-size: 0.78rem; color: #718096; text-transform: uppercase; letter-spacing: .05em; }
  .card-value { font-size: 2.2rem; font-weight: 700; }
  .card.blue .card-value { color: #63b3ed; }
  .card.green .card-value { color: #68d391; }
  .card.red .card-value { color: #fc8181; }
  .card.yellow .card-value { color: #f6e05e; }

  .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 28px; }
  @media(max-width:900px){ .grid2{grid-template-columns:1fr;} }

  .panel {
    background: #1a1f2e; border: 1px solid #2d3748; border-radius: 12px; overflow: hidden;
  }
  .panel-header {
    padding: 16px 20px; border-bottom: 1px solid #2d3748;
    font-weight: 600; font-size: 0.95rem; color: #e2e8f0;
    display: flex; align-items: center; gap: 8px;
  }
  .panel-body { padding: 16px 20px; }

  table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
  th { padding: 10px 12px; text-align: left; color: #718096; font-weight: 600;
       font-size: 0.75rem; text-transform: uppercase; letter-spacing: .04em;
       border-bottom: 1px solid #2d3748; }
  td { padding: 10px 12px; border-bottom: 1px solid #1e2535; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #202536; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
  .badge-green { background: #1c4532; color: #68d391; }
  .badge-red { background: #4a1e1e; color: #fc8181; }
  .badge-blue { background: #1a365d; color: #63b3ed; }

  .bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
  .bar-label { font-size: 0.8rem; color: #cbd5e0; width: 160px; flex-shrink: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .bar-track { flex: 1; height: 8px; background: #2d3748; border-radius: 4px; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg,#4299e1,#63b3ed); transition: width .6s ease; }
  .bar-count { font-size: 0.8rem; color: #718096; width: 28px; text-align: right; }

  .full-panel { background: #1a1f2e; border: 1px solid #2d3748; border-radius: 12px; overflow: hidden; margin-bottom: 28px; }
  .requests-table td { font-size: 0.82rem; }
  .status-open { color: #f6e05e; }
  .status-done { color: #68d391; }
  .empty { color: #4a5568; font-size: 0.85rem; padding: 24px 0; text-align: center; }

  .refresh-btn {
    background: #2d3748; border: 1px solid #4a5568; color: #e2e8f0;
    padding: 6px 14px; border-radius: 8px; cursor: pointer; font-size: 0.82rem;
    margin-left: auto; transition: background .15s;
  }
  .refresh-btn:hover { background: #3d4a5c; }
  .last-updated { font-size: 0.75rem; color: #4a5568; margin-left: 10px; }
</style>
</head>
<body>
<header>
  <div class="dot"></div>
  <h1>🎓 juz40_career</h1>
  <div style="margin-left:auto;display:flex;align-items:center;gap:10px;">
    <span id="lastUpdated" class="last-updated"></span>
    <button class="refresh-btn" onclick="loadData()">🔄 Жаңарту</button>
  </div>
</header>

<main>
  <div class="cards" id="cards"></div>

  <div class="grid2">
    <div class="panel">
      <div class="panel-header">📂 Бөлімдер бойынша</div>
      <div class="panel-body" id="sectionBars"></div>
    </div>
    <div class="panel">
      <div class="panel-header">📚 Пәндер бойынша</div>
      <div class="panel-body" id="subjectBars"></div>
    </div>
  </div>

  <div class="grid2">
    <div class="panel">
      <div class="panel-header">🎓 Курс бойынша</div>
      <div class="panel-body" id="courseBars"></div>
    </div>
    <div class="panel">
      <div class="panel-header">👤 Менеджерлер нәтижесі</div>
      <div class="panel-body" id="managerTable"></div>
    </div>
  </div>

  <div class="full-panel">
    <div class="panel-header" style="display:flex;align-items:center;">
      📨 Барлық өтініштер журналы
      <span id="reqCount" style="margin-left:8px;font-size:0.78rem;color:#718096;"></span>
    </div>
    <div style="overflow-x:auto;">
      <table class="requests-table">
        <thead>
          <tr>
            <th>#</th><th>Уақыт</th><th>Аты-жөні</th><th>Курс</th>
            <th>Пән</th><th>ҰБТ</th><th>Өңір</th><th>Квота</th>
            <th>Байланыс</th><th>Менеджер</th><th>Мәртебе</th>
          </tr>
        </thead>
        <tbody id="requestsBody"></tbody>
      </table>
      <div id="emptyRequests" class="empty" style="display:none;">Өтініштер жоқ</div>
    </div>
  </div>
</main>

<script>
function makeBars(containerId, obj, maxVal) {
  const el = document.getElementById(containerId);
  if (!obj || Object.keys(obj).length === 0) {
    el.innerHTML = '<div class="empty">Деректер жоқ</div>';
    return;
  }
  const entries = Object.entries(obj).sort((a,b) => b[1]-a[1]);
  const max = maxVal || Math.max(...entries.map(e => typeof e[1]==='object' ? e[1].total||0 : e[1]));
  el.innerHTML = entries.map(([k, v]) => {
    const count = typeof v === 'object' ? v.total||0 : v;
    const pct = max > 0 ? Math.round(count/max*100) : 0;
    const label = k.includes('. ') ? k.split('. ').slice(1).join('. ') : k;
    return `<div class="bar-row">
      <div class="bar-label" title="${k}">${label}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
      <div class="bar-count">${count}</div>
    </div>`;
  }).join('');
}

async function loadData() {
  try {
    const res = await fetch('/api/stats');
    const d = await res.json();

    // Cards
    document.getElementById('cards').innerHTML = `
      <div class="card blue"><div class="card-icon">👥</div><div class="card-label">Жалпы запрос</div><div class="card-value">${d.total_users}</div></div>
      <div class="card yellow"><div class="card-icon">📨</div><div class="card-label">Менеджерге жіберілді</div><div class="card-value">${d.to_manager}</div></div>
      <div class="card green"><div class="card-icon">✅</div><div class="card-label">Шешілді</div><div class="card-value">${d.resolved}</div></div>
      <div class="card red"><div class="card-icon">❌</div><div class="card-label">Шешілмеді</div><div class="card-value">${d.unresolved}</div></div>
    `;

    makeBars('sectionBars', d.by_section);
    makeBars('subjectBars', d.by_subject);
    makeBars('courseBars', d.by_course);

    // Manager table
    const mgr = d.manager_stats;
    const mgrEl = document.getElementById('managerTable');
    if (!mgr || Object.keys(mgr).length === 0) {
      mgrEl.innerHTML = '<div class="empty">Деректер жоқ</div>';
    } else {
      let rows = '';
      for (const [name, dayStat] of Object.entries(mgr)) {
        let received=0, contacted=0, resolved=0;
        for (const v of Object.values(dayStat)) {
          received += v.received||0; contacted += v.contacted||0; resolved += v.resolved||0;
        }
        if (received === 0) continue;
        rows += `<tr>
          <td>${name}</td>
          <td><span class="badge badge-blue">${received}</span></td>
          <td><span class="badge badge-green">${resolved}</span></td>
        </tr>`;
      }
      mgrEl.innerHTML = rows ? `<table><thead><tr><th>Менеджер</th><th>Алды</th><th>Шешті</th></tr></thead><tbody>${rows}</tbody></table>`
                              : '<div class="empty">Деректер жоқ</div>';
    }

    // Requests log
    const logs = d.requests_log || [];
    document.getElementById('reqCount').textContent = `(${logs.length})`;
    const tbody = document.getElementById('requestsBody');
    const emptyDiv = document.getElementById('emptyRequests');
    if (logs.length === 0) {
      tbody.innerHTML = '';
      emptyDiv.style.display = 'block';
    } else {
      emptyDiv.style.display = 'none';
      tbody.innerHTML = [...logs].reverse().map(r => `<tr>
        <td style="color:#718096">${r.req_no||''}</td>
        <td style="color:#718096;white-space:nowrap">${r.time||''}</td>
        <td>${r.name||''}</td>
        <td><span class="badge badge-blue">${r.course||''}</span></td>
        <td>${r.subject||''}</td>
        <td>${r.ubt||''}</td>
        <td>${r.region||''}</td>
        <td>${r.quota||''}</td>
        <td>${r.contact||''}</td>
        <td>${r.manager||''}</td>
        <td><span class="${r.status==='open'?'status-open':'status-done'}">${r.status==='open'?'⏳ Ашық':'✅ Шешілді'}</span></td>
      </tr>`).join('');
    }

    document.getElementById('lastUpdated').textContent = 'Жаңартылды: ' + new Date().toLocaleTimeString('kk-KZ');
  } catch(e) {
    console.error(e);
  }
}

loadData();
setInterval(loadData, 15000);
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route("/api/stats")
def api_stats():
    return jsonify({
        "total_users": stats.data.get("total_users", 0),
        "to_manager": stats.data.get("to_manager", 0),
        "resolved": stats.data.get("resolved", 0),
        "unresolved": stats.data.get("unresolved", 0),
        "by_section": stats.data.get("by_section", {}),
        "by_subject": stats.data.get("by_subject", {}),
        "by_course": stats.data.get("by_course", {}),
        "manager_stats": stats.manager_stats,
        "requests_log": stats.requests_log,
    })

def run_dashboard(port=5000):
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
