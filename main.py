from fastapi import FastAPI

# Iniciando a API

app = FastAPI()

# Adicione abaixo as rotas que você estiver desenvolvendo. OBS: Adicione os imports das rotas abaixo, não adicione no começo do código.

from ROUTES import auth_router

app.include_router(auth_router)