"""
Report Generator for Grover's Benchmark
Combines visualizations into a single PDF report
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pathlib import Path
import sys
from datetime import datetime

import visualize
import bloch_animation

def generate_pdf_report():
    # Setup paths
    benchmark_dir = Path('benchmarks')
    if not benchmark_dir.exists():
        print("Error: benchmarks directory not found.")
        sys.exit(1)

    # Find latest CSV
    csv_files = list(benchmark_dir.glob('grover_benchmark_*.csv'))
    if not csv_files:
        print("Error: No benchmark CSV files found.")
        sys.exit(1)
    
    latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = benchmark_dir / f"grover_report_{timestamp}.pdf"

    print(f"Generating PDF report from: {latest_csv.name}")

    # Load data
    ideal_data, noisy_data, metrics = visualize.load_benchmark_data(latest_csv)

    # Create PDF
    with PdfPages(report_file) as pdf:
        # Page 1: Dual Bar Chart
        fig1 = visualize.create_dual_bar_chart(ideal_data, noisy_data, metrics, output_file=None)
        pdf.savefig(fig1)
        plt.close(fig1)
        print("Added Comparison Chart to PDF")

        # Page 2: Probability Evolution
        # Note: bloch_animation.create_probability_evolution rebuilds the circuit simulations internally
        # independent of the specific CSV run, which is acceptable for this level of demo.
        # Ideally, we would pass the data from CSV if we wanted perfect sync, but the evolution 
        # is theoretical/simulated anyway.
        fig2 = bloch_animation.create_probability_evolution(output_file=None)
        pdf.savefig(fig2)
        plt.close(fig2)
        print("Added Probability Evolution to PDF")

        # Metadata Page (Optional text page)
        fig_text = plt.figure(figsize=(8.5, 11))
        fig_text.text(0.1, 0.9, "Grover's Benchmark Report", fontsize=24, fontweight='bold')
        fig_text.text(0.1, 0.85, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fontsize=12)
        fig_text.text(0.1, 0.80, f"Source Data: {latest_csv.name}", fontsize=12)
        fig_text.text(0.1, 0.75, f"Hellinger Fidelity: {metrics.get('fidelity', 'N/A')}", fontsize=14)
        pdf.savefig(fig_text)
        plt.close(fig_text)

    print(f"\nReport successfully saved to: {report_file}")

if __name__ == "__main__":
    generate_pdf_report()
