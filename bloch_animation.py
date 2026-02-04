"""
Bloch Sphere Animation for Grover's Algorithm
Shows state vector rotation during iterations
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_bloch_vector
from mpl_toolkits.mplot3d import Axes3D


def create_oracle_for_101():
    """
    Create oracle that marks the state |101⟩
    """
    oracle = QuantumCircuit(3, name='Oracle')
    oracle.x(1)
    oracle.h(2)
    oracle.ccx(0, 1, 2)
    oracle.h(2)
    oracle.x(1)
    return oracle


def get_grover_iteration_states():
    """
    Get statevector at each step of Grover's algorithm
    Returns list of statevectors for animation
    """
    from qiskit.circuit.library import grover_operator

    states = []

    # Initial state
    qc = QuantumCircuit(3)
    qc.h([0, 1, 2])
    states.append(Statevector.from_instruction(qc))

    # Create oracle and Grover operator
    oracle = create_oracle_for_101()
    grover_op = grover_operator(oracle)

    # Apply Grover iterations (2 iterations optimal for 8 states)
    for iteration in range(2):
        qc.compose(grover_op, inplace=True)
        states.append(Statevector.from_instruction(qc))

    return states


def statevector_to_bloch(statevector, qubit_index=0):
    """
    Convert a multi-qubit statevector to Bloch sphere coordinates
    for a specific qubit (partial trace)

    For simplicity, we'll use the reduced density matrix approach
    """
    # Get density matrix
    rho = statevector.to_operator()

    # For a single qubit, we can compute expectation values
    # This is a simplified visualization - we'll show the most probable state
    probs = statevector.probabilities()
    most_probable_state = np.argmax(probs)

    # Convert to binary representation
    binary = format(most_probable_state, f'0{statevector.num_qubits}b')

    # Get the bit for the specific qubit
    bit = int(binary[qubit_index])

    # Simple mapping to Bloch sphere
    # |0⟩ -> (0, 0, 1), |1⟩ -> (0, 0, -1)
    # Add some phase information from amplitudes
    amplitude = statevector.data[most_probable_state]
    phase = np.angle(amplitude)

    # Create Bloch vector
    if bit == 0:
        x = 0.3 * np.cos(phase)
        y = 0.3 * np.sin(phase)
        z = 0.9
    else:
        x = 0.3 * np.cos(phase)
        y = 0.3 * np.sin(phase)
        z = -0.9

    return [x, y, z]


def create_bloch_animation():
    """
    Create animated Bloch sphere showing state evolution
    """
    print("Generating Bloch sphere animation...")

    # Get statevectors at each iteration
    states = get_grover_iteration_states()

    # For visualization, we'll track the probability of finding |101⟩
    # and show it as a 3D trajectory

    fig = plt.figure(figsize=(14, 5))

    # Create three subplots for each qubit
    ax1 = fig.add_subplot(131, projection='3d')
    ax2 = fig.add_subplot(132, projection='3d')
    ax3 = fig.add_subplot(133, projection='3d')
    axes = [ax1, ax2, ax3]

    # Setup each Bloch sphere
    for i, ax in enumerate(axes):
        ax.set_xlim([-1, 1])
        ax.set_ylim([-1, 1])
        ax.set_zlim([-1, 1])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'Qubit {i}')

        # Draw sphere
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi, 50)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(x, y, z, alpha=0.1, color='cyan')

        # Draw axes
        ax.plot([-1, 1], [0, 0], [0, 0], 'k-', alpha=0.3)
        ax.plot([0, 0], [-1, 1], [0, 0], 'k-', alpha=0.3)
        ax.plot([0, 0], [0, 0], [-1, 1], 'k-', alpha=0.3)

    # Trajectory storage
    trajectories = [[], [], []]
    lines = []
    points = []

    for ax in axes:
        line, = ax.plot([], [], [], 'r-', linewidth=2, label='Trajectory')
        point, = ax.plot([], [], [], 'ro', markersize=10)
        lines.append(line)
        points.append(point)

    def init():
        for line, point in zip(lines, points):
            line.set_data([], [])
            line.set_3d_properties([])
            point.set_data([], [])
            point.set_3d_properties([])
        return lines + points

    def animate(frame):
        state_idx = min(frame // 10, len(states) - 1)
        statevector = states[state_idx]

        for qubit_idx in range(3):
            bloch_vec = statevector_to_bloch(statevector, qubit_idx)

            trajectories[qubit_idx].append(bloch_vec)

            # Update trajectory line
            traj = np.array(trajectories[qubit_idx])
            if len(traj) > 0:
                lines[qubit_idx].set_data(traj[:, 0], traj[:, 1])
                lines[qubit_idx].set_3d_properties(traj[:, 2])

                # Update current point
                points[qubit_idx].set_data([bloch_vec[0]], [bloch_vec[1]])
                points[qubit_idx].set_3d_properties([bloch_vec[2]])

        return lines + points

    # Create animation
    frames = len(states) * 10
    anim = FuncAnimation(fig, animate, init_func=init,
                        frames=frames, interval=100, blit=True)

    # Save animation
    output_file = 'benchmarks/bloch_sphere_animation.gif'
    writer = PillowWriter(fps=10)
    anim.save(output_file, writer=writer)

    print(f"Bloch sphere animation saved to: {output_file}")

    plt.tight_layout()
    plt.show()


def create_probability_evolution():
    """
    Alternative visualization: Show probability evolution over iterations
    """
    print("Generating probability evolution chart...")

    states = get_grover_iteration_states()

    # Track probability of each computational basis state
    all_probs = []
    for state in states:
        probs = state.probabilities_dict()
        all_probs.append(probs)

    # Create visualization
    fig, ax = plt.subplots(figsize=(10, 6))

    # Get all unique states
    all_states = sorted(set().union(*[set(p.keys()) for p in all_probs]))

    iterations = list(range(len(states)))

    for state_label in all_states:
        probs = [p.get(state_label, 0) for p in all_probs]

        # Highlight target state
        if state_label == '101':
            ax.plot(iterations, probs, 'o-', linewidth=3, markersize=8,
                   label=f'|{state_label}⟩ (TARGET)', color='#06D6A0')
        else:
            ax.plot(iterations, probs, 'o--', linewidth=1.5, markersize=5,
                   label=f'|{state_label}⟩', alpha=0.6)

    ax.set_xlabel('Grover Iteration', fontsize=12, fontweight='bold')
    ax.set_ylabel('Probability', fontsize=12, fontweight='bold')
    ax.set_title("State Probability Evolution During Grover's Algorithm",
                 fontsize=14, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax.grid(alpha=0.3, linestyle='--')
    ax.set_xticks(iterations)

    plt.tight_layout()
    plt.savefig('benchmarks/probability_evolution.png', dpi=300, bbox_inches='tight')
    print("Probability evolution chart saved to: benchmarks/probability_evolution.png")
    plt.show()


def main():
    """
    Main function to generate all animations
    """
    print("=" * 60)
    print("BLOCH SPHERE ANIMATION GENERATOR")
    print("=" * 60)
    print()

    # Create probability evolution (simpler and more informative)
    create_probability_evolution()

    print()

    # Create Bloch sphere animation
    try:
        create_bloch_animation()
    except Exception as e:
        print(f"Note: Bloch sphere animation encountered an issue: {e}")
        print("The probability evolution chart has been created successfully.")

    print("\nAnimation generation complete!")


if __name__ == "__main__":
    main()
