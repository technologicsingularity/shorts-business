#!/usr/bin/env python3
"""
Update dashboard data from polymarket_tracker.py
Run this after every trade to refresh dashboard
"""

import json
import subprocess
import sys
from datetime import datetime

# Import fetch_live_prices from tracker
sys.path.insert(0, '/data/.openclaw/workspace')
from polymarket_tracker import fetch_live_prices, load_trades as tracker_load_trades

def load_trades():
    """Load trades from JSON."""
    with open('/data/.openclaw/workspace/polymarket_trades.json', 'r') as f:
        return json.load(f)

def calculate_position_pnl(position, current_price):
    """Calculate P&L for a position given current market price."""
    entry = position['entry_price']
    amount = position['amount']
    
    if position['bet_type'] == 'YES':
        pnl_pct = (current_price - entry) / entry
    else:
        pnl_pct = (entry - current_price) / entry
    
    pnl_amount = amount * pnl_pct
    return pnl_amount, pnl_pct * 100

def get_probability_model(entry_price, current_price, bet_type):
    """Basic probability modeling for position outcome."""
    prob_delta = current_price - entry_price
    
    if bet_type == 'YES':
        win_prob = current_price
        potential_return = (1 - entry_price) / entry_price if entry_price > 0 else 0
    else:
        win_prob = 1 - current_price
        potential_return = entry_price / (1 - entry_price) if entry_price < 1 else 0
    
    ev = (win_prob * potential_return) - (1 - win_prob) * 1
    
    if ev > 0.1:
        prediction = "strong_win"
        confidence = min(95, 50 + ev * 100)
    elif ev > 0:
        prediction = "likely_win"
        confidence = min(75, 50 + ev * 50)
    elif ev > -0.1:
        prediction = "uncertain"
        confidence = 50
    else:
        prediction = "at_risk"
        confidence = max(25, 50 + ev * 50)
    
    return {
        "expected_value": round(ev, 3),
        "win_probability": round(win_prob * 100, 1),
        "prediction": prediction,
        "confidence": round(confidence, 1),
        "price_momentum": round(prob_delta * 100, 2)
    }

def get_strategy_performance(data):
    """Calculate win rate and returns by strategy."""
    strategies = {}
    
    # Process closed positions
    for p in data['closed']:
        strat = p.get('strategy', 'unknown')
        if strat not in strategies:
            strategies[strat] = {'wins': 0, 'losses': 0, 'total_pnl': 0, 'count': 0, 'open_count': 0}
        
        strategies[strat]['count'] += 1
        strategies[strat]['total_pnl'] += p['pnl_amount']
        if p['pnl_amount'] > 0:
            strategies[strat]['wins'] += 1
        else:
            strategies[strat]['losses'] += 1
    
    # Process open positions
    for p in data['positions']:
        strat = p.get('strategy', 'unknown')
        if strat not in strategies:
            strategies[strat] = {'wins': 0, 'losses': 0, 'total_pnl': 0, 'count': 0, 'open_count': 0}
        strategies[strat]['open_count'] += 1
        
        # Calculate unrealized P&L
        current = p.get('current_price', p['entry_price'])
        pnl, _ = calculate_position_pnl(p, current)
        strategies[strat]['total_pnl'] += pnl
    
    # Calculate percentages and format
    result = {}
    for strat, s in strategies.items():
        total_trades = s['wins'] + s['losses']
        result[strat] = {
            'wins': s['wins'],
            'losses': s['losses'],
            'open_count': s['open_count'],
            'total_trades': total_trades,
            'win_rate': round((s['wins'] / total_trades * 100), 1) if total_trades > 0 else 0,
            'total_pnl': round(s['total_pnl'], 2),
            'avg_return': round(s['total_pnl'] / total_trades, 2) if total_trades > 0 else 0
        }
    
    return result

def get_portfolio_data():
    """Get current portfolio data from tracker."""
    data = load_trades()
    
    open_positions = len(data['positions'])
    closed_positions = len(data['closed'])
    bankroll = data['bankroll']
    starting = data.get('starting_bankroll', 10000.00)
    total_return = ((bankroll - starting) / starting) * 100
    
    # Calculate realized stats
    if data['closed']:
        wins = sum(1 for p in data['closed'] if p.get('pnl_amount', 0) > 0)
        win_rate = (wins / len(data['closed'])) * 100
    else:
        wins = 0
        win_rate = 0
    
    # Build enhanced positions list with P&L and predictions
    enhanced_positions = []
    total_unrealized_pnl = 0
    
    for p in data['positions']:
        current_price = p.get('current_price', p['entry_price'])
        pnl_amount, pnl_pct = calculate_position_pnl(p, current_price)
        total_unrealized_pnl += pnl_amount
        
        # Get probability model
        prediction = get_probability_model(p['entry_price'], current_price, p['bet_type'])
        
        # Get price history for this position
        pos_id = str(p['id'])
        price_history = data.get('price_history', {}).get(pos_id, [])
        
        # Get market data if available
        market_data = p.get('market_data', {})
        
        enhanced_positions.append({
            "id": p['id'],
            "name": p['market_name'],
            "category": p.get('category', 'general'),
            "entry_price": p['entry_price'],
            "current_price": current_price,
            "bet_type": p['bet_type'],
            "amount": round(p['amount'], 2),
            "strategy": p.get('strategy', 'unknown'),
            "thesis": p.get('thesis', 'Unknown')[:50] + '...' if len(p.get('thesis', '')) > 50 else p.get('thesis', 'Unknown'),
            "pnl_amount": round(pnl_amount, 2),
            "pnl_percent": round(pnl_pct, 2),
            "prediction": prediction,
            "opened_at": p['opened_at'],
            "last_price_update": p.get('last_price_update'),
            "price_history": price_history,
            "market_data": market_data
        })
    
    # Get historical data for charts
    history = data.get('history', [])
    
    # Calculate win rate progression (simplified - assume even distribution over time)
    win_rate_progression = []
    if data['closed']:
        cumulative_wins = 0
        cumulative_total = 0
        for i, p in enumerate(data['closed']):
            cumulative_total += 1
            if p['pnl_amount'] > 0:
                cumulative_wins += 1
            win_rate_progression.append({
                'trade': i + 1,
                'win_rate': round((cumulative_wins / cumulative_total) * 100, 1)
            })
    
    # Build dashboard data
    dashboard_data = {
        "bankroll": round(bankroll, 2),
        "starting_bankroll": starting,
        "total_return_pct": round(total_return, 2),
        "open_positions": open_positions,
        "closed_positions": closed_positions,
        "win_rate": round(win_rate, 1),
        "wins": wins,
        "losses": closed_positions - wins,
        "unrealized_pnl": round(total_unrealized_pnl, 2),
        "total_value": round(bankroll + sum(p['amount'] for p in data['positions']), 2),
        "positions": enhanced_positions,
        "strategy_performance": get_strategy_performance(data),
        "history": history,
        "win_rate_progression": win_rate_progression,
        "last_updated": datetime.now().isoformat() + "Z"
    }
    
    return dashboard_data

def update_dashboard():
    """Update dashboard JSON file."""
    # Step 1: Fetch live prices from Polymarket API
    print("🔄 Fetching live prices from Polymarket API...")
    price_result = fetch_live_prices()
    print(f"   Updated {price_result['updated']} positions\n")
    
    # Step 2: Generate dashboard data
    data = get_portfolio_data()
    
    # Write to dashboard data file
    dashboard_path = '/data/.openclaw/workspace/polymarket-dashboard/data.json'
    with open(dashboard_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Git commit and push
    subprocess.run(['git', '-C', '/data/.openclaw/workspace/polymarket-dashboard', 'add', '.'], check=True)
    subprocess.run(['git', '-C', '/data/.openclaw/workspace/polymarket-dashboard', 'commit', '-m', f'Update data: {data["last_updated"]}'], check=False)
    subprocess.run(['git', '-C', '/data/.openclaw/workspace/polymarket-dashboard', 'push', 'origin', 'main'], check=True)
    
    print(f"✅ Dashboard updated!")
    print(f"💰 Bankroll: ${data['bankroll']}")
    print(f"📊 Return: {data['total_return_pct']}%")
    print(f"📂 Positions: {data['open_positions']} open")
    print(f"🌐 Live at: https://technologicsingularity.github.io/polymarket-dashboard")
    
    # Also commit changes to the main workspace (price updates)
    try:
        subprocess.run(['git', '-C', '/data/.openclaw/workspace', 'add', 'polymarket_trades.json'], check=False)
        subprocess.run(['git', '-C', '/data/.openclaw/workspace', 'commit', '-m', f'Update prices: {data["last_updated"]}'], check=False)
        subprocess.run(['git', '-C', '/data/.openclaw/workspace', 'push'], check=False)
    except Exception as e:
        print(f"Note: Could not push main workspace changes: {e}")

if __name__ == '__main__':
    update_dashboard()
