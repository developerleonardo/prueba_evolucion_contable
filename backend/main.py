from fastapi import FastAPI, File, UploadFile
from lectura_csv import leer_csv, COLUMNAS_FACTURAS, COLUMNAS_CONTABILIDAD

app = FastAPI(title="prueba_evolucion_contable")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/procesar")
def procesar(facturas: UploadFile = File(...), contabilidad: UploadFile = File(...)):
    df_facturas = leer_csv(facturas, COLUMNAS_FACTURAS, "facturas")
    df_contabilidad = leer_csv(contabilidad, COLUMNAS_CONTABILIDAD, "contabilidad")

    return {
        "facturas": {
            "columnas": df_facturas.columns.tolist(),
            "filas": len(df_facturas),
        },
        "contabilidad": {
            "columnas": df_contabilidad.columns.tolist(),
            "filas": len(df_contabilidad),
        },
    }