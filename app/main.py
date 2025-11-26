from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.DB.session import get_db
from app.Routers.auth_router import auth_router
from fastapi.security import OAuth2PasswordBearer
from app.Routers.topic import topic_router
from app.Routers.trainer_topic import trainer_topic_router
import logging

logging.basicConfig(level=logging.DEBUG)

# Enable SQLAlchemy verbose logs
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
logging.getLogger("sqlalchemy.pool").setLevel(logging.INFO)
logging.getLogger("sqlalchemy.dialects").setLevel(logging.INFO)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
app.include_router(auth_router)
app.include_router(topic_router)
app.include_router(trainer_topic_router)