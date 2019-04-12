from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, IBMQ, Aer
import qiskit

sim = False
shots = 8192

def cnot_test(quantity, flip):
    qA = QuantumRegister(1)
    qB = QuantumRegister(1)
    cA = ClassicalRegister(1)
    cB = ClassicalRegister(1)
    qc = QuantumCircuit(qA, qB, cA, cB)
    
    if flip:
        qc.x(qA[0])

    for i in range(0, quantity):
        qc.barrier()
        qc.cx(qA[0], qB[0])
    qc.barrier()
    qc.measure(qA, cA)
    qc.measure(qB, cB)
    return qc

def make_circuit(flip=True, quantum_control=False, simplify=False, extra_measure=False):
    qA = QuantumRegister(1)
    cA0 = ClassicalRegister(1)
    qB = QuantumRegister(1)
    cB = ClassicalRegister(1)
    m = quantum_control and extra_measure
    if not m:
        qc = QuantumCircuit(qA, qB, cA0, cB)
    else:
        cA1 = ClassicalRegister(1)
        cA2 = ClassicalRegister(1)
        qc = QuantumCircuit(qA, qB, cA0, cA1, cA2, cB)

    qc.h(qA[0])
    qc.barrier()
    qc.measure(qA, cA0)
    if flip:
        qc.barrier()
        if quantum_control:
            qc.cx(qA[0], qB[0])
            if m:
                qc.barrier()
                qc.measure(qA, cA1)
        else:
            qc.x(qB[0]).c_if(cA, 1)
        qc.barrier()
    else:
        if quantum_control:
            if not simplify:
                qc.barrier()
                qc.cx(qA[0], qB[0])
                qc.barrier()
                if m:
                    qc.measure(qA, cA1)
                    qc.barrier()
                qc.cx(qA[0], qB[0])
                qc.barrier()
                if m:
                    qc.measure(qA, cA2)
                    qc.barrier()
            else:
                qc.barrier()
        else:
            qc.barrier()
            qc.iden(qB[0]).c_if(cA, 1)
            qc.barrier()
    qc.measure(qB, cB)
    return qc

IBMQ.load_accounts()
if sim:
    backend = Aer.get_backend('qasm_simulator')
else:
    backend = IBMQ.get_backend('ibmqx4')

#circuit = make_circuit(flip=True, quantum_control=True, simplify=False, extra_measure=True)
circuit = cnot_test(2, True)
print("Running circuit:")
print(circuit.draw('text'))
print("for", shots, "shots on backend", backend, "with result:");

job = qiskit.execute(circuit, backend=backend, shots=shots)

result = job.result()

print(result.get_counts(circuit))
print("\n")