"""
Scalability Visualization
Depth vs. Width and Success Probability analysis
"""

import matplotlib.pyplot as plt
import csv
from pathlib import Path
import sys


def load_scalability_data(csv_file):
    """Load scalability study data"""
    data = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                'n_qubits': int(row['n_qubits']),
                'transpiled_depth': int(row['transpiled_depth']),
                'cnot_count': int(row['cnot_count']),
                'noisy_success': float(row['noisy_success']),
                'ideal_success': float(row['ideal_success']),
                'fidelity': float(row['fidelity'])
            })
    return data


def plot_scalability_analysis(data, output_file='public/results/scalability.png'):
    """Create dual-axis scalability plot"""
    n_qubits = [d['n_qubits'] for d in data]
    depths = [d['transpiled_depth'] for d in data]
    noisy_success = [d['noisy_success'] * 100 for d in data]
    cnot_counts = [d['cnot_count'] for d in data]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Axis 1: Circuit Depth
    color1 = '#2E86AB'
    ax1.set_xlabel('Number of Qubits (n)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Transpiled Circuit Depth', fontsize=12, fontweight='bold', color=color1)
    line1 = ax1.plot(n_qubits, depths, 'o-', linewidth=2.5, markersize=8,
                     color=color1, label='Circuit Depth')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(alpha=0.3, linestyle='--')

    # Axis 2: Success Probability
    ax2 = ax1.twinx()
    color2 = '#A23B72'
    ax2.set_ylabel('Success Probability (Noisy) [%]', fontsize=12, fontweight='bold', color=color2)
    line2 = ax2.plot(n_qubits, noisy_success, 's--', linewidth=2.5, markersize=8,
                     color=color2, label='Noisy Success %')
    ax2.tick_params(axis='y', labelcolor=color2)

    # Add CNOT count as bars
    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))
    color3 = '#06D6A0'
    ax3.set_ylabel('CNOT/ECR Count', fontsize=11, fontweight='bold', color=color3)
    ax3.bar(n_qubits, cnot_counts, alpha=0.3, color=color3, width=0.3, label='CNOTs')
    ax3.tick_params(axis='y', labelcolor=color3)

    ax1.set_title("Grover's Algorithm Scalability Analysis\nDepth vs. Width Trade-off",
                  fontsize=14, fontweight='bold', pad=20)

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', fontsize=10)

    ax1.set_xticks(n_qubits)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Scalability chart saved to: {output_file}")


def main():
    """Main visualization function"""
    benchmark_dir = Path('benchmarks')
    csv_files = list(benchmark_dir.glob('scalability_study_*.csv'))

    if not csv_files:
        print("Error: No scalability study CSV found. Run scalability_study.py first.")
        sys.exit(1)

    latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading data from: {latest_csv}")

    data = load_scalability_data(latest_csv)
    plot_scalability_analysis(data)


if __name__ == "__main__":
    main()
