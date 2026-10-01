import pandas as pd

# Diferencia máxima aceptada por redondeo
TOLERANCIA = 1

COLUMNAS_NUMERICAS = [
    "base_gravable", "tarifa_iva", "valor_iva",
    "tarifa_retencion", "valor_retencion", "total_factura",
]

def convertir_numeros(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte las columnas numéricas de texto a número.
    Si un valor no se puede convertir (o está vacío), queda como NaN."""
    df = df.copy()
    for columna in COLUMNAS_NUMERICAS:
        df[columna] = pd.to_numeric(df[columna], errors="coerce")
    return df

def regla_iva(df: pd.DataFrame) -> list[str]:
    """IVA esperado = base gravable x tarifa de IVA.
    Devuelve una lista con un texto por factura ('' si no hay problema)."""
    mensajes = []
    for _, fila in df.iterrows():
        base = fila["base_gravable"]
        tarifa = fila["tarifa_iva"]
        iva_factura = fila["valor_iva"]

        # Verificar que los datos estén completos
        if pd.isna(base) or pd.isna(tarifa) or pd.isna(iva_factura):
            mensajes.append("")
            continue

        iva_esperado = round(base * tarifa)
        diferencia = iva_factura - iva_esperado

        if abs(diferencia) > TOLERANCIA:
            mensajes.append(
                f"IVA incorrecto: esperado {iva_esperado:,.0f}, "
                f"factura {iva_factura:,.0f} (diferencia {diferencia:,.0f})"
            )
        else:
            mensajes.append("")
    return mensajes