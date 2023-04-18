import secure
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.staticfiles import StaticFiles
from starlette.routing import Route
from tortoise.contrib.starlette import register_tortoise
from settings import templates, DB_URI, SECRET_KEY
from accounts.models import UserAuthentication
from accounts.routes import accounts_routes


# Security Headers are HTTP response headers that, when set,
# can enhance the security of your web application
# by enabling browser security policies.
# more on https://secure.readthedocs.io/en/latest/headers.html
secure_headers = secure.Secure()


async def index(request):
    results = "Home page"
    return templates.TemplateResponse(
        "index.html", {"request": request, "results": results}
    )


routes = [
    Route("/", index),
]


app = Starlette(debug=True, routes=routes)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/accounts", accounts_routes)
app.add_middleware(AuthenticationMiddleware, backend=UserAuthentication())
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# middleware for secure headers
@app.middleware("http")
async def set_secure_headers(request, call_next):
    response = await call_next(request)
    secure_headers.framework.starlette(response)
    return response


@app.exception_handler(404)
async def not_found(request, exc):
    """
    Return an HTTP 404 page.
    """
    template = "404.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context, status_code=404)


@app.exception_handler(500)
async def server_error(request, exc):
    """
    Return an HTTP 500 page.
    """
    template = "500.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context, status_code=500)


register_tortoise(
    app,
    db_url=DB_URI,
    modules={"models": ["accounts.models"]},
    generate_schemas=True,
)
