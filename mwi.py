from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, IBMQ, Aer, compile
import qiskit
import json
import time

name = 'TwoTargets'
sim = True
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

def multi_qubit(B_CNOT, C_CNOT, D_CNOT):
    A = QuantumRegister(1)
    B = QuantumRegister(1)
    C = QuantumRegister(1)
    D = QuantumRegister(1)

    a = ClassicalRegister(1)
    b = ClassicalRegister(1)
    c = ClassicalRegister(1)
    d = ClassicalRegister(1)

    qc = QuantumCircuit(A, B, C, D, a, b, c, d)

    qc.h(A[0])
    qc.barrier()

    qc.measure(A, a)
    qc.barrier()

    for i in range(0, B_CNOT):
        qc.cx(A[0], B[0])
        qc.barrier()
    for i in range(0, C_CNOT):
        qc.cx(A[0], C[0])
        qc.barrier()
    for i in range(0, D_CNOT):
        qc.cx(A[0], D[0])
        qc.barrier()

    qc.measure(B, b)
    qc.barrier()
    qc.measure(C, c)
    qc.barrier()
    qc.measure(D, d)

    return qc


def make_circuit(quantum_control=False, simplify=False,
        extra_measure=False, cnot_count=1, hadamard_count=1):
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

    for i in range(0, hadamard_count):
        qc.h(qA[0])
        qc.barrier()
    qc.measure(qA, cA0)
    qc.barrier()
    for i in range(0, cnot_count):
        if quantum_control:
            qc.cx(qA[0], qB[0])
            if m:
                qc.barrier()
                qc.measure(qA, cA1)
        else:
            qc.x(qB[0]).c_if(cA, 1)
        qc.barrier()
    qc.measure(qB, cB)
    return qc

IBMQ.load_accounts()
if sim:
    backend = Aer.get_backend('qasm_simulator')
else:
    backend = IBMQ.get_backend('ibmqx4')

n = 3
output = {"runs": []}
for i in range(0, n):
    for j in range(0, n):
        for k in range(0, n):
            print('starting circuit:', i, j, k)
            run = {}
            circuit = multi_qubit(i, j, k)
            qobj = compile(circuit, backend=backend, shots=shots, memory=True)
            compiled = qobj.as_dict()['experiments'][0]['header']['compiled_circuit_qasm']
            orig = circuit.qasm()
            run['original circuit'] = orig
            run['compiled circuit'] = compiled

            run['B CNOTS'] = i
            run['C CNOTS'] = j
            run['D CNOTS'] = k

            run['submit timestamp'] = time.time()
            job = backend.run(qobj)
            result = job.result()
            run['complete timestamp'] = time.time()

            run['memory'] = result.get_memory()
            run['counts'] = result.get_counts()
            run['backend'] = str(backend)
            run['shots'] = shots

            output['runs'].append(run)

output['qiskit version'] = qiskit.__version__
with open('mwi.py', 'r') as this_file:
    output['python source'] = this_file.read()

with open(name + '.json', 'w') as out_file:
    json.dump(output, out_file, sort_keys=True, separators=(',',':'), allow_nan=False)
    out_file.write('\n')
