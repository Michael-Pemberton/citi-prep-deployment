from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from banking_api.controllers.customers import router as customers_router
from banking_api.controllers.accounts import router as accounts_router
from banking_api.database import connect_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="Banking REST API",
    description="A Banking REST API built with FastAPI and MongoDB Atlas.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://citi-prep-deployment.vercel.app"],  # Restrict to your Vercel frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(customers_router)
app.include_router(accounts_router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "Banking API is running. Visit /docs for the interactive API explorer."}
