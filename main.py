from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# A aplicação reúne as rotas por domínio e centraliza a configuração do acesso à API.
app = FastAPI()

from ROUTES import auth_router, arts_router, purchase_router, cart_router, user_router

app.include_router(auth_router)
app.include_router(arts_router)
app.include_router(purchase_router)
app.include_router(cart_router)
app.include_router(user_router)

origins = [
    "http://localhost:80",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
