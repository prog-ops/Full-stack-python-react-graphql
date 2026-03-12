from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
import strawberry
from app.graphql.queries import Query
from app.graphql.mutations import Mutation
from app.database import init_db, get_db

# Init db table when app starts
init_db()

# Combine Query (and Mutation later) in one Schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# To insert db session into GraphQL context
async def get_context(db=Depends(get_db)):
    return {"db": db}

# GraphQL router
graphql_app = GraphQLRouter(schema, context_getter=get_context, multipart_uploads_enabled=True)

app = FastAPI(
    title="Inventory API",
    description="Python FastAPI Backend for Inventory with React frontend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Attach the route on endpoint "/graphql"
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Inventory API. Go to /graphql to explore."}