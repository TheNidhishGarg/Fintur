"""
=============================================================
ETF SIP PORTFOLIO BACKTESTER
=============================================================
- Reads ETF catalogue from ETFS.json (dynamic, never hardcoded)
- Uses technical.py for ALL price data (latest + historical)
- Auto-selects best affordable ETF per asset class
- Runs 5-year monthly SIP backtest
- No fractional units (floor division)
=============================================================
"""

import json
import os
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(BASE_DIR, "app", "tools")
ETFS_FILE = os.path.join(BASE_DIR, "ETFS.json")

if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

# Import technical.py bypassing @tool decorator
from technical import fetch_technical_data
_fetch = fetch_technical_data.func


# ── Load ETFS.json dynamically ────────────────────────────────────────────────

def load_etf_catalogue() -> dict:
    """Load ETFS.json → {category_name: [etf_list]}"""
    with open(ETFS_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    catalogue = {}
    for cat in raw.get("categories", []):
        name = cat["category_name"]
        etfs = cat.get("etfs", [])
        if etfs:
            catalogue[name] = [
                {
                    "rank":           e["rank"],
                    "name":           e["full_name"],
                    "ticker":         e["ticker"],
                    "pick_type":      e.get("pick_type", ""),
                    "liquidity":      e.get("liquidity_flag", ""),
                    "aum_cr":         e.get("aum_cr", 0),
                    "expense_ratio":  e.get("expense_ratio_pct"),
                    "tracking_error": e.get("tracking_error_pct"),
                    "returns":        e.get("returns_pct", {}),
                    "reason":         e.get("reason_for_rank", ""),
                }
                for e in etfs
            ]
    return catalogue


# ── Alias map: ARJUN keys → ETFS.json category names ─────────────────────────

ASSET_ALIASES = {
    # Large Cap
    "large cap":                      "Large Cap Equity",
    "large-cap":                      "Large Cap Equity",
    "largecap":                       "Large Cap Equity",
    "large cap equity":               "Large Cap Equity",
    "large cap equity etf":           "Large Cap Equity",
    "large cap etf":                  "Large Cap Equity",
    # Large & Mid Cap
    "large & mid cap":                "Large & Mid Cap",
    "large and mid cap":              "Large & Mid Cap",
    "large+mid cap":                  "Large & Mid Cap",
    "large mid cap":                  "Large & Mid Cap",
    "large & mid cap etf":            "Large & Mid Cap",
    # Mid Cap
    "mid cap":                        "Mid Cap",
    "mid-cap":                        "Mid Cap",
    "midcap":                         "Mid Cap",
    "mid cap etf":                    "Mid Cap",
    "mid cap equity etf":             "Mid Cap",
    # Small Cap
    "small cap":                      "Small Cap",
    "small-cap":                      "Small Cap",
    "smallcap":                       "Small Cap",
    "small cap etf":                  "Small Cap",
    "small cap equity etf":           "Small Cap",
    # Flexi / Multi Cap
    "flexi cap":                      "Flexi/Multi Cap",
    "flexi-cap":                      "Flexi/Multi Cap",
    "flexicap":                       "Flexi/Multi Cap",
    "multi cap":                      "Flexi/Multi Cap",
    "multicap":                       "Flexi/Multi Cap",
    "flexi/multi cap":                "Flexi/Multi Cap",
    "flexi cap etf":                  "Flexi/Multi Cap",
    "flexi cap equity etf":           "Flexi/Multi Cap",
    "multi cap etf":                  "Flexi/Multi Cap",
    # Value / Contra
    "value":                          "Value / Contra",
    "contra":                         "Value / Contra",
    "value funds":                    "Value / Contra",
    "value / contra":                 "Value / Contra",
    "value/contra":                   "Value / Contra",
    "value etf":                      "Value / Contra",
    # Debt / Liquid
    "debt":                           "Debt / Liquid",
    "liquid":                         "Debt / Liquid",
    "debt funds":                     "Debt / Liquid",
    "liquid funds":                   "Debt / Liquid",
    "overnight":                      "Debt / Liquid",
    "debt / liquid":                  "Debt / Liquid",
    "debt etf":                       "Debt / Liquid",
    "liquid etf":                     "Debt / Liquid",
    "debt fund":                      "Debt / Liquid",
    # Short Duration
    "short duration":                 "Short Duration Debt",
    "short duration debt":            "Short Duration Debt",
    "short-duration debt":            "Short Duration Debt",
    "short duration etf":             "Short Duration Debt",
    # Corporate Bond
    "corporate bond":                 "Corporate Bond",
    "corporate bond funds":           "Corporate Bond",
    "corporate bond etf":             "Corporate Bond",
    # Gilt / Govt Securities
    "gilt":                           "Government Securities / Gilt",
    "government securities":          "Government Securities / Gilt",
    "g-sec":                          "Government Securities / Gilt",
    "gsec":                           "Government Securities / Gilt",
    "government securities etf":      "Government Securities / Gilt",
    "gilt etf":                       "Government Securities / Gilt",
    # Gold
    "gold":                           "Gold",
    "gold etf":                       "Gold",
    # Silver
    "silver":                         "Silver",
    "silver/commodities":             "Silver",
    "commodities":                    "Silver",
    "silver etf":                     "Silver",
    # International
    "international equity":           "International Equity",
    "international":                  "International Equity",
    "global equity":                  "International Equity",
    "us equity":                      "International Equity",
    "international equity etf":       "International Equity",
    "global equity etf":              "International Equity",
    # REITs
    "reit":                           "REIT (Real Estate Investment Trust)",
    "reits":                          "REIT (Real Estate Investment Trust)",
    "real estate":                    "REIT (Real Estate Investment Trust)",
    "reit etf":                       "REIT (Real Estate Investment Trust)",
    "reits etf":                      "REIT (Real Estate Investment Trust)",
    "thematic":               "Thematic / Sectoral",
    "sectoral":               "Thematic / Sectoral",
    "thematic/sectoral":      "Thematic / Sectoral",
    "thematic / sectoral":    "Thematic / Sectoral",
    "hybrid":                 None,   # No ETF equivalent
    "balanced advantage":     None,
    "elss":                   None,   # No ETF equivalent
}

LIQUIDITY_EMOJI = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}


def _normalise(raw: str) -> str:
    """
    Normalise asset class name from ARJUN JSON to ETFS.json category key.
    Strips common suffixes ARJUN tends to append (ETF, Fund, Funds, equity etc.)
    then does alias lookup.
    """
    key = raw.strip().lower()

    # Strip suffixes ARJUN commonly appends
    for suffix in [" etf", " etfs", " fund", " funds"]:
        if key.endswith(suffix):
            key = key[: -len(suffix)].strip()
            break   # strip only one suffix

    # Direct alias lookup
    if key in ASSET_ALIASES:
        return ASSET_ALIASES[key]

    # Try original (without suffix stripped) as fallback
    original = raw.strip().lower()
    if original in ASSET_ALIASES:
        return ASSET_ALIASES[original]

    # Last resort: return stripped title-cased key so catalogue lookup can try
    return raw.strip()


# ── Price fetching via technical.py ──────────────────────────────────────────

def get_latest_price(ticker: str) -> float:
    """Fetch latest closing price for an ETF via technical.py."""
    try:
        result = _fetch(ticker=ticker, period="5d")
        if "error" in result:
            return 0.0
        daily = result.get("Daily_Data", [])
        if not daily:
            return 0.0
        return float(daily[-1].get("Close") or 0.0)
    except Exception as e:
        print(f"    ⚠️  Price fetch failed for {ticker}: {e}")
        return 0.0


def get_price_history(ticker: str, start_date: str, end_date: str) -> list:
    """Fetch daily price history for backtesting via technical.py."""
    try:
        result = _fetch(ticker=ticker, start_date=start_date, end_date=end_date)
        if "error" in result:
            return []
        return result.get("Daily_Data", [])
    except Exception as e:
        print(f"    ⚠️  History fetch failed for {ticker}: {e}")
        return []


# ── Auto ETF Selection ────────────────────────────────────────────────────────

def auto_select_etfs(allocation: dict, monthly_sip: float) -> dict:
    """
    For each asset class:
    1. Load options from ETFS.json
    2. Fetch live price via technical.py
    3. Pick best rank ETF where floor(monthly_amount / price) >= 1
    4. If all too expensive → pick cheapest available + warn user
    5. Display full comparison table to user

    Returns: {asset_class: {ticker, name, live_price, units_per_month, ...}}
    """
    catalogue = load_etf_catalogue()
    selections = {}

    print("\n" + "="*68)
    print("   ETF SELECTION — Best affordable ETFs auto-selected")
    print("   Live prices fetched from NSE via technical.py")
    print("="*68)

    for asset_class, pct in allocation.items():
        if pct == 0:
            continue

        cat_key = _normalise(asset_class)
        if cat_key is None:
            print(f"\n  ⚠️  {asset_class}: No ETF equivalent (Hybrid/ELSS) — skipping")
            continue

        options = catalogue.get(cat_key, [])
        if not options:
            print(f"\n  ⚠️  {asset_class}: Not found in ETF catalogue — skipping")
            continue

        monthly_amount = monthly_sip * (pct / 100)

        print(f"\n  📊 {asset_class.upper()}  ({pct}% = ₹{monthly_amount:,.0f}/month)")
        print(f"  {'─'*64}")

        # Fetch live prices for all options
        priced = []
        for opt in options:
            price = get_latest_price(opt["ticker"])
            units = int(monthly_amount // price) if price > 0 else 0
            priced.append({**opt, "live_price": price, "units_per_month": units})

            liq     = LIQUIDITY_EMOJI.get(opt["liquidity"], "⚪")
            ret     = opt["returns"]
            ret_str = f"1Y:{ret.get('1Y','?')}%"
            if ret.get("3Y"):
                ret_str += f" 3Y:{ret['3Y']}%"
            if ret.get("5Y"):
                ret_str += f" 5Y:{ret['5Y']}%"
            afford  = f"✅ {units} units/mo" if units >= 1 else "❌ Too expensive"

            print(f"  [{opt['rank']}] {opt['name']}  [{opt['ticker']}]  {opt['pick_type']}")
            print(f"       {liq} {opt['liquidity']} | AUM ₹{opt['aum_cr']:,}Cr | "
                  f"ER:{opt.get('expense_ratio','?')}% | {ret_str}")
            print(f"       Live Price: ₹{price:,.2f}  →  {afford}")

        # Pick best affordable rank (1 → 2 → 3)
        chosen = None
        for opt in priced:
            if opt["units_per_month"] >= 1:
                chosen = opt
                break

        if chosen is None:
            # All too expensive — pick cheapest and warn
            valid = [o for o in priced if o["live_price"] > 0]
            if valid:
                chosen = min(valid, key=lambda x: x["live_price"])
                print(f"\n  ⚠️  All ETFs above ₹{monthly_amount:,.0f}/month allocation.")
                print(f"  ℹ️  Selected cheapest: {chosen['name']} @ ₹{chosen['live_price']:,.2f}")
                print(f"  ℹ️  You'll buy 0 units this month. Increase SIP or reduce diversification.")
            else:
                print(f"\n  ❌ Could not fetch prices for any {asset_class} ETF — skipping")
                continue

        selections[asset_class] = {
            "name":            chosen["name"],
            "ticker":          chosen["ticker"],
            "live_price":      chosen["live_price"],
            "monthly_amount":  round(monthly_amount, 2),
            "units_per_month": chosen["units_per_month"],
            "pick_type":       chosen["pick_type"],
            "liquidity":       chosen["liquidity"],
            "aum_cr":          chosen["aum_cr"],
            "expense_ratio":   chosen["expense_ratio"],
            "returns":         chosen["returns"],
            "reason":          chosen["reason"],
        }

        liq = LIQUIDITY_EMOJI.get(chosen["liquidity"], "⚪")
        print(f"\n  ✅ AUTO-SELECTED: {chosen['name']}  ({chosen['ticker']})")
        print(f"     {liq} {chosen['liquidity']} | "
              f"₹{chosen['live_price']:,.2f}/unit | "
              f"{chosen['units_per_month']} units/month | "
              f"{chosen['pick_type']}")

    return selections


# ── Build monthly price series from daily records ─────────────────────────────

def _build_monthly_series(daily_records: list) -> dict:
    """First trading day of each month → {YYYY-MM: price}"""
    monthly = {}
    for rec in daily_records:
        date_str = str(rec.get("Date", ""))[:10]
        ym = date_str[:7]
        if ym not in monthly:
            price = rec.get("Close")
            if price is not None:
                monthly[ym] = float(price)
    return monthly


def _ffill_price(price_history: dict, asset_class: str, ym: str) -> float:
    """Get price for YYYY-MM, forward-filling if missing."""
    ph = price_history[asset_class]
    if ym in ph:
        return ph[ym]
    prior = [m for m in sorted(ph.keys()) if m <= ym]
    return ph[prior[-1]] if prior else 0.0


# ── Core Backtest Engine ──────────────────────────────────────────────────────

def run_backtest(
    allocation: dict,
    etf_selections: dict,
    monthly_sip: float,
    years: int = 5,
) -> dict:
    """
    Monthly SIP backtest using technical.py price history.

    Each month:
    - Invest (allocation% × SIP) in each ETF
    - Buy floor(amount / price) units — no fractional units
    - Higher price → fewer units next month (real SIP behaviour)
    - Track total invested, portfolio value, gains
    """
    end_dt    = datetime.today()
    start_dt  = end_dt - relativedelta(years=years)
    start_str = start_dt.strftime("%Y-%m-%d")
    end_str   = end_dt.strftime("%Y-%m-%d")

    print(f"\n  📅 Period: {start_dt.strftime('%b %Y')} → {end_dt.strftime('%b %Y')}")
    print(f"  💰 Monthly SIP: ₹{monthly_sip:,.0f}")
    print(f"  📥 Fetching 5-year history via technical.py...\n")

    # Fetch price history for each ETF
    price_history = {}
    for asset_class, info in etf_selections.items():
        ticker = info["ticker"]
        print(f"    {asset_class} → {ticker}")
        daily = get_price_history(ticker, start_str, end_str)
        if daily:
            monthly = _build_monthly_series(daily)
            if monthly:
                price_history[asset_class] = monthly
                print(f"    ✅ {len(monthly)} months fetched")
            else:
                print(f"    ⚠️  Monthly series empty for {ticker}")
        else:
            print(f"    ⚠️  No data for {ticker}")

    if not price_history:
        return {"error": "No historical price data available."}

    active = list(price_history.keys())

    # Normalise allocation to active classes only
    raw_alloc = {k: allocation.get(k, 0) for k in active}
    total_pct = sum(raw_alloc.values())
    if total_pct == 0:
        return {"error": "Allocation sum is 0."}
    norm_alloc = {k: v / total_pct for k, v in raw_alloc.items()}

    # Common monthly dates across all ETFs
    common_months = sorted(set.intersection(*[set(price_history[k].keys()) for k in active]))
    if not common_months:
        common_months = sorted(set.union(*[set(price_history[k].keys()) for k in active]))

    # Monthly simulation
    units_held     = {k: 0.0 for k in active}
    total_invested = 0.0
    monthly_records = []

    for ym in common_months:
        month_invested = 0.0

        for asset_class in active:
            price = _ffill_price(price_history, asset_class, ym)
            if price <= 0:
                continue
            amount = monthly_sip * norm_alloc[asset_class]
            units  = int(amount // price)     # floor — no fractional units
            units_held[asset_class] += units
            month_invested += units * price

        total_invested += month_invested

        portfolio_value = sum(
            units_held[k] * _ffill_price(price_history, k, ym)
            for k in active
        )

        monthly_records.append({
            "date":            ym,
            "total_invested":  round(total_invested, 2),
            "portfolio_value": round(portfolio_value, 2),
            "gains":           round(portfolio_value - total_invested, 2),
        })

    if not monthly_records:
        return {"error": "No monthly records generated."}

    # Year-wise summary
    yearly_summary = {}
    for rec in monthly_records:
        year = rec["date"][:4]
        yearly_summary[year] = {
            "total_invested":      rec["total_invested"],
            "portfolio_value":     rec["portfolio_value"],
            "gains":               rec["gains"],
            "absolute_return_pct": round(
                (rec["gains"] / rec["total_invested"]) * 100, 2
            ) if rec["total_invested"] > 0 else 0.0,
        }

    final     = monthly_records[-1]
    total_inv = final["total_invested"]
    final_val = final["portfolio_value"]
    gain      = final["gains"]
    abs_ret   = round((gain / total_inv) * 100, 2) if total_inv > 0 else 0.0
    xirr_val  = _calc_xirr(monthly_records)

    # Final holdings
    last_ym = common_months[-1]
    final_holdings = {}
    for asset_class in active:
        info  = etf_selections.get(asset_class, {})
        price = _ffill_price(price_history, asset_class, last_ym)
        units = units_held[asset_class]
        final_holdings[asset_class] = {
            "ticker":         info.get("ticker", ""),
            "name":           info.get("name", ""),
            "units_held":     int(units),
            "current_price":  round(price, 2),
            "current_value":  round(units * price, 2),
            "allocation_pct": round(norm_alloc[asset_class] * 100, 1),
        }

    return {
        "summary": {
            "backtest_period":       f"{start_dt.strftime('%b %Y')} to {end_dt.strftime('%b %Y')}",
            "years":                 years,
            "monthly_sip":           monthly_sip,
            "total_invested":        round(total_inv, 2),
            "final_portfolio_value": round(final_val, 2),
            "total_gains":           round(gain, 2),
            "absolute_return_pct":   abs_ret,
            "xirr_pct":              xirr_val,
            "total_months":          len(monthly_records),
        },
        "yearly_summary":  yearly_summary,
        "final_holdings":  final_holdings,
        "monthly_detail":  monthly_records,
    }


def _calc_xirr(monthly_records: list) -> float:
    try:
        from scipy.optimize import brentq
        prev_inv  = 0.0
        cashflows = []
        dates_cf  = []
        for rec in monthly_records:
            month_inv = rec["total_invested"] - prev_inv
            cashflows.append(-month_inv)
            dates_cf.append(datetime.strptime(rec["date"] + "-01", "%Y-%m-%d"))
            prev_inv = rec["total_invested"]
        cashflows[-1] += monthly_records[-1]["portfolio_value"]

        def npv(rate):
            t0 = dates_cf[0]
            return sum(
                cf / (1 + rate) ** ((d - t0).days / 365.0)
                for cf, d in zip(cashflows, dates_cf)
            )
        try:
            return round(brentq(npv, -0.999, 10.0, maxiter=1000) * 100, 2)
        except ValueError:
            return 0.0
    except ImportError:
        inv = monthly_records[-1]["total_invested"]
        val = monthly_records[-1]["portfolio_value"]
        yrs = len(monthly_records) / 12
        if inv <= 0 or yrs <= 0:
            return 0.0
        return round(((val / inv) ** (1 / yrs) - 1) * 100, 2)


# ── Pretty print ──────────────────────────────────────────────────────────────

def _print_summary(results: dict):
    s = results["summary"]
    print("\n" + "="*68)
    print("   📊 BACKTEST RESULTS")
    print("="*68)
    print(f"  Period         : {s['backtest_period']}")
    print(f"  Monthly SIP    : ₹{s['monthly_sip']:>12,.0f}")
    print(f"  Total Invested : ₹{s['total_invested']:>12,.0f}")
    print(f"  Final Value    : ₹{s['final_portfolio_value']:>12,.0f}")
    print(f"  Total Gains    : ₹{s['total_gains']:>12,.0f}")
    print(f"  Absolute Return: {s['absolute_return_pct']:>11.1f}%")
    print(f"  XIRR           : {s['xirr_pct']:>11.1f}%")
    print(f"\n  {'YEAR':<8} {'INVESTED':>13} {'VALUE':>13} {'GAINS':>13} {'RETURN':>8}")
    print(f"  {'─'*58}")
    for year, d in results["yearly_summary"].items():
        print(
            f"  {year:<8} "
            f"₹{d['total_invested']:>12,.0f} "
            f"₹{d['portfolio_value']:>12,.0f} "
            f"₹{d['gains']:>12,.0f} "
            f"{d['absolute_return_pct']:>7.1f}%"
        )
    print(f"\n  {'ASSET CLASS':<22} {'TICKER':<14} {'UNITS':>7} {'PRICE':>10} {'VALUE':>13}")
    print(f"  {'─'*70}")
    for ac, h in results["final_holdings"].items():
        print(
            f"  {ac:<22} "
            f"{h['ticker']:<14} "
            f"{h['units_held']:>7} "
            f"₹{h['current_price']:>9,.2f} "
            f"₹{h['current_value']:>12,.0f}"
        )
    print("="*68)


# ── Parse ARJUN JSON ──────────────────────────────────────────────────────────

def parse_arjun_allocation(arjun_json: dict) -> tuple:
    tenure_keys = [k for k in arjun_json if k.startswith("tenure_")]
    if tenure_keys:
        print("\n  Multiple tenures found:")
        for i, key in enumerate(tenure_keys, 1):
            print(f"  {i}. {key}")
        while True:
            try:
                idx = int(input("\n  Which tenure to backtest? Enter number: ").strip()) - 1
                if 0 <= idx < len(tenure_keys):
                    block = arjun_json[tenure_keys[idx]]
                    selected_key = tenure_keys[idx]
                    break
            except (ValueError, KeyboardInterrupt):
                pass
            print("  Invalid choice.")
    else:
        block = arjun_json
        selected_key = "portfolio"

    monthly_sip = float((block.get("_sip_plan") or {}).get("monthly_sip") or 0)
    if monthly_sip == 0:
        while True:
            try:
                monthly_sip = float(input("\n  Enter monthly SIP amount (₹): ").strip().replace(",", ""))
                if monthly_sip > 0:
                    break
            except ValueError:
                pass
            print("  Please enter a valid number.")

    allocation = {
        k: v.get("percentage", 0)
        for k, v in block.get("allocation", {}).items()
        if isinstance(v, dict) and v.get("percentage", 0) > 0
    }
    return allocation, monthly_sip, selected_key


# ── Entry point called from agent1advisor.py ─────────────────────────────────

def run_backtest_from_arjun(arjun_json: dict, years: int = 5) -> dict:
    print("\n" + "="*68)
    print("   PORTFOLIO BACKTESTER — 5 Year SIP Simulation")
    print("   ETF data: ETFS.json (2025-2026 NSE Research)")
    print("   Price data: Live NSE via technical.py")
    print("="*68)

    allocation, monthly_sip, tenure_label = parse_arjun_allocation(arjun_json)
    if not allocation:
        return {"error": "Could not parse allocation."}

    print(f"\n  📋 Allocation ({tenure_label}):")
    for k, v in allocation.items():
        print(f"     {k}: {v}%  →  ₹{monthly_sip * v / 100:,.0f}/month")

    etf_selections = auto_select_etfs(allocation, monthly_sip)
    if not etf_selections:
        return {"error": "No ETFs could be selected."}

    print("\n  ⏳ Running backtest...")
    results = run_backtest(allocation, etf_selections, monthly_sip, years=years)

    if "error" not in results:
        _print_summary(results)

    return results


# ── Standalone test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = {
        "_sip_plan": {"monthly_sip": 10000},
        "allocation": {
            "Large Cap":            {"percentage": 30},
            "Mid Cap":              {"percentage": 20},
            "Small Cap":            {"percentage": 10},
            "Gold":                 {"percentage": 10},
            "International Equity": {"percentage": 10},
            "Debt":                 {"percentage": 20},
        }
    }
    results = run_backtest_from_arjun(sample, years=5)
    output  = {k: v for k, v in results.items() if k != "monthly_detail"}
    print("\n  JSON Output:")
    print(json.dumps(output, indent=2, ensure_ascii=False))