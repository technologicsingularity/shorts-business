#!/usr/bin/env python3
"""
DEEP Polymarket Analysis
Comprehensive market scanner for all opportunities
"""

import subprocess
import json
import re
from datetime import datetime

SKILL_PATH = "/data/.openclaw/workspace/skills/polymarket-odds/polymarket.mjs"

def get_all_events():
    """Get all active events across categories."""
    categories = ['sports', 'politics', 'crypto', 'business', 'tech', 'entertainment']
    all_events = []
    
    for cat in categories:
        try:
            result = subprocess.run(
                ['node', SKILL_PATH, 'events', f'--tag={cat}', '--limit=50'],
                capture_output=True, text=True, timeout=30
            )
            
            # Parse output for markets with volume
            lines = result.stdout.split('\n')
            current_event = None
            
            for line in lines:
                if '🎯' in line:
                    current_event = {
                        'category': cat,
                        'title': line.replace('🎯', '').strip(),
                        'markets': []
                    }
                    all_events.append(current_event)
                elif '📊' in line and current_event:
                    # Extract market data
                    yes_match = re.search(r'Yes:\s*([\d.]+)%', line)
                    no_match = re.search(r'No:\s*([\d.]+)%', line)
                    slug_match = re.search(r'Slug:\s*(\S+)', line)
                    
                    if yes_match and no_match:
                        market = {
                            'odds_yes': float(yes_match.group(1)),
                            'odds_no': float(no_match.group(1)),
                            'slug': slug_match.group(1) if slug_match else 'unknown'
                        }
                        current_event['markets'].append(market)
        except Exception as e:
            print(f"Error scanning {cat}: {e}")
    
    return all_events

def analyze_opportunities(events):
    """Find trading opportunities."""
    opportunities = {
        'fade_extreme': [],
        'close_to_even': [],
        'high_volume': [],
        'short_term': []
    }
    
    for event in events:
        for market in event.get('markets', []):
            yes = market['odds_yes']
            no = market['odds_no']
            
            # Strategy 1: Fade extremes
            if yes > 90 or yes < 10:
                opportunities['fade_extreme'].append({
                    'event': event['title'],
                    'category': event['category'],
                    'odds_yes': yes,
                    'odds_no': no,
                    'recommendation': 'NO' if yes > 90 else 'YES',
                    'edge': f"Market overpricing at {max(yes, no):.1f}%"
                })
            
            # Strategy 2: Close to 50/50 (uncertainty)
            elif 48 <= yes <= 52:
                opportunities['close_to_even'].append({
                    'event': event['title'],
                    'category': event['category'],
                    'odds_yes': yes,
                    'odds_no': no,
                    'recommendation': 'WAIT_FOR_INFO'
                })
    
    return opportunities

def generate_report():
    """Generate comprehensive analysis."""
    print("=" * 80)
    print("🔬 DEEP POLYMARKET ANALYSIS")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 80)
    
    print("\n📊 Scanning all markets...")
    events = get_all_events()
    
    print(f"✅ Found {len(events)} events across all categories\n")
    
    opportunities = analyze_opportunities(events)
    
    # Report extreme odds
    print("🎯 FADE THE EXTREME OPPORTUNITIES")
    print("-" * 80)
    print(f"Total found: {len(opportunities['fade_extreme'])}\n")
    
    for i, opp in enumerate(opportunities['fade_extreme'][:10], 1):
        direction = "📉 BET NO" if opp['recommendation'] == 'NO' else "📈 BET YES"
        print(f"{i}. {opp['event'][:60]}")
        print(f"   Category: {opp['category']}")
        print(f"   Odds: Yes {opp['odds_yes']:.1f}% | No {opp['odds_no']:.1f}%")
        print(f"   Action: {direction}")
        print(f"   Edge: {opp['edge']}\n")
    
    # Report close markets
    print("\n⚖️  CLOSE TO EVEN (Information Uncertainty)")
    print("-" * 80)
    print(f"Total found: {len(opportunities['close_to_even'])}\n")
    
    for opp in opportunities['close_to_even'][:5]:
        print(f"• {opp['event'][:60]}")
        print(f"  ({opp['category']}) - {opp['odds_yes']:.1f}% / {opp['odds_no']:.1f}%")
    
    print("\n" + "=" * 80)
    print("💡 TOP RECOMMENDATIONS:")
    print("=" * 80)
    
    if opportunities['fade_extreme']:
        top = opportunities['fade_extreme'][0]
        print(f"\n🥇 #1 PICK: {top['event'][:50]}...")
        print(f"    Bet: {top['recommendation']} | Confidence: HIGH")
        print(f"    Rationale: {top['edge']}")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    generate_report()
