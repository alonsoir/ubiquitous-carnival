# Importar los módulos necesarios
from qiskit import QuantumCircuit, execute, Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# Crear un circuito cuántico
circuito = QuantumCircuit(1, 1)
circuito.h(0)
circuito.measure(0, 0)

# Mostrar el circuito
print("Circuito cuántico:")
print(circuito.draw())

# Ejecutar el circuito en el simulador
simulador = Aer.get_backend('qasm_simulator')
resultado = execute(circuito, backend=simulador, shots=1000).result()

# Obtener y mostrar los resultados
conteos = resultado.get_counts(circuito)
print("Resultados de la medición:", conteos)

# Graficar los resultados
plot_histogram(conteos)
plt.show()
