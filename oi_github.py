#!/usr/bin/env python3
"""Doc du lieu OI vang tu GitHub (Hark cap nhat) va dua ra phuong an theo sigma.
Sua GH_RAW neu ten repo khac. Chay: python3 oi_github.py --once"""
import json, sys, urllib.request
GH_RAW = "https://raw.githubusercontent.com/mrtruong1319-ctrl/gold-oi-data/main/data/latest.json"
def plan(d):
    c, s = d["gc_close"], d["sigma_usd"]
    up, dn = c + s, c - s
    pc, oc = d["price_change"], d["oi_change"]
    if pc < 0 and oc < 0: bias = "Long dang cat lo: cho hoi len +0.5 den +1 sigma moi Sell, khong duoi Sell day"
    elif pc < 0 and oc > 0: bias = "Short moi vao: uu tien Sell khi hoi, han che Buy"
    elif pc > 0 and oc > 0: bias = "Long moi vao: uu tien Buy khi chinh, han che Sell"
    else: bias = "Short dang dong: Buy khi chinh, Sell chi o +1 sigma co tu choi"
    return "\n".join([
        f"📊 OI VANG COMEX {d['last_session']} ({'chot' if d['report']=='F' else 'so bo'})",
        f"⚖️ OI {d['oi_total']:,} ({oc:+,}) | Dec {d['chg_dec26']:+,} Feb {d['chg_feb27']:+,} | roll net {d['roll_net']:+,}",
        f"💰 GC {c:,.1f} ({pc:+.1f}) | sigma ~${s}",
        f"🔎 {d['reading']}",
        f"🎯 Sell: H1 dong lai duoi {up:,.0f} (+1σ) | Buy: H1 dong lai tren {dn:,.0f} (-1σ)",
        f"🛑 Stop 0.5σ (~${s/2:.0f}), chot ve {c:,.0f}, 0.01 lot",
        f"🧭 {bias}",
        "Chi la khung tham khao, chua backtest."])
if __name__ == "__main__":
    d = json.load(urllib.request.urlopen(GH_RAW, timeout=20))
    print(plan(d))
