# core/utils.py
import re

def parse_price_string(price_str: str) -> float:
    """
    Convierte una cadena de precio con separadores de miles a un float.
    Ejemplos: "1.500.000" -> 1500000.0, "1,500,000.50" -> 1500000.50
    """
    if not isinstance(price_str, str):
        return 0.0
    # Eliminar separadores de miles (puntos o comas)
    cleaned_str = re.sub(r'[.,](?=\d{3})', '', price_str)
    # Reemplazar la coma decimal por un punto si es necesario
    cleaned_str = cleaned_str.replace(',', '.')
    try:
        return float(cleaned_str)
    except (ValueError, TypeError):
        return 0.0
