from fastapi import FastAPI

app = FastAPI()

from ROUTES import auth_router, arts_router

# Adicione abaixo as rotas que você estiver desenvolvendo

app.include_router(arts_router)