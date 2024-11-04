import sys
import time

# Aumentar el límite de conversión de enteros a cadenas
sys.set_int_max_str_digits(0)

def fibonacci_iterativo(n):
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"--> Tiempo total de ejecución de '{func.__name__}': {elapsed_time:.4f} segundos")
        return result
    return wrapper

@timing_decorator
def fibonacci(n):
    return fibonacci_iterativo(n)

if __name__ == "__main__":
    print(f"fibonacci(50000) es {fibonacci(50000)}")  # Calcular Fibonacci sin problemas de recursión