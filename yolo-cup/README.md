# 🥤 YOLO Cup

## GPU-Accelerated Polymer Degradation Simulation

Predicting biodegradable cup compositions that degrade in <100 years instead of 450-1,000 years.

### Quick Start

```bash
cd /data/.openclaw/workspace/yolo-cup

# Run single simulation
python3 src/yolo_cup_sim.py --composition "PLA:0.4,PHA:0.3,starch:0.2,chitosan:0.1" --years 50

# Run batch overnight
python3 batch_runner.py
```

### Test Compositions

1. **Pure PLA** - Baseline current "biodegradable" standard
2. **PLA/PHA 70/30** - Improved marine degradability
3. **Optimized Blend** - 40% PLA + 30% PHA + 20% starch + 10% chitosan
4. **Starch/Chitosan** - Low cost, fast degradation
5. **Low Cost** - 70% starch + 30% lignin (under $1/kg)
6. **Marine Friendly** - PHA-based for ocean environments

### Cost Analysis

| Polymer | Cost/kg |
|---------|---------|
| PLA | $2.50 |
| PHA | $4.00 |
| Starch | $0.80 |
| Chitosan | $3.00 |
| Lignin | $1.50 |

Target: <$2.00/kg for viable Solo cup alternative

### Directory Structure

```
yolo-cup/
├── src/              # Simulation source code
├── results/          # Simulation outputs
├── configs/          # Configuration files
├── docs/             # Documentation
└── batch_runner.py   # Overnight batch testing
```

### Night Mode

Running batch simulations overnight with 15-minute progress checks.
Results will be ready by morning (7am).

### Target Performance

- **Degradation:** <100 years to 50% breakdown (vs 450-1,000 for polystyrene)
- **Cost:** <$0.05 per cup at volume
- **Function:** Must survive beer pong and flip cup

### Status

🟡 **Running** - Batch simulations in progress
Check `/results/batch_summary.json` for latest results.

---

Created: March 2026  
Authors: Jordan & Alita
