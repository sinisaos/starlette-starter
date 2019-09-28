from starlette.routing import Route, Router
from accounts.views import login, register, logout, dashboard, profile


routes = Router([
    Route("/login", endpoint=login, methods=["GET", "POST"], name="login"),
    Route("/register", endpoint=register,
          methods=["GET", "POST"], name="register"),
    Route("/logout", endpoint=logout, methods=["GET", "POST"], name="logout"),
    Route("/dashboard", endpoint=dashboard, methods=["GET"], name="dashboard"),
    Route("/profile", endpoint=profile, methods=["GET"], name="profile")
])
