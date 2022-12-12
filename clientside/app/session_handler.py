import functools
import typing as t

PROTECTED = ":shield:"

AUTH_404 = (
    "Your session is not authenticated! Please go to the **Welcome Page**. "
    "and follow the instruction on the side of the application. "
    "If you are new to the application please contact with the "
    "product owner/operations for an user manual or additional information."
)


def session_handler(func: t.Callable) -> t.Callable:
    """Use case handler to validate any use case"""

    @functools.wraps(func)
    def wrapper(ctx) -> None:
        if 'authenticated' in ctx.session_state and ctx.session_state['authenticated']:
            # Do something before
            func(ctx)
            # Do something after
        else:
            msg = f"{PROTECTED} {AUTH_404}"
            ctx.markdown(msg)
    return wrapper
