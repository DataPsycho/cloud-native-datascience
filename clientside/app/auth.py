import logging


def add_auth_to_session(ctx, uid: str) -> None:
    """
    Add authentication into session
    :param ctx: Streamlit Module
    :param uid: The User ID to add
    :return: Boolean added or Not
    """
    try:
        ctx.session_state["authenticated"] = True
        ctx.session_state["uid"] = uid
    except Exception as e:
        logging.info(e)
