from fastapi import FastAPI, APIRouter


# Несколько примеров рецептов. На данный момент это просто и минимально, но служит нашим целям обучения.
RECIPES = [
    {
        "id": 1,
        "label": "Chicken Vesuvio",
        "source": "Serious Eats",
        "url": "http://www.seriouseats.com/recipes/2011/12/chicken-vesuvio-recipe.html",
    },
    {
        "id": 2,
        "label": "Chicken Paprikash",
        "source": "No Recipes",
        "url": "http://norecipes.com/recipe/chicken-paprikash/",
    },
    {
        "id": 3,
        "label": "Cauliflower and Tofu Curry Recipe",
        "source": "Serious Eats",
        "url": "http://www.seriouseats.com/recipes/2011/02/cauliflower-and-tofu-curry-recipe.html",
    },
]

# 1. Создали экземпляр объекта FastAPI, который представляет собой класс Python, предоставляющий все функции для API.
app = FastAPI(title="Recipe API", openapi_url="/openapi.json")

# 2. Создали экземпляр APIRouter, с помощью которого сгруппировали наши конечные точки API.
api_router = APIRouter()


# 3. Добавив @api_router.get("/", status_code=200) декоратор к функции root, определяем базовую точку GET для API.
@api_router.get("/", status_code=200)
def root() -> dict:
    """
    Root Get
    """
    return {"msg": "Hello, World!"}


# Моделируем выборку данных по идентификатору из базы данных. Затем данные сериализуются и возвращаются в формате JSON.
@api_router.get("/recipe/{recipe_id}", status_code=200)
def fetch_recipe(*, recipe_id: int) -> dict:
    """
     Fetch a single recipe by ID
    """

    result = [recipe for recipe in RECIPES if recipe["id"] == recipe_id]
    if result:
        return result[0]


# 4. Используем метод include_router для регистрации маршрутизатора, созданного на шаге 2, в объекте FastAPI.
app.include_router(api_router)


# 5. Если мы запускаем python app/main.py. Импортируем, uvicorn так как FastAPI зависит от этого веб-сервера.
if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")

