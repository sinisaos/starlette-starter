import uvicorn
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.staticfiles import StaticFiles
from settings import SECRET_KEY, database, templates
from tables import UserAuthentication
from accounts.routes import routes

app = Starlette(debug=True)
app.mount("/static", StaticFiles(directory="../static"), name="static")
app.mount("/accounts", routes)
app.add_middleware(AuthenticationMiddleware, backend=UserAuthentication())
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


@app.route('/', methods=["GET"])
async def index(request):
    results = "Home page"
    return templates.TemplateResponse(
        "index.html", {"request": request, "results": results}
    )


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
