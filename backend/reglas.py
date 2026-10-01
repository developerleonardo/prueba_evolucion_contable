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

def regla_total(df: pd.DataFrame) -> list[str]:
    """total esperado = base gravable + IVA esperado - retención.
    Se usa el IVA recalculado."""
    mensajes = []
    for _, fila in df.iterrows():
        base = fila["base_gravable"]
        tarifa = fila["tarifa_iva"]
        retencion = fila["valor_retencion"]
        total_factura = fila["total_factura"]

        if pd.isna(base) or pd.isna(tarifa) or pd.isna(retencion) or pd.isna(total_factura):
            mensajes.append("")
            continue

        iva_esperado = round(base * tarifa)
        total_esperado = base + iva_esperado - retencion
        diferencia = total_factura - total_esperado

        if abs(diferencia) > TOLERANCIA:
            mensajes.append(
                f"Total incorrecto: esperado {total_esperado:,.0f}, "
                f"factura {total_factura:,.0f} (diferencia {diferencia:,.0f})"
            )
        else:
            mensajes.append("")
    return mensajes

def regla_duplicados(df: pd.DataFrame) -> list[str]:
    """Una factura está duplicada si su id aparece más de una vez
    en el archivo de facturas. Se marcan todas las filas repetidas."""
    ids = df["id_factura"].str.strip()
    es_duplicada = ids.duplicated(keep=False) & ids.notna()

    mensajes = []
    for id_factura, duplicada in zip(ids, es_duplicada):
        if duplicada:
            mensajes.append(f"Factura duplicada: el id {id_factura} aparece más de una vez en facturas")
        else:
            mensajes.append("")
    return mensajes


def regla_sin_contabilizar(df_facturas: pd.DataFrame, df_contabilidad: pd.DataFrame) -> list[str]:
    """La factura no tiene ningún registro en el archivo de contabilidad."""
    ids_contabilizados = set(df_contabilidad["id_factura"].dropna().str.strip())

    mensajes = []
    for id_factura in df_facturas["id_factura"].str.strip():
        if pd.notna(id_factura) and id_factura not in ids_contabilizados:
            mensajes.append("Sin registro contable: el id no aparece en contabilidad")
        else:
            mensajes.append("")
    return mensajes

    