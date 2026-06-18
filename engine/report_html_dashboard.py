"""
HTML Dashboard Generator
Generates a beautiful self-contained HTML dashboard from reconciliation results.
"""
import json
from datetime import datetime


def build_html_dashboard(api_en, results, start_date, end_date, free_count=0):
    """Generate a complete HTML dashboard from reconciliation results."""
    try:
        from engine.report_summary import compute_summary_stats
        from engine.report_phase_summary import build_phase1_summary, build_phase2_summary
        import pandas as pd

        s = compute_summary_stats(api_en, results)
        if not s:
            return None

        op = round(s["orch_orders"] / max(s["api_orders"], 1) * 100, 1)
        pp = round(s["psp_orders"]  / max(s["api_orders"], 1) * 100, 1)

        p1r = build_phase1_summary(api_en, results)
        p2r = build_phase2_summary(results)

        def fmt_num(v):
            try: return f"{int(v):,}"
            except: return str(v)

        def fmt_amt(v):
            try: return f"${float(v):,.2f}"
            except: return str(v)

        def fmt_pct(v):
            try:
                p = float(v)
                c = "#00875a" if p >= 95 else "#e65100" if p >= 85 else "#e53935"
                return f'<span style="color:{c};font-weight:700">{p:.1f}%</span>'
            except: return str(v)

        def diff_color(v):
            try:
                f = float(str(v).replace(",","").replace("$",""))
                if f > 0: return f'<span style="color:#e53935;font-weight:700">{v}</span>'
                return str(v)
            except: return str(v)

        # Build Phase 1 table rows
        p1_rows = ""
        if p1r:
            for r in p1r:
                p1_rows += f"""
                <tr>
                    <td class="nm">{r["Bank Name"]}</td>
                    <td>{fmt_num(r["API Qty"])}</td>
                    <td>{fmt_amt(r["API Amt"])}</td>
                    <td>{fmt_num(r["Bank Qty"])}</td>
                    <td>{fmt_amt(r["Bank Amt"])}</td>
                    <td style="color:#e53935;font-weight:700">{fmt_num(r["Mismatch Qty"])}</td>
                    <td style="color:#e53935;font-weight:700">{fmt_amt(r["Mismatch Amt"])}</td>
                    <td style="color:#e53935;font-weight:700">{fmt_num(r["Not in Bank Qty"])}</td>
                    <td style="color:#e53935;font-weight:700">{fmt_amt(r["Not in Bank Amt"])}</td>
                    <td>{fmt_num(r["Extra in Bank Qty"])}</td>
                    <td>{fmt_pct(r["Match %"])}</td>
                </tr>"""

        # Build Phase 2 table rows
        p2_rows = ""
        if p2r:
            for r in p2r:
                p2_rows += f"""
                <tr>
                    <td class="nm">{r["PSP Name"]}</td>
                    <td>{fmt_num(r["Orchestrator Qty"])}</td>
                    <td>{fmt_amt(r["Orchestrator Amt"])}</td>
                    <td>{fmt_num(r["PSP Qty"])}</td>
                    <td>{fmt_amt(r["PSP Amt"])}</td>
                    <td style="color:#e53935;font-weight:700">{fmt_num(r["Mismatch Qty"])}</td>
                    <td style="color:#e53935;font-weight:700">{fmt_amt(r["Mismatch Amt"])}</td>
                    <td style="color:#e53935;font-weight:700">{fmt_num(r["Not in PSP Qty"])}</td>
                    <td style="color:#e53935;font-weight:700">{fmt_amt(r["Not in PSP Amt"])}</td>
                    <td>{fmt_num(r["Extra in PSP Qty"])}</td>
                    <td>{fmt_pct(r["Match %"])}</td>
                </tr>"""

        updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FundedNext — Revenue Reconciliation Dashboard</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: #f0f2f7; color: #1e293b; }}
  .header {{ background: linear-gradient(135deg, #0a1628, #1a2540);
             padding: 24px 40px; display: flex; align-items: center;
             justify-content: space-between; }}
  .logo {{ display: flex; align-items: center; gap: 14px; }}
  .mark {{ width: 48px; height: 48px; background: #f5a623; border-radius: 10px;
           font-weight: 900; font-size: 20px; color: #0a1628;
           display: flex; align-items: center; justify-content: center; }}
  .brand {{ color: #fff; font-size: 22px; font-weight: 800; }}
  .subtitle {{ color: rgba(255,255,255,.45); font-size: 11px;
               letter-spacing: 1.5px; text-transform: uppercase; }}
  .period {{ text-align: right; }}
  .period-label {{ color: rgba(255,255,255,.5); font-size: 11px; }}
  .period-value {{ color: #f5a623; font-size: 16px; font-weight: 700; }}
  .updated {{ color: rgba(255,255,255,.35); font-size: 10px; margin-top: 4px; }}
  .container {{ max-width: 1400px; margin: 0 auto; padding: 32px 24px; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(5, 1fr);
               gap: 16px; margin-bottom: 32px; }}
  .kpi {{ background: #fff; border-radius: 12px; padding: 20px;
          text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,.06);
          border: 1px solid #e2e8f0; }}
  .kpi-val {{ font-size: 28px; font-weight: 800; color: #0a1628; }}
  .kpi-lbl {{ font-size: 10px; color: #94a3b8; margin-top: 6px;
              text-transform: uppercase; letter-spacing: .8px; font-weight: 600; }}
  .kpi-sub {{ font-size: 12px; font-weight: 700; margin-top: 4px; }}
  .section {{ background: #fff; border-radius: 12px; padding: 24px;
              margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,.06);
              border: 1px solid #e2e8f0; }}
  .section-title {{ font-size: 14px; font-weight: 700; color: #0a1628;
                   padding: 10px 14px; border-left: 4px solid #f5a623;
                   background: rgba(245,166,35,.05); border-radius: 0 6px 6px 0;
                   margin-bottom: 16px; }}
  .tbl-wrap {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
  th {{ background: #0a1628; color: #fff; padding: 10px 12px;
        text-align: center; white-space: nowrap; font-size: 11px; font-weight: 600; }}
  th:first-child {{ text-align: left; }}
  td {{ padding: 9px 12px; text-align: right; border-bottom: 1px solid #f1f5f9;
        white-space: nowrap; }}
  td.nm {{ text-align: left; font-weight: 700; color: #0a1628;
           background: #f8fafc; }}
  tr:hover td {{ background: #f1f5f9; }}
  tr:nth-child(even) td {{ background: #fafbfe; }}
  tr:nth-child(even) td.nm {{ background: #f5f7fc; }}
  tr:hover td.nm {{ background: #eef2ff; }}
  .free-note {{ background: #fffbeb; border: 1px solid #fde68a;
                border-radius: 8px; padding: 10px 16px; margin-bottom: 24px;
                font-size: 13px; color: #92400e; }}
  .footer {{ text-align: center; padding: 24px; color: #94a3b8; font-size: 12px; }}
  @media (max-width: 768px) {{
    .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .header {{ flex-direction: column; gap: 16px; text-align: center; }}
  }}
</style>
</head>
<body>

<div class="header">
  <div class="logo">
    <div class="mark">FN</div>
    <div>
      <div class="brand">FundedNext</div>
      <div class="subtitle">Revenue Reconciliation Dashboard</div>
    </div>
  </div>
  <div class="period">
    <div class="period-label">Reconciliation Period</div>
    <div class="period-value">{start_date} → {end_date}</div>
    <div class="updated">Last updated: {updated}</div>
  </div>
</div>

<div class="container">

  <div class="kpi-grid">
    <div class="kpi">
      <div class="kpi-val">{fmt_num(s["api_orders"])}</div>
      <div class="kpi-lbl">API Orders</div>
      <div class="kpi-sub" style="color:#0a1628">{fmt_amt(s["api_rev"])}</div>
    </div>
    <div class="kpi">
      <div class="kpi-val" style="color:{"#00875a" if op>=95 else "#e65100"}">{fmt_num(s["orch_orders"])}</div>
      <div class="kpi-lbl">Orchestrator</div>
      <div class="kpi-sub" style="color:{"#00875a" if op>=95 else "#e65100"}">{op}% · {fmt_amt(s["orch_rev"])}</div>
    </div>
    <div class="kpi">
      <div class="kpi-val" style="color:{"#00875a" if pp>=95 else "#e65100"}">{fmt_num(s["psp_orders"])}</div>
      <div class="kpi-lbl">PSP Reconciled</div>
      <div class="kpi-sub" style="color:{"#00875a" if pp>=95 else "#e65100"}">{pp}% · {fmt_amt(s["psp_rev"])}</div>
    </div>
    <div class="kpi">
      <div class="kpi-val" style="color:#e53935">{fmt_num(s["diff_orch"])}</div>
      <div class="kpi-lbl">Diff (Orch)</div>
      <div class="kpi-sub" style="color:#e53935">{fmt_amt(s["diff_orch_rev"])}</div>
    </div>
    <div class="kpi">
      <div class="kpi-val" style="color:#e53935">{fmt_num(s["diff_psp"])}</div>
      <div class="kpi-lbl">Diff (PSP)</div>
      <div class="kpi-sub" style="color:#e53935">{fmt_amt(s["diff_psp_rev"])}</div>
    </div>
  </div>

  {"" if free_count == 0 else f'<div class="free-note">ℹ️ {free_count:,} free accounts excluded from reconciliation (100% Discount, Free Account, Internal Testing, etc.)</div>'}

  <div class="section">
    <div class="section-title">Phase 1 — API vs Bank</div>
    <div class="tbl-wrap">
      <table>
        <thead><tr>
          <th>Bank</th><th>API Qty</th><th>API Amt</th>
          <th>Bank Qty</th><th>Bank Amt</th>
          <th>Mismatch Qty</th><th>Mismatch Amt</th>
          <th>Not in Bank Qty</th><th>Not in Bank Amt</th>
          <th>Extra Qty</th><th>Match %</th>
        </tr></thead>
        <tbody>{p1_rows}</tbody>
      </table>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Phase 2 — Orchestrator vs PSP</div>
    <div class="tbl-wrap">
      <table>
        <thead><tr>
          <th>PSP</th><th>Orch Qty</th><th>Orch Amt</th>
          <th>PSP Qty</th><th>PSP Amt</th>
          <th>Mismatch Qty</th><th>Mismatch Amt</th>
          <th>Not in PSP Qty</th><th>Not in PSP Amt</th>
          <th>Extra Qty</th><th>Match %</th>
        </tr></thead>
        <tbody>{p2_rows}</tbody>
      </table>
    </div>
  </div>

</div>

<div class="footer">
  FundedNext Revenue Reconciliation Portal · Generated {updated}
</div>

</body>
</html>"""

        return html

    except Exception as e:
        return None
