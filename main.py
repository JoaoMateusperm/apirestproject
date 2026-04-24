from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Primeiro projeto"}

print("Atualização do Teste!")