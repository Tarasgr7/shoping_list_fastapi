from .utils import *
from utils.auth_utils import *
from fastapi import status


app.dependency_overrides[get_db]=override_get_db
app.dependency_overrides[get_current_user]=override_get_current_user


def test_return_user(test_user):
  response=client.get("/user")
  assert response.status_code == status.HTTP_200_OK