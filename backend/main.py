from fastapi import FastAPI, File, UploadFile
from lectura_csv import leer_csv, COLUMNAS_FACTURAS, COLUMNAS_CONTABILIDAD
from reglas import convertir_numeros, regla_iva, regla_total

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
    df_facturas["causa_total"] = regla_total(df_facturas)

    hay_error = (df_facturas["causa_iva"] != "") | (df_facturas["causa_total"] != "")
    registros_con_error = df_facturas[hay_error]

    return {
        "facturas": {
            "columnas": df_facturas.columns.tolist(),
            "filas": len(df_facturas),
        },
        "contabilidad": {
            "columnas": df_contabilidad.columns.tolist(),
            "filas": len(df_contabilidad),
        },
        "errores_iva": registros_con_error[["id_factura", "causa_iva", "causa_total"]].to_dict(orient="records")
    }