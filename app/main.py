from fastapi import FastAPI, APIRouter, Query, HTTPException
from typing import Optional, Any

from app.schemas import RecipeSearchResults, Recipe, RecipeCreate
from app.recipe_data import RECIPES


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
@api_router.get("/recipe/{recipe_id}", status_code=200, response_model=Recipe)
def fetch_recipe(*, recipe_id: int) -> Any:
    """
     Fetch a single recipe by ID
    """

    result = [recipe for recipe in RECIPES if recipe["id"] == recipe_id]
    if not result:
        # Если рецепт не найден, мы поднимаем HTTPException передачу status_code404
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {recipe_id} not found"
        )
    return result[0]


# Создаём GET конечная точку /search/. Обратите внимание, что у него нет параметров пути
@api_router.get("/search/", status_code=200)  # определяет логику для новой конечной точки.
def search_recipes(
    *,
    keyword: Optional[str] = Query(None, min_length=3, example="chicken"),
    max_results: Optional[int] = 10) \
    -> dict:
    """
    Search for recipes based on label keyword
    """
    if not keyword:
        # we use Python list slicing to limit results
        # based on the max_results query parameter
        return {"results": RECIPES[:max_results]}

    results = filter(lambda recipe: keyword.lower() in recipe["label"].lower(), RECIPES)
    return {"results": list(results)[:max_results]}


# New addition, using Pydantic model `RecipeCreate` to define
# the POST request body
@api_router.post("/recipe/", status_code=201, response_model=Recipe)
def create_recipe(*, recipe_in: RecipeCreate) -> dict:
     """Create a new recipe (in memory only)"""
     new_entry_id = len(RECIPES) + 1
     recipe_entry = Recipe(
        id=new_entry_id,
        label=recipe_in.label,
        source=recipe_in.source,
        url=recipe_in.url,
     )
     RECIPES.append(recipe_entry.dict())

     return recipe_entry


# 4. Используем метод include_router для регистрации маршрутизатора, созданного на шаге 2, в объекте FastAPI.
app.include_router(api_router)


# 5. Если мы запускаем python app/main.py. Импортируем, uvicorn так как FastAPI зависит от этого веб-сервера.
if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")

