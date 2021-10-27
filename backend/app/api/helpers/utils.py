import json
import typing
from flask import Response

from app.database.models import db


def success(data: str):
    return Response(status=200, response=json.dumps(data), content_type="application/json")


def error(description: typing.Union[str, dict], status_code=502):
    return Response(status=status_code, response=json.dumps(description), content_type="application/json")
