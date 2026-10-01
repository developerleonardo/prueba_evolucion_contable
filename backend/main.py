from fastapi import FastAPI, File, UploadFile
from lectura_csv import leer_csv, COLUMNAS_FACTURAS, COLUMNAS_CONTABILIDAD
from reglas import convertir_numeros, regla_iva, regla_total, regla_duplicados, regla_sin_contabilizar

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
    df_facturas["causa_duplicados"] = regla_duplicados(df_facturas)
    df_facturas["causa_sin_contabilizar"] = regla_sin_contabilizar(df_facturas, df_contabilidad)

    columnas_causa = ["causa_iva", "causa_total", "causa_duplicados", "causa_sin_contabilizar"]
    hay_error = (df_facturas[columnas_causa] != "").any(axis=1)
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
        "errores_iva": registros_con_error[["id_factura"] + columnas_causa].to_dict(orient="records")
    }