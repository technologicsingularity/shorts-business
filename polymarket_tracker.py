#!/usr/bin/env python3
"""
Polymarket Paper Trading Tracker
Records all paper trades, calculates P&L, generates reports
"""

import json
import os
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

DATA_FILE = Path('/data/.openclaw/workspace/polymarket_trades.json')
POLYMARKET_API = "https://gamma-api.polymarket.com"

# Rate limiting config
LAST_API_CALL = 0
MIN_API_INTERVAL = 5  # seconds between calls (3-4 calls per second is safe)

def load_trades():
    """Load all paper trades from JSON."""
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return {
        'positions': [], 
        'closed': [], 
        'bankroll': 10000.00, 
        'history': [],
        'starting_bankroll': 10000.00
    }

def save_trades(data):
    """Save trades to JSON."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def rate_limited_api_call(url, params=None, retries=3):
    """Make API call with rate limiting protection."""
    global LAST_API_CALL
    
    # Ensure minimum interval between calls
    elapsed = time.time() - LAST_API_CALL
    if elapsed < MIN_API_INTERVAL:
        time.sleep(MIN_API_INTERVAL - elapsed)
    
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=30)
            LAST_API_CALL = time.time()
            
            if response.status_code == 429:  # Rate limited
                wait_time = int(response.headers.get('Retry-After', 60))
                print(f"  ⚠️ Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️ API call failed (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return None
    
    return None

def fetch_market_by_slug(slug):
    """Fetch market data from Polymarket Gamma API by slug."""
    url = f"{POLYMARKET_API}/markets"
    params = {"slug": slug}
    
    data = rate_limited_api_call(url, params)
    if data and len(data) > 0:
        return data[0]
    return None

def fetch_live_prices():
    """
    Fetch current market prices for all open positions from Polymarket API.
    Updates positions with live prices and records price history.
    """
    data = load_trades()
    
    if not data['positions']:
        print("No open positions to update.")
        return {"updated": 0, "errors": 0, "skipped": 0}
    
    # Initialize price_history if not exists
    if 'price_history' not in data:
        data['price_history'] = {}
    
    updated = 0
    errors = 0
    skipped = 0
    price_updates = {}
    
    print(f"🔍 Fetching live prices for {len(data['positions'])} positions...")
    
    for position in data['positions']:
        slug = position.get('market_slug')
        if not slug:
            print(f"  ⚠️ Position #{position['id']} has no market_slug, skipping")
            skipped += 1
            continue
        
        print(f"  📡 Fetching: {slug[:50]}...")
        
        market_data = fetch_market_by_slug(slug)
        
        if market_data:
            # Extract current price from market data
            # Polymarket Gamma API returns outcomePrices as a JSON string like '["0.45", "0.55"]'
            # Index 0 = Yes price, Index 1 = No price
            outcome_prices_str = market_data.get('outcomePrices', '[]')
            outcome_prices = []
            if isinstance(outcome_prices_str, str):
                try:
                    outcome_prices = json.loads(outcome_prices_str)
                except json.JSONDecodeError:
                    outcome_prices = []
            elif isinstance(outcome_prices_str, list):
                outcome_prices = outcome_prices_str
            
            # Get the relevant price based on bet type
            bet_type = position.get('bet_type', 'YES')
            current_price = 0
            if outcome_prices and len(outcome_prices) >= 2:
                if bet_type.upper() == 'YES':
                    current_price = float(outcome_prices[0])
                else:
                    current_price = float(outcome_prices[1])
            
            # Fallback to lastTradePrice if available
            if current_price == 0:
                last_trade = market_data.get('lastTradePrice')
                if last_trade:
                    current_price = float(last_trade)
            
            if current_price > 0:
                old_price = position.get('current_price', position['entry_price'])
                position['current_price'] = current_price
                position['last_price_update'] = datetime.now().isoformat()
                position['market_data'] = {
                    'volume': market_data.get('volume', 0),
                    'liquidity': market_data.get('liquidity', 0),
                    'spread': market_data.get('spread', 0),
                    'updated_at': market_data.get('updatedAt')
                }
                
                # Record price history
                pos_id = str(position['id'])
                if pos_id not in data['price_history']:
                    data['price_history'][pos_id] = []
                
                data['price_history'][pos_id].append({
                    'timestamp': datetime.now().isoformat(),
                    'price': current_price,
                    'entry_price': position['entry_price']
                })
                
                # Keep only last 90 days of price history per position
                cutoff = (datetime.now() - timedelta(days=90)).isoformat()
                data['price_history'][pos_id] = [
                    h for h in data['price_history'][pos_id] 
                    if h['timestamp'] > cutoff
                ]
                
                price_change = current_price - old_price
                emoji = "🟢" if price_change >= 0 else "🔴"
                print(f"    {emoji} {position['market_name'][:40]}: {old_price:.3f} → {current_price:.3f}")
                updated += 1
            else:
                print(f"    ⚠️ Invalid price for {slug[:40]}")
                errors += 1
        else:
            print(f"    ❌ Failed to fetch {slug[:40]}")
            errors += 1
    
    # Save updated data
    save_trades(data)
    
    print(f"\n✅ Live prices updated: {updated} positions")
    if errors > 0:
        print(f"❌ Errors: {errors}")
    if skipped > 0:
        print(f"⏭️ Skipped: {skipped}")
    
    return {"updated": updated, "errors": errors, "skipped": skipped}

def get_strategy_type(entry_price, thesis=""):
    """Auto-classify strategy based on entry price and thesis."""
    thesis_lower = thesis.lower()
    
    if "fade" in thesis_lower or entry_price < 0.05:
        return "fade"
    elif "arbitrage" in thesis_lower or "arb" in thesis_lower:
        return "arbitrage"
    elif "whale" in thesis_lower or "smart money" in thesis_lower or "insider" in thesis_lower:
        return "whale-tracking"
    elif "momentum" in thesis_lower or "trend" in thesis_lower:
        return "momentum"
    elif "news" in thesis_lower or "event" in thesis_lower:
        return "news"
    elif entry_price > 0.6:
        return "high-probability"
    elif entry_price < 0.15:
        return "longshot"
    else:
        return "value"

def calculate_position_pnl(position, current_price):
    """Calculate P&L for a position given current market price."""
    entry = position['entry_price']
    amount = position['amount']
    
    if position['bet_type'] == 'YES':
        # YES bet: profit if price goes up from entry
        pnl_pct = (current_price - entry) / entry
    else:
        # NO bet: profit if price goes down from entry
        pnl_pct = (entry - current_price) / entry
    
    pnl_amount = amount * pnl_pct
    return pnl_amount, pnl_pct * 100

def get_probability_model(entry_price, current_price, bet_type):
    """Basic probability modeling for position outcome."""
    # Calculate implied probability delta
    prob_delta = current_price - entry_price
    
    # Calculate expected value based on current odds
    if bet_type == 'YES':
        win_prob = current_price
        potential_return = (1 - entry_price) / entry_price  # Decimal odds
    else:
        win_prob = 1 - current_price
        potential_return = entry_price / (1 - entry_price)
    
    # Expected value calculation
    ev = (win_prob * potential_return) - (1 - win_prob) * 1
    
    # Determine prediction
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
        "price_momentum": round(prob_delta * 100, 2)  # Percentage point change
    }

def open_position(market_slug, market_name, bet_type, entry_price, size, thesis, category="general", strategy=None):
    """Open a new paper trade position."""
    data = load_trades()
    
    # Auto-detect strategy if not provided
    if strategy is None:
        strategy = get_strategy_type(entry_price, thesis)
    
    # Check bankroll
    bet_amount = data['bankroll'] * (size / 100)
    if bet_amount > data['bankroll'] * 0.05:
        return {"error": "Position size exceeds 5% max rule"}
    
    position = {
        'id': len(data['positions']) + len(data['closed']) + 1,
        'market_slug': market_slug,
        'market_name': market_name,
        'category': category,
        'bet_type': bet_type,  # 'YES' or 'NO'
        'entry_price': entry_price,
        'current_price': entry_price,  # Initially same as entry
        'size_percent': size,
        'amount': bet_amount,
        'thesis': thesis,
        'strategy': strategy,
        'opened_at': datetime.now().isoformat(),
        'status': 'open'
    }
    
    data['positions'].append(position)
    data['bankroll'] -= bet_amount  # Reserve the capital
    
    # Record bankroll history point
    record_history_point(data)
    
    save_trades(data)
    
    return {
        "success": True,
        "position": position,
        "bankroll_remaining": data['bankroll']
    }

def update_position_prices(price_updates):
    """Update current prices for open positions."""
    """price_updates: dict of position_id -> current_price"""
    data = load_trades()
    
    # Initialize price_history if not exists
    if 'price_history' not in data:
        data['price_history'] = {}
    
    for position in data['positions']:
        if position['id'] in price_updates:
            new_price = price_updates[position['id']]
            position['current_price'] = new_price
            position['last_price_update'] = datetime.now().isoformat()
            
            # Record price history
            pos_id = str(position['id'])
            if pos_id not in data['price_history']:
                data['price_history'][pos_id] = []
            
            data['price_history'][pos_id].append({
                'timestamp': datetime.now().isoformat(),
                'price': new_price,
                'entry_price': position['entry_price']
            })
            
            # Keep only last 90 days of price history
            cutoff = (datetime.now() - timedelta(days=90)).isoformat()
            data['price_history'][pos_id] = [
                h for h in data['price_history'][pos_id] 
                if h['timestamp'] > cutoff
            ]
    
    save_trades(data)
    return {"updated": len(price_updates)}

def get_price_history(position_id):
    """Get price history for a specific position."""
    data = load_trades()
    return data.get('price_history', {}).get(str(position_id), [])

def close_position(position_id, exit_price, reason="manual"):
    """Close a position and calculate P&L."""
    data = load_trades()
    
    position = None
    for i, p in enumerate(data['positions']):
        if p['id'] == position_id:
            position = data['positions'].pop(i)
            break
    
    if not position:
        return {"error": f"Position {position_id} not found"}
    
    # Calculate P&L
    if position['bet_type'] == 'YES':
        pnl_pct = (exit_price - position['entry_price']) / position['entry_price']
    else:  # NO bet
        pnl_pct = (position['entry_price'] - exit_price) / position['entry_price']
    
    pnl_amount = position['amount'] * pnl_pct
    
    closed_position = {
        **position,
        'exit_price': exit_price,
        'pnl_amount': pnl_amount,
        'pnl_percent': pnl_pct * 100,
        'closed_at': datetime.now().isoformat(),
        'close_reason': reason,
        'status': 'closed'
    }
    
    data['closed'].append(closed_position)
    data['bankroll'] += position['amount'] + pnl_amount  # Return capital + P&L
    
    # Record bankroll history point
    record_history_point(data, pnl=pnl_amount)
    
    save_trades(data)
    
    return {
        "success": True,
        "position": closed_position,
        "pnl": pnl_amount,
        "pnl_percent": pnl_pct * 100,
        "bankroll": data['bankroll']
    }

def record_history_point(data, pnl=0):
    """Record a bankroll history data point."""
    if 'history' not in data:
        data['history'] = []
    
    data['history'].append({
        'date': datetime.now().isoformat(),
        'bankroll': data['bankroll'],
        'pnl': pnl,
        'open_positions': len(data['positions']),
        'total_positions': len(data['positions']) + len(data['closed'])
    })
    
    # Keep last 365 days of history
    cutoff = (datetime.now() - timedelta(days=365)).isoformat()
    data['history'] = [h for h in data['history'] if h['date'] > cutoff]

def get_strategy_performance():
    """Calculate win rate and returns by strategy."""
    data = load_trades()
    
    strategies = {}
    
    # Initialize with closed positions
    for p in data['closed']:
        strat = p.get('strategy', 'unknown')
        if strat not in strategies:
            strategies[strat] = {'wins': 0, 'losses': 0, 'total_pnl': 0, 'count': 0}
        
        strategies[strat]['count'] += 1
        strategies[strat]['total_pnl'] += p['pnl_amount']
        if p['pnl_amount'] > 0:
            strategies[strat]['wins'] += 1
        else:
            strategies[strat]['losses'] += 1
    
    # Add open positions info (unrealized P&L)
    for p in data['positions']:
        strat = p.get('strategy', 'unknown')
        if strat not in strategies:
            strategies[strat] = {'wins': 0, 'losses': 0, 'total_pnl': 0, 'count': 0, 'open_count': 0}
        if 'open_count' not in strategies[strat]:
            strategies[strat]['open_count'] = 0
        strategies[strat]['open_count'] += 1
    
    # Calculate percentages
    for strat in strategies:
        s = strategies[strat]
        total_trades = s.get('wins', 0) + s.get('losses', 0)
        s['win_rate'] = (s['wins'] / total_trades * 100) if total_trades > 0 else 0
        s['avg_return'] = (s['total_pnl'] / total_trades) if total_trades > 0 else 0
    
    return strategies

def get_portfolio_summary():
    """Get current portfolio status."""
    data = load_trades()
    
    open_positions = len(data['positions'])
    closed_positions = len(data['closed'])
    
    # Calculate realized stats from closed positions
    if data['closed']:
        wins = sum(1 for p in data['closed'] if p['pnl_amount'] > 0)
        losses = sum(1 for p in data['closed'] if p['pnl_amount'] <= 0)
        total_pnl = sum(p['pnl_amount'] for p in data['closed'])
        win_rate = (wins / len(data['closed'])) * 100
        avg_return = sum(p['pnl_percent'] for p in data['closed']) / len(data['closed'])
    else:
        wins = losses = total_pnl = win_rate = avg_return = 0
    
    # Calculate unrealized P&L from open positions
    unrealized_pnl = 0
    for p in data['positions']:
        current = p.get('current_price', p['entry_price'])
        pnl, _ = calculate_position_pnl(p, current)
        unrealized_pnl += pnl
    
    return {
        "bankroll": data['bankroll'],
        "starting_bankroll": data.get('starting_bankroll', 10000.00),
        "total_return_pct": ((data['bankroll'] - 10000) / 10000) * 100,
        "open_positions": open_positions,
        "closed_positions": closed_positions,
        "win_rate": win_rate,
        "wins": wins,
        "losses": losses,
        "total_pnl": total_pnl,
        "unrealized_pnl": unrealized_pnl,
        "avg_return_per_trade": avg_return,
        "strategy_performance": get_strategy_performance()
    }

def print_portfolio():
    """Print formatted portfolio summary."""
    summary = get_portfolio_summary()
    
    print("=" * 60)
    print("📊 POLYMARKET PAPER TRADING PORTFOLIO")
    print("=" * 60)
    print(f"💰 Bankroll: ${summary['bankroll']:.2f}")
    print(f"📈 Total Return: {summary['total_return_pct']:.2f}%")
    print(f"📂 Open Positions: {summary['open_positions']}")
    print(f"✅ Closed Trades: {summary['closed_positions']}")
    print(f"🎯 Win Rate: {summary['win_rate']:.1f}% ({summary['wins']}W/{summary['losses']}L)")
    print(f"💵 Total P&L: ${summary['total_pnl']:.2f}")
    print(f"📊 Avg Return/Trade: {summary['avg_return_per_trade']:.2f}%")
    print("=" * 60)
    
    if summary['open_positions'] > 0:
        print("\n🔓 OPEN POSITIONS:")
        data = load_trades()
        for p in data['positions']:
            current = p.get('current_price', p['entry_price'])
            pnl, pnl_pct = calculate_position_pnl(p, current)
            emoji = "🟢" if pnl >= 0 else "🔴"
            print(f"  #{p['id']}: {p['market_name'][:50]}...")
            print(f"     {p['bet_type']} @ {p['entry_price']:.1%} → {current:.1%} | ${p['amount']:.0f} | {emoji} {pnl:+.2f}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print_portfolio()
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == 'buy' and len(sys.argv) >= 7:
        # python3 tracker.py buy <slug> <name> <YES/NO> <price> <size%> <thesis> [category] [strategy]
        strategy = sys.argv[9] if len(sys.argv) > 9 else None
        result = open_position(
            sys.argv[2], sys.argv[3], sys.argv[4],
            float(sys.argv[5]), float(sys.argv[6]),
            sys.argv[7], sys.argv[8] if len(sys.argv) > 8 else "general",
            strategy
        )
        print(json.dumps(result, indent=2))
    
    elif cmd == 'sell' and len(sys.argv) >= 4:
        # python3 tracker.py sell <position_id> <exit_price> [reason]
        result = close_position(
            int(sys.argv[2]), float(sys.argv[3]),
            sys.argv[4] if len(sys.argv) > 4 else "manual"
        )
        print(json.dumps(result, indent=2))
    
    elif cmd == 'list':
        data = load_trades()
        print(f"\n🔓 Open Positions ({len(data['positions'])}):")
        for p in data['positions']:
            print(f"  #{p['id']}: {p['market_name']}")
        print(f"\n✅ Closed Positions ({len(data['closed'])}):")
        for p in data['closed'][-5:]:  # Last 5
            emoji = "🟢" if p['pnl_amount'] > 0 else "🔴"
            print(f"  {emoji} #{p['id']}: {p['pnl_percent']:+.1f}%")
    
    elif cmd == 'fetch-prices':
        result = fetch_live_prices()
        print(json.dumps(result, indent=2))
    
    elif cmd == 'history' and len(sys.argv) >= 3:
        position_id = sys.argv[2]
        history = get_price_history(position_id)
        print(f"\n📈 Price History for Position #{position_id}:")
        for h in history[-10:]:  # Last 10 points
            print(f"  {h['timestamp'][:19]}: {h['price']:.4f} (entry: {h['entry_price']:.4f})")
    
    else:
        print("Usage:")
        print("  tracker.py                              # Show portfolio")
        print("  tracker.py list                         # List all positions")
        print("  tracker.py buy <slug> <name> <YES/NO> <price> <size%> <thesis> [category] [strategy]")
        print("  tracker.py sell <position_id> <exit_price> [reason]")
        print("  tracker.py fetch-prices                 # Fetch live prices from Polymarket API")
        print("  tracker.py history <position_id>        # Show price history for position")
