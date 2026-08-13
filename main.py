from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

from ROUTES import auth_router, arts_router, purchase_router, cart_router, user_router

app.include_router(auth_router)
app.include_router(arts_router)
app.include_router(purchase_router)
app.include_router(cart_router)
app.include_router(user_router)

origins = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:80",
    "http://127.0.0.1:8080",
    "https://athena-frontend-83xp.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
