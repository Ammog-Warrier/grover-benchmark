"""
Visualization Script for Grover's Algorithm Benchmarking
Generates dual-bar chart comparing ideal vs noisy distributions
"""

import matplotlib.pyplot as plt
import numpy as np
import csv
from pathlib import Path
import sys


def load_benchmark_data(csv_file):
    """
    Load benchmark data from CSV file
    """
    ideal_data = {}
    noisy_data = {}
    metrics = {}

    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        lines = list(reader)

        # Find where data ends and metrics begin
        data_section = True
        for i, row in enumerate(lines[1:], 1):  # Skip header
            if len(row) == 0:
                data_section = False
                continue

            if data_section:
                state, ideal_count, ideal_prob, noisy_count, noisy_prob = row
                ideal_data[state] = float(ideal_prob)
                noisy_data[state] = float(noisy_prob)
            else:
                if len(row) >= 2 and row[0] == 'Hellinger Fidelity':
                    metrics['fidelity'] = float(row[1])

    return ideal_data, noisy_data, metrics


def create_dual_bar_chart(ideal_data, noisy_data, metrics, output_file='benchmarks/comparison_chart.png'):
    """
    Create dual-bar chart comparing ideal vs noisy distributions
    """
    states = sorted(ideal_data.keys())
    ideal_probs = [ideal_data[state] for state in states]
    noisy_probs = [noisy_data[state] for state in states]

    x = np.arange(len(states))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))

    # Create bars
    bars1 = ax.bar(x - width/2, ideal_probs, width, label='Ideal',
                   color='#2E86AB', alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x + width/2, noisy_probs, width, label='Noisy (FakeBrisbane)',
                   color='#A23B72', alpha=0.8, edgecolor='black')

    # Highlight target state |101⟩
    target_idx = states.index('101')
    ax.bar(target_idx - width/2, ideal_probs[target_idx], width,
           color='#06D6A0', alpha=0.9, edgecolor='black', linewidth=2)
    ax.bar(target_idx + width/2, noisy_probs[target_idx], width,
           color='#06D6A0', alpha=0.9, edgecolor='black', linewidth=2)

    # Customize chart
    ax.set_xlabel('Quantum State', fontsize=12, fontweight='bold')
    ax.set_ylabel('Probability', fontsize=12, fontweight='bold')
    ax.set_title("Grover's Algorithm: Ideal vs Noisy Simulation\nTarget State: |101⟩",
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels([f'|{s}⟩' for s in states])
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Add fidelity annotation
    if 'fidelity' in metrics:
        ax.text(0.02, 0.98, f"Hellinger Fidelity: {metrics['fidelity']:.4f}",
                transform=ax.transAxes, fontsize=11,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # Add value labels on bars
    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            if height > 0.01:  # Only show labels for visible bars
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=8)

    add_value_labels(bars1)
    add_value_labels(bars2)

    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Dual-bar chart saved to: {output_file}")
        
    return fig



def main():
    """
    Main visualization function
    """
    # Get the most recent benchmark CSV
    benchmark_dir = Path('benchmarks')

    if not benchmark_dir.exists():
        print("Error: benchmarks directory not found. Run main.py first.")
        sys.exit(1)

    csv_files = list(benchmark_dir.glob('grover_benchmark_*.csv'))

    if not csv_files:
        print("Error: No benchmark CSV files found. Run main.py first.")
        sys.exit(1)

    # Use the most recent file
    latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading data from: {latest_csv}")

    # Load data
    ideal_data, noisy_data, metrics = load_benchmark_data(latest_csv)

    # Create visualization
    create_dual_bar_chart(ideal_data, noisy_data, metrics, output_file='benchmarks/comparison_chart.png')
    plt.show()


if __name__ == "__main__":
    main()
