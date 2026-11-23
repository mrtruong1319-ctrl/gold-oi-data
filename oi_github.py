#!/usr/bin/env python3
"""Phan tich OI vang COMEX day du tu GitHub (Hark cap nhat).
Chay: python3 oi_github.py   (chi can Python 3, khong cai them gi)"""
import csv, io, json, urllib.request
BASE = "https://raw.githubusercontent.com/mrtruong1319-ctrl/gold-oi-data/main/data/"

def get(name):
    return urllib.request.urlopen(BASE + name, timeout=20).read().decode()

def f(x):
    try: return float(x)
    except: return None

def read4(pc, oc):
    if pc is None or oc is None: return "-"
    if pc < 0 and oc < 0: return "dong Long"
    if pc < 0 and oc > 0: return "Short moi"
    if pc > 0 and oc > 0: return "Long moi"
    return "dong Short"

def analyse():
    d = json.loads(get("latest.json"))
    daily = list(csv.DictReader(io.StringIO(get("cme_gc_oi_daily.csv"))))
    cot = list(csv.DictReader(io.StringIO(get("cot_gc_weekly.csv"))))
    c, s, pc, oc = d["gc_close"], d["sigma_usd"], d["price_change"], d["oi_change"]
    out = [f"📊 OI VANG COMEX {d['last_session']} ({'chot' if d['report']=='F' else 'so bo'}) | cap nhat {d.get('updated_vn','')}"]

    # 1. Phien moi nhat
    out.append(f"⚖️ OI {d['oi_total']:,} ({oc:+,}) | GC {c:,.1f} ({pc:+.1f})")
    out.append(f"🔁 Roll: Dec {d['chg_dec26']:+,} / Feb {d['chg_feb27']:+,} -> net {d['roll_net']:+,}")
    real = "THAT (khong chi la roll)" if abs(d['roll_net']) >= abs(oc) * 0.5 else "phan lon do roll"
    out.append(f"🔎 {read4(pc, d['roll_net'])} - {real}")

    # 2. Chuoi phien & 5 phien
    rows = [r for r in daily if f(r["price_change"]) is not None]
    streak, kind = 0, read4(pc, oc)
    for r in reversed(rows):
        if read4(f(r["price_change"]), f(r["oi_change"])) == kind: streak += 1
        else: break
    last5 = rows[-5:]
    dp = sum(f(r["price_change"]) for r in last5)
    doi = sum(f(r["oi_change"]) for r in last5)
    cnt = {}
    for r in last5:
        k = read4(f(r["price_change"]), f(r["oi_change"])); cnt[k] = cnt.get(k, 0) + 1
    out.append(f"📈 Chuoi: {streak} phien '{kind}' lien tiep")
    out.append(f"🗓️ 5 phien: gia {dp:+.1f}, OI {doi:+,.0f} -> {read4(dp, doi)} | " + ", ".join(f"{k} {v}" for k, v in cnt.items()))

    # 3. Vi the dai han (COT)
    if cot:
        oi_peak = max(cot, key=lambda r: f(r["oi"]))
        mm_peak = max(cot, key=lambda r: f(r["mm_net"]))
        lc = cot[-1]
        pct_oi = d["oi_total"] / f(oi_peak["oi"]) * 100
        pct_mm = f(lc["mm_net"]) / f(mm_peak["mm_net"]) * 100
        out.append(f"🏦 OI = {pct_oi:.0f}% dinh 6T ({int(f(oi_peak['oi'])):,} ngay {oi_peak['date']})")
        out.append(f"🐋 MM net {int(f(lc['mm_net'])):,} ({lc['date']}) = {pct_mm:.0f}% dinh {int(f(mm_peak['mm_net'])):,}")
        if pct_mm > 60: out.append("   -> Quy van con nhieu Long, du dia xa tiep con lon")
        elif pct_mm < 30: out.append("   -> Long da xa gan het, de co hoi phuc ky thuat")
        else: out.append("   -> Long da xa mot phan, trung tinh")

    # 4. Moc sigma
    out.append(f"🎯 Moc (sigma ~${s}, GVZ {d.get('gvz','-')}): +2σ {c+2*s:,.0f} | +1σ {c+s:,.0f} | 0 {c:,.0f} | -1σ {c-s:,.0f} | -2σ {c-2*s:,.0f}")

    # 5. Phuong an
    if pc < 0 and oc < 0:
        bias = "Long dang cat lo: cho hoi len +1σ bi tu choi moi Sell, khong duoi Sell day"
        plan = [f"Sell A: H1 dong duoi {c+s:,.0f} sau khi cham tren -> SL {c+s+s*0.6:,.0f}, TP {c+s/2:,.0f} roi {c:,.0f}",
                f"Sell B: len {c+2*s:,.0f} bi dap -> SL {c+2*s+s/4:,.0f}, TP {c+s:,.0f}",
                f"Buy: chi khi H1 dong lai tren {c-s:,.0f} sau khi thung -> SL {c-1.5*s:,.0f}, TP {c:,.0f}"]
    elif pc < 0 and oc > 0:
        bias = "Short moi vao: uu tien Sell khi hoi, han che Buy"
        plan = [f"Sell: hoi {c+s/2:,.0f}-{c+s:,.0f} -> SL {c+1.5*s:,.0f}, TP {c-s/2:,.0f}"]
    elif pc > 0 and oc > 0:
        bias = "Long moi vao: uu tien Buy khi chinh, han che Sell"
        plan = [f"Buy: chinh {c-s:,.0f}-{c-s/2:,.0f} -> SL {c-1.5*s:,.0f}, TP {c+s/2:,.0f}"]
    else:
        bias = "Short dang dong: Buy khi chinh, Sell chi o +1σ co tu choi"
        plan = [f"Buy: chinh {c-s/2:,.0f} -> SL {c-s:,.0f}, TP {c+s/2:,.0f}",
                f"Sell: chi o {c+s:,.0f} co nen tu choi -> SL {c+1.5*s:,.0f}"]
    out.append(f"🧭 {bias}")
    out += ["   " + p for p in plan]
    out.append("🛑 0.01 lot (FTMO 10k), toi da 2 lenh/ngay. Khung tham khao, chua backtest.")
    if d["report"] == "P": out.append("⚠️ So lieu so bo, ban chot ra ~23:00 VN.")
    return "\n".join(out)

if __name__ == "__main__":
    print(analyse())
