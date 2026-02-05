
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
# Assuming main.py is in the same directory or python path
try:
    from main import get_grover_oracle, calculate_hellinger_fidelity
except ImportError:
    # Fallback if imports fail (e.g. running from different dir), though we are in project root
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
    """
    Builds a Grover circuit for N qubits targeting the specific bitstring.
    """
    n = len(target_bitstring)
    qc = QuantumCircuit(n, n) # n qubits, n classical bits
    
    # Initialization
    qc.h(range(n))
    qc.barrier()
    
    # Oracle
    oracle = get_grover_oracle(target_bitstring)
    
    # Grover Operator
    grover_op = grover_operator(oracle)
    
    # Optimal iterations: round(pi/4 * sqrt(2^n))
    # N=3 -> ~2
    # N=4 -> ~3
    optimal_iterations = int(np.round(np.pi / 4 * np.sqrt(2**n)))
    
    for _ in range(optimal_iterations):
        qc.compose(grover_op, inplace=True)
        qc.barrier()
        
    # Measure
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
        # Create Noise Model
        noise_model = NoiseModel()
        # Depolarizing error on 1-qubit gates ('u') and 2-qubit gates ('cx')
        # Note: 'u' covers u1, u2, u3. using 'u' is standard for base gate noise in some contexts, 
        # but often we specify ['u1', 'u2', 'u3', 'sx', 'rz']. 
        # The user asked for "apply to all cx and u gates".
        # We will add to 'u1', 'u2', 'u3' and 'cx'. And maybe 'rx', 'ry', 'rz' if they are broken down?
        # A clearer way with Aer is to add to all 1-qubit and 2-qubit gates or specific names.
        # User said "cx and u gates". We'll interpret 'u' as the generic single qubit unitary.
        
        error_1q = depolarizing_error(error_rate, 1)
        error_2q = depolarizing_error(error_rate, 2)
        
        noise_model.add_all_qubit_quantum_error(error_1q, ['u', 'u1', 'u2', 'u3', 'rz', 'sx', 'x', 'h']) # Broad coverage to be safe or just u
        # Strictly "cx and u gates":
        # noise_model.add_all_qubit_quantum_error(error_1q, ['u'])
        # noise_model.add_all_qubit_quantum_error(error_2q, ['cx'])
        # However, transpile typically uses specific basis gates.
        # We'll stick to adding to 'u' and 'cx' and hope transpilation uses them (Aer usually supports 'u').
        # Better: add to standard basis set [id, rz, sx, x, cx] used by IBM backends?
        # Use instructions: "Apply this error to all cx and u gates."
        noise_model.add_all_qubit_quantum_error(error_1q, ['u']) 
        noise_model.add_all_qubit_quantum_error(error_2q, ['cx'])

        backend = AerSimulator(noise_model=noise_model)
        
        # SamplerV2
        sampler = BackendSamplerV2(backend=backend)
        
        # Transpile 
        # We need to transpile to a basis that matches our noise model? 
        # If we added noise to 'u' and 'cx', we should transpile to ['u', 'cx'].
        transpiled_qc = transpile(qc, backend, basis_gates=['u', 'cx'], optimization_level=1)
        
        job = sampler.run([transpiled_qc], shots=4096)
        result = job.result()
        
        # Process results
        # SamplerV2 returns BitArray in data.c (assuming 'c' register)
        # We need to check register name. qc constructed with QuantumCircuit(n, n) uses 'c' ?? 
        # Wait, qiskit default cr name is 'c' only if not specified? 
        # Actually in 1.0, it might be 'c0' or similar.
        # Safer: Inspect the data object keys.
        data_keys = result[0].data.keys() # e.g. ['c']
        # For now assume 'c' or the first one found.
        c_reg_name = list(data_keys)[0]
        counts = result[0].data[c_reg_name].get_counts()
        
        # Success probability (target '101')
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
    plt.savefig('noise_sensitivity_sweep.png')
    print("Saved plot: noise_sensitivity_sweep.png")

def run_experiment_2_topology():
    print("\n" + "="*50)
    print("Experiment 2: Topology Comparison")
    print("="*50)
    
    target = '1101' # 4-qubit target (implied by "4-qubit Grover circuit" and random choice or specific. "1011" or "1101")
    # Let's use '1011' or similar. User: "Run the same 4-qubit Grover circuit".
    # I'll pick '1101' arbitrarily or '1111'. '1011' is nice.
    target = '1011'
    qc = build_grover_circuit(target)
    
    backends = {
        'FakeBrisbane': FakeBrisbane(),
        'FakeKyoto': FakeKyoto(),
        'FakeSherbrooke': FakeSherbrooke()
    }
    
    fidelities = {}
    shots = 4096
    
    # Ideal simulation for reference
    ideal_backend = AerSimulator()
    ideal_sampler = BackendSamplerV2(backend=ideal_backend)
    ideal_qc = transpile(qc, ideal_backend)
    ideal_job = ideal_sampler.run([ideal_qc], shots=shots)
    ideal_counts = ideal_job.result()[0].data.c.get_counts() # assuming 'c'
    
    best_backend = None
    best_fidelity = -1.0
    
    for name, backend in backends.items():
        print(f"Running on {name}...")
        
        # Transpile for specific backend to handle coupling map
        transpiled_qc = transpile(qc, backend, optimization_level=3)
        
        # Run using BackendSamplerV2 with the fake backend
        # Using AerSimulator.from_backend to simulate it is robust
        sim_backend = AerSimulator.from_backend(backend)
        sampler = BackendSamplerV2(backend=sim_backend)
        
        job = sampler.run([transpiled_qc], shots=shots)
        result = job.result()
        
        # Get counts
        # Register name might vary? usually 'c' if original only had one
        c_reg_name = list(result[0].data.keys())[0]
        noisy_counts = result[0].data[c_reg_name].get_counts()
        
        fid = calculate_hellinger_fidelity(ideal_counts, noisy_counts, shots)
        fidelities[name] = fid
        print(f"  > Fidelity: {fid:.4f}")
        
        if fid > best_fidelity:
            best_fidelity = fid
            best_backend = name
            
    # Save Best Topology
    with open('best_topology.txt', 'w') as f:
        f.write(f"Best Performing Topology: {best_backend}\n")
        f.write(f"Fidelity: {best_fidelity:.6f}\n")
        f.write(f"Circuit Target: {target}\n")
    print(f"Saved best topology to best_topology.txt")
    
    # Plotting
    plt.figure(figsize=(10, 6))
    names = list(fidelities.keys())
    vals = list(fidelities.values())
    
    plt.bar(names, vals, color=['#4285F4', '#DB4437', '#F4B400']) # Google colors for fun
    plt.ylabel('Hellinger Fidelity')
    plt.title(f'Topology Comparison (4-Qubit Grover, Target={target})')
    plt.ylim(0, 1.0)
    for i, v in enumerate(vals):
        plt.text(i, v + 0.01, f"{v:.3f}", ha='center')
        
    plt.savefig('topology_comparison.png')
    print("Saved plot: topology_comparison.png")
    
if __name__ == "__main__":
    run_experiment_1_noise_sweep()
    run_experiment_2_topology()
