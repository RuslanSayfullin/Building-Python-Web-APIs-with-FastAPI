from fastapi import FastAPI, APIRouter


# 1. Создали экземпляр объекта FastAPI, который представляет собой класс Python, предоставляющий все функции для API.
app = FastAPI(
    title="Recipe API", openapi_url="/openapi.json"
)

# 2. Создали экземпляр APIRouter, с помощью которого сгруппировали наши конечные точки API.
api_router = APIRouter()


# 3. Добавив @api_router.get("/", status_code=200) декоратор к функции root, определяем базовую точку GET для API.
@api_router.get("/", status_code=200)
def root() -> dict:
    """
    Root Get
    """
    return {"msg": "Hello, World!"}


# 4. Используем метод include_router для регистрации маршрутизатора, созданного на шаге 2, в объекте FastAPI.
app.include_router(api_router)


# 5. Если мы запускаем python app/main.py. Импортируем, uvicorn так как FastAPI зависит от этого веб-сервера.
if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")

