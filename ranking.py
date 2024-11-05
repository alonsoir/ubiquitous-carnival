import matplotlib.pyplot as plt

# Datos de las escalas con valores de diferentes teorías
nombres = [
    "Preon (Teoría M)",             # 10^-33 m a 10^-18 m
    "Quarks (Teoría M)",            # 10^-18 m a 10^-19 m
    "Partículas fermiónicas (Estándar)",  # 10^-15 m a 10^-18 m
    "Partículas bosónicas (Estándar)",     # 10^-15 m a 10^-18 m
    "Brana fundamental (Teoría M)", # 10^-33 m a 10^-18 m
    "Forma de Calabi-Yau (Teoría de Cuerdas)", # 10^-7 m a 10^-6 m
    "Longitud de Planck (Gravedad Cuántica de Bucles)" # 1.616 x 10^-35 m
]

# Rangos de tamaños en metros según las teorías
tamaños = [
    (10**-33, 10**-18),   # Preon (Teoría M)
    (10**-19, 10**-18),   # Quarks (Teoría M)
    (10**-18, 10**-15),   # Partículas fermiónicas (Estándar)
    (10**-18, 10**-15),   # Partículas bosónicas (Estándar)
    (10**-33, 10**-18),   # Brana fundamental (Teoría M)
    (10**-7, 10**-6),     # Forma de Calabi-Yau (Teoría de Cuerdas)
    (1.616e-35, 1.616e-35)# Longitud de Planck (Gravedad Cuántica de Bucles)
]

# Crear el gráfico
plt.figure(figsize=(10, 6))
plt.barh(nombres, [max(size) - min(size) for size in tamaños], color='skyblue')
plt.xscale('log')
plt.xlabel('Rango de Tamaño (m)')
plt.title('Ranking de Estructuras Fundamentales y Tamaños Según Teorías')
plt.axvline(x=1.616e-35, color='red', linestyle='--', label='Longitud de Planck (1.616 x 10^-35 m)')
plt.legend()
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.savefig('fundamental_structure_sizes_theories.png')