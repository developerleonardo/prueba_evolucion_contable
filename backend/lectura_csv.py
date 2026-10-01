import pandas as pd
from fastapi import UploadFile, HTTPException

COLUMNAS_FACTURAS = [
    "id_factura", "nit_proveedor", "fecha_factura", "concepto",
    "base_gravable", "tarifa_iva", "valor_iva",
    "tarifa_retencion", "valor_retencion", "total_factura",
]

COLUMNAS_CONTABILIDAD = [
    "id_factura", "fecha_contabilizacion", "cuenta_contable",
    "centro_costo", "valor_debito", "valor_credito", "estado",
]

def leer_csv(archivo: UploadFile, columnas_requeridas: list[str], nombre: str) -> pd.DataFrame:
    """Lee un CSV y valida que tenga las columnas obligatorias."""

    # 1. Validar la extensión del archivo
    if not archivo.filename or not archivo.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail=f"El archivo de {nombre} debe ser un .csv")

    # 2. Leer el CSV
    try:
        df = pd.read_csv(archivo.file, encoding="utf-8-sig", dtype=str)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"No se pudo leer el archivo de {nombre}. Verifica que sea un CSV válido y no esté vacío.",
        )

    # 3. Quitar espacios en blanco de las columnas
    df.columns = df.columns.str.strip()

    # 4. Validar la presencia de las columnas obligatorias
    faltantes = [col for col in columnas_requeridas if col not in df.columns]
    if faltantes:
        raise HTTPException(
            status_code=400,
            detail=f"Al archivo de {nombre} le faltan las columnas: {', '.join(faltantes)}",
        )

    # 5. Validar que el dataframe no esté vacío
    if df.empty:
        raise HTTPException(status_code=400, detail=f"El archivo de {nombre} no tiene registros")

    return df