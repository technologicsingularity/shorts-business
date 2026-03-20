# Polymarket Paper Trading System

## Strategy: Consistent Edge, Not Home Runs

**Core Philosophy:**
- Find markets with clear information asymmetry
- Bet on high-probability outcomes (60%+ implied odds)
- Diversify across many small bets
- Track everything, iterate on strategy

## Pipeline Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│  SCANNER    │───→│  ANALYZER    │───→│ PAPER TRADE │───→│  TRACKER    │
│  (Find      │    │  (Edge calc) │    │ (Simulated) │    │ (Performance│
│   markets)  │    │              │    │             │    │   metrics)  │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
```

## 1. SCANNER — Market Discovery

**Daily Scan (3x/day):**
- Morning: New markets, overnight line moves
- Afternoon: Volume spikes, news-driven shifts
- Evening: Close-of-day positions, next day setups

**Search Criteria:**
- Liquidity > $50K (easy entry/exit)
- Time horizon: 7-90 days (not too far, not too soon)
- Clear resolution criteria
- Volume trending up (smart money entering)

## 2. ANALYZER — Edge Detection

**Bet Types We Track:**

### A. Information Arbitrage
- News not yet priced in
- Public data ≠ market odds
- Example: Weather for outdoor events, polling data

### B. Momentum Plays
- Odds moving toward consensus
- Early market inefficiencies
- Fade the public when they overreact

### C. Calendar Effects
- Seasonal patterns
- Event-driven catalysts
- "Buy the rumor, sell the news"

### D. Contrarian Value
- Market overreacts to recent news
- Odds too extreme (>90% or <10%)
- Mean reversion opportunities

## 3. PAPER TRADE — Simulated Betting

**Position Sizing:**
- Virtual bankroll: $10,000
- Max bet size: 5% ($500 per position)
- Max concurrent bets: 10
- Target: 20-30 bets/month

**Entry Rules:**
- Only bet when we have 5%+ edge vs "true" probability
- Record entry price, date, thesis
- Set mental stop-loss (30% loss = exit)

## 4. TRACKER — Performance Analytics

**Metrics We Track:**
- Win rate (%)
- Average return per bet
- Sharpe ratio (risk-adjusted returns)
- Max drawdown
- Best/worst performing categories
- Strategy attribution (which approach works)

**Reporting:**
- Daily: New positions, closed positions, P&L
- Weekly: Strategy performance, edge calibration
- Monthly: Full portfolio review, strategy refinement

## Risk Management

**Hard Rules:**
- No bet > 5% of bankroll
- No correlated bets (don't bet on same event twice)
- No chasing losses (stick to system)
- No FOMO (if missed entry, wait for next)

## Initial Strategies to Test

### Strategy 1: "Fade the Extreme"
- Bet against >90% or <10% odds
- Markets tend to overprice certainty
- Small bets, high frequency

### Strategy 2: "News Lag"
- Monitor news/social for info not yet priced
- Rapid response to new data
- Requires fast execution

### Strategy 3: "Volume Follow"
- Big volume spikes = smart money
- Follow the whales
- Enter after volume confirms direction

---

**Goal:** 15%+ annual return with <20% drawdown
**Timeline:** Test for 3 months, then evaluate
**Success Metric:** Beat "buy and hold" in major markets
