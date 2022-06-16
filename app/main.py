from fastapi import FastAPI


# Init application
app = FastAPI()

@app.get("/")
def root():
    return {"message":"Hello World"}
