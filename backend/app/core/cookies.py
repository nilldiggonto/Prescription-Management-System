from fastapi import Response

from app.core.config import Settings

ACCESS_TOKEN_COOKIE = "access_token"
CSRF_TOKEN_COOKIE = "csrf_token"


def set_auth_cookies(
    response: Response,
    *,
    access_token_raw: str,
    csrf_token: str,
    remember_me: bool,
    settings: Settings,
) -> None:
    max_age = (
        settings.access_token_remember_me_expire_days * 24 * 3600
        if remember_me
        else settings.access_token_expire_days * 24 * 3600
    )

    response.set_cookie(
        ACCESS_TOKEN_COOKIE,
        access_token_raw,
        max_age=max_age if remember_me else None,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
    )
    response.set_cookie(
        CSRF_TOKEN_COOKIE,
        csrf_token,
        max_age=max_age if remember_me else None,
        httponly=False,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
    )


def clear_auth_cookies(response: Response, settings: Settings) -> None:
    response.delete_cookie(ACCESS_TOKEN_COOKIE, path="/", secure=settings.cookie_secure, samesite=settings.cookie_samesite)
    response.delete_cookie(CSRF_TOKEN_COOKIE, path="/", secure=settings.cookie_secure, samesite=settings.cookie_samesite)
