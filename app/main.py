from fastapi import FastAPI, APIRouter


# Создали экземпляр объекта FastAPI app, который представляет собой класс Python, предоставляющий все функции для API.
app = FastAPI(
    title="Recipe API", openapi_url="/openapi.json"
)

# 2
api_router = APIRouter()

# 3
@api_router.get("/", status_code=200)
def root() -> dict:
    """
    Root Get
    """
    return {"msg": "Hello, World!"}

# 4
app.include_router(api_router)


# 5
if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")

