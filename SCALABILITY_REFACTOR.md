# Scalability Refactor Summary

## Changes Made

### 1. Dynamic Oracle Generation
**File:** [main.py](main.py)
- Added `get_grover_oracle(target_bitstring)` - works for any n-qubit target
- Uses X-gate wrapping for '0' bits, multi-controlled Z via H-MCX-H pattern
- Backward compatible via `create_oracle_for_101()` wrapper

### 2. Scalability Study Module
**File:** [scalability_study.py](scalability_study.py) (NEW)
- Analyzes n=3,4,5,6 qubit systems
- Calculates optimal iterations: k ≈ π/4 × √(2^n)
- Transpiles with FakeBrisbane (optimization_level=3)
- Collects metrics: width, depth, CNOT count, fidelity, success rates
- Outputs to `benchmarks/scalability_study_TIMESTAMP.csv`

### 3. Scalability Visualization
**File:** [visualize_scalability.py](visualize_scalability.py) (NEW)
- Dual-axis plot: Circuit Depth + Success Probability vs. Qubits
- Triple metric display (depth, success %, CNOT count)
- Outputs to `benchmarks/scalability_chart.png`

## Key Results

| Qubits | Depth | CNOTs | Ideal Success | Noisy Success | Fidelity |
|--------|-------|-------|---------------|---------------|----------|
| 3      | 174   | 39    | 94.2%         | 75.2%         | 0.921    |
| 4      | 470   | 111   | 96.3%         | 41.5%         | 0.603    |
| 5      | 1,846 | 530   | 99.9%         | 5.4%          | 0.058    |
| 6      | 6,840 | 1,940 | 99.6%         | 1.6%          | 0.023    |

**Insight:** Noise impact grows exponentially - success drops from 75% → 1.6% as qubits scale 3→6.

## Usage

```bash
# Run scalability analysis
python scalability_study.py

# Generate visualization
python visualize_scalability.py

# Test dynamic oracle
python -c "from main import get_grover_oracle; print(get_grover_oracle('1010'))"
```

## Preserved Features
✅ DataBin fix from earlier debug session
✅ Qiskit 2.x compatibility (grover_operator function)
✅ All original benchmarking functionality
