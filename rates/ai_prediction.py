import numpy as np
from datetime import timedelta
from django.utils import timezone
from rates.models import GoldSilverRate

def predict_future_price(metal, hours=24):
    """
    Simple AI prediction using Linear Regression on recent historical data.
    Returns predicted price and confidence trend.
    """
    # Fetch last 100 points
    history = GoldSilverRate.objects.filter(metal=metal).order_by('-timestamp')[:100]
    
    if len(history) < 20:
        return None, "Insufficient data for prediction. Need at least 20 data points."

    # Reverse to get chronological order
    history = list(history)[::-1]
    
    # X = timestamps (in seconds from first point), Y = prices
    start_time = history[0].timestamp
    x = np.array([(h.timestamp - start_time).total_seconds() for h in history])
    y = np.array([float(h.price_inr) for h in history])
    
    # Linear Regression: y = mx + c
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A, y, rcond=None)[0]
    
    # Predict for current_time + hours
    target_time = timezone.now() + timedelta(hours=hours)
    target_x = (target_time - start_time).total_seconds()
    predicted_price = m * target_x + c
    
    # Determine trend
    current_price = y[-1]
    percent_diff = ((predicted_price - current_price) / current_price) * 100
    
    trend = "Bullish 📈" if m > 0 else "Bearish 📉"
    summary = f"Predicted to reach ₹{predicted_price:.2f}/g in {hours}h ({trend}, {percent_diff:+.2f}%)"
    
    return predicted_price, summary
