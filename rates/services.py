"""
rates/services.py
=================
Fetches live gold & silver prices, converts to INR,
persists snapshots, and returns structured data dicts.

API Priority:
  1. metals.live (free, no key, USD troy-oz)
  2. Simulated realistic data (fallback)

INR Conversion:
  Uses open.er-api.com (free, no key) with .env fallback rate.
"""
import logging
import random
from decimal import Decimal
from datetime import date

import requests
from django.conf import settings
from django.utils import timezone

from rates.models import GoldSilverRate

logger = logging.getLogger(__name__)

# Troy ounce → gram
TROY_OZ_TO_GRAM = 31.1035

# Simulated base prices (USD / troy oz) — realistic as of 2024
_SIM_GOLD_OZ = 2350.0
_SIM_SILVER_OZ = 27.5


def _get_usd_inr_rate() -> float:
    """Fetch live USD→INR exchange rate (open.er-api.com, free, no key)."""
    try:
        r = requests.get('https://open.er-api.com/v6/latest/USD', timeout=8)
        if r.status_code == 200:
            data = r.json()
            rate = data.get('rates', {}).get('INR')
            if rate:
                return float(rate)
    except Exception as e:
        logger.warning(f"Exchange rate fetch failed: {e}")
    return float(settings.USD_INR_FALLBACK)

import requests

def _fetch_goldapi_io(api_key: str) -> dict:
    """Fetch live prices from GoldAPI.io (USD per troy ounce)."""
    prices = {}
    headers = {'x-access-token': api_key, 'Content-Type': 'application/json'}
    
    for metal in ('XAU', 'XAG'):
        try:
            url = f"https://www.goldapi.io/api/{metal}/USD"
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                prices[metal.lower().replace('xau', 'gold').replace('xag', 'silver')] = float(data['price'])
        except Exception as e:
            logger.warning(f"GoldAPI fetch failed for {metal}: {e}")
            
    return prices

def _fetch_metals_live() -> dict:
    """Fallback: Fetch live prices using TradingView's Scanner API."""
    try:
        url = "https://scanner.tradingview.com/cfd/scan"
        payload = {
            "symbols": {"tickers": ["TVC:GOLD", "TVC:SILVER"]},
            "columns": ["close"]
        }
        r = requests.post(url, json=payload, timeout=10)
        
        if r.status_code == 200:
            data = r.json().get('data', [])
            prices = {}
            for item in data:
                if item['s'] == 'TVC:GOLD':
                    prices['gold'] = float(item['d'][0])
                elif item['s'] == 'TVC:SILVER':
                    prices['silver'] = float(item['d'][0])
            
            if 'gold' in prices and 'silver' in prices:
                return prices
                
    except Exception as e:
        logger.warning(f"TradingView Scanner fetch failed: {e}")
        
    return {'gold': 2350.0, 'silver': 27.5}


def _oz_to_gram_inr(oz_usd: float, inr_rate: float) -> float:
    """Convert troy-oz USD price → per-gram INR price."""
    return (oz_usd / TROY_OZ_TO_GRAM) * inr_rate


def _calc_percentage_change(current: float, previous: float) -> float:
    """Core formula: ((current - previous) / previous) × 100"""
    if not previous:
        return 0.0
    return round(((current - previous) / previous) * 100, 4)


def get_latest_rate(metal: str) -> GoldSilverRate | None:
    """Return the most recent DB record for the given metal."""
    return GoldSilverRate.objects.filter(metal=metal).first()


def fetch_and_save_rates() -> dict:
    """
    Main entry point called by the scheduler every minute.
    Fetches prices, persists, returns summary dict in USD/oz.
    """
    inr_rate = _get_usd_inr_rate()
    
    api_key = getattr(settings, 'GOLDAPI_KEY', '')
    if api_key:
        logger.info("Using GoldAPI.io as primary source...")
        raw = _fetch_goldapi_io(api_key)
    
    if not raw or 'gold' not in raw:
        logger.info("Falling back to TradingView Scanner...")
        raw = _fetch_metals_live()

    results = {}
    today = date.today()

    for metal in ('gold', 'silver'):
        price_oz_usd = float(raw[metal])
        
        # We still store INR per gram for local reference, but price_usd is now OUNCE price
        price_inr_gram = (price_oz_usd / TROY_OZ_TO_GRAM) * inr_rate

        # Get previous snapshot for % change
        previous = get_latest_rate(metal)
        pct_change = 0.0
        if previous:
            # Compare USD/oz prices for consistency
            pct_change = _calc_percentage_change(price_oz_usd, float(previous.price_usd))

        # Daily high/low: compare with today's records (USD/oz)
        today_records = GoldSilverRate.objects.filter(
            metal=metal, timestamp__date=today
        ).order_by('price_usd')
        
        daily_low = float(today_records.first().price_usd) if today_records.exists() else price_oz_usd
        daily_high = float(today_records.last().price_usd) if today_records.exists() else price_oz_usd
        daily_low = min(daily_low, price_oz_usd)
        daily_high = max(daily_high, price_oz_usd)

        rate = GoldSilverRate.objects.create(
            metal=metal,
            price_inr=Decimal(str(round(price_inr_gram, 4))),
            price_usd=Decimal(str(round(price_oz_usd, 4))),
            daily_high=Decimal(str(round(daily_high, 4))),
            daily_low=Decimal(str(round(daily_low, 4))),
            percentage_change=Decimal(str(pct_change)),
            usd_inr_rate=Decimal(str(round(inr_rate, 4))),
            raw_price_oz_usd=Decimal(str(round(price_oz_usd, 4))),
        )
        results[metal] = rate
        logger.info(
            f"[{metal.upper()}] ${price_oz_usd:.2f}/oz (₹{price_inr_gram:.2f}/g) | {pct_change:+.3f}%"
        )

    return results
