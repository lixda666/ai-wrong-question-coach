#!/usr/bin/env python3
"""
Report Generator for AI Wrong Question Coach

Generates HTML (interactive) and Markdown analysis reports from mistake analysis data.
The HTML report includes Chart.js visualizations, error breakdown, knowledge point mapping,
variant exercises, and a review schedule.

Call from command line:
    python report_generator.py --input analysis.json --output report
"""

import json
import sys
from datetime import datetime
from pathlib import Path


# ── Color Palette ──────────────────────────────────────────────────────────
# Clean, modern palette — no emoji, minimal aesthetic

COLORS = {
    "primary": "#2C3E50",
    "accent": "#3498DB",
    "success": "#27AE60",
    "warning": "#F39C12",
    "danger": "#E74C3C",
    "bg": "#FAFAFA",
    "card_bg": "#FFFFFF",
    "text": "#2C3E50",
    "text_secondary": "#7F8C8D",
    "border": "#ECF0F1",
}

CHART_COLORS = [
    "#3498DB", "#E74C3C", "#2ECC71", "#F39C12", "#9B59B6",
    "#1ABC9C", "#E67E22", "#2980B9", "#27AE60", "#C0392B",
]

ERROR_TYPE_LABELS = {
    "ERR_CONCEPT": "Concept Confusion",
    "ERR_CALC": "Calculation Error",
    "ERR_READ": "Misreading Question",
    "ERR_METHOD": "Method Error",
    "ERR_GAP": "Knowledge Gap",
    "ERR_FORMAT": "Non-standard Solution",
    "ERR_PSYCH": "Test-taking Factors",
}

ERROR_TYPE_LABELS_CN = {
    "ERR_CONCEPT": "概念混淆",
    "ERR_CALC": "计算失误",
    "ERR_READ": "审题不清",
    "ERR_METHOD": "方法错误",
    "ERR_GAP": "知识盲区",
    "ERR_FORMAT": "解题不规范",
    "ERR_PSYCH": "考试心理因素",
}


# ── Template ───────────────────────────────────────────────────────────────

def html_template() -> str:
    """Return the HTML report template as a string."""
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI 错题教练 -- 错题分析报告</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root {
    --primary: #2C3E50;
    --accent: #3498DB;
    --success: #27AE60;
    --warning: #F39C12;
    --danger: #E74C3C;
    --bg: #FAFAFA;
    --card-bg: #FFFFFF;
    --text: #2C3E50;
    --text-secondary: #7F8C8D;
    --border: #ECF0F1;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
    -webkit-font-smoothing: antialiased;
  }

  /* ── Header ── */
  .header {
    background: linear-gradient(135deg, #2C3E50 0%, #34495E 100%);
    color: #FFFFFF;
    padding: 48px 40px;
  }
  .header h1 { font-size: 28px; font-weight: 600; letter-spacing: 0.5px; }
  .header .meta { margin-top: 12px; font-size: 14px; opacity: 0.75; }
  .header .meta span { margin-right: 32px; }

  /* ── Container ── */
  .container { max-width: 1100px; margin: 0 auto; padding: 40px 32px; }

  /* ── Cards ── */
  .card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 32px;
    margin-bottom: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }
  .card h2 {
    font-size: 20px;
    font-weight: 600;
    color: var(--primary);
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 2px solid var(--accent);
  }
  .card h3 {
    font-size: 16px;
    font-weight: 600;
    color: var(--primary);
    margin: 20px 0 12px;
  }

  /* ── Stat Grid ── */
  .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; }
  .stat-item {
    text-align: center;
    padding: 20px 16px;
    background: var(--bg);
    border-radius: 6px;
  }
  .stat-value { font-size: 32px; font-weight: 700; color: var(--accent); }
  .stat-label { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }

  /* ── Chart Wrapper ── */
  .chart-wrapper { max-width: 100%; margin: 16px 0; }
  .chart-wrapper canvas { max-height: 320px; }
  .chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
  @media (max-width: 768px) { .chart-row { grid-template-columns: 1fr; } }

  /* ── Mistake List ── */
  .mistake-item {
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 20px;
    margin-bottom: 16px;
    transition: box-shadow 0.2s;
  }
  .mistake-item:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
  .mistake-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
  .mistake-id { font-weight: 600; color: var(--primary); }
  .mistake-subject {
    font-size: 12px;
    padding: 2px 10px;
    border-radius: 12px;
    background: #EBF5FB;
    color: #2980B9;
  }
  .mistake-question {
    background: var(--bg);
    padding: 12px 16px;
    border-radius: 4px;
    font-size: 14px;
    margin-bottom: 12px;
    border-left: 3px solid var(--accent);
  }
  .mistake-analysis { font-size: 14px; color: var(--text-secondary); margin-bottom: 8px; }
  .mistake-kp {
    display: inline-block;
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 4px;
    background: #FDEBD0;
    color: #E67E22;
    margin-right: 6px;
    margin-bottom: 6px;
  }
  .mistake-error-tag {
    display: inline-block;
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 4px;
    margin-right: 6px;
    margin-bottom: 6px;
  }
  .tag-concept { background: #FADBD8; color: #C0392B; }
  .tag-calc { background: #D5F5E3; color: #1E8449; }
  .tag-read { background: #D6EAF8; color: #2471A3; }
  .tag-method { background: #E8DAEF; color: #6C3483; }
  .tag-gap { background: #FCF3CF; color: #B7950B; }
  .tag-format { background: #D5DBDB; color: #616A6B; }
  .tag-psych { background: #FDEDEC; color: #922B21; }

  .error-tag-classes {
    "ERR_CONCEPT": "tag-concept",
    "ERR_CALC": "tag-calc",
    "ERR_READ": "tag-read",
    "ERR_METHOD": "tag-method",
    "ERR_GAP": "tag-gap",
    "ERR_FORMAT": "tag-format",
    "ERR_PSYCH": "tag-psych",
  }

  /* ── Schedule ── */
  .schedule-timeline { position: relative; padding-left: 24px; }
  .schedule-timeline::before {
    content: "";
    position: absolute;
    left: 8px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: var(--border);
  }
  .schedule-day {
    position: relative;
    margin-bottom: 12px;
    padding: 12px 16px 12px 24px;
    border-radius: 6px;
    background: var(--bg);
    cursor: pointer;
    transition: background 0.15s, transform 0.1s;
  }
  .schedule-day:hover { background: #EBF5FB; }
  .schedule-day:active { transform: scale(0.99); }
  .schedule-day::before {
    content: "";
    position: absolute;
    left: -20px;
    top: 18px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--accent);
    border: 2px solid var(--card-bg);
  }
  .schedule-date { font-weight: 600; font-size: 14px; color: var(--primary); display: flex; align-items: center; gap: 8px; }
  .schedule-date::after { content: "查看详情 →"; font-size: 12px; color: var(--accent); font-weight: 400; }
  .schedule-items { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }

  /* ── Modal ── */
  .modal-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(44, 62, 80, 0.55);
    z-index: 9999;
    align-items: center;
    justify-content: center;
    padding: 24px;
    animation: modalFadeIn 0.18s ease-out;
  }
  .modal-overlay.active { display: flex; }
  @keyframes modalFadeIn { from { opacity: 0; } to { opacity: 1; } }

  .modal-box {
    background: var(--card-bg);
    border-radius: 10px;
    max-width: 760px;
    width: 100%;
    max-height: 86vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
    animation: modalSlideUp 0.22s ease-out;
  }
  @keyframes modalSlideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 24px 28px 16px;
    border-bottom: 1px solid var(--border);
  }
  .modal-date { font-size: 22px; font-weight: 700; color: var(--primary); }
  .modal-subtitle { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
  .modal-close {
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 6px 14px;
    border-radius: 4px;
    font-size: 13px;
    cursor: pointer;
    transition: background 0.15s;
  }
  .modal-close:hover { background: #EBF5FB; }

  .modal-body {
    padding: 20px 28px 28px;
    overflow-y: auto;
  }

  .review-kp-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 12px 14px;
    background: #FEF9E7;
    border-radius: 6px;
    margin-bottom: 18px;
  }
  .review-kp-chips .kp-chip-label {
    font-size: 12px;
    color: #B7950B;
    font-weight: 600;
    margin-right: 4px;
  }
  .review-kp-chip {
    font-size: 12px;
    padding: 2px 10px;
    border-radius: 12px;
    background: #FCF3CF;
    color: #B7950B;
  }

  .review-item {
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 16px;
    margin-bottom: 14px;
    background: #FCFCFD;
  }
  .review-item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  .review-item-id { font-weight: 600; color: var(--accent); font-size: 14px; }
  .review-item-question { font-size: 14px; color: var(--text); margin-bottom: 10px; line-height: 1.6; }
  .review-item-analysis {
    font-size: 13px;
    color: var(--text-secondary);
    background: var(--bg);
    padding: 10px 12px;
    border-left: 3px solid var(--warning);
    border-radius: 0 4px 4px 0;
    margin-bottom: 10px;
    line-height: 1.6;
  }
  .review-item-variants-title {
    font-size: 12px;
    color: var(--accent);
    font-weight: 600;
    margin-top: 8px;
    margin-bottom: 4px;
  }
  .review-variant {
    font-size: 13px;
    color: var(--text);
    margin-bottom: 6px;
    padding-left: 8px;
    border-left: 2px solid #EBF5FB;
  }
  .review-variant-answer { color: var(--success); font-size: 12px; display: block; margin-top: 2px; }
  .review-empty { text-align: center; color: var(--text-secondary); padding: 40px 0; font-size: 14px; }

  /* ── Variant Exercises ── */
  .variant-box {
    background: #F8F9FA;
    border-radius: 6px;
    padding: 16px;
    margin-top: 12px;
  }
  .variant-box .variant-label {
    font-size: 12px;
    color: var(--accent);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
  }

  /* ── Footer ── */
  .footer {
    text-align: center;
    padding: 32px;
    color: var(--text-secondary);
    font-size: 12px;
    border-top: 1px solid var(--border);
    margin-top: 40px;
  }
</style>
</head>
<body>

<div class="header">
  <h1>{{REPORT_TITLE}}</h1>
  <div class="meta">
    <span>科目：{{SUBJECT}}</span>
    <span>学段：{{STAGE}}</span>
    <span>生成时间：{{GENERATED_AT}}</span>
  </div>
</div>

<div class="container">

  <!-- Summary Stats -->
  <div class="card">
    <h2>总览</h2>
    <div class="stat-grid">
      {{STAT_CARDS}}
    </div>
  </div>

  <!-- Error Distribution Chart -->
  <div class="card">
    <h2>错误类型分布</h2>
    <div class="chart-row">
      <div class="chart-wrapper">
        <canvas id="errorPieChart"></canvas>
      </div>
      <div class="chart-wrapper">
        <canvas id="errorBarChart"></canvas>
      </div>
    </div>
  </div>

  <!-- Knowledge Point Analysis -->
  <div class="card">
    <h2>知识点分析</h2>
    <div class="chart-row">
      <div class="chart-wrapper">
        <canvas id="kpBarChart"></canvas>
      </div>
      <div class="chart-wrapper">
        <canvas id="kpRadarChart"></canvas>
      </div>
    </div>
    <h3>薄弱知识点</h3>
    {{KP_TABLE}}
  </div>

  <!-- Forgetting Curve -->
  <div class="card">
    <h2>记忆保持曲线</h2>
    <div class="chart-wrapper">
      <canvas id="retentionChart"></canvas>
    </div>
    <p style="font-size:13px;color:var(--text-secondary);margin-top:12px;">
      基于艾宾浩斯遗忘曲线，并结合 SM-2 难度系数动态调整。在计划的时间节点复习，记忆保持率可维持在 {{TARGET_RETENTION}}% 以上。
    </p>
  </div>

  <!-- Mistake Detail -->
  <div class="card">
    <h2>错题详情</h2>
    {{MISTAKE_LIST}}
  </div>

  <!-- Review Schedule -->
  <div class="card">
    <h2>复习计划</h2>
    <div class="stat-grid" style="margin-bottom:24px;">
      {{SCHEDULE_STATS}}
    </div>
    <h3>即将复习（点击日期查看当天复习内容）</h3>
    <div class="schedule-timeline">
      {{SCHEDULE_TIMELINE}}
    </div>
  </div>

  <!-- Improvement Suggestions -->
  <div class="card">
    <h2>改进建议</h2>
    {{SUGGESTIONS}}
  </div>

</div>

<!-- Review Detail Modal -->
<div class="modal-overlay" id="reviewModal" onclick="closeModal(event)">
  <div class="modal-box" onclick="event.stopPropagation()">
    <div class="modal-header">
      <div>
        <div class="modal-date" id="modalDate">2026-07-16</div>
        <div class="modal-subtitle" id="modalSubtitle">复习内容预览</div>
      </div>
      <button class="modal-close" onclick="closeModal()" aria-label="关闭">关闭</button>
    </div>
    <div class="modal-body" id="modalBody">
      <!-- Filled by JS -->
    </div>
  </div>
</div>

<div class="footer">
  <p>由 AI 错题教练 生成 · 由 WorkBuddy 提供技术支持</p>
  <p style="margin-top:8px;">
    管理错题集：在命令行执行 <code>python scripts/mistake_webui.py --collection COLLECTION.json --port 5000</code>，然后打开浏览器访问管理界面，即可添加、导入、删除错题。
  </p>
</div>

<script>
{{REVIEW_DATA_BLOCK}}
{{CHART_SCRIPTS}}
</script>

</body>
</html>'''


# ── Chart Script Generator ─────────────────────────────────────────────────

def generate_chart_scripts(data: dict) -> str:
    """Generate Chart.js scripts for all visualizations."""
    scripts = []

    # Pie chart: Error distribution
    error_dist = data.get("error_distribution", {})
    pie_labels = json.dumps([ERROR_TYPE_LABELS_CN.get(k, k) for k in error_dist.keys()], ensure_ascii=False)
    pie_data = json.dumps(list(error_dist.values()))
    pie_colors = json.dumps(CHART_COLORS[:len(error_dist)])

    scripts.append(f'''
// Error Type Pie Chart
new Chart(document.getElementById('errorPieChart'), {{
  type: 'doughnut',
  data: {{
    labels: {pie_labels},
    datasets: [{{
      data: {pie_data},
      backgroundColor: {pie_colors},
      borderWidth: 1,
      borderColor: '#fff'
    }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: true,
    plugins: {{
      legend: {{ position: 'bottom', labels: {{ padding: 16, usePointStyle: true }} }}
    }}
  }}
}});
''')

    # Bar chart: Error type breakdown (horizontal, sorted descending)
    # Use error_distribution directly so the chart never goes blank when
    # error_by_subject is absent.
    error_dist = data.get("error_distribution", {})
    # Filter out zero-count entries, then sort by count desc
    sorted_items = sorted(
        [(ERROR_TYPE_LABELS_CN.get(k, k), v) for k, v in error_dist.items() if v and v > 0],
        key=lambda x: -x[1],
    )
    bar_labels = [item[0] for item in sorted_items]
    bar_values = [item[1] for item in sorted_items]
    bar_colors = CHART_COLORS[: len(bar_labels)] if bar_labels else []

    scripts.append(f'''
// Error Bar Chart (horizontal, sorted by count)
new Chart(document.getElementById('errorBarChart'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(bar_labels, ensure_ascii=False)},
    datasets: [{{
      label: '错误次数',
      data: {json.dumps(bar_values)},
      backgroundColor: {json.dumps(bar_colors)},
      borderRadius: 4,
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: true,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        callbacks: {{
          label: function(ctx) {{ return '错误次数：' + ctx.parsed.x; }}
        }}
      }}
    }},
    scales: {{
      x: {{ beginAtZero: true, ticks: {{ stepSize: 1, precision: 0 }}, grid: {{ color: '#ECF0F1' }} }},
      y: {{ grid: {{ display: false }} }}
    }}
  }}
}});
''')

    # Knowledge point bar chart
    kp_data = data.get("kp_error_counts", {})
    kp_labels = json.dumps(list(kp_data.keys())[:10], ensure_ascii=False)
    kp_values = json.dumps(list(kp_data.values())[:10])

    scripts.append(f'''
// Knowledge Point Error Chart
new Chart(document.getElementById('kpBarChart'), {{
  type: 'bar',
  data: {{
    labels: {kp_labels},
    datasets: [{{
      label: 'Error Count',
      data: {kp_values},
      backgroundColor: '#3498DB',
      borderRadius: 4,
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ beginAtZero: true, ticks: {{ stepSize: 1 }}, grid: {{ color: '#ECF0F1' }} }},
      y: {{ grid: {{ display: false }} }}
    }}
  }}
}});
''')

    # Radar chart: Weak areas
    kp_radar_labels = json.dumps(list(kp_data.keys())[:8], ensure_ascii=False)
    kp_radar_values = json.dumps(list(kp_data.values())[:8])
    max_val = max(kp_data.values()) if kp_data else 5

    scripts.append(f'''
// Knowledge Point Radar Chart
new Chart(document.getElementById('kpRadarChart'), {{
  type: 'radar',
  data: {{
    labels: {kp_radar_labels},
    datasets: [{{
      label: 'Weakness Level',
      data: {kp_radar_values},
      backgroundColor: 'rgba(52, 152, 219, 0.15)',
      borderColor: '#3498DB',
      borderWidth: 2,
      pointBackgroundColor: '#3498DB',
      pointRadius: 4,
    }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: true,
    scales: {{
      r: {{
        beginAtZero: true,
        max: {max_val + 2},
        ticks: {{ stepSize: 1 }},
        grid: {{ color: '#ECF0F1' }}
      }}
    }},
    plugins: {{ legend: {{ display: false }} }}
  }}
}});
''')

    # Retention curve
    retention = data.get("retention_curve", [])
    retention_labels = json.dumps([p.get("day", 0) for p in retention])
    retention_values = json.dumps([p.get("retention", 0) for p in retention])
    target_pct = data.get("target_retention", 85) / 100.0

    scripts.append(f'''
// Retention Curve
new Chart(document.getElementById('retentionChart'), {{
  type: 'line',
  data: {{
    labels: {retention_labels},
    datasets: [{{
      label: '预计保持率',
      data: {retention_values},
      borderColor: '#27AE60',
      backgroundColor: 'rgba(39, 174, 96, 0.08)',
      borderWidth: 2,
      fill: true,
      tension: 0.3,
      pointRadius: 1,
    }}, {{
      label: '目标线 (85%)',
      data: Array({len(retention)}).fill({target_pct}),
      borderColor: '#E74C3C',
      borderWidth: 1,
      borderDash: [5, 5],
      fill: false,
      pointRadius: 0,
    }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: true,
    scales: {{
      x: {{ title: {{ display: true, text: '天数' }} }},
      y: {{
        min: 0,
        max: 1,
        ticks: {{ callback: function(v) {{ return (v*100).toFixed(0) + '%'; }} }},
        title: {{ display: true, text: '记忆保持率' }}
      }}
    }},
    plugins: {{
      legend: {{ position: 'bottom', labels: {{ padding: 16, usePointStyle: true }} }}
    }}
  }}
}});
''')

    return '\n'.join(scripts)


# ── HTML Generator ─────────────────────────────────────────────────────────

def generate_html(data: dict) -> str:
    """Generate complete HTML report from analysis data."""
    html = html_template()

    # Replace placeholders
    html = html.replace("{{REPORT_TITLE}}", data.get("title", "Mistake Analysis Report"))
    html = html.replace("{{SUBJECT}}", data.get("subject", "Multiple"))
    html = html.replace("{{STAGE}}", data.get("stage", "K12"))
    html = html.replace("{{GENERATED_AT}}", data.get("generated_at", datetime.now().strftime("%Y-%m-%d %H:%M")))

    # Stats
    stats = data.get("statistics", {})
    stat_html = ""
    for stat in stats.get("items", []):
        stat_html += f'''<div class="stat-item">
  <div class="stat-value">{stat['value']}</div>
  <div class="stat-label">{stat['label']}</div>
</div>\n'''
    html = html.replace("{{STAT_CARDS}}", stat_html)

    # KP Table
    kp_table_data = data.get("kp_error_counts", {})
    kp_table_html = '<table style="width:100%;border-collapse:collapse;font-size:14px;">'
    kp_table_html += '<tr style="background:#F8F9FA;"><th style="padding:10px;text-align:left;border-bottom:2px solid #ECF0F1;">知识点</th><th style="padding:10px;text-align:center;border-bottom:2px solid #ECF0F1;">错误次数</th><th style="padding:10px;text-align:left;border-bottom:2px solid #ECF0F1;">风险等级</th></tr>'
    for kp, count in sorted(kp_table_data.items(), key=lambda x: -x[1])[:10]:
        risk = "高" if count >= 3 else "中" if count >= 2 else "低"
        risk_color = "#E74C3C" if risk == "高" else "#F39C12" if risk == "中" else "#27AE60"
        kp_table_html += f'<tr><td style="padding:10px;border-bottom:1px solid #ECF0F1;">{kp}</td><td style="padding:10px;text-align:center;border-bottom:1px solid #ECF0F1;">{count}</td><td style="padding:10px;border-bottom:1px solid #ECF0F1;color:{risk_color};font-weight:600;">{risk}</td></tr>'
    kp_table_html += '</table>'
    html = html.replace("{{KP_TABLE}}", kp_table_html)

    # Mistake list
    mistakes = data.get("mistakes", [])
    mistake_html = ""
    for m in mistakes:
        error_tags = ""
        tag_map = {
            "ERR_CONCEPT": "tag-concept",
            "ERR_CALC": "tag-calc",
            "ERR_READ": "tag-read",
            "ERR_METHOD": "tag-method",
            "ERR_GAP": "tag-gap",
            "ERR_FORMAT": "tag-format",
            "ERR_PSYCH": "tag-psych",
        }
        for et in m.get("error_types", []):
            cls = tag_map.get(et, "")
            label = ERROR_TYPE_LABELS_CN.get(et, et)
            error_tags += f'<span class="mistake-error-tag {cls}">{label}</span>'

        kp_tags = ""
        for kp in m.get("knowledge_points", []):
            kp_tags += f'<span class="mistake-kp">{kp}</span>'

        variants = m.get("variants", [])
        variant_html = ""
        if variants:
            variant_html = '<div class="variant-box"><div class="variant-label">同类练习题</div>'
            for i, v in enumerate(variants, 1):
                if isinstance(v, dict):
                    q_text = v.get("question", "")
                    a_text = v.get("answer", "")
                    if a_text:
                        variant_html += f'<p style="margin-bottom:8px;font-size:14px;"><strong>{i}.</strong> {q_text}<br><span style="color:var(--success);font-size:13px;">参考答案：{a_text}</span></p>'
                    else:
                        variant_html += f'<p style="margin-bottom:8px;font-size:14px;"><strong>{i}.</strong> {q_text}</p>'
                else:
                    variant_html += f'<p style="margin-bottom:8px;font-size:14px;"><strong>{i}.</strong> {v}</p>'
            variant_html += '</div>'

        # Knowledge point display: extract name from dict or use string directly
        kp_display_tags = ""
        for kp in m.get("knowledge_points", []):
            if isinstance(kp, dict):
                kp_display_tags += f'<span class="mistake-kp">{kp.get("name", str(kp))}</span>'
            else:
                kp_display_tags += f'<span class="mistake-kp">{kp}</span>'

        mistake_html += f'''<div class="mistake-item" id="mistake-{m.get("id", "")}">
  <div class="mistake-header">
    <span class="mistake-id">#{m.get("id", "")}</span>
    <span class="mistake-subject">{m.get("subject", "")}</span>
  </div>
  <div class="mistake-question">{m.get("question", "")}</div>
  <div class="mistake-analysis"><strong>错因分析：</strong> {m.get("analysis", "")}</div>
  <div style="margin-top:8px;">{kp_display_tags}</div>
  <div style="margin-top:4px;">{error_tags}</div>
  {variant_html}
</div>
'''
    html = html.replace("{{MISTAKE_LIST}}", mistake_html)

    # Schedule stats
    sched_stats = data.get("schedule_statistics", {})
    sched_html = ""
    for ss in sched_stats.get("items", []):
        sched_html += f'''<div class="stat-item">
  <div class="stat-value">{ss['value']}</div>
  <div class="stat-label">{ss['label']}</div>
</div>\n'''
    html = html.replace("{{SCHEDULE_STATS}}", sched_html)

    # Schedule timeline
    timeline = data.get("schedule_timeline", [])
    timeline_html = ""
    # Build a lookup: index in timeline -> serializable payload
    schedule_payload = []
    for idx, entry in enumerate(timeline[:15]):
        date_str = entry.get("date", "")
        items_str = entry.get("items", "")
        day_idx = entry.get("day", idx)
        # Parse the items string client-side via JS; we just pass it raw.
        schedule_payload.append({
            "date": date_str,
            "day": day_idx,
            "items": items_str,
        })
        timeline_html += f'''<div class="schedule-day" onclick="openReviewModal({idx})">
  <div class="schedule-date">{date_str} <span style="color:var(--text-secondary);font-weight:400;font-size:12px;">（第 {day_idx} 天）</span></div>
  <div class="schedule-items">{items_str}</div>
</div>
'''
    html = html.replace("{{SCHEDULE_TIMELINE}}", timeline_html)

    # Embed mistakes + schedule payload as JSON for the modal
    mistakes_json = json.dumps(data.get("mistakes", []), ensure_ascii=False)
    schedule_json = json.dumps(schedule_payload, ensure_ascii=False)
    total_mistakes = len(data.get("mistakes", []))

    err_labels_cn_json = json.dumps(ERROR_TYPE_LABELS_CN, ensure_ascii=False)

    review_data_block = f'''
// Review detail data (injected by Python)
window.__REVIEW_DATA__ = {{
  schedule: {schedule_json},
  mistakes: {mistakes_json},
  totalMistakes: {total_mistakes},
}};

// Error type label map (CN) for client-side rendering
window.__ERR_LABELS_CN__ = {err_labels_cn_json};

// ── Helpers ────────────────────────────────────────────────────────────────

function parseQuestionIds(itemsStr, totalMistakes) {{
  // Accepts forms like:
  //   "Q1-Q10（初次分析）"             -> [Q1..Q10]
  //   "Q5, Q9（易错题，先复习）"        -> [Q5, Q9]
  //   "全部10题（第一轮全面复习 ...）"  -> all mistake ids (in original order)
  //   "Q4, Q8, Q10（中值定理 ...）"     -> [Q4, Q8, Q10]
  if (!itemsStr) return [];
  const ids = [];
  // 1. range like Q1-Q10 (or with en/em dashes)
  const rangeRe = /Q\\s*(\\d+)\\s*[-–—]\\s*Q\\s*(\\d+)/i;
  const rangeMatch = itemsStr.match(rangeRe);
  if (rangeMatch) {{
    const a = parseInt(rangeMatch[1], 10);
    const b = parseInt(rangeMatch[2], 10);
    const lo = Math.min(a, b);
    const hi = Math.max(a, b);
    for (let i = lo; i <= hi; i++) ids.push('Q' + i);
  }}
  // 2. individual Q5, Q9 (skip those already inside a range)
  const singleRe = /Q\\s*(\\d+)(?!\\s*[-–—])/gi;
  let m;
  while ((m = singleRe.exec(itemsStr)) !== null) {{
    const id = 'Q' + m[1];
    if (!ids.includes(id)) ids.push(id);
  }}
  // 3. "全部N题" -> all mistakes in order
  if (ids.length === 0) {{
    const allRe = /全部\\s*(\\d+)\\s*题/;
    const allMatch = itemsStr.match(allRe);
    const n = allMatch ? parseInt(allMatch[1], 10) : (totalMistakes || 0);
    for (let i = 1; i <= n; i++) ids.push('Q' + i);
  }}
  return ids;
}}

function lookupMistakes(ids) {{
  const all = window.__REVIEW_DATA__.mistakes || [];
  return ids.map(id => all.find(m => String(m.id) === String(id))).filter(Boolean);
}}

function escapeHtml(s) {{
  if (s == null) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}}

function renderReviewItem(m) {{
  const errLabels = window.__ERR_LABELS_CN__ || {{}};
  // Error types
  const errs = (m.error_types || []).map(et => {{
    const label = errLabels[et] || et;
    return '<span style="font-size:11px;padding:2px 6px;border-radius:4px;background:#E8DAEF;color:#6C3483;margin-right:4px;">' + escapeHtml(label) + '</span>';
  }}).join('');
  // Knowledge points
  const kps = (m.knowledge_points || []).map(kp => {{
    const name = (typeof kp === 'object' && kp) ? (kp.name || kp.kp_id || JSON.stringify(kp)) : String(kp);
    return '<span style="font-size:11px;padding:2px 6px;border-radius:4px;background:#FDEBD0;color:#E67E22;margin-right:4px;margin-bottom:4px;display:inline-block;">' + escapeHtml(name) + '</span>';
  }}).join('');
  // Variants
  let variantsHtml = '';
  const variants = m.variants || [];
  if (variants.length) {{
    variantsHtml = '<div class="review-item-variants-title">同类练习题</div>';
    variants.forEach((v, i) => {{
      let qText = '', aText = '';
      if (typeof v === 'object' && v) {{
        qText = v.question || '';
        aText = v.answer || '';
      }} else {{
        qText = String(v);
      }}
      variantsHtml += '<div class="review-variant">'
        + '<strong>' + (i + 1) + '.</strong> ' + escapeHtml(qText)
        + (aText ? '<span class="review-variant-answer">参考答案：' + escapeHtml(aText) + '</span>' : '')
        + '</div>';
    }});
  }}
  return ''
    + '<div class="review-item">'
    +   '<div class="review-item-header">'
    +     '<span class="review-item-id">#' + escapeHtml(m.id || '') + '</span>'
    +     '<span>' + errs + '</span>'
    +   '</div>'
    +   '<div class="review-item-question">' + escapeHtml(m.question || '') + '</div>'
    +   '<div class="review-item-analysis"><strong>错因分析：</strong>' + escapeHtml(m.analysis || '') + '</div>'
    +   (kps ? '<div style="margin-bottom:8px;">' + kps + '</div>' : '')
    +   variantsHtml
    + '</div>';
}}

function openReviewModal(idx) {{
  const entry = (window.__REVIEW_DATA__ && window.__REVIEW_DATA__.schedule) ? window.__REVIEW_DATA__.schedule[idx] : null;
  if (!entry) return;
  const ids = parseQuestionIds(entry.items, window.__REVIEW_DATA__.totalMistakes);
  const mistakes = lookupMistakes(ids);

  document.getElementById('modalDate').textContent = entry.date;
  document.getElementById('modalSubtitle').textContent = '第 ' + entry.day + ' 天 · 涉及 ' + ids.length + ' 道题';

  const body = document.getElementById('modalBody');
  if (mistakes.length === 0) {{
    // Fallback: show the raw items string
    body.innerHTML = '<div class="review-empty">该日无详细题目数据<br><span style="font-size:12px;color:var(--text-secondary);">' + escapeHtml(entry.items) + '</span></div>';
  }} else {{
    // Aggregate all knowledge points across the day's questions
    const kpMap = new Map();
    mistakes.forEach(m => {{
      (m.knowledge_points || []).forEach(kp => {{
        if (typeof kp === 'object' && kp) {{
          const key = kp.kp_id || kp.name;
          if (key) kpMap.set(key, kp.name || key);
        }} else {{
          kpMap.set(String(kp), String(kp));
        }}
      }});
    }});
    const kpChips = Array.from(kpMap.values())
      .map(name => '<span class="review-kp-chip">' + escapeHtml(name) + '</span>')
      .join('');
    const kpBlock = kpChips
      ? '<div class="review-kp-chips"><span class="kp-chip-label">涉及知识点：</span>' + kpChips + '</div>'
      : '';
    const itemsHtml = mistakes.map(renderReviewItem).join('');
    body.innerHTML = kpBlock + itemsHtml;
  }}

  document.getElementById('reviewModal').classList.add('active');
  document.body.style.overflow = 'hidden';
}}

function closeModal(ev) {{
  // Allow closing on overlay click or close button
  if (ev && ev.target && ev.target.id !== 'reviewModal' && !ev.target.classList.contains('modal-close')) return;
  document.getElementById('reviewModal').classList.remove('active');
  document.body.style.overflow = '';
}}

document.addEventListener('keydown', function(e) {{
  if (e.key === 'Escape') closeModal();
}});
'''

    # Target retention
    html = html.replace("{{TARGET_RETENTION}}", str(data.get("target_retention", 85)))

    # Suggestions
    suggestions = data.get("suggestions", [])
    sugg_html = ""
    for s in suggestions:
        priority_class = "danger" if s.get("priority") == "high" else "warning" if s.get("priority") == "medium" else "success"
        sugg_html += f'''<div style="border-left:3px solid var(--{priority_class});padding:12px 16px;margin-bottom:12px;background:var(--bg);border-radius:0 6px 6px 0;">
  <strong style="color:var(--{priority_class});">{s.get("title", "")}</strong>
  <p style="margin-top:4px;font-size:14px;color:var(--text-secondary);">{s.get("description", "")}</p>
</div>
'''
    html = html.replace("{{SUGGESTIONS}}", sugg_html)

    # Review detail data block (must come before chart scripts)
    html = html.replace("{{REVIEW_DATA_BLOCK}}", review_data_block)

    # Charts
    html = html.replace("{{CHART_SCRIPTS}}", generate_chart_scripts(data))

    return html


# ── Markdown Generator ─────────────────────────────────────────────────────

def generate_markdown(data: dict) -> str:
    """Generate Markdown report from analysis data."""
    lines = []

    lines.append(f"# {data.get('title', '错题分析报告')}")
    lines.append("")
    lines.append(f"**科目：** {data.get('subject', '未指定')} | **学段：** {data.get('stage', 'K12')} | **生成时间：** {data.get('generated_at', '')}")
    lines.append("")

    # Statistics
    lines.append("## 总览")
    lines.append("")
    stats = data.get("statistics", {})
    for item in stats.get("items", []):
        lines.append(f"- **{item['label']}：** {item['value']}")
    lines.append("")

    # Error Distribution
    lines.append("## 错误类型分布")
    lines.append("")
    error_dist = data.get("error_distribution", {})
    for et, count in error_dist.items():
        label = ERROR_TYPE_LABELS_CN.get(et, et)
        bar = "#" * count
        lines.append(f"- {label}：{bar} ({count})")
    lines.append("")

    # Knowledge Points
    lines.append("## 薄弱知识点")
    lines.append("")
    kp_data = data.get("kp_error_counts", {})
    for kp, count in sorted(kp_data.items(), key=lambda x: -x[1])[:10]:
        risk = "高" if count >= 3 else "中" if count >= 2 else "低"
        lines.append(f"- `[{risk}]` {kp} -- {count} 次错误")
    lines.append("")

    # Mistake Details
    lines.append("## 错题详情")
    lines.append("")
    for m in data.get("mistakes", []):
        lines.append(f"### #{m.get('id', '')} -- {m.get('subject', '')}")
        lines.append("")
        lines.append(f"**题目：** {m.get('question', '')}")
        lines.append("")
        lines.append(f"**错因分析：** {m.get('analysis', '')}")
        lines.append("")
        kp_list = m.get("knowledge_points", [])
        if kp_list and isinstance(kp_list[0], dict):
            kps = ", ".join(kp.get("name", str(kp)) for kp in kp_list)
        else:
            kps = ", ".join(str(kp) for kp in kp_list)
        if kps:
            lines.append(f"**知识点：** {kps}")
            lines.append("")
        errors = ", ".join(ERROR_TYPE_LABELS_CN.get(e, e) for e in m.get("error_types", []))
        if errors:
            lines.append(f"**错误类型：** {errors}")
            lines.append("")
        variants = m.get("variants", [])
        if variants:
            lines.append("**同类练习题：**")
            for i, v in enumerate(variants, 1):
                if isinstance(v, dict):
                    q_text = v.get("question", "")
                    a_text = v.get("answer", "")
                    if a_text:
                        lines.append(f"{i}. {q_text}")
                        lines.append(f"   - 参考答案：{a_text}")
                    else:
                        lines.append(f"{i}. {q_text}")
                else:
                    lines.append(f"{i}. {v}")
            lines.append("")
        lines.append("---")
        lines.append("")

    # Schedule
    lines.append("## 复习计划")
    lines.append("")
    sched_stats = data.get("schedule_statistics", {}).get("items", [])
    for item in sched_stats:
        lines.append(f"- **{item['label']}：** {item['value']}")
    lines.append("")
    lines.append("> 提示：HTML 报告中点击每个日期可查看当日涉及的错题详情、错因分析与同类练习题。")
    lines.append("")

    for entry in data.get("schedule_timeline", [])[:15]:
        lines.append(f"- **{entry['date']}（第 {entry.get('day', 0)} 天）：** {entry['items']}")
    lines.append("")

    # Suggestions
    lines.append("## 改进建议")
    lines.append("")
    for s in data.get("suggestions", []):
        priority_cn = {"high": "高", "medium": "中", "low": "低"}.get(s.get("priority", ""), s.get("priority", ""))
        lines.append(f"- **[{priority_cn}] {s.get('title', '')}** -- {s.get('description', '')}")
    lines.append("")

    lines.append("---")
    lines.append("*由 AI 错题教练 生成 · 由 WorkBuddy 提供技术支持*")

    return "\n".join(lines)


# ── CLI Entry Point ────────────────────────────────────────────────────────


def main():
    if len(sys.argv) < 3:
        print("Usage: python report_generator.py --input analysis.json --output report_name")
        print()
        print("Outputs: report_name.html and report_name.md")
        print()
        print("Input JSON structure:")
        sample = {
            "title": "Mistake Analysis Report",
            "subject": "Math",
            "stage": "Senior High",
            "generated_at": "2026-07-16 08:42",
            "statistics": {"items": [
                {"label": "Total Mistakes", "value": "15"},
                {"label": "Knowledge Points", "value": "8"},
            ]},
            "error_distribution": {"ERR_CALC": 5, "ERR_CONCEPT": 4, "ERR_GAP": 3},
            "error_by_subject": {"Math": {"ERR_CALC": 3, "ERR_CONCEPT": 2}},
            "kp_error_counts": {"Quadratic Functions": 4, "Trigonometry": 3},
            "retention_curve": [{"day": 0, "retention": 1.0}, {"day": 1, "retention": 0.9}],
            "mistakes": [{
                "id": "Q001", "subject": "Math", "question": "Solve x^2 - 5x + 6 = 0",
                "analysis": "Factoring error: (x-2)(x-3) instead of (x-2)(x-3)=0",
                "knowledge_points": ["Quadratic Equations"],
                "error_types": ["ERR_CALC"],
                "variants": ["Solve x^2 + x - 6 = 0", "Find roots of 2x^2 - 7x + 3 = 0"],
            }],
            "schedule_statistics": {"items": [
                {"label": "Review Sessions", "value": "12"},
                {"label": "Coverage", "value": "2026-07-17 ~ 2026-10-15"},
            ]},
            "schedule_timeline": [
                {"date": "2026-07-17", "items": "Review Q001, Q003, Q007 (5 items)"},
            ],
            "suggestions": [
                {"title": "Focus on Quadratic Functions", "description": "Review factoring techniques.", "priority": "high"},
            ],
            "target_retention": 85,
        }
        print(json.dumps(sample, indent=2, ensure_ascii=False))
        sys.exit(1)

    args = sys.argv[1:]
    input_path = None
    output_base = None

    i = 0
    while i < len(args):
        if args[i] == "--input" and i + 1 < len(args):
            input_path = args[i + 1]
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output_base = args[i + 1]
            i += 2
        else:
            i += 1

    if not input_path or not output_base:
        print("Error: --input and --output are required", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Generate HTML
    html = generate_html(data)
    html_path = f"{output_base}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML report: {html_path}")

    # Generate Markdown
    md = generate_markdown(data)
    md_path = f"{output_base}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Markdown report: {md_path}")

    print("Done.")


if __name__ == "__main__":
    main()
