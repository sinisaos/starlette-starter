import datetime
from settings import templates, BASE_HOST
from starlette.responses import RedirectResponse
from starlette.authentication import requires
from utils import pagination
from accounts.forms import RegistrationForm, LoginForm
from accounts.models import (
    User,
    check_password,
    generate_jwt,
    hash_password,
    ADMIN,
)


async def register(request):
    """
    Validate form, register and authenticate user with JWT token
    """
    results = await User.all()
    data = await request.form()
    form = RegistrationForm(data)
    username = form.username.data
    email = form.email.data
    password = form.password.data
    if request.method == "POST" and form.validate():
        for result in results:
            if email == result.email or username == result.username:
                user_error = "User with that email or username already exists."
                return templates.TemplateResponse(
                    "accounts/register.html",
                    {
                        "request": request,
                        "form": form,
                        "user_error": user_error
                    },
                )
        query = User(
            username=username,
            email=email,
            joined=datetime.datetime.now(),
            last_login=datetime.datetime.now(),
            login_count=1,
            password=hash_password(password),
        )
        await query.save()
        user_query = await User.get(
            username=username)
        hashed_password = user_query.password
        valid_password = check_password(password, hashed_password)
        response = RedirectResponse(url="/", status_code=302)
        if valid_password:
            response.set_cookie(
                "jwt", generate_jwt(user_query.username), httponly=True
            )
            response.set_cookie(
                "admin", ADMIN, httponly=True
            )
        return response
    return templates.TemplateResponse(
        "accounts/register.html", {
            "request": request,
            "form": form
        }
    )


async def login(request):
    """
    Validate form, login and authenticate user with JWT token
    """
    path = request.query_params['next']
    data = await request.form()
    form = LoginForm(data)
    username = form.username.data
    password = form.password.data
    if request.method == "POST" and form.validate():
        try:
            results = await User.get(
                username=username)
            hashed_password = results.password
            valid_password = check_password(password, hashed_password)
            if not valid_password:
                user_error = "Invalid username or password"
                return templates.TemplateResponse(
                    "accounts/login.html",
                    {
                        "request": request,
                        "form": form,
                        "user_error": user_error
                    },
                )
            # update login counter and login time
            results.login_count += 1
            results.last_login = datetime.datetime.now()
            await results.save()
            response = RedirectResponse(BASE_HOST + path, status_code=302)
            response.set_cookie(
                "jwt", generate_jwt(results.username), httponly=True
            )
            response.set_cookie(
                "admin", ADMIN, httponly=True
            )
            return response
        except:  # noqa
            user_error = "Please register you don't have account"
            return templates.TemplateResponse(
                "accounts/login.html",
                {
                    "request": request,
                    "form": form,
                    "user_error": user_error,
                },
            )
    return templates.TemplateResponse("accounts/login.html", {
        "request": request,
        "form": form,
        "path": path
    })


@requires("authenticated")
async def user_delete(request):
    """
    Delete user
    """
    id = request.path_params["id"]
    if request.method == "POST":
        await User.get(id=id).delete()
        if request.user.username == ADMIN:
            return RedirectResponse(url="/accounts/dashboard", status_code=302)
        request.session.clear()
        response = RedirectResponse(url="/", status_code=302)
        response.delete_cookie("jwt")
        return response


@requires(["authenticated", ADMIN], redirect="index")
async def dashboard(request):
    auth_user = request.user.display_name
    page_query = pagination.get_page_number(url=request.url)
    count = await User.all().count()
    paginator = pagination.Pagination(page_query, count)
    results = (
        await User.all()
        .limit(paginator.page_size)
        .offset(paginator.offset())
    )
    page_controls = pagination.get_page_controls(
        url=request.url,
        current_page=paginator.current_page(),
        total_pages=paginator.total_pages()
    )
    return templates.TemplateResponse(
        "accounts/dashboard.html",
        {
            "request": request,
            "results": results,
            "auth_user": auth_user,
            "page_controls": page_controls,
            "count": count
        },
    )


@requires("authenticated", redirect="index")
async def profile(request):
    if request.user.is_authenticated:
        auth_user = request.user.display_name
        results = await User.get(username=auth_user)
        return templates.TemplateResponse(
            "accounts/profile.html",
            {
                "request": request,
                "results": results,
                "auth_user": auth_user,
            }
        )


async def logout(request):
    request.session.clear()
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("jwt")
    return response
