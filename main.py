"""
Grover's Algorithm Benchmarking Suite
3-Qubit Implementation targeting state '101'
Qiskit 1.x Compatible
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


# IBM Quantum Token (Replace with your actual token)
placeholder_token = "YOUR_IBM_TOKEN_HERE"


def create_oracle_for_101():
    """
    Create oracle that marks the state |101⟩
    Uses phase kickback with ancilla qubit
    """
    oracle = QuantumCircuit(3, name='Oracle')

    # We want to mark |101⟩, so flip qubit 1 (which is 0)
    oracle.x(1)

    # Multi-controlled Z gate (marks the target state)
    oracle.h(2)
    oracle.ccx(0, 1, 2)
    oracle.h(2)

    # Uncompute the X gate
    oracle.x(1)

    return oracle


def create_grover_circuit():
    """
    Create complete Grover circuit for 3-qubit search targeting |101⟩
    """
    # Create quantum circuit
    qc = QuantumCircuit(3, 3)

    # Initialize to uniform superposition
    qc.h([0, 1, 2])
    qc.barrier()

    # Create oracle
    oracle = create_oracle_for_101()

    # Create Grover operator (oracle + diffusion) using the grover_operator function
    grover_op = grover_operator(oracle)

    # For N=8 states, optimal iterations = π/4 * sqrt(8) ≈ 2.22 → 2 iterations
    num_iterations = 2

    for i in range(num_iterations):
        qc.compose(grover_op, inplace=True)
        qc.barrier()

    # Measure
    qc.measure([0, 1, 2], [0, 1, 2])

    return qc


def run_ideal_simulation(circuit, shots=8192):
    """
    Execute circuit on ideal AerSimulator
    """
    print("Running IDEAL simulation...")

    # Use AerSimulator backend
    simulator = AerSimulator()

    # Transpile for the backend
    pm = generate_preset_pass_manager(optimization_level=1, backend=simulator)
    transpiled_qc = pm.run(circuit)

    # Run simulation
    job = simulator.run(transpiled_qc, shots=shots)
    result = job.result()

    # Extract counts
    counts = result.get_counts()

    return counts


def run_noisy_simulation(circuit, shots=8192):
    """
    Execute circuit with FakeBrisbane noise model
    """
    print("Running NOISY simulation with FakeBrisbane noise model...")

    # Get fake backend
    fake_backend = FakeBrisbane()

    # Create noisy simulator
    noisy_sim = AerSimulator.from_backend(fake_backend)

    # Transpile with optimization level 3
    pm = generate_preset_pass_manager(
        optimization_level=3,
        backend=fake_backend
    )
    transpiled_qc = pm.run(circuit)

    print(f"Circuit depth after transpilation: {transpiled_qc.depth()}")
    print(f"Circuit gates after transpilation: {transpiled_qc.count_ops()}")

    # Run on noisy simulator
    job = noisy_sim.run(transpiled_qc, shots=shots)
    result = job.result()
    counts = result.get_counts()

    return counts


def calculate_hellinger_fidelity(ideal_counts, noisy_counts, shots):
    """
    Calculate Hellinger fidelity between two probability distributions

    Hellinger fidelity: F(P,Q) = (Σ √(p_i * q_i))²
    """
    # Get all possible states
    all_states = set(ideal_counts.keys()) | set(noisy_counts.keys())

    # Convert counts to probabilities
    ideal_probs = {state: ideal_counts.get(state, 0) / shots for state in all_states}
    noisy_probs = {state: noisy_counts.get(state, 0) / shots for state in all_states}

    # Calculate Hellinger fidelity
    hellinger_sum = sum(
        np.sqrt(ideal_probs[state] * noisy_probs[state])
        for state in all_states
    )

    fidelity = hellinger_sum ** 2

    return fidelity


def save_results_to_csv(ideal_counts, noisy_counts, fidelity, shots):
    """
    Save benchmark results to CSV file in /benchmarks folder
    """
    # Create benchmarks directory if it doesn't exist
    Path("benchmarks").mkdir(exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"benchmarks/grover_benchmark_{timestamp}.csv"

    # Prepare data
    all_states = sorted(set(ideal_counts.keys()) | set(noisy_counts.keys()))

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write header
        writer.writerow(['Quantum State', 'Ideal Counts', 'Ideal Probability',
                        'Noisy Counts', 'Noisy Probability'])

        # Write data for each state
        for state in all_states:
            ideal_count = ideal_counts.get(state, 0)
            noisy_count = noisy_counts.get(state, 0)
            ideal_prob = ideal_count / shots
            noisy_prob = noisy_count / shots

            writer.writerow([state, ideal_count, f"{ideal_prob:.4f}",
                           noisy_count, f"{noisy_prob:.4f}"])

        # Write summary statistics
        writer.writerow([])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Shots', shots])
        writer.writerow(['Hellinger Fidelity', f"{fidelity:.6f}"])
        writer.writerow(['Target State', '101'])
        writer.writerow(['Success Probability (Ideal)',
                        f"{ideal_counts.get('101', 0) / shots:.4f}"])
        writer.writerow(['Success Probability (Noisy)',
                        f"{noisy_counts.get('101', 0) / shots:.4f}"])

    print(f"\nResults saved to: {filename}")
    return filename


def main():
    """
    Main execution function
    """
    print("=" * 60)
    print("GROVER'S ALGORITHM BENCHMARKING SUITE")
    print("Target State: |101⟩")
    print("=" * 60)
    print()

    # Create Grover circuit
    print("Creating Grover circuit...")
    grover_circuit = create_grover_circuit()

    print(f"Circuit depth: {grover_circuit.depth()}")
    print(f"Circuit operations: {grover_circuit.count_ops()}")
    print()

    # Set number of shots
    shots = 8192

    # Run ideal simulation
    ideal_counts = run_ideal_simulation(grover_circuit, shots)
    print(f"Ideal results: {dict(sorted(ideal_counts.items(), key=lambda x: x[1], reverse=True))}")
    print()

    # Run noisy simulation
    noisy_counts = run_noisy_simulation(grover_circuit, shots)
    print(f"Noisy results: {dict(sorted(noisy_counts.items(), key=lambda x: x[1], reverse=True))}")
    print()

    # Calculate Hellinger fidelity
    fidelity = calculate_hellinger_fidelity(ideal_counts, noisy_counts, shots)

    print("=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    print(f"Hellinger Fidelity: {fidelity:.6f}")
    print(f"Success Probability (Ideal): {ideal_counts.get('101', 0) / shots * 100:.2f}%")
    print(f"Success Probability (Noisy): {noisy_counts.get('101', 0) / shots * 100:.2f}%")
    print()

    # Save results
    csv_file = save_results_to_csv(ideal_counts, noisy_counts, fidelity, shots)

    print("\nBenchmarking complete!")


if __name__ == "__main__":
    main()
