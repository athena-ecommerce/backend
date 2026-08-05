from fastapi import FastAPI

# Iniciando a API

app = FastAPI()

# Adicione abaixo as rotas que você estiver desenvolvendo. OBS: Adicione os imports das rotas abaixo, não adicione no começo do código.

from ROUTES import auth_router, arts_router, purchase_route, cart_router, user_router

app.include_router(auth_router)
app.include_router(arts_router)
app.include_router(purchase_route)
app.include_router(cart_router)
app.include_router(user_router)