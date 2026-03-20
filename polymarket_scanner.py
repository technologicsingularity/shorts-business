#!/usr/bin/env python3
"""
Polymarket Opportunity Scanner
Finds markets with potential edge for paper trading
"""

import subprocess
import json
import re
from datetime import datetime

SKILL_PATH = "/data/.openclaw/workspace/skills/polymarket-odds/polymarket.mjs"

def run_polymarket(cmd):
    """Execute polymarket CLI command."""
    result = subprocess.run(
        ['node', SKILL_PATH] + cmd,
        capture_output=True, text=True
    )
    return result.stdout

def scan_markets(category="sports", min_liquidity=50000):
    """Scan for markets matching our criteria."""
    output = run_polymarket(['events', f'--tag={category}', '--limit=20'])
    
    opportunities = []
    
    # Parse output (simplified - looking for patterns)
    lines = output.split('\n')
    current_market = None
    
    for line in lines:
        # Look for market headers
        if '🎯' in line:
            current_market = line.replace('🎯', '').strip()
        
        # Look for odds lines
        if 'Yes:' in line and 'No:' in line:
            # Extract odds
            yes_match = re.search(r'Yes:\s*([\d.]+)%', line)
            no_match = re.search(r'No:\s*([\d.]+)%', line)
            
            if yes_match and no_match:
                yes_odds = float(yes_match.group(1))
                no_odds = float(no_match.group(1))
                
                # Flag extreme odds (our "Fade the Extreme" strategy)
                if yes_odds > 90 or yes_odds < 10:
                    opportunities.append({
                        'market': current_market,
                        'type': 'extreme_odds',
                        'signal': 'FADE',
                        'yes_odds': yes_odds,
                        'no_odds': no_odds,
                        'edge': 'Market overpricing certainty',
                        'recommendation': 'NO' if yes_odds > 90 else 'YES'
                    })
                
                # Flag near 50/50 (information uncertainty)
                elif 45 <= yes_odds <= 55:
                    opportunities.append({
                        'market': current_market,
                        'type': 'uncertain',
                        'signal': 'WAIT',
                        'yes_odds': yes_odds,
                        'no_odds': no_odds,
                        'edge': 'Market unsure, wait for clarity',
                        'recommendation': 'MONITOR'
                    })
    
    return opportunities

def scan_all_categories():
    """Scan multiple categories for opportunities."""
    all_opps = []
    
    categories = ['sports', 'politics', 'crypto', 'business']
    
    for cat in categories:
        try:
            opps = scan_markets(cat)
            for opp in opps:
                opp['category'] = cat
            all_opps.extend(opps)
        except Exception as e:
            print(f"Error scanning {cat}: {e}")
    
    return all_opps

def generate_daily_report():
    """Generate daily scan report."""
    print("=" * 70)
    print("🔍 POLYMARKET DAILY SCAN REPORT")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    opportunities = scan_all_categories()
    
    # Filter to actionable opportunities
    fade_extreme = [o for o in opportunities if o['type'] == 'extreme_odds']
    uncertain = [o for o in opportunities if o['type'] == 'uncertain']
    
    print(f"\n🎯 FADE THE EXTREME OPPORTUNITIES ({len(fade_extreme)}):")
    print("-" * 70)
    for opp in fade_extreme[:5]:  # Top 5
        direction = "📉 BET NO" if opp['recommendation'] == 'NO' else "📈 BET YES"
        print(f"\n  {opp['market'][:60]}")
        print(f"     Category: {opp['category']}")
        print(f"     Odds: Yes {opp['yes_odds']:.1f}% | No {opp['no_odds']:.1f}%")
        print(f"     Strategy: {direction}")
        print(f"     Thesis: {opp['edge']}")
    
    print(f"\n⏳ UNCERTAIN MARKETS TO MONITOR ({len(uncertain)}):")
    print("-" * 70)
    for opp in uncertain[:3]:
        print(f"\n  {opp['market'][:60]}")
        print(f"     Category: {opp['category']}")
        print(f"     Status: Waiting for information edge")
    
    print("\n" + "=" * 70)
    print("💡 RECOMMENDED ACTION:")
    print("=" * 70)
    
    if fade_extreme:
        top = fade_extreme[0]
        print(f"\n🥇 TOP PICK: {top['market'][:50]}...")
        print(f"   Bet: {top['recommendation']} at {top['yes_odds'] if top['recommendation'] == 'YES' else top['no_odds']:.1f}%")
        print(f"   Confidence: Medium-High (fade extreme odds)")
        print("\n   To paper trade:")
        print(f"   python3 polymarket_tracker.py buy <slug> '<name>' {top['recommendation']} <price> 3 '<thesis>' {top['category']}")
    else:
        print("\n   No strong signals today. Wait for better setups.")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    generate_daily_report()
