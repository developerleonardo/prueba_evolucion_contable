from fastapi import FastAPI, File, UploadFile
from lectura_csv import leer_csv, COLUMNAS_FACTURAS, COLUMNAS_CONTABILIDAD
from reglas import convertir_numeros, regla_iva

app = FastAPI(title="prueba_evolucion_contable")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/procesar")
def procesar(facturas: UploadFile = File(...), contabilidad: UploadFile = File(...)):
    df_facturas = leer_csv(facturas, COLUMNAS_FACTURAS, "facturas")
    df_contabilidad = leer_csv(contabilidad, COLUMNAS_CONTABILIDAD, "contabilidad")

    df_facturas = convertir_numeros(df_facturas)
    df_facturas["causa_iva"] = regla_iva(df_facturas)

    errores_iva = df_facturas[df_facturas["causa_iva"] != ""]

    return {
        "facturas": {
            "columnas": df_facturas.columns.tolist(),
            "filas": len(df_facturas),
        },
        "contabilidad": {
            "columnas": df_contabilidad.columns.tolist(),
            "filas": len(df_contabilidad),
        },
        "errores_iva": errores_iva[["id_factura", "causa_iva"]].to_dict(orient="records")
    }