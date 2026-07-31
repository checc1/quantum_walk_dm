from qiskit import QuantumCircuit, transpile
import os
import numpy as np
#from IPython.display import display
from tqdm import tqdm
from pathlib import Path
import scipy.stats as stats
from qiskit.circuit.library import QFT, unitary_overlap
from matplotlib import pyplot as plt
from qiskit.providers.basic_provider import BasicProvider
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import SamplerV2

from qiskit import qasm2

provider = BasicProvider()

def saveAccount():
    tokenNuovo = "1IGwM9BTW4nFEuVn0CaHILAKYzjVTc1XAgCFELHZn5Q1"
    QiskitRuntimeService.save_account(
        # overwrite=True,
        # instance="ibm-q/open/main",
        token=tokenNuovo,
        # channel="ibm_quantum"  # `channel` distinguishes between different account types
        #set_as_default=True,
        overwrite=True,
        #instance="crn:v1:bluemix:public:quantum-computing:us-east:a/51642a0a58bb4b1bab5ea597db326c14:9a5f743f-a145-4029-9464-da2dcbad65ea::"
        #instance = "crn:v1:bluemix:public:quantum-computing:us-east:a/ca46a7f2538849bbb47a7bbe23beea43:bb5d0a51-38aa-4e38-be02-6c14d9d75b7a::" # account Popo nuovo!
        #instance="crn:v1:bluemix:public:quantum-computing:us-east:a/5c6ac64dcd0640378ede92bbe092a13d:e4b0291b-85bd-4c23-88ae-779ac696a214::"
        # `channel` distinguishes between different account types
        instance = "crn:v1:bluemix:public:quantum-computing:us-east:a/6bfbebaf999944c09603aadaa9ec263e:ba15ee74-38c2-41ee-96c5-7d89458e8973::"

    )

def backendInfo():
    service = QiskitRuntimeService()
    backend = service.backend("ibm_torino")
    print(backend)


#saveAccount()
#backendInfo()

def generateCircQW(t, numPause, posQubits, coinQubit):
    # numQubits SONO I QUBITS DEI COLORI
    # coinQubit E' IL QUBIT DEL COIN
    # coin is the last qubit (index numQubits), the others previous numQubits (index from 0 to numQubits-1) are for state
    numQubits = len(posQubits)
    allQubits = posQubits + [coinQubit]
    #qreg = QuantumRegister(allQubits)
    #creg = ClassicalRegister(posQubits)
    circuit = QuantumCircuit(133, numQubits)
    #for q in range(numQubits):
    for q in posQubits:
        circuit.h(q)

    for currT in range(t):
        for i,q in enumerate(posQubits):
            circuit.p(-(2 * np.pi) / (2 ** (i + 1)), q)

        circuit.h(coinQubit)  # unbalanced
        # circuit.y(numQubits) #balanced

        for i,q in enumerate(posQubits[1:]):
            circuit.cp((2 * np.pi) / (2 ** (i + 1)), coinQubit, q)

        for i in range(numPause):
            for q in allQubits:
              #print(q)
              circuit.x(q)
              circuit.x(q)
                # circuit.id(q)

    qft = QFT(numQubits, do_swaps=False, inverse=True).to_gate()
    circuit.append(qft, qargs=posQubits)

    #circuit.append(qft.to_gate(), posQubits)  ### qui specifico alla QFT di agire sui qubits che dico io == allQubits

    # circuit.measure_all()
    for i, q in enumerate(posQubits):
        circuit.measure(q, i)

    return circuit

def generateCircQRWDoubleQFT(t, numPause, posQubits, numQubits):
    # coin is the last qubit (index numQubits), the others previous numQubits (index from 0 to numQubits-1) are for state

    circuit = QuantumCircuit(numQubits + 1, numQubits)

    qft = QFT(numQubits, do_swaps=False, inverse=False)
    circuit.append(qft.to_gate(), range(numQubits))

    for currT in range(t):
        for q in range(numQubits):
            circuit.p(-(2 * np.pi) / (2 ** (q + 1)), q)

        circuit.h(numQubits)  # unbalanced
        # circuit.y(numQubits) #balanced

        for q in range(1, numQubits):
            circuit.cp((2 * np.pi) / (2 ** q), numQubits, q)

        for i in range(numPause):
            for q in range(numQubits + 1):
                circuit.x(q)
                circuit.x(q)
                # circuit.id(q)

    iqft = QFT(numQubits, do_swaps=False, inverse=True)
    circuit.append(iqft.to_gate(), range(numQubits))

    # circuit.measure_all()
    for q in range(numQubits):
        circuit.measure(q, q)

    return circuit


saveAccount()
p = 0
#save = False
save = True
# posQubits = [0, 1, 4, 6, 5]
posQubits = [1, 2, 3, 5, 6, 16]
numQubits = len(posQubits)
# qubit_priority_list = [3, 6, 4, 1, 5, 0, 2]
qubit_priority_listTorino = list(range(133))
qubit_priority_listBrisbane = list(range(127))
qubit_priority_listFez = list(range(156))
qubit_priority_listMarrakech = list(range(156))
#starmon7_basis_gates = ['id', 'z', 's', 'sdg', 't', 'tdg', 'x', 'rx', 'y', 'ry', 'cz']
service = QiskitRuntimeService()
#backend = service.backend("ibm_brisbane")
backend = service.backend("ibm_torino")
#backend = service.backend("ibm_fez")
#backend = service.backend("ibm_marrakech")
numT = 30
numShots = 20_000
numStates = 2 ** numQubits
optimization = True
coinQubit = 4
onlyLastT = False
drawCircuits = False
#drawCircuits = True
drawTransCircuits = False
#drawTransCircuits = True
path = "/home/francesco/data/francesco_true/PycharmProjects/quantumDiffusionMedical/probs"
execute = True
#execute = False
circName = "circ"
quantDevice = "ibm_torino"
#quantDevice = "ibm_brisbane"
#quantDevice = "ibm_fez"
#quantDevice = "ibm_marrakech"
commonFileName = f"probs-quantRunJanuary27-{circName}-opt{optimization}-shots{numShots}-device{quantDevice}-numT{numT}-st{numStates}-p{p}-qubits{posQubits}"
#saveAccount()
print(f"Running {commonFileName}.npy")

probsT = 1

probs = np.zeros((numT, numStates))
probs[0, 0] = 1

sampler = SamplerV2(backend)

for t in tqdm(range(1, numT)):

    circ = generateCircQW(t, p, posQubits, coinQubit)

    if drawCircuits:
        fig = plt.figure()
        ax = fig.add_subplot()
        circ.draw('mpl', style="iqp", idle_wires=False, ax=ax)
        ax.set_title(f"t={t}")
        #plt.savefig(f"/content/circuitTstep{t}.png", dpi=300)
        plt.savefig(f"/home/francesco/PycharmProjects/quantumDiffusionMedical/circuits/circ{t}.png", dpi=300)
        plt.show(block=True)
        #display(circ.draw())

    # Transpile the ideal circuit to a circuit that can be directly executed by the backend
    if optimization:
        transpiled_circuit = transpile(circ, backend, optimization_level=3,
                                       initial_layout=qubit_priority_listTorino,)
    else:
        transpiled_circuit = transpile(circ, backend, optimization_level=0,
                                       initial_layout=qubit_priority_listTorino,)

    if drawTransCircuits:
        display(transpiled_circuit.draw())

        fig = plt.figure()
        ax = fig.add_subplot()
        transpiled_circuit.draw('mpl', style="iqp", idle_wires=False, ax=ax)
        ax.set_title(f"t={t}")
        plt.savefig(f"/home/francesco/PycharmProjects/quantumDiffusionMedical/circuits/circTranspM{t}.png", dpi=300)
        plt.show(block=True)

    if execute:
        job = sampler.run([transpiled_circuit], shots=numShots)
        pub_result = job.result()[0]
        counts = pub_result.data.c.get_counts()

        ### QUA SOTTO FUNZIONANO PER QUANTUM_INSPIRE, SOPRA PER REAL IBM MACHINE
        """job = backend.run(transpiled_circuit, shots=numShots)
        # job = backend.run(circ, shots=numShots)
        pub_result = job.result()
        counts = pub_result.get_counts()"""

        for i in range(numStates):
            key = bin(i)[2:].zfill(numQubits)
            if key in counts.keys():
                probs[probsT, i] = counts[key] / numShots

        probsT += 1

    if save:
        Path(path).mkdir(parents=True, exist_ok=True)
        saveFilename = os.path.join(path, f"{commonFileName}-PART{t}.npy")
        np.save(open(saveFilename, "wb"), probs)
        # print(f'Saved partial to {saveFilename}')

if save:
    Path(path).mkdir(parents=True, exist_ok=True)
    saveFilename = os.path.join(path, f"{commonFileName}.npy")
    np.save(open(saveFilename, "wb"), probs)
    print(f'Saved to {saveFilename}')

    print(f"KL(T): {stats.entropy(probs[-1], np.ones(numStates) / numStates):.3f}")