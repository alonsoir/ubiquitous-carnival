import aiohttp
import asyncio

# URLs de la API
urls = {
    "precios_completos": "https://api.preciodelaluz.org/v1/prices/all?zone=PCB",
    "precio_medio": "https://api.preciodelaluz.org/v1/prices/avg?zone=PCB",
    "precio_maximo": "https://api.preciodelaluz.org/v1/prices/max?zone=PCB",
    "precio_minimo": "https://api.preciodelaluz.org/v1/prices/min?zone=PCB",
    "precio_actual": "https://api.preciodelaluz.org/v1/prices/now?zone=PCB",
    "precios_economicos": "https://api.preciodelaluz.org/v1/prices/cheapests?zone=PCB&n=2"
}


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls.values()]
        results = await asyncio.gather(*tasks)

        # Procesar los resultados
        umbral_barato = 0.11  # Euros por kWh
        coste_acceso = 0.05  # Coste fijo por kWh

        # Variables para almacenar precios extremos
        max_precio = float('-inf')
        min_precio = float('inf')
        total_precio = 0
        count_precio = 0

        # Precio completo
        data_completo = results[0]
        print("------ Precios Completos ------")

        for hour, details in data_completo.items():
            date = details['date']
            hour_range = details['hour']
            price_mwh = details['price'] / 100  # Convertir de €/MWh a €/kWh
            price_kwh = price_mwh / 1000  # Convertir de €/MWh a €/kWh
            is_cheap = 'Sí' if details['is-cheap'] else 'No'

            # Calcular el precio total incluyendo impuestos y cargos
            precio_base = price_kwh
            impuesto_electricidad = precio_base * 0.0511  # Impuesto sobre la electricidad
            total_con_impuestos = precio_base + coste_acceso + impuesto_electricidad
            total_con_iva = total_con_impuestos * 1.21  # Añadir IVA

            print(f"Fecha: {date}, Hora: {hour_range}, Precio Base: {precio_base:.5f} €/kWh, Barato: {is_cheap}")
            print(f"Precio Total (con Acceso e Impuestos): {total_con_impuestos:.5f} €/kWh")
            print(f"Precio Final (con IVA): {total_con_iva:.5f} €/kWh")

            # Actualizar precios extremos
            if price_kwh < umbral_barato:
                print(f"Precio barato encontrado: {price_kwh:.5f} €/kWh")

            # Acumular para calcular el promedio
            total_precio += price_kwh
            count_precio += 1

            if price_kwh > max_precio:
                max_precio = price_kwh
                max_fecha_hora = f"{date} entre las {hour_range} horas"
                max_total_con_impuestos = total_con_impuestos
                max_total_con_iva = total_con_iva

            if price_kwh < min_precio:
                min_precio = price_kwh
                min_fecha_hora = f"{date} entre las {hour_range} horas"
                min_total_con_impuestos = total_con_impuestos
                min_total_con_iva = total_con_iva

            print("------")

        # Precio medio
        precio_medio = total_precio / count_precio if count_precio > 0 else 0

        print("------ Resumen ------")
        print(f"Precio Máximo: {max_precio:.5f} €/kWh en {max_fecha_hora}")
        print(f"Total (con Acceso e Impuestos): {max_total_con_impuestos:.5f} €/kWh")
        print(f"Total (con IVA): {max_total_con_iva:.5f} €/kWh")

        print(f"Precio Mínimo: {min_precio:.5f} €/kWh en {min_fecha_hora}")
        print(f"Total (con Acceso e Impuestos): {min_total_con_impuestos:.5f} €/kWh")
        print(f"Total (con IVA): {min_total_con_iva:.5f} €/kWh")

        print(f"Precio Medio: {precio_medio:.5f} €/kWh")

        # Precio actual
        print("------ Precio Actual ------")
        precio_actual = results[4]['price'] / 1000  # Convertir a €/kWh
        print(f"Precio Actual: {precio_actual:.5f} €/kWh")

        # Precios económicos
        print("------ Precios Más Económicos ------")

        if isinstance(results[5], list):
            for precio in results[5]:
                precio_economico = precio['price'] / 1000  # Convertir a €/kWh
                print(f"Precio Económico: {precio_economico:.5f} €/kWh")
        else:
            print("Error: La respuesta para precios económicos no es una lista.")


# Ejecutar el script principal
if __name__ == "__main__":
    asyncio.run(main())