from fastapi import FastAPI, HTTPException
from starlette import status
from app.schema import UserMessage
import app.redis_db as redis_db
from app.config import settings
import requests

app = FastAPI(title=settings.PROJECT_NAME,
              version=settings.PROJECT_VERSION,
              root_path="/v1/dialogs"
              )


@app.post("/dialog/{from_user}/send/{to_user}")
def send_message_to_user(from_user: int, to_user: int, user_message: UserMessage):
    # token: str = Depends(dep.get_token)
    # user_id_from_token = dep.get_current_user(token)
    url = (f"http://{settings.DIALOG_UNREAD_MESSAGES_HOST}:{settings.DIALOG_UNREAD_MESSAGES_PORT}"
           f"{settings.DIALOG_UNREAD_ADD_URL}{from_user}/{to_user}")
    headers = {"Content-Type": "application/json"}

    try:
        if redis_db.redis_db_send_message_from_to(from_user, to_user, user_message.message):
            try:
                response = requests.post(url, headers=headers)
            except requests.exceptions.RequestException as e:
                print(f"An error occurred request: {e}, Status code {response.status_code}")
            return {"Message send": "ok", "from": from_user, "to": to_user}
        else:
            return {"Message send": "false"}
    except BaseException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User message not send"
        )


@app.post("/dialog/{from_user}/get/{to_user}")
def get_messages_from_to_user(from_user: int, to_user: int):
    # token: str = Depends(dep.get_token)
    # user_id_from_token = dep.get_current_user(token)

    try:
        result = redis_db.redis_db_get_user_messages(from_user, to_user)
        if result:
            return result
        else:
            return {"Message get": "false"}
    except BaseException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User dialog not found"
        )


@app.get("/dialog/{user_id}/list")
def get_all_messages_from_user(user_id: int):
    try:
        result_query = []
        for r in redis_db.redis_search_user_dialog(user_id):
            result_query.append(r)
        return result_query
    except BaseException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dialog not find"
        )
