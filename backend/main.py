from fastapi import FastAPI

app = FastAPI(title="prueba_evolucion_contable")

@app.get("/health")
def health():
    return {"status": "ok"}