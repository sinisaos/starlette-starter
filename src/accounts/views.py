import datetime
from settings import database, templates
from starlette.responses import RedirectResponse
from starlette.authentication import requires
from accounts.forms import RegistrationForm, LoginForm
from tables import (
    users,
    check_password,
    generate_jwt,
    hash_password,
    ADMIN
)


async def register(request):
    """
    Validate form, register and authenticate user with JWT token
    """
    query = users.select().order_by(users.c.id.desc())
    results = await database.fetch_all(query=query)
    data = await request.form()
    form = RegistrationForm(data)
    username = form.username.data
    email = form.email.data
    password = form.password.data
    if request.method == "POST" and form.validate():
        for result in results:
            if email == result["email"] or username == result["username"]:
                user_error = "User with that email or username already exists."
                return templates.TemplateResponse(
                    "accounts/register.html",
                    {
                        "request": request,
                        "form": form,
                        "user_error": user_error
                    },
                )
        query = users.insert().values(
            username=username,
            email=email,
            joined=datetime.datetime.now(),
            last_login=datetime.datetime.now(),
            login_count=1,
            password=hash_password(password),
        )
        await database.execute(query)
        user_query = users.select().where(users.c.username == username)
        user_results = await database.fetch_one(user_query)
        hashed_password = user_results["password"]
        valid_password = check_password(password, hashed_password)
        request.session["user"] = user_results["username"].capitalize()
        response = RedirectResponse(url="/", status_code=302)
        if valid_password:
            response.set_cookie(
                "jwt", generate_jwt(user_results["username"]), httponly=True
            )
        return response
    return templates.TemplateResponse(
        "accounts/register.html", {"request": request, "form": form}
    )


async def login(request):
    """
    Validate form, login and authenticate user with JWT token
    """
    data = await request.form()
    form = LoginForm(data)
    username = form.username.data
    password = form.password.data
    if request.method == "POST" and form.validate():
        try:
            query = users.select().where(users.c.username == username)
            results = await database.fetch_one(query)
            hashed_password = results["password"]
            valid_password = check_password(password, hashed_password)
            if not valid_password:
                user_error = "Invalid username or password"
                return templates.TemplateResponse(
                    "accounts/login.html",
                    {
                        "request": request, "form": form,
                        "user_error": user_error
                    },
                )
            request.session["user"] = results["username"].capitalize()
            # update login counter and login time
            update_query = users.update(users.c.username == username).values(
                login_count=users.c.login_count + 1,
                last_login=datetime.datetime.now()
            )
            await database.execute(update_query)
            response = RedirectResponse(url="/", status_code=302)
            response.set_cookie(
                "jwt", generate_jwt(results["username"]), httponly=True
            )
            return response
        except TypeError:
            user_error = "Please register you don't have account"
            return templates.TemplateResponse(
                "accounts/login.html",
                {"request": request, "form": form, "user_error": user_error},
            )
    return templates.TemplateResponse("accounts/login.html",
                                      {
                                          "request": request,
                                          "form": form
                                      })


@requires(["authenticated", ADMIN])
async def dashboard(request):
    if request.user.is_authenticated:
        auth_user = request.user.display_name
        query = users.select().order_by(users.c.id.desc())
        results = await database.fetch_all(query=query)
        return templates.TemplateResponse(
            "accounts/dashboard.html",
            {
                "request": request,
                "results": results,
                "auth_user": auth_user
            },
        )


@requires(["authenticated"])
async def profile(request):
    if request.user.is_authenticated:
        auth_user = request.user.display_name
        query = users.select().where(users.c.username == auth_user)
        results = await database.fetch_one(query)
        return templates.TemplateResponse(
            "accounts/profile.html",
            {
                "request": request,
                "results": results,
                "auth_user": auth_user
            },
        )


async def logout(request):
    request.session.clear()
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("jwt")
    return response
