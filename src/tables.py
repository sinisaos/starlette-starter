import bcrypt
import jwt
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    DateTime,
    create_engine,
)
from datetime import datetime
from starlette.authentication import (
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
    AuthCredentials,
)
from settings import SECRET_KEY, DB_URI

# change this line to set another user as admin user
ADMIN = "admin"

engine = create_engine(DB_URI)

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer(), primary_key=True),
    Column("username", String(100), nullable=False),
    Column("email", String(100), nullable=False),
    Column("joined", DateTime(), default=datetime.now()),
    Column("last_login", DateTime(), default=datetime.now()),
    Column("login_count", Integer(), nullable=False),
    Column("password", String(100), nullable=False),
)

# add another tables here

metadata.create_all(engine)


class UserAuthentication(AuthenticationBackend):
    async def authenticate(self, request):
        jwt_cookie = request.cookies.get("jwt")
        if jwt_cookie:
            try:
                payload = jwt.decode(
                    jwt_cookie.encode("utf8"),
                    str(SECRET_KEY),
                    algorithms=["HS256"]
                )
                if SimpleUser(payload["user_id"]).username == ADMIN:
                    return (
                        AuthCredentials(["authenticated", ADMIN]),
                        SimpleUser(payload["user_id"]),
                    )
                else:
                    return (
                        AuthCredentials(["authenticated"]),
                        SimpleUser(payload["user_id"]),
                    )
            except AuthenticationError:
                raise AuthenticationError("Invalid auth credentials")
        else:
            # unauthenticated
            return


def hash_password(password: str):
    return bcrypt.hashpw(password, bcrypt.gensalt())


def check_password(password: str, hashed_password):
    return bcrypt.checkpw(password, hashed_password)


def generate_jwt(user_id):
    payload = {"user_id": user_id}
    token = jwt.encode(payload, str(SECRET_KEY),
                       algorithm="HS256").decode("utf-8")
    return token
