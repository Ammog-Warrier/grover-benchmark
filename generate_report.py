
"""
Report Generator for Grover's Benchmark
Combines the latest results into a single clean PDF report.
Reads static assets from public/results/ and outputs PDF to benchmarks/.
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg
from pathlib import Path
from datetime import datetime
import sys

def generate_pdf_report():
    # Setup paths
    results_dir = Path('public/results')
    benchmark_dir = Path('benchmarks')
    
    # Create benchmarks dir if it doesn't exist (it holds the PDF)
    benchmark_dir.mkdir(exist_ok=True)
    
    if not results_dir.exists():
        print("Error: public/results directory not found.")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = benchmark_dir / f"grover_report_{timestamp}.pdf"

    print(f"Generating PDF report to: {report_file}")

    # List of images to include with titles
    # Using the filenames we established
    images_to_include = [
        ("topology_comparison.png", "Topology Comparison"),
        ("scalability.png", "Scalability Analysis"),
        ("bloch_sphere.png", "Bloch Sphere Visualization"),
        ("noise_sensitivity_sweep.png", "Noise Sensitivity Analysis"),
        ("probability_evolution.png", "Probability Evolution"),
        ("comparison_chart.png", "Ideal vs. Noisy Distribution")
    ]

    with PdfPages(report_file) as pdf:
        # Title Page
        fig_title = plt.figure(figsize=(11, 8.5)) # Landscapeish or Portrait
        ax_title = fig_title.add_subplot(111)
        ax_title.axis('off')
        
        ax_title.text(0.5, 0.7, "Grover's Algorithm Benchmarking Report", 
                     ha='center', va='center', fontsize=24, fontweight='bold')
        ax_title.text(0.5, 0.6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                     ha='center', va='center', fontsize=14)
        ax_title.text(0.5, 0.5, "Consolidated Performance Metrics & Visualizations", 
                     ha='center', va='center', fontsize=16, style='italic')
        
        # Read and add text content if available (e.g., best_topology.txt)
        txt_path = results_dir / "best_topology.txt"
        if txt_path.exists():
            try:
                with open(txt_path, 'r') as f:
                    content = f.read()
                ax_title.text(0.5, 0.3, "Best Topology Summary:\n" + content, 
                             ha='center', va='center', fontsize=12, 
                             bbox=dict(boxstyle="round,pad=0.5", fc="wheat", ec="black", alpha=0.5))
                print("Added best_topology.txt content to Title Page")
            except Exception as e:
                print(f"Failed to read text file: {e}")

        pdf.savefig(fig_title)
        plt.close(fig_title)

        # Add each image
        for filename, title in images_to_include:
            img_path = results_dir / filename
            if img_path.exists():
                try:
                    # Create a figure for the image
                    img = mpimg.imread(str(img_path))
                    
                    # Determine aspects and page flow
                    # Basic approach: One image per page
                    
                    # A4 (ish) page size in inches
                    page_w, page_h = 11.69, 8.27 # A4 Landscape
                    
                    fig = plt.figure(figsize=(page_w, page_h))
                    ax = fig.add_subplot(111)
                    
                    ax.imshow(img)
                    ax.axis('off')
                    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
                    
                    plt.tight_layout()
                    pdf.savefig(fig)
                    plt.close(fig)
                    print(f"Added {filename} to PDF")
                except Exception as e:
                    print(f"Failed to process {filename}: {e}")
            else:
                print(f"Warning: Image {filename} not found in {results_dir}")

    print(f"\nReport successfully saved to: {report_file}")

if __name__ == "__main__":
    generate_pdf_report()
