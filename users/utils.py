from Graston.settings import SECRET_KEY
import datetime
import jwt


def get_tokens(user):

    access_payload = {
        "user_id": user.id,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=61),
        "iat": datetime.datetime.now(datetime.UTC),
        "refresh": False,
    }

    refresh_payload = {
        "user_id": user.id,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=70),
        "iat": datetime.datetime.now(datetime.UTC),
        "refresh": True,
    }

    # remember to search about best encoding algorithm & add the algorithm name to .env file
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm="HS256")

    return access_token, refresh_token
