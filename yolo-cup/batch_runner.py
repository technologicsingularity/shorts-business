#!/usr/bin/env python3
"""
YOLO Cup - Batch Simulation Runner
Tests multiple polymer compositions overnight
"""

import subprocess
import json
from pathlib import Path
import time
from datetime import datetime

# Test compositions
COMPOSITIONS = [
    {'name': 'pure_pla', 'comp': 'PLA:1.0'},
    {'name': 'pla_pha_70_30', 'comp': 'PLA:0.7,PHA:0.3'},
    {'name': 'pla_pha_starch_40_30_30', 'comp': 'PLA:0.4,PHA:0.3,starch:0.3'},
    {'name': 'optimized_blend', 'comp': 'PLA:0.4,PHA:0.3,starch:0.2,chitosan:0.1'},
    {'name': 'starch_chitosan', 'comp': 'starch:0.6,chitosan:0.4'},
    {'name': 'low_cost', 'comp': 'starch:0.7,lignin:0.3'},
    {'name': 'marine_friendly', 'comp': 'PHA:0.6,starch:0.3,chitosan:0.1'},
]

def run_batch(output_dir: Path):
    """Run all compositions and collect results"""
    
    print("🥤 YOLO CUP - Batch Simulation Runner")
    print("=" * 60)
    print(f"Starting: {datetime.now()}")
    print(f"Testing {len(COMPOSITIONS)} polymer compositions")
    print()
    
    results_summary = []
    
    for i, test in enumerate(COMPOSITIONS, 1):
        print(f"\n[{i}/{len(COMPOSITIONS)}] Running: {test['name']}")
        print(f"Composition: {test['comp']}")
        
        try:
            # Run simulation (reduced params for CPU-only overnight run)
            result = subprocess.run([
                '/usr/bin/python3', 'src/yolo_cup_sim.py',
                '--composition', test['comp'],
                '--years', '100',
                '--chain_length', '800',
                '--output_dir', str(output_dir)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ {test['name']} completed")
                
                # Parse output for key metrics
                lines = result.stdout.split('\n')
                years = None
                degradation = None
                cost = None
                
                for line in lines:
                    if 'Simulation time:' in line:
                        years = float(line.split(':')[1].strip().split()[0])
                    if 'Final degradation:' in line:
                        degradation = float(line.split(':')[1].strip().replace('%', ''))
                    if 'Cost per kg:' in line:
                        cost = float(line.split('$')[1].strip())
                
                results_summary.append({
                    'name': test['name'],
                    'composition': test['comp'],
                    'years': years,
                    'degradation_pct': degradation,
                    'cost_per_kg': cost,
                    'status': 'success'
                })
            else:
                print(f"❌ {test['name']} failed")
                results_summary.append({
                    'name': test['name'],
                    'composition': test['comp'],
                    'status': 'failed',
                    'error': result.stderr[-200:]
                })
                
        except subprocess.TimeoutExpired:
            print(f"⏱️  {test['name']} timed out")
            results_summary.append({
                'name': test['name'],
                'composition': test['comp'],
                'status': 'timeout'
            })
        except Exception as e:
            print(f"❌ {test['name']} error: {e}")
            results_summary.append({
                'name': test['name'],
                'composition': test['comp'],
                'status': 'error',
                'error': str(e)
            })
        
        # Small delay between runs
        time.sleep(2)
    
    # Save summary
    summary_file = output_dir / 'batch_summary.json'
    with open(summary_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(COMPOSITIONS),
            'results': results_summary
        }, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"✅ Batch complete! Summary saved to: {summary_file}")
    print(f"Finished: {datetime.now()}")
    
    # Print quick summary
    print("\n📊 Quick Results:")
    for r in results_summary:
        if r['status'] == 'success':
            print(f"  {r['name']}: {r['years']:.1f} years, ${r['cost_per_kg']:.2f}/kg")
        else:
            print(f"  {r['name']}: {r['status']}")
    
    return results_summary


if __name__ == '__main__':
    output_dir = Path('/data/.openclaw/workspace/yolo-cup/results')
    output_dir.mkdir(parents=True, exist_ok=True)
    run_batch(output_dir)
