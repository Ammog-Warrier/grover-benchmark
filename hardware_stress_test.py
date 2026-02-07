
import numpy as np
import matplotlib.pyplot as plt
import csv
from datetime import datetime
from pathlib import Path

from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import grover_operator
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit.primitives import BackendSamplerV2
from qiskit_ibm_runtime.fake_provider import FakeBrisbane, FakeKyoto, FakeSherbrooke

# Import from local main.py
try:
    from main import get_grover_oracle, calculate_hellinger_fidelity
except ImportError:
    print("Could not import from main.py, defining functions locally.")
    
    def get_grover_oracle(target_bitstring):
        n = len(target_bitstring)
        oracle = QuantumCircuit(n, name='Oracle')
        for i, bit in enumerate(target_bitstring):
            if bit == '0':
                oracle.x(i)
        oracle.h(n-1)
        if n == 3:
            oracle.ccx(0, 1, 2)
        else:
            oracle.mcx(list(range(n-1)), n-1)
        oracle.h(n-1)
        for i, bit in enumerate(target_bitstring):
            if bit == '0':
                oracle.x(i)
        return oracle

    def calculate_hellinger_fidelity(ideal_counts, noisy_counts, shots):
        all_states = set(ideal_counts.keys()) | set(noisy_counts.keys())
        ideal_probs = {state: ideal_counts.get(state, 0) / shots for state in all_states}
        noisy_probs = {state: noisy_counts.get(state, 0) / shots for state in all_states}
        hellinger_sum = sum(np.sqrt(ideal_probs[state] * noisy_probs[state]) for state in all_states)
        return hellinger_sum ** 2


def build_grover_circuit(target_bitstring):
    """Builds a Grover circuit for N qubits targeting the specific bitstring."""
    n = len(target_bitstring)
    qc = QuantumCircuit(n, n) 
    
    qc.h(range(n))
    qc.barrier()
    
    oracle = get_grover_oracle(target_bitstring)
    grover_op = grover_operator(oracle)
    
    optimal_iterations = int(np.round(np.pi / 4 * np.sqrt(2**n)))
    
    for _ in range(optimal_iterations):
        qc.compose(grover_op, inplace=True)
        qc.barrier()
        
    qc.measure(range(n), range(n))
    return qc

def run_experiment_1_noise_sweep():
    print("\n" + "="*50)
    print("Experiment 1: Noise Sensitivity Sweep")
    print("="*50)
    
    target = '101'
    qc = build_grover_circuit(target)
    
    # Error rates (log space)
    error_rates = np.logspace(np.log10(0.0001), np.log10(0.1), 10)
    
    success_probs = []
    
    print(f"Sweeping depolarizing error from {error_rates[0]:.4f} to {error_rates[-1]:.4f} across {len(error_rates)} points.")
    
    for error_rate in error_rates:
        noise_model = NoiseModel()
        
        error_1q = depolarizing_error(error_rate, 1)
        error_2q = depolarizing_error(error_rate, 2)
        
        # Apply error to standard gates
        noise_model.add_all_qubit_quantum_error(error_1q, ['u']) 
        noise_model.add_all_qubit_quantum_error(error_2q, ['cx'])

        backend = AerSimulator(noise_model=noise_model)
        sampler = BackendSamplerV2(backend=backend)
        
        transpiled_qc = transpile(qc, backend, basis_gates=['u', 'cx'], optimization_level=1)
        
        job = sampler.run([transpiled_qc], shots=4096)
        result = job.result()
        
        # Handle result data structure
        data_keys = result[0].data.keys() 
        c_reg_name = list(data_keys)[0]
        counts = result[0].data[c_reg_name].get_counts()
        
        target_count = counts.get(target, 0)
        prob = target_count / 4096
        success_probs.append(prob)
        print(f"Error: {error_rate:.4f} -> Success: {prob:.4f}")

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.semilogx(error_rates, success_probs, 'o-', label='Success Probability')
    plt.axhline(y=0.125, color='r', linestyle='--', label='Classical Breakeven (12.5%)')
    plt.xlabel('Gate Error Rate (Depolarizing)')
    plt.ylabel('Success Probability P(|101>)')
    plt.title('Experiment 1: Noise Sensitivity Sweep')
    plt.grid(True, which="both", ls="-")
    plt.legend()
    
    output_path = 'public/results/noise_sensitivity_sweep.png'
    plt.savefig(output_path)
    print(f"Saved plot: {output_path}")

def run_experiment_2_topology():
    print("\n" + "="*50)
    print("Experiment 2: Topology Comparison")
    print("="*50)
    
    target = '1011'
    qc = build_grover_circuit(target)
    
    backends = {
        'FakeBrisbane': FakeBrisbane(),
        'FakeKyoto': FakeKyoto(),
        'FakeSherbrooke': FakeSherbrooke()
    }
    
    fidelities = {}
    shots = 4096
    
    # Ideal simulation
    ideal_backend = AerSimulator()
    ideal_sampler = BackendSamplerV2(backend=ideal_backend)
    ideal_qc = transpile(qc, ideal_backend)
    ideal_job = ideal_sampler.run([ideal_qc], shots=shots)
    ideal_counts = ideal_job.result()[0].data.c.get_counts()
    
    best_backend = None
    best_fidelity = -1.0
    
    for name, backend in backends.items():
        print(f"Running on {name}...")
        
        transpiled_qc = transpile(qc, backend, optimization_level=3)
        sim_backend = AerSimulator.from_backend(backend)
        sampler = BackendSamplerV2(backend=sim_backend)
        
        job = sampler.run([transpiled_qc], shots=shots)
        result = job.result()
        
        c_reg_name = list(result[0].data.keys())[0]
        noisy_counts = result[0].data[c_reg_name].get_counts()
        
        fid = calculate_hellinger_fidelity(ideal_counts, noisy_counts, shots)
        fidelities[name] = fid
        print(f"  > Fidelity: {fid:.4f}")
        
        if fid > best_fidelity:
            best_fidelity = fid
            best_backend = name
            
    with open('public/results/best_topology.txt', 'w') as f:
        f.write(f"Best Performing Topology: {best_backend}\n")
        f.write(f"Fidelity: {best_fidelity:.6f}\n")
        f.write(f"Circuit Target: {target}\n")
    print(f"Saved best topology to public/results/best_topology.txt")
    
    # Plotting
    plt.figure(figsize=(10, 6))
    names = list(fidelities.keys())
    vals = list(fidelities.values())
    
    plt.bar(names, vals, color=['#4285F4', '#DB4437', '#F4B400'])
    plt.ylabel('Hellinger Fidelity')
    plt.title(f'Topology Comparison (4-Qubit Grover, Target={target})')
    plt.ylim(0, 1.0)
    for i, v in enumerate(vals):
        plt.text(i, v + 0.01, f"{v:.3f}", ha='center')
        
    output_path = 'public/results/topology_comparison.png'
    plt.savefig(output_path)
    print(f"Saved plot: {output_path}")
    
if __name__ == "__main__":
    run_experiment_1_noise_sweep()
    run_experiment_2_topology()
