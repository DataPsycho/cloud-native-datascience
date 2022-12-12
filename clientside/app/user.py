import typing as t


def get_user_from_session(ctx: t.ClassVar) -> t.Union[None, str]:
    """
    Get user id form the streamlit session variable
    :param ctx: Streamlit module
    :return: User ID
    """
    if ctx.session_state.get("authenticated"):
        return ctx.session_state.get("uid")
    return None
