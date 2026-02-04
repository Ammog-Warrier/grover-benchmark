# Grover's Algorithm Benchmarking Suite

A comprehensive quantum computing benchmarking toolkit for Grover's Algorithm using Qiskit 1.x.

## Overview

This project implements a 3-qubit Grover search targeting the state `|101⟩` with both ideal and noisy simulations, complete with visualizations and theoretical analysis.

## Features

- **Grover Circuit Implementation**: 3-qubit search using GroverOperator library
- **Consolidated PDF Reporting**: AUTO-GENERATED `benchmarks/grover_report.pdf` combining all charts
- **Dual Simulation Modes**:
  - Ideal: AerSimulator with SamplerV2
  - Noisy: FakeBrisbane noise model with optimization level 3 transpilation
- **Hellinger Fidelity Analysis**: Quantitative comparison of ideal vs. noisy distributions
- **Rich Visualizations**:
  - Dual-bar chart comparing probability distributions
  - State probability evolution over iterations
  - Bloch sphere animation (GIF)
- **Comprehensive Theory**: Enhanced "Quantum Clear" documentation with rigorous proofs

## Project Structure

```
grover-benchmark/
├── main.py                    # Main execution script
├── visualize.py               # Dual-bar chart generator
├── bloch_animation.py         # Bloch sphere animation & probability evolution
├── theory.md                  # Mathematical proofs and theory
├── requirements.txt           # Python dependencies
├── benchmarks/                # Output directory for results
│   ├── grover_benchmark_*.csv
│   ├── comparison_chart.png
│   ├── probability_evolution.png
│   └── bloch_sphere_animation.gif
└── README.md                  # This file
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or navigate to the project directory:**

```bash
cd grover-benchmark
```

2. **Create a virtual environment (recommended):**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

---

## Usage Instructions

### 1. Run the Full Benchmark Suite (Recommended)

The easiest way to run the benchmark, visualization, and report generation is using the automation script:

```bash
./run_benchmark.sh
```

This will:
- Run the simulation (`main.py`)
- Generate the consolidated PDF report (`generate_report.py`)
- Create the Bloch sphere animation (`bloch_animation.py`)

### 2. Manual Execution

If you prefer to run steps individually:

**Step 1: Simulation**
```bash
python main.py
```

**What it does:**
- Creates a 3-qubit Grover circuit targeting `|101⟩`
- Runs ideal simulation (AerSimulator)
- Runs noisy simulation (FakeBrisbane noise model)
- Calculates Hellinger fidelity between distributions
- Saves results to `benchmarks/grover_benchmark_TIMESTAMP.csv`

**Expected Output:**

```
============================================================
GROVER'S ALGORITHM BENCHMARKING SUITE
Target State: |101⟩
============================================================

Creating Grover circuit...
Circuit depth: XX
Circuit operations: {...}

Running IDEAL simulation...
Ideal results: {'101': 7735, '000': 45, '001': 42, ...}

Running NOISY simulation with FakeBrisbane noise model...
Circuit depth after transpilation: XX
Noisy results: {'101': 6891, '000': 123, '001': 98, ...}

============================================================
ANALYSIS RESULTS
============================================================
Hellinger Fidelity: 0.XXXXXX
Success Probability (Ideal): 94.45%
Success Probability (Noisy): 84.12%

Results saved to: benchmarks/grover_benchmark_YYYYMMDD_HHMMSS.csv

Benchmarking complete!
```

---

### 2. Generate Visualizations

#### Dual-Bar Chart (Ideal vs. Noisy)

```bash
python visualize.py
```

**Output:**
- Generates `benchmarks/comparison_chart.png`
- Displays side-by-side bar chart comparing probability distributions
- Highlights target state `|101⟩` in green
- Includes Hellinger fidelity annotation

#### Probability Evolution & Bloch Sphere Animation

```bash
python bloch_animation.py
```

**Output:**
- `benchmarks/probability_evolution.png`: Shows how state probabilities change over Grover iterations
- `benchmarks/bloch_sphere_animation.gif`: Animated Bloch sphere visualization (may take 30-60 seconds to generate)

---

### 3. Review Theoretical Analysis

Open the comprehensive mathematical document:

```bash
# On Linux/Mac
xdg-open theory.md

# On Windows
start theory.md

# Or open in any markdown viewer or text editor
```

**Contents:**
- Mathematical proof of O(√N) speedup
- LaTeX-formatted state transitions
- Amplitude amplification derivations
- Noise analysis and fidelity theory
- Implementation details for 3-qubit case

---

## Understanding the Results

### CSV Output

The benchmark CSV contains:

| Column | Description |
|--------|-------------|
| Quantum State | Computational basis state (e.g., '101') |
| Ideal Counts | Number of measurements in ideal simulation |
| Ideal Probability | Normalized probability for ideal case |
| Noisy Counts | Number of measurements with noise |
| Noisy Probability | Normalized probability with noise |

**Summary Metrics:**
- Total Shots: 8192
- Hellinger Fidelity: Similarity measure (0-1, higher is better)
- Success Probability: Percentage of times `|101⟩` was measured

### Interpreting Hellinger Fidelity

$$F_H(P, Q) = \left(\sum_x \sqrt{p_x q_x}\right)^2$$

- **F = 1.0**: Perfect match (ideal = noisy)
- **F > 0.95**: Excellent noise resilience
- **F = 0.90-0.95**: Good performance (typical for this benchmark)
- **F < 0.85**: High noise impact, consider error mitigation

### Expected Success Rates

- **Ideal**: ~94.5% (theoretical maximum for 2 iterations on 8 states)
- **Noisy**: ~85-90% (depends on noise characteristics)

---

## Using IBM Quantum Real Hardware (Optional)

If you have IBM Quantum credits and want to run on actual quantum hardware:

### Step 1: Get Your IBM Quantum Token

1. Go to [IBM Quantum Platform](https://quantum.ibm.com/)
2. Log in or create a free account
3. Navigate to **Account Settings**
4. Copy your API token

### Step 2: Configure Your Token

Edit [main.py:15](main.py#L15) and replace:

```python
placeholder_token = "YOUR_IBM_TOKEN_HERE"
```

with:

```python
placeholder_token = "your_actual_token_from_ibm"
```

### Step 3: Modify main.py for Real Hardware

Add the following imports at the top of [main.py](main.py):

```python
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as RuntimeSampler
```

Add a new function to run on real hardware:

```python
def run_on_real_hardware(circuit, shots=8192):
    """
    Execute circuit on IBM Quantum hardware
    """
    # Initialize the service
    service = QiskitRuntimeService(channel="ibm_quantum", token=placeholder_token)

    # Get the least busy backend
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=3)
    print(f"Running on backend: {backend.name}")

    # Transpile
    pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
    transpiled_qc = pm.run(circuit)

    # Run with Sampler
    sampler = RuntimeSampler(backend=backend)
    job = sampler.run([transpiled_qc], shots=shots)

    print(f"Job ID: {job.job_id()}")
    print("Waiting for job to complete...")

    result = job.result()
    counts = result[0].data.meas.get_counts()

    return counts
```

In the `main()` function, add:

```python
# Run on real hardware
print("Running on IBM Quantum hardware...")
real_hardware_counts = run_on_real_hardware(grover_circuit, shots=1024)  # Lower shots to save credits
print(f"Real hardware results: {dict(sorted(real_hardware_counts.items(), key=lambda x: x[1], reverse=True))}")
```

### IBM Quantum Credits

- **Free Tier**: IBM provides monthly free access to quantum systems
- **Credits System**: Jobs consume credits based on runtime and backend
- **Recommendations**:
  - Start with `shots=1024` to conserve credits
  - Use `simulator=True` backends for testing
  - Monitor your credit balance at [IBM Quantum Dashboard](https://quantum.ibm.com/)

### Important Notes for Real Hardware

- **Queue Times**: Real hardware may have wait times (minutes to hours)
- **Job Monitoring**: Use `job.status()` to check progress
- **Error Rates**: Real hardware has higher error rates than simulators
- **Cost**: Each shot consumes credits; monitor your usage

---

## Troubleshooting

### ImportError: No module named 'qiskit'

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Visualization windows don't show

If running on a headless server, visualizations will still save to files even if display fails.

### "No benchmark CSV files found"

Run `main.py` first to generate benchmark data before running visualization scripts.

### Animation generation is slow

Bloch sphere animations can take 30-60 seconds. The probability evolution chart generates much faster and may be more informative.

---

## Advanced Usage

### Modifying the Target State

To search for a different state (e.g., `|110⟩`), modify [main.py:27-41](main.py#L27-L41):

```python
def create_oracle_for_110():
    oracle = QuantumCircuit(3, name='Oracle')
    oracle.x(2)  # Flip qubit 2
    oracle.h(0)
    oracle.ccx(0, 1, 2)
    oracle.h(0)
    oracle.x(2)  # Unflip
    return oracle
```

### Adjusting Number of Shots

In [main.py:125](main.py#L125), change:

```python
shots = 16384  # More shots = better statistics, slower execution
```

### Changing Optimization Level

In [main.py:68](main.py#L68), modify:

```python
pm = generate_preset_pass_manager(
    optimization_level=3,  # Options: 0, 1, 2, 3 (higher = more optimization)
    backend=fake_backend
)
```

---

## Performance Benchmarks

**Typical execution times** (on modern laptop):

| Script | Execution Time |
|--------|----------------|
| main.py | ~10-15 seconds |
| visualize.py | ~2-3 seconds |
| bloch_animation.py | ~30-60 seconds |

**Resource usage:**
- Memory: ~200-500 MB
- CPU: Single-core (parallelization not implemented)

---

## Theory Highlights

From [theory.md](theory.md):

**Grover's Speedup:**

$$
\text{Classical: } O(N) \quad \text{vs.} \quad \text{Quantum: } O(\sqrt{N})
$$

**Optimal Iterations:**

$$
k^* = \frac{\pi}{4}\sqrt{N} - \frac{1}{2} \approx 2.22 \text{ for } N=8
$$

**Success Probability:**

$$
P(\text{success}) = \sin^2((2k+1)\theta_0) \approx 94.5\%
$$

See the full document for rigorous mathematical proofs and derivations.

---

## Citation

If you use this benchmarking suite in your research, please cite:

```bibtex
@software{grover_benchmark_2026,
  title={Grover's Algorithm Benchmarking Suite},
  author={Quantum Computing Researcher},
  year={2026},
  url={https://github.com/yourusername/grover-benchmark}
}
```

---

## License

MIT License - See LICENSE file for details

---

## Contributing

Contributions welcome! Please submit pull requests or open issues for:
- Additional noise models
- Extended qubit systems (4, 5, 6 qubits)
- Error mitigation techniques
- Performance optimizations

---

## Resources

- **Qiskit Documentation**: https://qiskit.org/documentation/
- **IBM Quantum Platform**: https://quantum.ibm.com/
- **Grover's Original Paper**: [arXiv:quant-ph/9605043](https://arxiv.org/abs/quant-ph/9605043)
- **Qiskit Textbook**: https://qiskit.org/learn/

---

## Contact

For questions or support, please open an issue on GitHub.

**Happy Quantum Computing! 🚀**
