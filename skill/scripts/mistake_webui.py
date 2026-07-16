#!/usr/bin/env python3
"""
Mistake Collection Web UI — interactive management console.

Start with:
    python mistake_webui.py --collection COLLECTION.json --port 5000

Then open http://localhost:5000 in a browser. The page lets you:
- Add mistakes via a form (text description)
- Import mistakes via file upload (CSV/JSON/Markdown)
- Delete mistakes one by one
- Regenerate the analysis report

The underlying CRUD is delegated to mistake_manager.py.
"""

import json, io, sys, csv, re, os, traceback
from pathlib import Path
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory

# ── Path setup ──────────────────────────────────────────────────────────────

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))
from mistake_manager import (
    load_collection, save_collection, add_mistake, delete_mistake,
    edit_mistake, import_csv, import_json, import_markdown, compute_statistics,
    MISTAKE_SCHEMA, ERROR_TYPES,
)
from report_generator import generate_html, generate_markdown

app = Flask(__name__)
COLLECTION_PATH: Path = None
OUTPUT_DIR: Path = None

# ── Page template ───────────────────────────────────────────────────────────

MANAGEMENT_HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>错题集管理</title>
<style>
  :root {
    --primary: #2C3E50; --accent: #3498DB; --success: #27AE60;
    --warning: #F39C12; --danger: #E74C3C; --bg: #FAFAFA;
    --card: #FFFFFF; --text: #2C3E50; --text2: #7F8C8D; --border: #ECF0F1;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; background: var(--bg); color: var(--text); line-height: 1.7; }
  .header { background: linear-gradient(135deg, #2C3E50, #34495E); color:#fff; padding:32px 40px; display:flex; justify-content:space-between; align-items:center; }
  .header h1 { font-size:24px; font-weight:600; }
  .header .actions { display:flex; gap:10px; }
  .container { max-width:1000px; margin:0 auto; padding:32px 24px; }
  .card { background:var(--card); border:1px solid var(--border); border-radius:8px; padding:24px; margin-bottom:20px; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
  .card h2 { font-size:18px; font-weight:600; color:var(--primary); margin-bottom:16px; padding-bottom:10px; border-bottom:2px solid var(--accent); }
  .btn { display:inline-block; padding:8px 18px; border-radius:5px; font-size:13px; font-weight:600; cursor:pointer; border:none; transition:0.15s; }
  .btn-primary { background:var(--accent); color:#fff; }
  .btn-primary:hover { background:#2980B9; }
  .btn-danger { background:var(--danger); color:#fff; }
  .btn-danger:hover { background:#C0392B; }
  .btn-success { background:var(--success); color:#fff; }
  .btn-outline { background:transparent; border:1px solid var(--border); color:var(--text); }
  .btn-outline:hover { background:var(--bg); }
  .btn-sm { padding:3px 10px; font-size:11px; }

  .form-group { margin-bottom:14px; }
  .form-group label { display:block; font-size:13px; font-weight:600; color:var(--text); margin-bottom:4px; }
  .form-group input, .form-group textarea, .form-group select { width:100%; padding:8px 10px; border:1px solid var(--border); border-radius:4px; font-size:13px; font-family:inherit; }
  .form-group textarea { min-height:60px; resize:vertical; }
  .form-row { display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; }
  .form-inline { display:flex; gap:8px; align-items:center; }

  .stats-row { display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:12px; margin-bottom:16px; }
  .stat-item { text-align:center; padding:14px 10px; background:var(--bg); border-radius:6px; }
  .stat-value { font-size:24px; font-weight:700; color:var(--accent); }
  .stat-label { font-size:12px; color:var(--text2); margin-top:2px; }

  .mistake-table { width:100%; border-collapse:collapse; font-size:13px; }
  .mistake-table th { text-align:left; padding:8px 10px; border-bottom:2px solid var(--border); background:#F8F9FA; font-weight:600; }
  .mistake-table td { padding:8px 10px; border-bottom:1px solid var(--border); }
  .mistake-table tr:hover { background:#F5F9FC; }
  .mistake-table .q-cell { max-width:280px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .tag { display:inline-block; font-size:10px; padding:1px 6px; border-radius:3px; margin:1px 2px; }
  .tag-concept { background:#FADBD8; color:#C0392B; }
  .tag-calc { background:#D5F5E3; color:#1E8449; }
  .tag-method { background:#E8DAEF; color:#6C3483; }
  .tag-gap { background:#FCF3CF; color:#B7950B; }
  .tag-read { background:#D6EAF8; color:#2471A3; }
  .tag-diff-easy { background:#D5F5E3; color:#1E8449; }
  .tag-diff-medium { background:#FDEBD0; color:#E67E22; }
  .tag-diff-hard { background:#FADBD8; color:#C0392B; }

  .toast { position:fixed; bottom:30px; right:30px; padding:12px 20px; border-radius:6px; color:#fff; font-size:14px; z-index:999; opacity:0; transition:opacity 0.3s; pointer-events:none; }
  .toast.show { opacity:1; }
  .toast-ok { background:var(--success); }
  .toast-err { background:var(--danger); }

  .modal-overlay { display:none; position:fixed; inset:0; background:rgba(0,0,0,0.4); z-index:998; align-items:center; justify-content:center; }
  .modal-overlay.active { display:flex; }
  .modal-box { background:var(--card); border-radius:8px; max-width:560px; width:90%; max-height:80vh; overflow-y:auto; padding:24px; }
  .file-drop { border:2px dashed var(--border); border-radius:8px; padding:28px; text-align:center; color:var(--text2); transition:0.2s; cursor:pointer; }
  .file-drop:hover, .file-drop.drag-over { border-color:var(--accent); background:#EBF5FB; }
  .file-drop input[type=file] { display:none; }
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>错题集管理</h1>
    <div style="font-size:13px;opacity:0.7;margin-top:4px;">增删错题 · 文件导入 · 重新生成报告</div>
  </div>
  <div class="actions">
    <button class="btn btn-success" onclick="regenerateReport()">重新生成报告</button>
  </div>
</div>

<div class="container">

  <!-- Stats -->
  <div class="card">
    <h2>总览</h2>
    <div class="stats-row" id="statsRow"></div>
  </div>

  <!-- Add Form -->
  <div class="card">
    <h2>添加错题（文字描述）</h2>
    <div class="form-group">
      <label>题目内容 *</label>
      <textarea id="addQuestion" placeholder="输入或粘贴完整的题目描述..."></textarea>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>科目</label>
        <select id="addSubject">
          <option value="Math">Math（数学）</option>
          <option value="Physics">Physics（物理）</option>
          <option value="Chemistry">Chemistry（化学）</option>
          <option value="Chinese">Chinese（语文）</option>
          <option value="English">English（英语）</option>
          <option value="Biology">Biology（生物）</option>
          <option value="Geography">Geography（地理）</option>
          <option value="History">History（历史）</option>
          <option value="Politics">Politics（政治）</option>
        </select>
      </div>
      <div class="form-group">
        <label>学段</label>
        <select id="addStage">
          <option value="大学">大学</option>
          <option value="高中">高中</option>
          <option value="初中">初中</option>
          <option value="小学">小学</option>
        </select>
      </div>
      <div class="form-group">
        <label>难度</label>
        <select id="addDifficulty">
          <option value="medium">中等 (medium)</option>
          <option value="easy">简单 (easy)</option>
          <option value="hard">困难 (hard)</option>
        </select>
      </div>
    </div>
    <div class="form-group">
      <label>错误类型（逗号分隔，如 ERR_METHOD, ERR_CONCEPT）</label>
      <input type="text" id="addErrorTypes" placeholder="ERR_METHOD, ERR_CONCEPT">
      <div style="font-size:11px;color:var(--text2);margin-top:3px;">
        ERR_CONCEPT=概念混淆 | ERR_CALC=计算失误 | ERR_READ=审题不清 | ERR_METHOD=方法错误 | ERR_GAP=知识盲区 | ERR_FORMAT=解题不规范 | ERR_PSYCH=考试心理
      </div>
    </div>
    <div class="form-group">
      <label>知识点（逗号分隔）</label>
      <input type="text" id="addKP" placeholder="极限与等价无穷小, 洛必达法则">
    </div>
    <div class="form-group">
      <label>错误分析</label>
      <textarea id="addAnalysis" placeholder="简要描述错误原因..."></textarea>
    </div>
    <button class="btn btn-primary" onclick="addMistake()">添加到错题集</button>
  </div>

  <!-- File Import -->
  <div class="card">
    <h2>批量导入（文件上传）</h2>
    <div class="file-drop" id="fileDrop">
      <div style="font-size:32px;margin-bottom:8px;">+</div>
      <div>点击或拖拽 CSV / JSON / Markdown 文件到这里</div>
      <div style="font-size:11px;color:var(--text2);margin-top:4px;">CSV 需含 question 列；JSON 为数组或 {"mistakes": [...]}；Markdown 每道题以 ## Q 或 ### Q 开头</div>
      <input type="file" id="fileInput" accept=".csv,.json,.md,.markdown" onchange="uploadFile()">
    </div>
    <div id="importResult" style="margin-top:12px;"></div>
  </div>

  <!-- Mistake List -->
  <div class="card">
    <h2>错题列表</h2>
    <div id="mistakeList"></div>
  </div>

</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<!-- Delete Confirm Modal -->
<div class="modal-overlay" id="deleteModal">
  <div class="modal-box">
    <h3 style="margin-bottom:12px;">确认删除</h3>
    <p id="deleteModalText" style="margin-bottom:16px;color:var(--text2);"></p>
    <div style="display:flex;gap:8px;justify-content:flex-end;">
      <button class="btn btn-outline" onclick="closeDeleteModal()">取消</button>
      <button class="btn btn-danger" id="deleteConfirmBtn">确认删除</button>
    </div>
  </div>
</div>

<script>
// ── Toast ───────────────────────────────────────────────────────────────────
let toastTimer;
function showToast(msg, ok) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast ' + (ok ? 'toast-ok' : 'toast-err') + ' show';
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 2500);
}

// ── Load data ───────────────────────────────────────────────────────────────
async function loadData() {
  const resp = await fetch('/api/mistakes');
  const data = await resp.json();
  renderStats(data.stats);
  renderMistakes(data.mistakes);
}

function renderStats(stats) {
  document.getElementById('statsRow').innerHTML = ''
    + '<div class="stat-item"><div class="stat-value">' + (stats.total||0) + '</div><div class="stat-label">错题总数</div></div>'
    + '<div class="stat-item"><div class="stat-value">' + (stats.mastered||0) + '</div><div class="stat-label">已掌握</div></div>'
    + '<div class="stat-item"><div class="stat-value">' + (stats.mastery_rate||'0%') + '</div><div class="stat-label">掌握率</div></div>'
    + '<div class="stat-item"><div class="stat-value">' + (stats.unanalyzed||0) + '</div><div class="stat-label">未分析</div></div>'
    + '<div class="stat-item"><div class="stat-value">' + (stats.avg_review_count||0) + '</div><div class="stat-label">平均复习次数</div></div>';
}

const TAG_CLASS = {ERR_CONCEPT:'tag-concept',ERR_CALC:'tag-calc',ERR_READ:'tag-read',ERR_METHOD:'tag-method',ERR_GAP:'tag-gap'};
const DIFF_CLASS = {easy:'tag-diff-easy',medium:'tag-diff-medium',hard:'tag-diff-hard'};
const DIFF_CN = {easy:'简单',medium:'中等',hard:'困难'};

function escapeHtml(s) { return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function renderMistakes(mistakes) {
  const el = document.getElementById('mistakeList');
  if (!mistakes.length) { el.innerHTML = '<div style="text-align:center;color:var(--text2);padding:24px;">暂无错题，用上方表单添加</div>'; return; }
  let html = '<table class="mistake-table"><thead><tr><th>ID</th><th>题目</th><th>科目</th><th>难度</th><th>错误类型</th><th>知识点</th><th>操作</th></tr></thead><tbody>';
  mistakes.forEach(m => {
    const errs = (m.error_types||[]).map(et => '<span class="tag '+(TAG_CLASS[et]||'')+'">'+escapeHtml(et)+'</span>').join('');
    const diff = m.difficulty||'medium';
    const kps = (m.knowledge_points||[]).map(kp => {
      const name = typeof kp === 'object' ? (kp.name||'') : String(kp);
      return '<span class="tag tag-method">'+escapeHtml(name)+'</span>';
    }).join('');
    html += '<tr>'
      + '<td style="font-weight:600;color:var(--accent);">#' + escapeHtml(m.id) + '</td>'
      + '<td class="q-cell" title="'+escapeHtml(m.question)+'">' + escapeHtml(m.question) + '</td>'
      + '<td>' + escapeHtml(m.subject||'') + '</td>'
      + '<td><span class="tag '+(DIFF_CLASS[diff]||'')+'">'+(DIFF_CN[diff]||diff)+'</span></td>'
      + '<td>' + errs + '</td>'
      + '<td>' + kps + '</td>'
      + '<td><button class="btn btn-danger btn-sm" onclick="confirmDelete(\''+escapeHtml(m.id)+'\',\''+escapeHtml((m.question||'').slice(0,60).replace(/'/g,"\\'"))+'\')">删除</button></td>'
      + '</tr>';
  });
  html += '</tbody></table>';
  el.innerHTML = html;
}

// ── Add mistake ─────────────────────────────────────────────────────────────
async function addMistake() {
  const question = document.getElementById('addQuestion').value.trim();
  if (!question) { showToast('请填写题目内容', false); return; }
  const payload = {
    question: question,
    subject: document.getElementById('addSubject').value,
    stage: document.getElementById('addStage').value,
    difficulty: document.getElementById('addDifficulty').value,
    error_types: document.getElementById('addErrorTypes').value.split(',').map(s=>s.trim()).filter(Boolean),
    knowledge_points: document.getElementById('addKP').value.split(',').map(s=>s.trim()).filter(Boolean),
    analysis: document.getElementById('addAnalysis').value.trim(),
  };
  const resp = await fetch('/api/mistakes', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  if (resp.ok) {
    const result = await resp.json();
    showToast('已添加 ' + result.id, true);
    document.getElementById('addQuestion').value = '';
    document.getElementById('addAnalysis').value = '';
    document.getElementById('addKP').value = '';
    document.getElementById('addErrorTypes').value = '';
    loadData();
  } else {
    const err = await resp.json();
    showToast(err.error||'添加失败', false);
  }
}

// ── Delete ───────────────────────────────────────────────────────────────────
let deleteTarget = null;
function confirmDelete(id, preview) {
  deleteTarget = id;
  document.getElementById('deleteModalText').textContent = '确定要删除 ' + id + '「' + preview + '...」？此操作不可撤销。';
  document.getElementById('deleteModal').classList.add('active');
}
function closeDeleteModal() {
  document.getElementById('deleteModal').classList.remove('active');
  deleteTarget = null;
}
document.getElementById('deleteConfirmBtn').onclick = async function() {
  if (!deleteTarget) return;
  const resp = await fetch('/api/mistakes/' + deleteTarget, {method:'DELETE'});
  closeDeleteModal();
  if (resp.ok) {
    showToast('已删除 ' + deleteTarget, true);
    loadData();
  } else {
    showToast('删除失败', false);
  }
};

// ── File upload ─────────────────────────────────────────────────────────────
function uploadFile() {
  const file = document.getElementById('fileInput').files[0];
  if (!file) return;
  const form = new FormData();
  form.append('file', file);
  document.getElementById('importResult').innerHTML = '<span style="color:var(--accent);">正在导入...</span>';
  fetch('/api/import', {method:'POST',body:form})
    .then(r => r.json())
    .then(d => {
      if (d.count !== undefined) {
        document.getElementById('importResult').innerHTML = '<span style="color:var(--success);">成功导入 ' + d.count + ' 道错题</span>';
        showToast('导入 ' + d.count + ' 道错题', true);
        document.getElementById('fileInput').value = '';
        setTimeout(loadData, 500);
      } else {
        document.getElementById('importResult').innerHTML = '<span style="color:var(--danger);">' + (d.error||'导入失败') + '</span>';
        showToast(d.error||'导入失败', false);
      }
    })
    .catch(e => {
      document.getElementById('importResult').innerHTML = '<span style="color:var(--danger);">导入出错</span>';
      showToast('导入出错: ' + e.message, false);
    });
}

// File drop
const drop = document.getElementById('fileDrop');
drop.ondragover = e => { e.preventDefault(); drop.classList.add('drag-over'); };
drop.ondragleave = () => drop.classList.remove('drag-over');
drop.ondrop = e => {
  e.preventDefault(); drop.classList.remove('drag-over');
  if (e.dataTransfer.files.length) { document.getElementById('fileInput').files = e.dataTransfer.files; uploadFile(); }
};
drop.onclick = () => document.getElementById('fileInput').click();

// ── Regenerate report ───────────────────────────────────────────────────────
async function regenerateReport() {
  showToast('正在重新生成报告...', true);
  const resp = await fetch('/api/regenerate', {method:'POST'});
  if (resp.ok) {
    const d = await resp.json();
    showToast('报告已重新生成！', true);
    setTimeout(() => { if (d.html_url) window.open(d.html_url, '_blank'); }, 800);
  } else {
    showToast('报告生成失败', false);
  }
}

// ── Init ────────────────────────────────────────────────────────────────────
loadData();
</script>
</body>
</html>'''


# ── API Routes ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return MANAGEMENT_HTML


@app.route("/api/mistakes")
def api_list():
    collection = load_collection(str(COLLECTION_PATH))
    stats = compute_statistics(collection)
    return jsonify({"mistakes": collection["mistakes"], "stats": stats})


@app.route("/api/mistakes", methods=["POST"])
def api_add():
    try:
        data = request.get_json(force=True)
        collection = load_collection(str(COLLECTION_PATH))
        # Build mistake payload from form data
        payload = {}
        for key in MISTAKE_SCHEMA:
            if key in data and data[key] not in (None, ""):
                payload[key] = data[key]
        mistake = add_mistake(collection, payload)
        save_collection(collection, str(COLLECTION_PATH))
        return jsonify({"id": mistake["id"], "question": mistake["question"][:80]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/mistakes/<mid>", methods=["DELETE"])
def api_delete(mid):
    try:
        collection = load_collection(str(COLLECTION_PATH))
        ok = delete_mistake(collection, mid)
        if not ok:
            return jsonify({"error": f"Mistake {mid} not found"}), 404
        save_collection(collection, str(COLLECTION_PATH))
        return jsonify({"deleted": mid}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/import", methods=["POST"])
def api_import():
    try:
        if "file" not in request.files:
            return jsonify({"error": "未选择文件"}), 400
        f = request.files["file"]
        if not f.filename:
            return jsonify({"error": "文件名为空"}), 400

        ext = Path(f.filename).suffix.lower()
        collection = load_collection(str(COLLECTION_PATH))

        # Save uploaded file temporarily, then import
        tmp_path = COLLECTION_PATH.parent / f"__upload_{f.filename}"
        f.save(str(tmp_path))

        if ext == ".csv":
            count = import_csv(collection, str(tmp_path))
        elif ext == ".json":
            count = import_json(collection, str(tmp_path))
        elif ext in (".md", ".markdown"):
            count = import_markdown(collection, str(tmp_path))
        else:
            return jsonify({"error": f"不支持的文件格式: {ext}（支持 .csv / .json / .md）"}), 400

        tmp_path.unlink(missing_ok=True)
        save_collection(collection, str(COLLECTION_PATH))
        return jsonify({"count": count}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/regenerate", methods=["POST"])
def api_regenerate():
    try:
        collection = load_collection(str(COLLECTION_PATH))
        mistakes = collection["mistakes"]
        if not mistakes:
            return jsonify({"error": "错题集为空，无法生成报告"}), 400

        # Build a minimal analysis JSON (just enough to trigger report generation)
        error_dist = {}
        kp_counts = {}
        for m in mistakes:
            for et in m.get("error_types", []):
                error_dist[et] = error_dist.get(et, 0) + 1
            for kp in m.get("knowledge_points", []):
                name = kp["name"] if isinstance(kp, dict) else str(kp)
                kp_counts[name] = kp_counts.get(name, 0) + 1

        analysis = {
            "title": "错题集分析报告",
            "subject": "综合" if len(set(m.get("subject","") for m in mistakes)) > 2 else (mistakes[0].get("subject","") or "综合"),
            "stage": "综合" if len(set(m.get("stage","") for m in mistakes)) > 2 else (mistakes[0].get("stage","") or "K12"),
            "generated_at": datetime.now().strftime("%Y-%m-%d"),
            "statistics": {"items": [
                {"label": "错题总数", "value": str(len(mistakes))},
                {"label": "涉及知识点", "value": str(len(kp_counts))},
            ]},
            "error_distribution": error_dist,
            "kp_error_counts": kp_counts,
            "retention_curve": [{"day":d, "retention":round(0.97**d, 2)} for d in [0,1,2,3,4,5,6,7,10,15,20,30,45,60]],
            "mistakes": [{
                "id": m.get("id",""), "subject": m.get("subject",""),
                "question": m.get("question",""), "analysis": m.get("analysis",""),
                "knowledge_points": m.get("knowledge_points",[]),
                "error_types": m.get("error_types",[]),
                "variants": m.get("variants",[]),
            } for m in mistakes],
            "schedule_statistics": {"items": [
                {"label": "错题总数", "value": str(len(mistakes))},
            ]},
            "schedule_timeline": [{"date": datetime.now().strftime("%Y-%m-%d"), "day": 0, "items": "全部错题"}],
            "suggestions": [],
            "target_retention": 85,
        }

        out_dir = OUTPUT_DIR or COLLECTION_PATH.parent / "output"
        out_dir.mkdir(parents=True, exist_ok=True)
        analysis_path = out_dir / "analysis.json"
        with open(analysis_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)

        # Generate reports
        html = generate_html(analysis)
        html_path = out_dir / "report.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML report: {html_path}")

        md = generate_markdown(analysis)
        md_path = out_dir / "report.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Markdown report: {md_path}")

        return jsonify({
            "html_url": str(html_path),
            "md_url": str(md_path),
            "total": len(mistakes),
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    global COLLECTION_PATH, OUTPUT_DIR

    args = sys.argv[1:]
    coll = None
    port = 5000
    out_dir = None

    i = 0
    while i < len(args):
        if args[i] == "--collection" and i + 1 < len(args):
            coll = args[i + 1]; i += 2
        elif args[i] == "--port" and i + 1 < len(args):
            port = int(args[i + 1]); i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            out_dir = args[i + 1]; i += 2
        else:
            i += 1

    if not coll:
        print("Usage: python mistake_webui.py --collection COLLECTION.json [--port 5000] [--output DIR]")
        sys.exit(1)

    COLLECTION_PATH = Path(coll).resolve()
    OUTPUT_DIR = Path(out_dir).resolve() if out_dir else COLLECTION_PATH.parent / "output"

    # Ensure collection exists
    if not COLLECTION_PATH.exists():
        load_collection(str(COLLECTION_PATH))
        save_collection(load_collection(str(COLLECTION_PATH)), str(COLLECTION_PATH))

    print(f"Mistake Web UI starting...")
    print(f"  Collection: {COLLECTION_PATH}")
    print(f"  Output dir: {OUTPUT_DIR}")
    print(f"  Open http://localhost:{port} in your browser")
    print(f"  Press Ctrl+C to stop")

    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
