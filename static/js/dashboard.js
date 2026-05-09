let tvWidget = null;
let currentMetal = 'gold'; // 'gold' or 'silver'
let currentSymbol = 'OANDA:XAUUSD';

const formatUSD = (price) => {
    return '$' + parseFloat(price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const formatPct = (pct) => {
    const val = parseFloat(pct);
    const sign = val > 0 ? '+' : '';
    return sign + val.toFixed(3) + '%';
};

function initTradingView() {
    const container = document.getElementById('tv_chart_container');
    if (!container) return;

    tvWidget = new TradingView.widget({
        "autosize": true,
        "symbol": currentSymbol,
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "enable_publishing": false,
        "backgroundColor": "rgba(0, 0, 0, 0)",
        "gridColor": "rgba(255, 255, 255, 0.06)",
        "hide_top_toolbar": false,
        "hide_legend": false,
        "save_image": false,
        "container_id": "tv_chart_container"
    });
}

function loadTradingViewChart(symbol, btnElement = null) {
    currentSymbol = symbol;
    currentMetal = symbol.includes('XAU') ? 'gold' : 'silver';

    if (btnElement) {
        document.querySelectorAll('.chart-btn').forEach(btn => btn.classList.remove('active'));
        btnElement.classList.add('active');
    }

    initTradingView();
    fetchPrediction();
}

async function fetchLiveRates() {
    try {
        const response = await fetch('/api/rates/current/');
        const data = await response.json();
        if (data.gold) updateRateUI('gold', data.gold);
        if (data.silver) updateRateUI('silver', data.silver);
    } catch (e) { console.error(e); }
}

function updateRateUI(metal, data) {
    const isUp = data.pct_change >= 0;
    const pctClass = isUp ? 'change-up' : 'change-down';
    const icon = isUp ? '↑' : '↓';

    const priceEl = document.getElementById(`${metal}Price`);
    const pctEl = document.getElementById(`${metal}Pct`);
    const highEl = document.getElementById(`${metal}High`);
    const lowEl = document.getElementById(`${metal}Low`);

    if (priceEl) priceEl.innerText = formatUSD(data.price_usd);
    if (pctEl) {
        pctEl.className = `stat-change ${pctClass}`;
        pctEl.innerHTML = `${icon} ${formatPct(data.pct_change)}`;
    }
    if (highEl) highEl.innerText = formatUSD(data.daily_high);
    if (lowEl) lowEl.innerText = formatUSD(data.daily_low);

    if (metal === 'gold') {
        const timeEl = document.getElementById('lastUpdated');
        if (timeEl) timeEl.innerText = `Updated at ${new Date(data.updated).toLocaleTimeString()}`;
    }
}

async function fetchPrediction() {
    const metals = ['gold', 'silver'];
    for (const m of metals) {
        try {
            const response = await fetch(`/api/rates/prediction/?metal=${m}`);
            const data = await response.json();
            document.getElementById(`${m}Prediction`).innerText = data.summary;
        } catch (e) { console.error(e); }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initTradingView();
    fetchLiveRates();
    fetchPrediction();
    setInterval(fetchLiveRates, 5000);
});
