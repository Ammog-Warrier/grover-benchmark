"""
Scalability Analysis for Grover's Algorithm
Depth vs. Width analysis across multiple qubit counts
"""

import numpy as np
import csv
from datetime import datetime
from pathlib import Path

from qiskit import QuantumCircuit
from qiskit.circuit.library import grover_operator
from qiskit_aer import AerSimulator
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime.fake_provider import FakeBrisbane

from main import get_grover_oracle, calculate_hellinger_fidelity


def create_grover_circuit_nqubit(n, target_bitstring):
    """Create Grover circuit for n qubits"""
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    qc.barrier()

    oracle = get_grover_oracle(target_bitstring)
    grover_op = grover_operator(oracle)

    # Optimal iterations: k ≈ π/4 * sqrt(2^n)
    k_optimal = int(np.round(np.pi / 4 * np.sqrt(2**n)))

    for _ in range(k_optimal):
        qc.compose(grover_op, inplace=True)
        qc.barrier()

    qc.measure(range(n), range(n))
    return qc, k_optimal


def run_scalability_study():
    """Run scalability analysis for n=3,4,5,6"""
    print("=" * 60)
    print("GROVER SCALABILITY STUDY")
    print("=" * 60)
    print()

    results = []
    fake_backend = FakeBrisbane()
    simulator = AerSimulator()
    noisy_sim = AerSimulator.from_backend(fake_backend)
    shots = 4096

    for n in [3, 4, 5, 6]:
        print(f"Analyzing {n}-qubit system (N={2**n} states)")
        
        target = '1' * n
        qc, k_optimal = create_grover_circuit_nqubit(n, target)
        
        # Transpile for FakeBrisbane
        pm = generate_preset_pass_manager(optimization_level=3, backend=fake_backend)
        transpiled_qc = pm.run(qc)

        depth = transpiled_qc.depth()
        ops = transpiled_qc.count_ops()
        cnot_count = ops.get('ecr', 0) + ops.get('cx', 0) + ops.get('cnot', 0)

        # Run ideal simulation
        pm_ideal = generate_preset_pass_manager(optimization_level=1, backend=simulator)
        ideal_qc = pm_ideal.run(qc)
        ideal_counts = simulator.run(ideal_qc, shots=shots).result().get_counts()
        ideal_success = ideal_counts.get(target, 0) / shots

        # Run noisy simulation
        noisy_counts = noisy_sim.run(transpiled_qc, shots=shots).result().get_counts()
        noisy_success = noisy_counts.get(target, 0) / shots

        fidelity = calculate_hellinger_fidelity(ideal_counts, noisy_counts, shots)

        print(f"  Target: |{target}⟩, Iterations: {k_optimal}")
        print(f"  Depth: {depth}, CNOTs: {cnot_count}")
        print(f"  Success (Ideal/Noisy): {ideal_success*100:.1f}% / {noisy_success*100:.1f}%")
        print(f"  Fidelity: {fidelity:.4f}\n")

        results.append({
            'n_qubits': n,
            'N_states': 2**n,
            'target': target,
            'k_optimal': k_optimal,
            'original_depth': qc.depth(),
            'transpiled_depth': depth,
            'cnot_count': cnot_count,
            'ideal_success': ideal_success,
            'noisy_success': noisy_success,
            'fidelity': fidelity
        })

    # Save results
    Path("benchmarks").mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"benchmarks/scalability_study_{timestamp}.csv"

    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"Results saved to: {csv_file}")
    return results, csv_file


if __name__ == "__main__":
    run_scalability_study()
